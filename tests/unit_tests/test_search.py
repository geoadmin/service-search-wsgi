from unittest import TestCase

from gatilegrid import getTileGrid

from flask import url_for

from app import app
#from flask import url_for
#from app.helpers.helpers_search import ilen
from app.helpers.helpers_search import parse_box2d
from app.helpers.validation_search import SUPPORTED_OUTPUT_SRS

#from app.helpers.helpers_search import shift_to_lv95

sphinx_tests = True  # if there is access service-search-sphinx or not

# pylint: disable=invalid-name,too-many-lines


class TestsBase(TestCase):

    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()
        self.app = app.test_client()
        self.app.testing = True
        self.origin_headers = {"allowed": {"Origin": "some_random_domain"}}

        self.grids = {
            '21781': getTileGrid(21781),
            '2056': getTileGrid(2056),
            '3857': getTileGrid(3857),
            '4326': getTileGrid(4326)
        }

    def assertGeojsonFeature(self, feature, srid, hasGeometry=True, hasLayer=True):
        self.assertIn('id', feature)
        self.assertIn('properties', feature)
        self.assertNotIn('attributes', feature)
        if hasLayer:
            self.assertIn('layerBodId', feature)
            self.assertIn('layerName', feature)
        if hasGeometry:
            self.assertIn('geometry', feature)
            self.assertIn('type', feature)
            self.assertIn('type', feature['geometry'])
            self.assertIn('bbox', feature)
            self.assertBBoxValidity(feature['bbox'], srid)

    def assertEsrijsonFeature(self, feature, srid, hasGeometry=True, hasLayer=True):
        self.assertIn('id', feature)
        self.assertNotIn('properties', feature)
        self.assertIn('attributes', feature)
        if hasLayer:
            self.assertIn('layerBodId', feature)
            self.assertIn('layerName', feature)
        if hasGeometry:
            self.assertIn('geometry', feature)
            self.assertIn('bbox', feature)
            self.assertEqual(feature['geometry']['spatialReference']['wkid'], srid)
            self.assertBBoxValidity(feature['bbox'], srid)

    def assertBBoxValidity(self, bbox, srid):
        self.assertIn(srid, SUPPORTED_OUTPUT_SRS)
        grid = self.grids[str(srid)]
        minx, miny, maxx, maxy = bbox

        self.assertLessEqual(maxx, grid.MAXX)
        self.assertLessEqual(maxy, grid.MAXY)
        self.assertGreaterEqual(minx, grid.MINX)
        self.assertGreaterEqual(miny, grid.MINY)


