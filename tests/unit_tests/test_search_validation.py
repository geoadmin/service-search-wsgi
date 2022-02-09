from flask import url_for

from tests.unit_tests.base_test import BaseSearchTest


class TestSearchServiceValidation(BaseSearchTest):
    # pylint: disable=too-many-public-methods

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
        accepted_types = ['locations', 'layers', 'featuresearch']
        self.assertIn(
            response.json['error']['message'],
            "The type parameter you provided is not valid."
            f" Possible values are {', '.join(accepted_types)}"
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

    def test_bbox_wrong_number_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='all',
                type='locations',
                searchText='rue des berges',
                bbox='551306.5625,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Please provide 4 coordinates in a comma separated list',
            response.json['error']['message']
        )

    def test_bbox_check_first_second_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='all',
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

    def test_bbox_check_third_fourth_coordinates(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='all',
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
        self.assertIn('you provided does not exist', response.json['error']['message'])

    def test_search_locations_esrijson(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='api',
                type='locations',
                searchText='Wabern',
                return_geometry='true',
                geometryFormat='esrijson'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Param 'geometryFormat=esrijson' is not supported", response.json['error']['message']
        )

    def test_search_locations_bad_origin(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='inspire',
                type='locations',
                searchText='vaud',
                origins='dummy'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_search_locations_noparams(self):
        response = self.app.get(
            url_for('search_server', topic='inspire', type='locations'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_nodigit_timeinstant(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542199,206799,642201,226801',
                timeInstant='four'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Please provide an integer for the parameter timeInstant',
            response.json['error']['message']
        )

    def test_features_wrong_time(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeInstant='19    522'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_features_wrong_time_2(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeInstant='19    52.00'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_features_mix_timeinstant_timestamps(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeInstant='1952',
                timeStamps='1946'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_features_wrong_timestamps(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeStamps='19522'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_nondigit_timestamps(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeStamps='four'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Please provide integers for timeStamps parameter', response.json['error']['message']
        )

    def test_features_wrong_timestamps_2(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='19810590048970',
                features='ch.swisstopo.lubis-luftbilder_farbe',
                bbox='542200,206800,542200,206800',
                timeStamps='1952.00'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

    def test_locations_search_wrong_limit(self):
        response = self.app.get(
            url_for(
                'search_server', topic='ech', type='locations', searchText='chalais', limit='5.5'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)

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

    def test_bbox_nan(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='locations',
                searchText='rue des berges',
                bbox='551306.5625,NaN,551754.125,168514.625'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Please provide numerical values for the parameter bbox',
            response.json['error']['message'],
        )

    def test_search_lang_no_support(self):
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='boujean',
                searchLang='fr',
                features='ch.bfs.gebaeude_wohnungs_register,ch.swisstopo.lubis-luftbilder_farbe'
            ),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 400)
