import logging
from unittest.mock import patch

from flask import url_for

from tests.unit_tests.base_test import BaseSearchTest

logger = logging.getLogger(__name__)


# Mock Sphinx results for featuresearch with exact match boosting tests
MOCK_FEATURESEARCH_RESULTS_EXACT_MATCH = [{
    'error': '',
    'warning': '',
    'status': 0,
    'fields': ['detail', 'geom_quadindex'],
    'attrs': {
        'feature_id': 7,
        'detail': 7,
        'geom_st_box2d': 7,
        'geom_quadindex': 7,
        'label': 7,
        'layer': 7,
        'origin': 7,
        'lat': 5,
        'lon': 5,
        'agnostic': 1,
    },
    'matches': [
        # Result with exact match at end (should be boosted)
        {
            'id': 1741256,
            'weight': 2561,
            'attrs': {
                'detail': 'raeterschenstrasse 10 8418 schlatt zh schlatt _zh_ _zh_ 111001',
                'featureId': '111001_0',
                'feature_id': '111001_0',
                'geom_quadindex': '030010313122220212210',
                'geom_st_box2d': 'BOX(704071.1685604602 259725.79746988925,704071.1685604602 259725.79746988925)',
                'label': 'Räterschenstrasse 10 Schlatt (ZH)',
                'lat': 47.48006057739258,
                'layer': 'ch.bfs.gebaeude_wohnungs_register',
                'lon': 8.819401741027832,
                'origin': 'feature',
                'agnostic': 1,
            }
        },
        # Result with prefix match (should not be boosted)
        {
            'id': 9367,
            'weight': 2600,
            'attrs': {
                'detail': 'via valle verzasca 7 6632 vogorno verzasca _ti_ 11100130',
                'featureId': '11100130_0',
                'feature_id': '11100130_0',
                'geom_quadindex': '032031010211321121113',
                'geom_st_box2d': 'BOX(709621.1369603279 118878.52939728371,709621.1369603279 118878.52939728371)',
                'label': 'Via Valle Verzasca 7 Verzasca',
                'lat': 46.212425231933594,
                'layer': 'ch.bfs.gebaeude_wohnungs_register',
                'lon': 8.859180450439453,
                'origin': 'feature',
                'agnostic': 1,
            }
        },
        # Result with exact match at start (should be boosted)
        {
            'id': 106855,
            'weight': 2550,
            'attrs': {
                'detail': '111001 kirchstrasse 4 8887 mels mels _sg_',
                'featureId': '111001_2',
                'feature_id': '111001_2',
                'geom_quadindex': '030132220212010113133',
                'geom_st_box2d': 'BOX(750556.2385305155 212572.80229783672,750556.2385305155 212572.80229783672)',
                'label': 'Kirchstrasse 4 Mels',
                'lat': 47.04707717895508,
                'layer': 'ch.bfs.gebaeude_wohnungs_register',
                'lon': 9.420117378234863,
                'origin': 'feature',
                'agnostic': 1,
            }
        },
        # Result with exact match in middle (should be boosted)
        {
            'id': 106856,
            'weight': 2540,
            'attrs': {
                'detail': 'test 111001 example _sg_',
                'featureId': '111001_3',
                'feature_id': '111001_3',
                'geom_quadindex': '030132220212010113133',
                'geom_st_box2d': 'BOX(750556.2385305155 212572.80229783672,750556.2385305155 212572.80229783672)',
                'label': 'Test Example',
                'lat': 47.04707717895508,
                'layer': 'ch.bfs.gebaeude_wohnungs_register',
                'lon': 9.420117378234863,
                'origin': 'feature',
                'agnostic': 1,
            }
        },
    ],
    'total': 4,
    'total_found': 4,
    'time': 0.003,
    'words': []
}]