class TestSearchServiceView(TestsBase):

    def setUp(self):
        if not sphinx_tests:
            self.skipTest("Service search requires access to the sphinx server")
        super().setUp()

    def assertAttrs(self, type_, attrs, srid, returnGeometry=True, spatialOrder=False):  # pylint: disable=too-many-arguments,line-too-long
        self.assertIn('detail', attrs)
        self.assertIn('origin', attrs)
        self.assertIn('label', attrs)
        if type_ in ('locations'):
            self.assertIn('geom_quadindex', attrs)
            if returnGeometry:
                self.assertIn('lon', attrs)
                self.assertIn('lat', attrs)
                if srid == 21781:
                    self.assertLess(attrs['y'], self.grids['2056'].MINX)
                    self.assertLess(attrs['x'], self.grids['2056'].MINY)
                if srid in (2056, 4326, 3857):
                    self.assertGreater(attrs['y'], self.grids[str(srid)].MINX)
                    self.assertGreater(attrs['x'], self.grids[str(srid)].MINY)
            else:
                self.assertNotIn('lon', attrs)
                self.assertNotIn('lat', attrs)
                self.assertNotIn('geom_st_box2d', attrs)
                self.assertNotIn('x', attrs)
                self.assertNotIn('y', attrs)
        elif type_ == 'layers':
            self.assertIn('lang', attrs)
            self.assertIn('staging', attrs)
            self.assertIn('title', attrs)
            self.assertIn('topics', attrs)
        elif type_ == 'featuresearch':
            self.assertIn('lon', attrs)
            self.assertIn('lat', attrs)
            self.assertIn('geom_quadindex', attrs)
            self.assertIn('featureId', attrs)
            self.assertIn('layer', attrs)

        if type_ in ('locations', 'featuresearch') and returnGeometry:
            if hasattr(attrs, 'geom_st_box2d'):
                bbox = parse_box2d(attrs['geom_st_box2d'])
                self.assertBBoxValidity(bbox, srid)
            if spatialOrder:
                self.assertIn('@geodist', attrs)
            else:
                self.assertNotIn('@geodist', attrs)
        self.assertNotIn('x_lv95', attrs)
        self.assertNotIn('y_lv95', attrs)
        self.assertNotIn('geom_st_box2d_lv95', attrs)

    def test_no_type(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', searchText='ga'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_unaccepted_type(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', searchText='ga', type='unaccepted'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        acceptedTypes = ['locations', 'layers', 'featuresearch']
        self.assertIn(
            response.json['error']['message'],
            "The type parameter you provided is not valid. Possible values are %s" %
            (', '.join(acceptedTypes))
        )

    def test_searchtext_none_value_layers(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='layers'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    def test_searchtext_empty_string_layers(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='layers', searchText='     '),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    def test_searchtext_none_locations(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    def test_searchtext_none_value_locations(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations', searchText='     '),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    def test_searchtext_none_featuresearch(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='featuresearch'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    def test_searchtext_none_value_featuresearch(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='featuresearch', searchText='    '),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], "Please provide a search text")

    # e2e
    def test_search_layers(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='layers', searchText='wand'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['lang'], 'de')
        self.assertAttrs('layers', response.json['results'][0]['attrs'], 21781)

    # e2e
    def test_search_layers_geojson(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='layers',
                searchText='wand',
                geometryFormat='geojson'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/geo+json')
        self.assertEqual(response.json['type'], 'FeatureCollection')
        self.assertEqual(response.json['bbox'], [420000, 30000, 900000, 510000])

    # e2e
    def test_search_layers_geojson_with_projection(self):
        projections = {
            '2056': [2420000.0, 1029999.9, 2900000.0, 1509999.9],
            '4326': [5.140299, 45.398122, 11.591428, 49.66641],
            '3857': [572215.5, 5684416.9, 1290351.9, 6388703.1],
            '21781': [420000, 30000, 900000, 510000]
        }
        for sr in list(projections.keys()):
            response = self.app.get(
                url_for(
                    'search_server',
                    topic='inspire',
                    type='layers',
                    searchText='wand',
                    geometryFormat='geojson',
                    sr=sr
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/geo+json')
            self.assertEqual(response.json['type'], 'FeatureCollection')
            self.assertEqual(response.json['bbox'], projections[sr])

    # e2e test
    def test_search_locations_geojson_with_projection(self):
        projections = {
            '2056': [2534437.97, 1150655.173, 2544978.008, 1161554.51],
            '4326': [6.582954, 46.503985, 6.721812, 46.602977],
            '3857': [732811.1, 5861484.2, 748268.7, 5877509.0],
            '21781': [534437.969999999, 150655.173000001, 544978.008000001, 161554.509999998]
        }

        for sr in list(projections.keys()):
            response = self.app.get(
                url_for(
                    'search_server',
                    topic='inspire',
                    type='locations',
                    searchText='lausanne',
                    geometryFormat='geojson',
                    limit=1,
                    sr=sr
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/geo+json')
            self.assertEqual(response.json['type'], 'FeatureCollection')
            self.assertEqual(response.json['bbox'], projections[sr])

    # transform to unittest
    def test_search_layers_with_cb(self):

        response = self.app.get(
            url_for(
                'search_server', topic='inspire', type='layers', searchText='wand', callback='cb_'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/javascript')
        self.assertIn('cb_(', str(response.data.decode('utf-8')))

    # transform to unittest
    def test_search_layers_all_langs(self):
        langs = ('de', 'fr', 'it', 'en', 'rm')
        for lang in langs:
            response = self.app.get(
                url_for(
                    'search_server', topic='inspire', type='layers', searchText='wand', lang=lang
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.json['results'][0]['attrs']['lang'], lang)
            self.assertAttrs('layers', response.json['results'][0]['attrs'], 21781)

    # e2e test
    def test_search_layers_for_one_layer(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='layers',
                searchText='ch.blw.klimaeignung-spezialkulturen'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('layers', response.json['results'][0]['attrs'], 21781)

    # unittest
    def test_search_layers_accents(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='layers', searchText='%+&/()=?!üäöéà$@i£$'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['results']), 0)

    # e2e
    def test_search_locations(self):
        # default sr 21781
        response = self.app.get(
            url_for(
                'search_server', topic='inspire', type='locations', searchText='rue des berges'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        for sr in ('2056', '21781', '4326', '3857'):
            response = self.app.get(
                url_for('search_server', type='locations', searchText='rue des berges', sr=sr),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertGreater(len(response.json['results']), 0)
            self.assertAttrs('locations', response.json['results'][0]['attrs'], int(sr))

    # unittest
    def test_bbox_wrong_number_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                type='locations',
                searchText='rue des berges',
                bbox='551306.5625,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json['error']['message'],
            'Please provide 4 coordinates in a comma separated list'
        )

    # unittest - testing validator
    def test_bbox_check_first_second_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                type='locations',
                searchText='rue des berges',
                bbox='420000,420010,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            response.json['error']['message'],
            'The first coordinate must be higher than the second'
        )

    # unittest - testing validator
    def test_bbox_check_third_fourth_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                type='locations',
                searchText='rue des berges',
                bbox='551306.5625,167918.328125,420000,420010'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

        self.assertIn(
            response.json['error']['message'],
            'The third coordinate must be higher than the fourth'
        )

    # convert to unittest
    def test_search_loactions_with_cb(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='rue des berges',
                bbox='551306.5625,167918.328125,551754.125,168514.625',
                callback='cb_'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/javascript')

    # e2e test
    def test_search_locations_all_langs(self):
        # even if not lang dependent
        langs = ('de', 'fr', 'it', 'en', 'rm')
        for lang in langs:
            response = self.app.get(
                url_for(
                    'search_server',
                    topic='inspire',
                    type='locations',
                    searchText='mont d\'or',
                    lang=lang
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertGreater(len(list(response.json['results'])), 0)
            self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    # e2e test
    def test_search_locations_prefix_sentence_match(self):
        params = {'type': 'locations', 'searchText': 'lausann'}
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='lausann',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'lausanne vd')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'gg25')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        response = self.app.get(
            url_for(
                'search_server', topic='inspire', type='locations', searchText='lausann', sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'lausanne vd')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'gg25')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    # unittest
    def test_search_locations_wrong_topic(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='toto',
                type='locations',
                searchText='vd 446',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(response.json['error']['message'], 'The map you provided does not exist')

    # e2e test
    def test_search_locations_lausanne(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='lausanne',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'lausanne vd')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='lausanne', sr=2056),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'lausanne vd')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    """
    def test_search_locations_wil(self):
        params = {'type': 'locations', 'searchText': 'wil'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertEqual(resp.json['results'][0]['attrs']['detail'][:3], 'wil')
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['detail'][:3], 'wil')
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)

    def test_search_locations_fontenay(self):
        params = {'type': 'locations', 'searchText': 'fontenay 10 lausanne'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'chemin de fontenay 10 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'chemin de fontenay 10 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)

    def test_search_locations_wilenstrasse_wil(self):
        params = {'type': 'locations', 'searchText': 'wilenstrasse wil'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertIn('wilenstrasse', resp.json['results'][0]['attrs']['detail'])
        self.assertIn('wil', resp.json['results'][0]['attrs']['detail'])
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertIn('wilenstrasse', resp.json['results'][0]['attrs']['detail'])
        self.assertIn('wil', resp.json['results'][0]['attrs']['detail'])
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)

    def test_search_location_max_address(self):
        params = {'type': 'locations', 'searchText': 'seftigenstrasse'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        results_addresses = filter(
            lambda x: x if x['attrs']['origin'] == 'address' else False, resp.json['results']
        )
        self.assertLessEqual(ilen(results_addresses), 50)
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_no_geometry(self):
        params = {
            'type': 'locations', 'searchText': 'seftigenstrasse 264', 'returnGeometry': 'false'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertTrue('geom_st_box2d' not in resp.json['results'][0]['attrs'].keys())
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781, returnGeometry=False)

    def test_search_locations_geojson(self):
        params = {'type': 'locations', 'searchText': 'Wabern', 'geometryFormat': 'geojson'}
        resp = self.testapp.get('/rest/services/api/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/geo+json')
        self.assertEqual('FeatureCollection', resp.json['type'])
        self.assertGreater(len(list(resp.json['features'])), 0)
        self.assertGeojsonFeature(resp.json['features'][0], 21781, hasGeometry=True, hasLayer=False)
        self.assertAttrs('locations', resp.json['features'][0]['properties'], 21781)
        self.assertIn('wabern', str(resp.json['features']).lower())
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/api/SearchServer', params=params, status=200)
        self.assertEqual('FeatureCollection', resp.json['type'])
        self.assertGeojsonFeature(resp.json['features'][0], 2056, hasGeometry=True, hasLayer=False)
        self.assertIn('wabern', str(resp.json['features']).lower())
        params['sr'] = '3857'
        resp = self.testapp.get('/rest/services/api/SearchServer', params=params, status=200)
        self.assertEqual('FeatureCollection', resp.json['type'])
        self.assertGeojsonFeature(resp.json['features'][0], 3857, hasGeometry=True, hasLayer=False)
        self.assertIn('wabern', str(resp.json['features']).lower())
        params['sr'] = '4326'
        resp = self.testapp.get('/rest/services/api/SearchServer', params=params, status=200)
        self.assertEqual('FeatureCollection', resp.json['type'])
        self.assertGeojsonFeature(resp.json['features'][0], 4326, hasGeometry=True, hasLayer=False)
        self.assertIn('wabern', str(resp.json['features']).lower())

    def test_search_locations_esrijson(self):
        params = {'type': 'locations', 'searchText': 'Wabern', 'geometryFormat': 'esrijson'}
        resp = self.testapp.get('/rest/services/api/SearchServer', params=params, status=400)
        self.assertIn("Param 'geometryFormat=esrijson' is not supported", resp)

    def test_locations_searchtext_apostrophe(self):
        params = {'type': 'locations', 'searchText': 'av mont d\'or lausanne 1'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'avenue du mont-d\'or 1 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(resp.json['results'][0]['attrs']['num'], 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'avenue du mont-d\'or 1 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(resp.json['results'][0]['attrs']['num'], 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)

    def test_locations_searchtext_abbreviations(self):
        params = {'type': 'locations', 'searchText': 'Seftigenstr.', 'sr': '2056'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)
        params = {'type': 'locations', 'searchText': 'Bundespl.', 'sr': '2056'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)
        params = {'type': 'locations', 'searchText': 'pl. du March', 'sr': '2056'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056)

    def test_address_order(self):
        params = {'type': 'locations', 'searchText': 'isabelle de montolieu 2'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'chemin isabelle-de-montolieu 2 1010 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(resp.json['results'][0]['attrs']['num'], 2)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_address_with_letters(self):
        params = {'type': 'locations', 'searchText': 'Rhonesand 16'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 1)
        self.assertEqual(
            resp.json['results'][1]['attrs']['detail'],
            'rhonesandstrasse 16a 3900 brig 6002 brig-glis ch vs'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_ranking(self):
        params = {'type': 'locations', 'searchText': 'gstaad'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(resp.json['results'][0]['attrs']['detail'], 'gstaad saanen')
        params = {'type': 'locations', 'searchText': 'gstaad 10'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'gstaadstrasse 10 3792 saanen 843 saanen ch be'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_features_identify(self):
        params = {
            'type': 'featuresearch',
            'searchText': 'vd 446',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625',
            'features': 'ch.astra.ivs-reg_loc'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertAttrs(
            'featuresearch', resp.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        params['sr'] = '2056'
        params['bbox'] = shift_to_lv95(params['bbox'])
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_search_features_searchtext(self):
        params = {
            'type': 'featuresearch',
            'searchText': '4331',
            'features': 'ch.bafu.hydrologie-gewaesserzustandsmessstationen'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')

    def test_search_features_searchtext_limit(self):
        params = {
            'type': 'featuresearch',
            'searchText': '43',
            'features': 'ch.bafu.hydrologie-gewaesserzustandsmessstationen',
            'limit': '1'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 21781)
        params['sr'] = '2056'
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 2056)

    def test_search_features_non_existing_layer(self):
        params = {
            'type': 'featuresearch', 'searchText': 'toto', 'features': 'this_layer_is_not_existing'
        }
        self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=404)

    def test_search_features_non_searchable_layer(self):
        params = {
            'type': 'featuresearch',
            'searchText': 'toto',
            'features': 'ch.swisstopo.geologie-geotope'
        }
        self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=404)

    def test_search_locations_bbox(self):
        params = {'type': 'locations', 'searchText': 'Beaulieustrasse 2'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_escape_charachters(self):
        params = {'type': 'locations', 'searchText': 'Biel/Bienne'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertGreater(len(resp.json['results']), 0)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_authorized(self):
        params = {'type': 'locations', 'searchText': 'Beaulieustrasse 2'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(list(resp.json['results'])), 0)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_one_origin(self):
        params = {'type': 'locations', 'searchText': 'vaud', 'origins': 'gg25'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_several_origins(self):
        params = {'type': 'locations', 'searchText': 'vaud', 'origins': 'district,gg25'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(len(resp.json['results']), 3)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_bad_origin(self):
        params = {'type': 'locations', 'searchText': 'vaud', 'origins': 'dummy'}
        self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=400)

    def test_search_locations_prefix_parcel(self):
        params = {'type': 'locations', 'searchText': 'parcel val'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'parcel')
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_prefix_address(self):
        params = {'type': 'locations', 'searchText': 'address val'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'address')
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_parcel_keyword_only(self):
        params = {'type': 'locations', 'searchText': 'parzelle'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(len(resp.json['results']), 0)

    def test_search_locations_with_bbox(self):
        params = {
            'type': 'locations',
            'searchText': 'buechli tegerfelden',
            'bbox': '664100,268443,664150,268643'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781, spatialOrder=True)
        params['sr'] = '2056'
        params['bbox'] = shift_to_lv95(params['bbox'])
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_search_locations_with_bbox_sort(self):
        params = {
            'type': 'locations',
            'searchText': 'buechli tegerfelden',
            'bbox': '564100,168443,664150,268643'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781, spatialOrder=True)
        params['sr'] = '2056'
        params['bbox'] = shift_to_lv95(params['bbox'])
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056, spatialOrder=True)
        params = {
            'type': 'locations',
            'searchText': 'buechli tegerfelden',
            'bbox': '564100,168443,664150,268643',
            'sortbbox': 'true'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781, spatialOrder=True)
        params = {
            'type': 'locations',
            'searchText': 'buechli tegerfelden',
            'bbox': '564100,168443,664150,268643',
            'sortbbox': 'false'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(
            resp.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_search_locations_bbox_only(self):
        params = {'type': 'locations', 'bbox': '664126,268543,664126,268543'}
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781, spatialOrder=True)
        params['sr'] = '2056'
        params['bbox'] = shift_to_lv95(params['bbox'])
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertGreater(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_search_locations_noparams(self):
        params = {'type': 'locations'}
        self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=400)

    def test_features_timeinstant(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542199,206799,642201,226801',
            'timeInstant': '1981'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', resp.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        params['sr'] = '2056'
        params['bbox'] = shift_to_lv95(params['bbox'])
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_nodigit_timeinstant(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542199,206799,542201,206801',
            'timeInstant': 'four'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)
        resp.mustcontain('Please provide an integer for the parameter timeInstant')

    def test_features_timestamp(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'timeStamps': '1981'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 21781)

    def test_features_empty_timestamp(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542199,206799,542201,206801',
            'timeStamps': ''
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', resp.json['results'][0]['attrs'], 21781, spatialOrder=True
        )

    def test_features_none_first_timestamp(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'timeStamps': ',1989'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 21781)

    def test_features_multiple_timestamps(self):
        params = {
            'type':
                'featuresearch',
            'searchText':
                '198',
            'features':
                'ch.swisstopo.lubis-luftbilder_farbe,ch.swisstopo.lubis-luftbilder_schwarzweiss',
            'bbox':
                '542199,146799,692201,246801',
            'timeStamps':
                '1986,1989',
            'timeEnabled':
                'true,true'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', resp.json['results'][0]['attrs'], 21781, spatialOrder=True
        )

    def test_features_timeInterval(self):
        params = {
            'type':
                'featuresearch',
            'searchText':
                '1993034 1990-2010',
            'features':
                'ch.swisstopo.fixpunkte-lfp1,ch.swisstopo.lubis-luftbilder_schwarzweiss,ch.swisstopo.lubis-luftbilder_farbe',
            'timeEnabled':
                'false,true,true'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 21781)

    def test_features_timeInterval_only(self):
        params = {
            'type':
                'featuresearch',
            'searchText':
                '1990-2010',
            'features':
                'ch.swisstopo.fixpunkte-lfp1,ch.swisstopo.lubis-luftbilder_schwarzweiss,ch.swisstopo.lubis-luftbilder_farbe',
            'timeEnabled':
                'false,true,true'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(resp.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', resp.json['results'][0]['attrs'], 21781)

    def test_features_wrong_time(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542200,206800,542200,206800',
            'timeInstant': '19    522'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_features_wrong_time_2(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542200,206800,542200,206800',
            'timeInstant': '19    52.00'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_features_mix_timeinstant_timestamps(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542200,206800,542200,206800',
            'timeInstant': '1952',
            'timeStamps': '1946'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_features_wrong_timestamps(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542200,206800,542200,206800',
            'timeStamps': '19522'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_nondigit_timestamps(self):
        params = {
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'type': 'featuresearch',
            'bbox': '542200,206800,542200,206800',
            'timeStamps': 'four'
        }
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)
        resp.mustcontain('Please provide integers for timeStamps parameter')

    def test_features_wrong_timestamps_2(self):
        params = {
            'type': 'featuresearch',
            'searchText': '19810590048970',
            'features': 'ch.swisstopo.lubis-luftbilder_farbe',
            'bbox': '542200,206800,542200,206800',
            'timeStamps': '1952.00'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_locations_search_limit(self):
        params = {'type': 'locations', 'searchText': 'chalais', 'limit': '1'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(len(resp.json['results']), 1)
        self.assertAttrs('locations', resp.json['results'][0]['attrs'], 21781)

    def test_locations_search_wrong_limit(self):
        params = {'type': 'locations', 'searchText': 'chalais', 'limit': '5.5'}
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_search_max_words(self):
        params = {
            'type': 'locations',
            'searchText': 'this is a text with exactly 10 words, should work',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=200)
        params = {
            'type': 'layers',
            'searchText': 'this is a text with exactly 10 words, should work',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=200)
        params = {
            'type': 'featuresearch',
            'searchText': 'this is a text with exactly 10 words, should work',
            'features': 'ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=200)
        params = {
            'type': 'locations',
            'searchText': 'this is a text with exactly 11 words, should NOT work',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=400)
        params = {
            'type': 'layers',
            'searchText': 'this is a text with exactly 11 words, should NOT work',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=400)
        params = {
            'type': 'featuresearch',
            'searchText': 'this is a text with exactly 11 words, should NOT work',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=400)

    def test_bbox_nan(self):
        params = {
            'type': 'locations',
            'searchText': 'rue des berges',
            'bbox': '551306.5625,NaN,551754.125,168514.625'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=400)
        resp.mustcontain('Please provide numerical values for the parameter bbox')

    def test_fuzzy_locations_results(self):
        # Standard results
        params = {'type': 'locations', 'searchText': 'brigmat', 'lang': 'de'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertGreater(len(resp.json['results']), 0)
        self.assertNotIn('fuzzy', resp.json)
        # Fuzzy results
        params = {'type': 'locations', 'searchText': 'birgma', 'lang': 'de'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertGreater(len(resp.json['results']), 0)
        self.assertEqual(resp.json['fuzzy'], 'true')
        # No results
        params = {'type': 'locations', 'searchText': 'birgmasdfasdfa', 'lang': 'de'}
        resp = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertEqual(len(resp.json['results']), 0)
        self.assertEqual(resp.json['fuzzy'], 'true')

    def test_search_lang_param_same_entry(self):
        params = {
            'type': 'featuresearch',
            'searchLang': 'fr',
            'searchText': 'rue de boujean',
            'features': 'ch.bfs.gebaeude_wohnungs_register',
            'sr': '2056'
        }
        resp_fr = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertAttrs('featuresearch', resp_fr.json['results'][0]['attrs'], 2056)
        params = {
            'type': 'featuresearch',
            'searchLang': 'de',
            'searchText': 'bözingenstrasse',
            'features': 'ch.bfs.gebaeude_wohnungs_register',
            'sr': '2056'
        }
        resp_de = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        self.assertAttrs('featuresearch', resp_de.json['results'][0]['attrs'], 2056)
        self.assertEqual(
            resp_fr.json['results'][0]['attrs']['featureId'],
            resp_de.json['results'][0]['attrs']['featureId']
        )

    def test_search_lang_no_support(self):
        params = {
            'type': 'featuresearch',
            'searchLang': 'fr',
            'searchText': 'boujean',
            'features': 'ch.bfs.gebaeude_wohnungs_register,ch.swisstopo.lubis-luftbilder_farbe'
        }
        self.testapp.get('/rest/services/ech/SearchServer', params=params, status=400)

    def test_search_lang_integrity(self):
        params = {
            'type': 'featuresearch',
            'searchLang': 'fr',
            'searchText': 'aegerten 40',
            'features': 'ch.bfs.gebaeude_wohnungs_register'
        }
        resp_fr = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        params = {
            'type': 'featuresearch',
            'searchLang': 'de',
            'searchText': 'aegerten 40',
            'features': 'ch.bfs.gebaeude_wohnungs_register'
        }
        resp_de = self.testapp.get('/rest/services/ech/SearchServer', params=params, status=200)
        params = {
            'type': 'featuresearch',
            'searchText': 'aegerten 40',
            'features': 'ch.bfs.gebaeude_wohnungs_register'
        }
        resp_agnostic = self.testapp.get(
            '/rest/services/ech/SearchServer', params=params, status=200
        )

        ids_fr = [f['attrs']['featureId'] for f in resp_fr.json['results']]
        ids_de = [f['attrs']['featureId'] for f in resp_de.json['results']]
        ids = [f['attrs']['featureId'] for f in resp_agnostic.json['results']]
        self.assertEqual(len(set(ids_fr + ids_de)), len(ids))
        for i in ids_fr:
            self.assertIn(i, ids)
        for i in ids_de:
            self.assertIn(i, ids)

"""
