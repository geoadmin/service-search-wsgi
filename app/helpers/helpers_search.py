# -*- coding: utf-8 -*-

import datetime
import gzip
import logging
import math
import re
import unicodedata
import xml.etree.ElementTree as etree
from decimal import Decimal
from functools import partial
from io import BytesIO
from io import StringIO
from urllib.parse import quote
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import urlunparse

import requests
import six
import unidecode
from pyproj import Proj
from pyproj import transform as proj_transform
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPRequestTimeout
from pyramid.i18n import get_locale_name
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_url
from requests.exceptions import ConnectionError
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shape_transform
from shapely.wkt import dumps as shape_dumps
from shapely.wkt import loads as shape_loads
from six.moves import reduce
from six.moves import zip

unicode = str
long = int

log = logging.getLogger(__name__)

PROJECTIONS = {}

# Rounding to abount 0.1 meters
COORDINATES_DECIMALS_FOR_METRIC_PROJ = 1
COORDINATES_DECIMALS_FOR_DEGREE_PROJ = 6


def to_utf8(data):
    try:
        data = data.decode('utf8')
    except (UnicodeDecodeError, AttributeError):
        pass
    return data


# Number of element in an iterator


# used by validation_search.py and search.py
def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def versioned(path):
    version = get_current_registry().settings['app_version']
    entry_path = get_current_registry().settings['entry_path'] + '/'
    if version is not None:
        agnosticPath = make_agnostic(path)
        parsedURL = urlparse(agnosticPath)
        # we don't do version when behind pserve (at localhost)
        if 'localhost:' not in parsedURL.netloc:
            parts = parsedURL.path.split(entry_path, 1)
            if len(parts) > 1:
                parsedURL = parsedURL._replace(
                    path=parts[0] + entry_path + version + '/' + parts[1]
                )
                agnosticPath = urlunparse(parsedURL)
        return agnosticPath
    else:
        return path


def make_agnostic(path):
    handle_path = lambda x: x.split('://')[1] if len(x.split('://')) == 2 else path
    if path.startswith('http'):
        path = handle_path(path)
        return '//' + path
    else:
        return path


def make_api_url(request, agnostic=False):
    base_path = request.registry.settings['apache_base_path']
    base_path = '' if base_path == 'main' else '/' + base_path
    host = request.host + base_path if 'localhost' not in request.host else request.host
    if agnostic:
        return ''.join(('//', host))
    return ''.join((request.scheme, '://', host))


def make_geoadmin_url(request, agnostic=False):
    protocol = request.scheme
    base_url = ''.join((protocol, '://', request.registry.settings['geoadminhost']))
    if agnostic:
        return make_agnostic(base_url)
    return base_url


def resource_exists(path, headers={'User-Agent': 'mf-geoadmin/python'}, verify=False):
    try:
        r = requests.head(path, headers=headers, verify=verify)
    except ConnectionError:
        return False
    return r.status_code == requests.codes.ok


def check_url(url, config):
    if url is None:
        raise HTTPBadRequest('The parameter url is missing from the request')
    parsedUrl = urlparse(url)
    hostname = parsedUrl.hostname
    if hostname is None:
        raise HTTPBadRequest('Could not determine the hostname')
    domain = ".".join(hostname.split(".")[-2:])
    allowed_hosts = config['shortener.allowed_hosts'] if 'shortener.allowed_hosts' in config else ''
    allowed_domains = config['shortener.allowed_domains'
                            ] if 'shortener.allowed_domains' in config else ''
    if domain not in allowed_domains and hostname not in allowed_hosts:
        raise HTTPBadRequest(
            'Shortener can only be used for %s domains or %s hosts.' %
            (allowed_domains, allowed_hosts)
        )
    return url


def sanitize_url(url):
    sanitized = url
    try:
        sanitized = urljoin(url, urlparse(url).path.replace('//', '/'))
    except Exception:
        pass
    return sanitized


