# DOTO: merge this into utils.py
import logging
import math
import unicodedata
from decimal import Decimal
from functools import partial
from functools import reduce

from pyproj import Proj
from pyproj import transform as proj_transform
from shapely.geometry.base import BaseGeometry
from shapely.ops import transform as shape_transform
from shapely.wkt import dumps as shape_dumps
from shapely.wkt import loads as shape_loads

log = logging.getLogger(__name__)

# pylint: disable=invalid-name

PROJECTIONS = {}

# Rounding to abount 0.1 meters
COORDINATES_DECIMALS_FOR_METRIC_PROJ = 1
COORDINATES_DECIMALS_FOR_DEGREE_PROJ = 6

# Number of element in an iterator


def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def format_search_text(input_str):
    return remove_accents(escape_sphinx_syntax(input_str))


def format_locations_search_text(input_str):
    if input_str is None:
        return input_str
    # only remove trailing and leading dots
    input_str = ' '.join([w.strip('.') for w in input_str.split()])
    # remove double quotation marks
    input_str = input_str.replace('"', '')
    return format_search_text(input_str)


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


def get_proj_from_srid(srid):
    if srid in PROJECTIONS:
        return PROJECTIONS[srid]

    proj = Proj(init=f'EPSG:{srid}')
    PROJECTIONS[srid] = proj
    return proj


def get_precision_for_proj(srid):
    precision = COORDINATES_DECIMALS_FOR_METRIC_PROJ
    proj = get_proj_from_srid(srid)
    if proj.is_latlong():
        precision = COORDINATES_DECIMALS_FOR_DEGREE_PROJ
    return precision


def _round_bbox_coordinates(bbox, precision=None):
    tpl = f'%.{precision}f'
    if precision is not None:
        return [float(Decimal(tpl % c)) for c in bbox]
    return bbox


def _round_shape_coordinates(shape, precision=None):
    if precision is None:
        return shape

    return shape_loads(shape_dumps(shape, rounding_precision=precision))


def round_geometry_coordinates(geom, precision=None):
    if isinstance(geom, (
        list,
        tuple,
    )):
        return _round_bbox_coordinates(geom, precision=precision)
    if isinstance(geom, BaseGeometry):
        return _round_shape_coordinates(geom, precision=precision)
    return geom


def _transform_point(coords, srid_from, srid_to):
    proj_in = get_proj_from_srid(srid_from)
    proj_out = get_proj_from_srid(srid_to)
    return proj_transform(proj_in, proj_out, coords[0], coords[1])


def transform_round_geometry(geom, srid_from, srid_to, rounding=True):
    if srid_from == srid_to:
        if rounding:
            precision = get_precision_for_proj(srid_to)
            return round_geometry_coordinates(geom, precision=precision)
        return geom
    if isinstance(geom, (
        list,
        tuple,
    )):
        return _transform_coordinates(geom, srid_from, srid_to, rounding=rounding)
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
    except Exception as e:
        raise e from ValueError(
            f"Cannot transform coordinates {coordinates} from {srid_from} to {srid_to}"
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


# only used in test_search. DOTO
def shift_to_lv95(string_coords):
    coords = string_coords.split(',')
    for idx, coord in enumerate(coords):  # pylint: disable=unused-variable
        if idx % 2:
            coords[idx] = float(coords[idx]) + 1e6
        else:
            coords[idx] = float(coords[idx]) + 2e6
    return ','.join([str(c) for c in coords])
