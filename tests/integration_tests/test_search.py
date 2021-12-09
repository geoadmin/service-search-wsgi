from flask import url_for

#from flask import url_for
from app.helpers.helpers_search import ilen
from app.helpers.helpers_search import shift_to_lv95
from tests.unit_tests.base_test import BaseSearchTest

# pylint: disable=invalid-name,too-many-lines


class TestSearchService(BaseSearchTest):  # pylint: disable=too-many-public-methods

    def test_search_layers(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='layers', searchText='wand'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['lang'], 'de')
        self.assertAttrs('layers', response.json['results'][0]['attrs'], 21781)

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

    def test_search_layers_geojson_with_projection_one(self):
        projections = {
            '2056': [2420000.0, 1030000.0, 2900000.0, 1510000.0],
            '4326': [5.140299, 45.398122, 11.591427, 49.666411],
            '3857': [572215.4, 5684417.0, 1290351.8, 6388703.2],
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

    def test_search_locations_geojson_with_projection_two(self):
        projections = {
            '2056': [2534437.97, 1150655.173, 2544978.008, 1161554.51],
            '4326': [6.582954, 46.503985, 6.721811, 46.602978],
            '3857': [732811.1, 5861484.3, 748268.6, 5877509.0],
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

    def test_search_layers_accents(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='layers', searchText='%+&/()=?!üäöéà$@i£$'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['results']), 0)

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
                url_for(
                    'search_server',
                    topic='inspire',
                    type='locations',
                    searchText='rue des berges',
                    sr=sr
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
            self.assertGreater(len(response.json['results']), 0)
            self.assertAttrs('locations', response.json['results'][0]['attrs'], int(sr))

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

    def test_search_locations_prefix_sentence_match(self):
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
            url_for(
                'search_server', topic='ech', type='locations', searchText='lausanne', sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'lausanne vd')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_search_locations_wil(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='wil'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'][:3], 'wil')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='wil', sr='2056'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['detail'][:3], 'wil')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_search_locations_fontenay(self):
        response = self.app.get(
            url_for(
                'search_server', topic='ech', type='locations', searchText='fontenay 10 lausanne'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'chemin de fontenay 10 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='fontenay 10 lausanne',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'chemin de fontenay 10 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_search_locations_wilenstrasse_wil(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='wilenstrasse wil'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertIn('wilenstrasse', response.json['results'][0]['attrs']['detail'])
        self.assertIn('wil', response.json['results'][0]['attrs']['detail'])
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='wilenstrasse wil',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('wilenstrasse', response.json['results'][0]['attrs']['detail'])
        self.assertIn('wil', response.json['results'][0]['attrs']['detail'])
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_search_location_max_address(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='seftigenstrasse'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        results_addresses = filter(
            lambda x: x if x['attrs']['origin'] == 'address' else False, response.json['results']
        )
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(ilen(results_addresses), 50)
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_no_geometry(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='seftigenstrasse 264',
                returnGeometry='false'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertTrue('geom_st_box2d' not in response.json['results'][0]['attrs'].keys())
        self.assertAttrs(
            'locations', response.json['results'][0]['attrs'], 21781, returnGeometry=False
        )

    def test_search_locations_geojson(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='api',
                type='locations',
                searchText='Wabern',
                returnGeometry='true',
                geometryFormat='geojson'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.content_type, 'application/geo+json')
        self.assertEqual('FeatureCollection', response.json['type'])
        self.assertGreater(len(list(response.json['features'])), 0)
        self.assertGeojsonFeature(
            response.json['features'][0], 21781, hasGeometry=True, hasLayer=False
        )
        self.assertAttrs('locations', response.json['features'][0]['properties'], 21781)
        self.assertIn('wabern', str(response.json['features']).lower())
        response = self.app.get(
            url_for(
                'search_server',
                topic='api',
                type='locations',
                searchText='Wabern',
                returnGeometry='true',
                geometryFormat='geojson',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('FeatureCollection', response.json['type'])
        self.assertGeojsonFeature(
            response.json['features'][0], 2056, hasGeometry=True, hasLayer=False
        )
        self.assertIn('wabern', str(response.json['features']).lower())
        response = self.app.get(
            url_for(
                'search_server',
                topic='api',
                type='locations',
                searchText='Wabern',
                returnGeometry='true',
                geometryFormat='geojson',
                sr='3857'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('FeatureCollection', response.json['type'])
        self.assertGeojsonFeature(
            response.json['features'][0], 3857, hasGeometry=True, hasLayer=False
        )
        self.assertIn('wabern', str(response.json['features']).lower())
        response = self.app.get(
            url_for(
                'search_server',
                topic='api',
                type='locations',
                searchText='Wabern',
                returnGeometry='true',
                geometryFormat='geojson',
                sr='4326'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual('FeatureCollection', response.json['type'])
        self.assertGeojsonFeature(
            response.json['features'][0], 4326, hasGeometry=True, hasLayer=False
        )
        self.assertIn('wabern', str(response.json['features']).lower())

    def test_locations_searchtext_apostrophe(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='av mont d\'or lausanne 1',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'avenue du mont-d\'or 1 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(response.json['results'][0]['attrs']['num'], 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='av mont d\'or lausanne 1',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'avenue du mont-d\'or 1 1007 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(response.json['results'][0]['attrs']['num'], 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_locations_searchtext_abbreviations(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='Seftigenstr.',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)
        response = self.app.get(
            url_for(
                'search_server', topic='ech', type='locations', searchText='Bundespl.', sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='pl. du March',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056)

    def test_address_order(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='isabelle de montolieu 2'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'chemin isabelle-de-montolieu 2 1010 lausanne 5586 lausanne ch vd'
        )
        self.assertEqual(response.json['results'][0]['attrs']['num'], 2)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_address_with_letters(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='Rhonesand 16'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 1)
        self.assertEqual(
            response.json['results'][1]['attrs']['detail'],
            'rhonesandstrasse 16a 3900 brig 6002 brig-glis ch vs'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_ranking(self):
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='gstaad'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(response.json['results'][0]['attrs']['detail'], 'gstaad saanen')
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='gstaad 10'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'gstaadstrasse 10 3792 saanen 843 saanen ch be'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    # e2e test
    def test_search_features_identify(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='vd 446',
                bbox='551306.5625,167918.328125,551754.125,168514.625',
                features='ch.astra.ivs-reg_loc'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='vd 446',
                bbox=shift_to_lv95('551306.5625,167918.328125,551754.125,168514.625'),
                features='ch.astra.ivs-reg_loc',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 2056, spatialOrder=True
        )

    def test_search_features_searchtext(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='4331',
                features='ch.bafu.hydrologie-gewaesserzustandsmessstationen',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

    def test_search_features_searchtext_limit(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='43',
                features='ch.bafu.hydrologie-gewaesserzustandsmessstationen',
                limit='1'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 21781)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='43',
                features='ch.bafu.hydrologie-gewaesserzustandsmessstationen',
                limit='1',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 2056)

    def test_search_features_non_existing_layer(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='featuresearch',
                searchText='toto',
                features='this_layer_is_not_existing'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 404)

    def test_search_features_non_searchable_layer(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='featuresearch',
                searchText='toto',
                features='ch.swisstopo.geologie-geotope'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 404)

    def test_search_locations_next(self):
        response = self.app.get(
            url_for(
                'search_server', topic='inspire', type='locations', searchText='Beaulieustrasse 2'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(list(response.json['results'])), 0)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_escape_charachters(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations', searchText='Biel/Bienne'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['results']), 0)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_one_origin(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='vaud',
                origins='gg25'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_several_origins(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='vaud',
                origins='district,gg25'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['results']), 3)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_prefix_parcel(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations', searchText='parcel val'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'parcel')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_prefix_address(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations', searchText='parcel val'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['results']), 0)
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'parcel')
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_parcel_keyword_only(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations', searchText='parzelle'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['results']), 0)

        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox='664100,268443,664150,268643'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs(
            'locations', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox=shift_to_lv95('664100,268443,664150,268643'),
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_search_locations_with_bbox_sort(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox='564100,168443,664150,268643',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs(
            'locations', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox=shift_to_lv95('564100,168443,664150,268643'),
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056, spatialOrder=True)
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox='564100,168443,664150,268643',
                sortbbox='true'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli 1.1 5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs(
            'locations', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='buechli tegerfelden',
                bbox='564100,168443,664150,268643',
                sortbbox='false'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['results'][0]['attrs']['detail'],
            'buechli  5306 tegerfelden 4320 tegerfelden ch ag'
        )
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_locations_bbox_only(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                bbox='664126,268543,664126,268543',
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 1)
        self.assertAttrs(
            'locations', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                bbox=shift_to_lv95('664126,268543,664126,268543'),
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertGreater(len(response.json['results']), 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 2056, spatialOrder=True)

    def test_features_timeinstant(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542199,206799,642201,226801',
                timeInstant='1981'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox=shift_to_lv95('542199,206799,642201,226801'),
                timeInstant='1981',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 2056, spatialOrder=True
        )

    def test_features_timestamp(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                timeInstant='1981'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 21781)

    def test_features_empty_timestamp(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542199,206799,542201,206801',
                timeStamps=''
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )

    def test_features_none_first_timestamp(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                timeStamps=',1989'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 21781)

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='198',
                bbox='542199,146799,692201,246801',
                features=
                'ch.swisstopo.lubis-luftbilder_farbe,ch.swisstopo.lubis-luftbilder_schwarzweiss',
                timeStamps='1986,1989',
                timeEnabled='true,true'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs(
            'featuresearch', response.json['results'][0]['attrs'], 21781, spatialOrder=True
        )

    def test_features_timeInterval(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='1993034 1990-2010',
                features='ch.swisstopo.fixpunkte-lfp1,ch.swisstopo.lubis-luftbilder_schwarzweiss,'
                'ch.swisstopo.lubis-luftbilder_farbe',
                timeEnabled='false,true,true'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 21781)

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='1990-2010',
                features='ch.swisstopo.fixpunkte-lfp1,ch.swisstopo.lubis-luftbilder_schwarzweiss,'
                'ch.swisstopo.lubis-luftbilder_farbe',
                timeEnabled='false,true,true'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['results'][0]['attrs']['origin'], 'feature')
        self.assertAttrs('featuresearch', response.json['results'][0]['attrs'], 21781)

    def test_locations_search_limit(self):
        response = self.app.get(
            url_for(
                'search_server', topic='ech', type='locations', searchText='chalais', limit='1'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['results']), 1)
        self.assertAttrs('locations', response.json['results'][0]['attrs'], 21781)

    def test_search_max_words(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='this is a text with exactly 10 words, should work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='layers',
                searchText='this is a text with exactly 10 words, should work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                features='ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill',
                searchText='this is a text with exactly 10 words, should work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='this is a text with exactly 10 words, should NOT work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='layers',
                searchText='this is a text with exactly 10 words, should NOT work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                features='ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill',
                searchText='this is a text with exactly 10 words, should NOT work',
                bbox='551306.5625,167918.328125,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_fuzzy_locations_results(self):
        # Standard results
        response = self.app.get(
            url_for(
                'search_server', topic='ech', type='locations', searchText='brigmat', lang='de'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['results']), 0)
        self.assertNotIn('fuzzy', response.json)
        # Fuzzy results
        response = self.app.get(
            url_for('search_server', topic='ech', type='locations', searchText='birgma', lang='de'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['results']), 0)
        #self.assertEqual(response.json['fuzzy'], 'true') DOTO
        # No results
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='birgmasdfasdfa',
                lang='de'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['results']), 0)
        self.assertEqual(response.json['fuzzy'], 'true')

    def test_search_lang_param_same_entry(self):
        response_fr = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='rue de boujean',
                searchLang='fr',
                features='ch.bfs.gebaeude_wohnungs_register',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response_fr.status_code, 200)
        self.assertAttrs('featuresearch', response_fr.json['results'][0]['attrs'], 2056)
        response_de = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='bözingenstrasse',
                searchLang='de',
                features='ch.bfs.gebaeude_wohnungs_register',
                sr='2056'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response_de.status_code, 200)
        self.assertAttrs('featuresearch', response_de.json['results'][0]['attrs'], 2056)
        self.assertEqual(
            response_fr.json['results'][0]['attrs']['featureId'],
            response_de.json['results'][0]['attrs']['featureId']
        )

    def test_search_lang_integrity(self):
        response_fr = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchLang='fr',
                searchText='aegerten 40',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response_fr.status_code, 200)
        response_de = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchLang='de',
                searchText='aegerten 40',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response_de.status_code, 200)

        response_agnostic = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='aegerten 40',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response_agnostic.status_code, 200)

        ids_fr = [f['attrs']['featureId'] for f in response_fr.json['results']]
        ids_de = [f['attrs']['featureId'] for f in response_de.json['results']]
        ids = [f['attrs']['featureId'] for f in response_agnostic.json['results']]
        self.assertEqual(len(set(ids_fr + ids_de)), len(ids))
        for i in ids_fr:
            self.assertIn(i, ids)
        for i in ids_de:
            self.assertIn(i, ids)