def locale_negotiator(request):
    try:
        lang = request.params.get('lang')
    except UnicodeDecodeError:  # pragma: no cover
        raise HTTPBadRequest(
            'Could not parse URL and parameters. Request send must be encoded in utf-8.'
        )
    # This might happen if a POST request is aborted before all the data could be transmitted
    except IOError:  # pragma: no cover
        raise HTTPRequestTimeout('Request was aborted. Didn\'t receive full request')

    settings = get_current_registry().settings
    languages = settings['available_languages'].split()
    if lang == 'rm':
        return 'fi'
    elif lang is None or lang not in languages:
        if request.accept_language:
            return request.accept_language.best_match(languages, 'de')
        # the default_locale_name configuration variable
        return get_locale_name(request)
    return lang


# used by search.py
def format_search_text(input_str):
    return remove_accents(escape_sphinx_syntax(input_str))


# used by search.py
def format_locations_search_text(input_str):
    if input_str is None:
        return input_str
    # only remove trailing and leading dots
    input_str = ' '.join([w.strip('.') for w in input_str.split()])
    # remove double quotation marks
    input_str = input_str.replace('"', '')
    return format_search_text(input_str)


# used by format_search_text used by search.py
def remove_accents(input_str):
    if input_str is None:
        return input_str
    input_str = input_str.replace(u'ü', u'ue')
    input_str = input_str.replace(u'Ü', u'ue')
    input_str = input_str.replace(u'ä', u'ae')
    input_str = input_str.replace(u'Ä', u'ae')
    input_str = input_str.replace(u'ö', u'oe')
    input_str = input_str.replace(u'Ö', u'oe')
    return ''.join(
        c for c in unicodedata.normalize('NFD', input_str) if unicodedata.category(c) != 'Mn'
    )


# indirectly used by search
def escape_sphinx_syntax(input_str):
    if input_str is None:
        return input_str
    input_str = input_str.replace('|', '\\|')
    input_str = input_str.replace('!', '\\!')
    input_str = input_str.replace('@', '\\@')
    input_str = input_str.replace('&', '\\&')
    input_str = input_str.replace('~', '\\~')
    input_str = input_str.replace('^', '\\^')
    input_str = input_str.replace('=', '\\=')
    input_str = input_str.replace('/', '\\/')
    input_str = input_str.replace('(', '\\(')
    input_str = input_str.replace(')', '\\)')
    input_str = input_str.replace(']', '\\]')
    input_str = input_str.replace('[', '\\[')
    input_str = input_str.replace('*', '\\*')
    input_str = input_str.replace('<', '\\<')
    input_str = input_str.replace('$', '\\$')
    input_str = input_str.replace('"', '\"')
    return input_str


# used by _transform_point used by search.py
def get_proj_from_srid(srid):
    if srid in PROJECTIONS:
        return PROJECTIONS[srid]
    else:
        proj = Proj(init='EPSG:{}'.format(srid))
        PROJECTIONS[srid] = proj
        return proj


# indirectly used by search.py
def get_precision_for_proj(srid):
    precision = COORDINATES_DECIMALS_FOR_METRIC_PROJ
    proj = get_proj_from_srid(srid)
    if proj.is_latlong():
        precision = COORDINATES_DECIMALS_FOR_DEGREE_PROJ
    return precision


# indirectly used by search.py
def _round_bbox_coordinates(bbox, precision=None):
    tpl = '%.{}f'.format(precision)
    if precision is not None:
        return [float(Decimal(tpl % c)) for c in bbox]
    else:
        return bbox


# indirectly used by search.py
def _round_shape_coordinates(shape, precision=None):
    if precision is None:
        return shape
    else:
        return shape_loads(shape_dumps(shape, rounding_precision=precision))


