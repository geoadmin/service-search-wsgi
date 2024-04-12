import logging
import re

import pyproj.exceptions
from shapely.geometry import Point
from shapely.geometry import box
from shapely.geometry import mapping
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import GatewayTimeout
from werkzeug.exceptions import InternalServerError
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import ServiceUnavailable

from app.helpers import mortonspacekey as msk
from app.helpers.db import get_translation
from app.helpers.helpers_search import center_from_box2d
from app.helpers.helpers_search import format_locations_search_text
from app.helpers.helpers_search import format_search_text
from app.helpers.helpers_search import get_transformer
from app.helpers.helpers_search import ilen
from app.helpers.helpers_search import parse_box2d
from app.helpers.helpers_search import shift_to
from app.helpers.helpers_search import \
    transform_round_geometry as transform_shape
from app.helpers.validation_search import SearchValidation
from app.lib import sphinxapi
from app.settings import GEODATA_STAGING
from app.settings import SEARCH_SPHINX_HOST
from app.settings import SEARCH_SPHINX_PORT
from app.settings import SEARCH_SPHINX_TIMEOUT

logger = logging.getLogger(__name__)

# pylint: disable=invalid-name


class Search(SearchValidation):  # pylint: disable=too-many-instance-attributes

    LOCATION_LIMIT = 50
    LAYER_LIMIT = 30
    FEATURE_LIMIT = 20
    DEFAULT_SRID = 21781
    BBOX_SEARCH_LIMIT = 150

    def __init__(self, request, topic):
        super().__init__(request)

        self.topic_name = topic
        self.has_topic(self.topic_name)

        self.lang = 'de'
        if 'lang' in request.args:
            self.lang = request.args['lang']
        else:
            lang = request.accept_languages.best_match(self.availableLangs)
            if lang:
                self.lang = lang

        self.searchLang = request.args.get('searchLang')
        self.cbName = request.args.get('callback')
        # Order matters define srid first
        self.srid = request.args.get('sr', str(self.DEFAULT_SRID))
        self.bbox = request.args.get('bbox')
        self.sortbbox = request.args.get('sortbbox', 'true').lower() == 'true'
        self.returnGeometry = request.args.get('returnGeometry', 'true').lower() == 'true'
        self.quadindex = None
        self.origins = request.args.get('origins')
        self.featureIndexes = request.args.get('features')
        self.timeInstant = request.args.get('timeInstant')
        self.timeEnabled = request.args.get('timeEnabled')
        self.timeStamps = request.args.get('timeStamps')
        self.typeInfo = request.args.get('type')
        self.limit = request.args.get('limit')

        self.results = {'results': []}
        self.request = request

        morton_box = [420000, 30000, 900000, 510000]
        self.quadtree = msk.QuadTree(msk.BBox(*morton_box), 20)
        self.sphinx = sphinxapi.SphinxClient()
        self.sphinx.SetServer(SEARCH_SPHINX_HOST, SEARCH_SPHINX_PORT)
        self.sphinx.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)

    # is being called from routes.py directly
    def view_find_geojson(self):
        (features, bbox) = self._find_geojson()
        bounds = bbox.bounds if bbox is not None else None
        return {"type": "FeatureCollection", "bbox": bounds, "features": features}

    # is being called from routes.py directly
    @staticmethod
    def view_find_esrijson():
        raise BadRequest("Param 'geometryFormat=esrijson' is not supported")

    def _find_geojson(self):
        features = []
        features_bbox = None
        for item in self.search()['results']:
            if 'attrs' in item and 'id' in item and 'weight' in item:
                attributes = item['attrs']
                attributes['id'] = item['id']
                attributes['weight'] = item['weight']
                if attributes['origin'] != 'layer':
                    # Already reprojected
                    bounds = parse_box2d(attributes['geom_st_box2d'])
                else:
                    try:
                        # This is the requested QuadTree,
                        # because sphinx layer indices do not have extent
                        bounds = self.quadtree.bbox.bounds
                        bounds = transform_shape(bounds, self.DEFAULT_SRID, self.srid)
                    except ValueError as e:
                        msg = f"Search error: cannot reproject result to SRID: {self.srid}"
                        logger.error(msg, e)
                        raise InternalServerError(msg) from e
                bbox = box(*bounds)
                if features_bbox is None:
                    features_bbox = bbox
                else:
                    features_bbox.union(bbox)
                if 'x' in attributes.keys() and 'y' in attributes.keys():
                    feature = {
                        'type': 'Feature',
                        'id': item['id'],
                        'bbox': bbox.bounds,
                        'geometry': {
                            'type': 'Point', 'coordinates': [attributes['x'], attributes['y']]
                        },
                        'properties': attributes
                    }
                else:
                    feature = {
                        'type': 'Feature',
                        'id': item['id'],
                        'bbox': bbox.bounds,
                        'geometry': mapping(bbox),
                        'properties': attributes
                    }

                features.append(feature)
        return (features, features_bbox)

    # is being called from routes.py directly
    def search(self):
        self.sphinx.SetConnectTimeout(SEARCH_SPHINX_TIMEOUT)
        # create a quadindex if the bbox is defined
        if self.bbox is not None and self.typeInfo not in ('layers', 'featuresearch'):
            self._get_quad_index()
        if self.typeInfo == 'layers':
            # search all layers
            self.searchText = format_search_text(self.request.args.get('searchText'))
            self._layer_search()
        elif self.typeInfo == 'featuresearch':
            # search all features using searchText
            self.searchText = format_search_text(self.request.args.get('searchText'))
            self._feature_search()
        elif self.typeInfo in ('locations'):
            self.searchText = format_locations_search_text(self.request.args.get('searchText', ''))
            # swiss search
            self._swiss_search()
            # translate some gazetteer categories from swissnames3
            # tagged with <i>...</i> in the label attribute of the response
        return self.results

    def _fuzzy_search(self, searchTextFinal):
        logger.debug("Search fuzzy; searchText=%s", searchTextFinal)
        # We use different ranking for fuzzy search
        # For ranking modes, see http://sphinxsearch.com/docs/current.html#weighting
        self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_SPH04)
        # Only include results with a certain weight. This might need tweaking
        self.sphinx.SetFilterRange('@weight', 5000, 2**32 - 1)
        try:
            if self.typeInfo in ('locations'):
                results = self.sphinx.Query(searchTextFinal, index='swisssearch_fuzzy')
        except IOError as error:
            logger.exception('Failed to run query: %s', error)
            raise GatewayTimeout() from error

        if results is None:
            error = "Failed to run sphinx query"
            if self.sphinx.GetLastError():
                error += f": {self.sphinx.GetLastError()}"
            logger.error(error)
            raise ServiceUnavailable(description=error)

        results = results['matches']
        self.results['fuzzy'] = 'true'
        return results

    def _swiss_search(self):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals
        logger.debug("Search locations (swiss search); searchText=%s", self.searchText)

        limit = self.limit if self.limit and \
            self.limit <= self.LOCATION_LIMIT else self.LOCATION_LIMIT
        # Define ranking mode
        if self.bbox is not None and self.sortbbox:
            coords = self._get_geoanchor_from_bbox()
            self.sphinx.SetGeoAnchor('lat', 'lon', coords[1], coords[0])  # pylint: disable=unsubscriptable-object
            self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@geodist ASC')
            limit = self.limit if self.limit and \
                self.limit <= self.BBOX_SEARCH_LIMIT else self.BBOX_SEARCH_LIMIT
            logger.debug("SetGeoAnchor lat = %s, lon = %s", coords[1], coords[0])  # pylint: disable=unsubscriptable-object
        else:
            self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, 'rank ASC, @weight DESC, num ASC')
            logger.debug("SetRankingMode to wordcount")

        self.sphinx.SetLimits(0, limit)

        # Filter by origins if needed
        if self.origins is None:
            self._detect_keywords()
            # by default filter all available origins/ranks
            self.sphinx.SetFilter('rank', [1, 2, 3, 4, 5, 6, 7, 8, 10])
        else:
            self._filter_locations_by_origins()

        searchList = []
        if ilen(self.searchText) >= 1:
            searchText = self._query_fields('@detail')
            searchList.append(searchText)

        if self.bbox is not None:
            geomFilter = self._get_quadindex_string()
            searchList.append(geomFilter)

        if len(searchList) == 2:
            searchTextFinal = '(' + searchList[0] + ') & (' + searchList[1] + ')'
        elif len(searchList) == 1:
            searchTextFinal = searchList[0]

        if len(searchList) != 0:
            # wildcard search only if more than one character in searchtext
            if len(' '.join(self.searchText)) > 1 or self.bbox:
                # standard wildcard search
                self.sphinx.AddQuery(searchTextFinal, index='swisssearch')

            # exact prefix search, first 10 results
            searchText = '@detail "^{}"'.format(' '.join(self.searchText))  # pylint: disable=consider-using-f-string
            self.sphinx.AddQuery(searchText, index='swisssearch')

            try:
                results = self.sphinx.RunQueries()
            except IOError as error:
                logger.exception('Failed to run queries: %s', error)
                raise GatewayTimeout() from error

            # In case RunQueries doesn't return results (reason unknown)
            # related to issue
            if results is None:
                error = "Failed to run sphinx queries"
                if self.sphinx.GetLastError():
                    error += f": {self.sphinx.GetLastError()}"
                logger.error(error)
                raise ServiceUnavailable(description=error)

            wildcard_results = results[0].get('matches', [])
            merged_results = []
            if len(results) == 2:
                # we have results from both queries (exact + wildcard)
                # prepend exact search results to wildcard search result
                exact_results = results[1].get('matches', [])
                # exact matches have priority over prefix matches
                # searchText=waldhofstrasse+1
                # waldhofstrasse 1 -> weight 100
                # waldhofstrasse 1.1 -> weight 1
                for result in exact_results:
                    detail = result['attrs']['detail']
                    search_text_joined = ' '.join(self.searchText).lower()
                    if (
                        detail.startswith(f"{search_text_joined} ") or
                        detail == ' '.join(self.searchText).lower()
                    ):
                        result['weight'] += 99
                merged_results = exact_results + wildcard_results
            else:
                # we have results from one or no query
                merged_results = wildcard_results
            # remove duplicate from sphinx results, exact search results have priority over
            # wildcard search results
            results = []
            seen = []
            for d in merged_results:
                if d['id'] not in seen:
                    results.append(d)
                    seen.append(d['id'])

            # if standard index did not find anything, use soundex/metaphon indices
            # which should be more fuzzy in its results
            if len(results) <= 0:
                results = self._fuzzy_search(searchTextFinal)
        else:
            results = []
        if results is not None and len(results) != 0:
            self._parse_location_results(results, limit)

    def _layer_search(self):
        logger.debug("Search layer; searchText=%s", self.searchText)

        def staging_filter(staging):
            '''
            only layers in correct staging are searched
            translating staging to data_staging
            dev -> test
            int -> integration
            prod -> prod
            Args:
                String with the staging
            Return:
                String with the query for an explicit staging
            '''
            ret = '@staging prod'
            if staging in ('int', 'dev'):
                ret += ' | @staging integration'
                if staging == 'dev':
                    ret += ' | @staging test'
            return ret

        # 10 features per layer are returned at max
        layerLimit = (
            self.limit if self.limit and self.limit <= self.LAYER_LIMIT else self.LAYER_LIMIT
        )
        self.sphinx.SetLimits(0, layerLimit)
        self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
        self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@weight DESC')
        # Weights defaults to 1
        self.sphinx.SetFieldWeights({'@title': 4, '@detail': 2, '@layer': 1})

        index_name = f'layers_{self.lang}'
        topic_name = self.topic_name if self.topic_name != 'all' else ''
        # Whitelist hack
        if topic_name in ('api'):
            topicFilter = 'api'
        else:
            topicFilter = f'({topic_name} | ech)'
        searchText = ' '.join([
            self._query_fields('@(title,detail,layer)'),
            f'& @topics {topicFilter}',  # Filter by topic if string not empty, ech whitelist hack
            f'& {staging_filter(GEODATA_STAGING)}'  # Only layers in correct staging are searched
        ])
        try:
            results = self.sphinx.Query(searchText, index=index_name)
        except IOError as error:
            logger.exception('Failed to run queries: %s', error)
            raise GatewayTimeout() from error

        if results is None:
            error = "Failed to run sphinx query"
            if self.sphinx.GetLastError():
                error += f": {self.sphinx.GetLastError()}"
            logger.error(error)
            raise ServiceUnavailable(description=error)

        results = results['matches']
        if results is not None and len(results) != 0:
            self.results['results'] += results

    def _get_quadindex_string(self):
        ''' Recursive and inclusive search through
            quadindex windows. '''
        if self.quadindex is not None:
            buildQuadQuery = lambda x: ''.join(('@geom_quadindex ', x, ' | '))
            if len(self.quadindex) == 1:
                quadSearch = ''.join(('@geom_quadindex ', self.quadindex, '*'))
            else:
                quadSearch = ''.join(('@geom_quadindex ', self.quadindex, '* | '))
                quadSearch += ''.join(
                    buildQuadQuery(self.quadindex[:-x]) for x in range(1, len(self.quadindex))
                )[:-len(' | ')]
            return quadSearch
        return ''

    def _feature_search(self):
        logger.debug("Search feature; searchText=%s", self.searchText)

        # all features in given bounding box
        if self.featureIndexes is None:
            logger.error("No layername is given. Needed is bounding box and layer name")
            raise BadRequest('Bad request: no layername given')
        featureLimit = (
            self.limit if self.limit and self.limit <= self.FEATURE_LIMIT else self.FEATURE_LIMIT
        )
        self.sphinx.SetLimits(0, featureLimit)
        self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
        if self.bbox and self.sortbbox:
            coords = self._get_geoanchor_from_bbox()
            self.sphinx.SetGeoAnchor('lat', 'lon', coords[1], coords[0])  # pylint: disable=unsubscriptable-object
            self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@weight DESC, @geodist ASC')
            logger.debug("SetGeoAnchor lat = %s, lon = %s", coords[1], coords[0])  # pylint: disable=unsubscriptable-object
        else:
            self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@weight DESC')
            logger.debug("SetSortMode to sort extended with weight DESC")

        timeFilter = self._get_time_filter()
        if self.searchText:
            searchdText = self._query_fields('@detail')
        else:
            searchdText = ''
        self._add_feature_queries(searchdText, timeFilter)
        try:
            results = self.sphinx.RunQueries()
        except IOError as error:  # pragma: no cover
            logger.error('Failed to get sphinx queries: %s', error)
            raise GatewayTimeout() from error
        finally:
            self.sphinx.ResetFilters()

        if results:
            self._parse_feature_results(results)
        else:
            error = "Failed to run sphinx queries"
            if self.sphinx.GetLastError():
                error += f": {self.sphinx.GetLastError()}"
            logger.error(error)
            raise ServiceUnavailable(description=error)

    def _get_time_filter(self):
        self._check_timeparameters()
        years = []
        t = None
        timeInterval = re.search(r'((\b\d{4})-(\d{4}\b))', ' '.join(self.searchText)) or False
        # search for year with getparameter timeInstant=2010
        if self.timeInstant is not None:
            years = [self.timeInstant]
            t = 'instant'
        elif self.timeStamps is not None:
            years = self.timeStamps
            t = 'layers'
        # search for year interval with searchText Pattern .*YYYY-YYYY.*
        elif timeInterval:
            numbers = [timeInterval.group(2), timeInterval.group(3)]
            start = min(numbers)
            stop = max(numbers)
            # remove time intervall from searchtext
            self.searchText.remove(timeInterval.group(1))
            if min != max:
                t = 'range'
                years = [start, stop]
        return {'type': t, 'years': years}

    def _check_timeparameters(self):
        if self.timeInstant is not None and self.timeStamps is not None:
            msg = 'You are not allowed to mix timeStamps and timeInstant parameters'
            logger.error(
                "%s, timeInstant=%s, timeStamps=%s", msg, self.timeInstant, self.timeStamps
            )
            raise BadRequest(msg)

    def _get_geoanchor_from_bbox(self):
        transformer = get_transformer(self.DEFAULT_SRID, 4326)
        center = center_from_box2d(self.bbox)
        return transformer.transform(center[0], center[1])

    def _query_fields(self, fields):  # pylint: disable=too-many-locals
        # 10a, 10b needs to be interpreted as digit
        q = []
        isdigit = lambda x: bool(re.match('^[0-9]', x))
        hasDigit = bool(len([x for x in self.searchText if isdigit(x)]) > 0)
        hasNonDigit = bool(len([x for x in self.searchText if not isdigit(x)]) > 0)

        prefix_non_digit = lambda x: x if isdigit(x) else ''.join((x, '*'))
        infix_non_digit = lambda x: x if isdigit(x) else ''.join(('*', x, '*'))

        if hasNonDigit:
            exactAll = ' '.join(self.searchText)
            preNonDigit = ' '.join([prefix_non_digit(w) for w in self.searchText])
            infNonDigit = ' '.join([infix_non_digit(w) for w in self.searchText])
            q = [
                f'{fields} "{exactAll}"',
                f'{fields} "^{exactAll}"',
                f'{fields} "{exactAll}$"',
                f'{fields} "^{exactAll}$"',
                f'{fields} "{exactAll}"~5',
                f'{fields} "{preNonDigit}"',
                f'{fields} "^{preNonDigit}"',
                f'{fields} "{preNonDigit}"~5',
                f'{fields} "{infNonDigit}"',
                f'{fields} "^{infNonDigit}"',
                f'{fields} "{infNonDigit}"~5'
            ]

        if hasDigit:
            prefix_digit = lambda x: x if not isdigit(x) else ''.join((x, '*'))
            prefix_all = lambda x: ''.join((x, '*'))
            preDigit = ' '.join([prefix_digit(w) for w in self.searchText])
            preNonDigitAndPreDigit = ' '.join([prefix_all(w) for w in self.searchText])
            infNonDigitAndPreDigit = ' '.join([
                prefix_digit(infix_non_digit(w)) for w in self.searchText
            ])
            q = q + [
                f'{fields} "{preDigit}"',
                f'{fields} "^{preDigit}"',
                f'{fields} "{preNonDigitAndPreDigit}"',
                f'{fields} "{preNonDigitAndPreDigit}"~5',
                f'{fields} "{infNonDigitAndPreDigit}"'
            ]
        finalQuery = ' | '.join(q)
        return finalQuery

    @staticmethod
    def _origin_to_layerbodid(origin):
        origins2LayerBodId = {
            'zipcode': 'ch.swisstopo-vd.ortschaftenverzeichnis_plz',
            'gg25': 'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill',
            'district': 'ch.swisstopo.swissboundaries3d-bezirk-flaeche.fill',
            'kantone': 'ch.swisstopo.swissboundaries3d-kanton-flaeche.fill',
            'address': 'ch.bfs.gebaeude_wohnungs_register'
        }
        if origin in origins2LayerBodId:
            return origins2LayerBodId[origin]
        return None

    @staticmethod
    def _origins_to_ranks(origins):
        origin2Rank = {
            'zipcode': [1],
            'gg25': [2],
            'district': [3],
            'kantone': [4],
            'gazetteer': [5, 6],  # Not used, also 7
            'address': [7],
            'haltestellen': [8],
            'parcel': [10]
        }
        ranks = []
        try:
            for origin in origins:
                ranks += origin2Rank[origin]
        except KeyError as e:  # pragma: no cover
            msg = f'Bad value(s) in parameter origins {e}'
            logger.error(msg)
            raise BadRequest(msg) from e
        return ranks

    def _search_lang_to_filter(self):
        return {'de': [1], 'fr': [2], 'it': [3], 'rm': [4]}[self.searchLang]

    def _detect_keywords(self):
        if ilen(self.searchText) > 0:
            PARCEL_KEYWORDS = ('parzelle', 'parcelle', 'parcella', 'parcel')
            ADDRESS_KEYWORDS = ('addresse', 'adresse', 'indirizzo', 'address')
            firstWord = self.searchText[0].lower()
            if firstWord in PARCEL_KEYWORDS:
                # As one cannot apply filters on string attributes, we use the rank information
                self.sphinx.SetFilter('rank', self._origins_to_ranks(['parcel']))
                del self.searchText[0]
                logger.debug("SetFilter rank to parcel")
            elif firstWord in ADDRESS_KEYWORDS:
                self.sphinx.SetFilter('rank', self._origins_to_ranks(['address']))
                del self.searchText[0]
                logger.debug("SetFilter rank to address")

    def _filter_locations_by_origins(self):
        ranks = self._origins_to_ranks(self.origins)
        self.sphinx.SetFilter('rank', ranks)

    def _add_feature_queries(self, queryText, timeFilter):
        translated_layer = 'ch_bfs_gebaeude_wohnungs_register'
        for i, index in enumerate(self.featureIndexes):
            self.sphinx.ResetFiltersOnly()
            if timeFilter and self.timeEnabled is not None and self.timeEnabled[i]:
                if timeFilter['type'] == 'instant':
                    self.sphinx.SetFilter('year', timeFilter['years'])
                elif timeFilter['type'] == 'layers' and timeFilter['years'][i] is not None:
                    self.sphinx.SetFilter('year', [timeFilter['years'][i]])
                elif timeFilter['type'] == 'range':
                    self.sphinx.SetFilterRange(
                        'year', int(min(timeFilter['years'])), int(max(timeFilter['years']))
                    )
                logger.debug("SetFilter to year")
            if index.startswith(translated_layer):
                if self.searchLang:
                    self.sphinx.SetFilter('lang', self._search_lang_to_filter())
                    logger.debug("SetFilter to lang")
                else:
                    self.sphinx.SetFilter('agnostic', [1])
                    logger.debug("SetFilter to agnostic")
                self.sphinx.AddQuery(queryText, index=translated_layer)
            else:
                if self.searchLang:
                    msg = f'Parameter seachLang is not supported for {index}'
                    logger.error(msg)
                    raise BadRequest(msg)
                self.sphinx.AddQuery(queryText, index=str(index))

    def _box2d_transform(self, res):
        """Reproject a ST_BOX2 from EPSG:21781 to SRID"""
        try:
            box2d = res['geom_st_box2d']
            box_str = box2d[4:-1]
            b = map(float, re.split(' |,', box_str))
            shape = box(*b)
            bbox = transform_shape(shape, self.DEFAULT_SRID, self.srid).bounds
            res['geom_st_box2d'] = f"BOX({bbox[0]} {bbox[1]},{bbox[2]} {bbox[3]})"
        except Exception as e:
            msg = f'Error while converting BOX2D ({res}) to EPSG:{self.srid}'
            logger.error(msg, e)
            raise InternalServerError(msg) from e

    def _parse_locations(self, transformer, res):
        if not self.returnGeometry:
            attrs2Del = ['x', 'y', 'lon', 'lat', 'geom_st_box2d']
            list(map(lambda x: res.pop(x) if x in res else x, attrs2Del))
        elif int(self.srid) not in (21781, 2056):
            self._box2d_transform(res)
            if int(self.srid) == 4326:
                try:
                    res['x'] = res['lon']
                    res['y'] = res['lat']
                except KeyError as error:
                    logger.error("Sphinx location has no lat/long defined %s", res)
                    raise InternalServerError(
                        f'Sphinx location has no lat/long defined {res}'
                    ) from error
            else:
                try:
                    pnt = (res['y'], res['x'])
                    x, y = transformer.transform(pnt[0], pnt[1])
                    res['x'] = x
                    res['y'] = y
                except (pyproj.exceptions.CRSError) as error:
                    logger.error("Error while converting point %s to %s", res, self.srid)
                    raise InternalServerError(
                        f'Error while converting point({res}), to EPSG:{self.srid}'
                    ) from error
        return res

    def _parse_location_results(self, results, limit):
        nb_address = 0
        transformer = get_transformer(self.DEFAULT_SRID, self.srid)
        for result in self._yield_matches(results):
            origin = result['attrs']['origin']
            layer_bod_id = self._origin_to_layerbodid(origin)
            if layer_bod_id is not None:
                result['attrs']['layerBodId'] = layer_bod_id
                # Backward compatible
                result['attrs']['featureId'] = result['attrs']['feature_id']
                result['attrs'].pop('layerBodId', None)
            result['attrs'].pop('feature_id', None)
            result['attrs']['label'] = self._translate_label(result['attrs']['label'])
            if (
                origin == 'address' and nb_address < self.LOCATION_LIMIT and (
                    not self.bbox or
                    self._bbox_intersection(self.bbox, result['attrs']['geom_st_box2d'])
                )
            ):
                result['attrs'] = self._parse_locations(transformer, result['attrs'])
                self.results['results'].append(result)
                nb_address += 1
            else:
                if not self.bbox or self._bbox_intersection(
                    self.bbox, result['attrs']['geom_st_box2d']
                ):
                    self._parse_locations(transformer, result['attrs'])
                    self.results['results'].append(result)
        if len(self.results['results']) > 0:
            self.results['results'] = self.results['results'][:limit]

    def _parse_feature_results(self, results):
        for _, result in self._yield_results(results):
            if 'error' in result:
                if result['error'] != '':
                    raise NotFound(result['error'])
            if result is not None and 'matches' in result:
                for match in self._yield_matches(result['matches']):
                    # Backward compatible
                    if 'feature_id' in match['attrs']:
                        match['attrs']['featureId'] = match['attrs']['feature_id']
                    # lang and agnostic in combination with searchLang
                    if 'lang' in match['attrs']:
                        del match['attrs']['lang']
                    if 'agnostic' in match['attrs']:
                        del match['attrs']['agnostic']
                    if not self.bbox or self._bbox_intersection(
                        self.bbox, match['attrs']['geom_st_box2d']
                    ):
                        self.results['results'].append(match)

    @staticmethod
    def _yield_results(results):
        for idx, result in enumerate(results):
            yield idx, result

    def _yield_matches(self, matches):
        for match in matches:
            yield self._choose_srid(match)

    def _choose_srid(self, match):
        geom_entries = ['geom_st_box2d', 'x', 'y']
        if self.srid == 2056:
            for geom_entry in geom_entries:
                match = self._choose_lv95_coords(match, geom_entry)
        else:
            for geom_entry in geom_entries:
                geom_entry = f'{geom_entry}_lv95'
                if geom_entry in match['attrs']:
                    del match['attrs'][geom_entry]
        return match

    @staticmethod
    def _choose_lv95_coords(match, prefix):
        attr = f'{prefix}_lv95'
        if attr in match['attrs']:
            match['attrs'][prefix] = match['attrs'][attr]
            del match['attrs'][attr]
        return match

    def _translate_label(self, label):
        translation = re.search(r'.*(<i>[\s\S]*?<\/i>).*', label) or False
        if translation:
            translated = get_translation(translation.group(1), self.lang)
            label = label.replace(translation.group(1), f'<i>{translated}</i>')
        return label

    def _get_quad_index(self):
        try:
            quadindex = self.quadtree\
                .bbox_to_morton(
                    msk.BBox(self.bbox[0],
                             self.bbox[1],
                             self.bbox[2],
                             self.bbox[3]))
            self.quadindex = quadindex if quadindex != '' else None
        except ValueError:  # pragma: no cover
            self.quadindex = None

    def _bbox_intersection(self, ref, result):

        def _is_point(bbox):
            return bbox[0] == bbox[2] and bbox[1] == bbox[3]

        # We always keep the bbox in 21781
        if self.srid == 2056:
            ref = shift_to(ref, 2056)
        try:
            refbox = box(ref[0], ref[1], ref[2],
                         ref[3]) if not _is_point(ref) else Point(ref[0], ref[1])
            arr = parse_box2d(result)
            resbox = box(arr[0], arr[1], arr[2],
                         arr[3]) if not _is_point(arr) else Point(arr[0], arr[1])
        except ValueError as error:
            # We bail with True to be conservative and
            # not exclude this geometry from the result
            # set. should only happens if result does not have a bbox
            logger.error(
                'Failed to find the bbox intersection with ref=%s and result=%s, '
                'bail with True to be conservative: %s',
                ref,
                result,
                error
            )
            return True
        return refbox.intersects(resbox)