@patch('app.lib.sphinxapi.SphinxClient.RunQueries')
class TestFeatureSearchExactMatchBoost(BaseSearchTest):

    def test_exact_match_boosting_applied(self, mock):
        """Test that exact matches get +10000 weight boost"""
        mock.return_value = MOCK_FEATURESEARCH_RESULTS_EXACT_MATCH

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='111001',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')

        results = response.json['results']
        self.assertGreater(len(results), 0, "Should have results")

        # Find results by their feature IDs
        exact_at_end = next((r for r in results if r['attrs']['feature_id'] == '111001_0'), None)
        exact_at_start = next((r for r in results if r['attrs']['feature_id'] == '111001_2'), None)
        exact_in_middle = next((r for r in results if r['attrs']['feature_id'] == '111001_3'), None)
        prefix_match = next((r for r in results if r['attrs']['feature_id'] == '11100130_0'), None)

        # Exact matches should be boosted by 10000
        self.assertIsNotNone(exact_at_end, "Exact match at end should be in results")
        self.assertEqual(exact_at_end['weight'], 12561, "Exact match at end should be boosted by 10000")

        self.assertIsNotNone(exact_at_start, "Exact match at start should be in results")
        self.assertEqual(exact_at_start['weight'], 12550, "Exact match at start should be boosted by 10000")

        self.assertIsNotNone(exact_in_middle, "Exact match in middle should be in results")
        self.assertEqual(exact_in_middle['weight'], 12540, "Exact match in middle should be boosted by 10000")

        # Prefix match should not be boosted
        self.assertIsNotNone(prefix_match, "Prefix match should be in results")
        self.assertEqual(prefix_match['weight'], 2600, "Prefix match should not be boosted")

    def test_exact_matches_ranked_higher(self, mock):
        """Test that exact matches are ranked higher than prefix matches after boosting"""
        mock.return_value = MOCK_FEATURESEARCH_RESULTS_EXACT_MATCH

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='111001',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        results = response.json['results']

        # First result should be an exact match (highest boosted weight)
        self.assertIn(results[0]['attrs']['feature_id'], ['111001_0', '111001_2', '111001_3'],
                     "First result should be an exact match")

        # Prefix match should be ranked lower
        prefix_match_index = next(
            (i for i, r in enumerate(results) if r['attrs']['feature_id'] == '11100130_0'),
            None
        )
        self.assertIsNotNone(prefix_match_index, "Prefix match should be in results")
        self.assertGreater(prefix_match_index, 0, "Prefix match should not be first")

    def test_no_boosting_when_no_exact_match(self, mock):
        """Test that results without exact matches don't get boosted"""
        mock_results = [{
            'error': '',
            'warning': '',
            'status': 0,
            'fields': ['detail', 'geom_quadindex'],
            'attrs': {
                'feature_id': 7,
                'detail': 7,
                'geom_st_box2d': 7,
                'geom_quadindex': 7,
                'label': 7,
                'layer': 7,
                'origin': 7,
                'lat': 5,
                'lon': 5,
                'agnostic': 1,
            },
            'matches': [
                {
                    'id': 9367,
                    'weight': 2600,
                    'attrs': {
                        'detail': 'via valle verzasca 7 6632 vogorno verzasca _ti_ 11100130',
                        'featureId': '11100130_0',
                        'feature_id': '11100130_0',
                        'geom_quadindex': '032031010211321121113',
                        'geom_st_box2d': 'BOX(709621.1369603279 118878.52939728371,709621.1369603279 118878.52939728371)',
                        'label': 'Via Valle Verzasca 7 Verzasca',
                        'lat': 46.212425231933594,
                        'layer': 'ch.bfs.gebaeude_wohnungs_register',
                        'lon': 8.859180450439453,
                        'origin': 'feature',
                        'agnostic': 1,
                    }
                },
            ],
            'total': 1,
            'total_found': 1,
            'time': 0.003,
            'words': []
        }]

        mock.return_value = mock_results

        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='111001',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        results = response.json['results']

        # Weight should remain unchanged (no boost)
        self.assertEqual(results[0]['weight'], 2600, "Weight should not be boosted")

    def test_exact_match_case_insensitive(self, mock):
        """Test that exact match boosting is case-insensitive"""
        mock_results = [{
            'error': '',
            'warning': '',
            'status': 0,
            'fields': ['detail', 'geom_quadindex'],
            'attrs': {
                'feature_id': 7,
                'detail': 7,
                'geom_st_box2d': 7,
                'geom_quadindex': 7,
                'label': 7,
                'layer': 7,
                'origin': 7,
                'lat': 5,
                'lon': 5,
                'agnostic': 1,
            },
            'matches': [
                {
                    'id': 1,
                    'weight': 2500,
                    'attrs': {
                        'detail': 'test ABC123 example',
                        'feature_id': 'test_1',
                        'geom_quadindex': '030010313122220212210',
                        'geom_st_box2d': 'BOX(704071.1685604602 259725.79746988925,704071.1685604602 259725.79746988925)',
                        'label': 'Test 1',
                        'lat': 47.48006057739258,
                        'layer': 'ch.bfs.gebaeude_wohnungs_register',
                        'lon': 8.819401741027832,
                        'origin': 'feature',
                        'agnostic': 1,
                    }
                },
            ],
            'total': 1,
            'total_found': 1,
            'time': 0.003,
            'words': []
        }]

        mock.return_value = mock_results

        # Search with lowercase
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='abc123',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        results = response.json['results']

        # Should be boosted despite case difference
        self.assertEqual(results[0]['weight'], 12500, "Case-insensitive exact match should be boosted")