# used by transform_round_geometry used by search.py
def round_geometry_coordinates(geom, precision=None):
    if isinstance(geom, (
        list,
        tuple,
    )):
        return _round_bbox_coordinates(geom, precision=precision)
    elif isinstance(geom, BaseGeometry):
        return _round_shape_coordinates(geom, precision=precision)
    else:
        return geom


# used by search.py
def _transform_point(coords, srid_from, srid_to):
    proj_in = get_proj_from_srid(srid_from)
    proj_out = get_proj_from_srid(srid_to)
    return proj_transform(proj_in, proj_out, coords[0], coords[1])


# used by search.py
def transform_round_geometry(geom, srid_from, srid_to, rounding=True):
    if (srid_from == srid_to):
        if rounding:
            precision = get_precision_for_proj(srid_to)
            return round_geometry_coordinates(geom, precision=precision)
        return geom
    if isinstance(geom, (
        list,
        tuple,
    )):
        return _transform_coordinates(geom, srid_from, srid_to, rounding=rounding)
    else:
        return _transform_shape(geom, srid_from, srid_to, rounding=rounding)


# used by transform_round_geometry used by search.py
# Reprojecting pairs of coordinates and rounding them if necessary
# Only a point or a line are considered
def _transform_coordinates(coordinates, srid_from, srid_to, rounding=True):
    if len(coordinates) % 2 != 0:
        raise ValueError
    new_coords = []
    coords_iter = iter(coordinates)
    try:
        for pnt in zip(coords_iter, coords_iter):
            new_pnt = _transform_point(pnt, srid_from, srid_to)
            new_coords += new_pnt
        if rounding:
            precision = get_precision_for_proj(srid_to)
            new_coords = _round_bbox_coordinates(new_coords, precision=precision)
    except Exception:
        raise ValueError(
            "Cannot transform coordinates {} from {} to {}".format(coordinates, srid_from, srid_to)
        )
    return new_coords


# indirectly used by search.py
def _transform_shape(geom, srid_from, srid_to, rounding=True):
    proj_in = get_proj_from_srid(srid_from)
    proj_out = get_proj_from_srid(srid_to)

    projection_func = partial(proj_transform, proj_in, proj_out)

    new_geom = shape_transform(projection_func, geom)
    if rounding:
        precision = get_precision_for_proj(srid_to)
        return _round_shape_coordinates(new_geom, precision=precision)
    return new_geom


# float('NaN') does not raise an Exception. This function does.


# used by validation_search.py
def float_raise_nan(val):
    ret = float(val)
    if math.isnan(ret):
        raise ValueError('nan is not considered valid float')
    return ret


# used by search.py
def parse_box2d(stringBox2D):
    extent = stringBox2D.replace('BOX(', '').replace(')', '').replace(',', ' ')
    # Python2/3
    box = map(float, extent.split(' '))
    if not isinstance(box, list):
        box = list(box)
    return box


# used by center_from_box_2d used by search.py
def is_box2d(box2D):
    # Python2/3
    if not isinstance(box2D, list):
        box2D = list(box2D)
    # Bottom left to top right only
    if len(box2D) != 4 or box2D[0] > box2D[2] or box2D[1] > box2D[3]:
        raise ValueError('Invalid box2D.')
    return box2D


# used by search.py
def center_from_box2d(box2D):
    box2D = is_box2d(box2D)
    return [box2D[0] + ((box2D[2] - box2D[0]) / 2), box2D[1] + ((box2D[3] - box2D[1]) / 2)]


# used by validation_search.py and search.py
def shift_to(coords, srid):
    cds = []
    x_offset = 2e6
    y_offset = 1e6
    coords_copy = coords[:]
    while len(coords_copy) > 0:
        c = coords_copy.pop(0)
        if not isinstance(c, (int, float)):
            raise TypeError('Coordinates should be of type int or float')
        if srid == 2056:
            cds.append(c + x_offset if len(coords_copy) % 2 else c + y_offset)
        elif srid == 21781:
            cds.append(c - x_offset if len(coords_copy) % 2 else c - y_offset)
    return cds
