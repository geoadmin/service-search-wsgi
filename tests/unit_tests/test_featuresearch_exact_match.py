from unittest.mock import patch

from flask import url_for

from tests.unit_tests.base_test import BaseSearchTest

# Mock Sphinx results for featuresearch with exact match boosting tests
MOCK_FEATURESEARCH_RESULTS_EXACT_MATCH = [{
    'matches': [
        # Result with exact match at end (should be boosted)
        {
            'id': 1,
            'weight': 2561,
            'attrs': {
                'detail': 'raeterschenstrasse 10 8418 schlatt zh schlatt _zh_ _zh_ 111001',
                'feature_id': '111001_0',
            }
        },
        # Result with prefix match (should not be boosted)
        {
            'id': 2,
            'weight': 2600,
            'attrs': {
                'detail': 'via valle verzasca 7 6632 vogorno verzasca _ti_ 11100130',
                'feature_id': '11100130_0',
            }
        },
        # Result with exact match at start (should be boosted)
        {
            'id': 3,
            'weight': 2550,
            'attrs': {
                'detail': '111001 kirchstrasse 4 8887 mels mels _sg_',
                'feature_id': '111001_2',
            }
        },
        # Result with exact match in middle (should be boosted)
        {
            'id': 4,
            'weight': 2540,
            'attrs': {
                'detail': 'test 111001 example _sg_',
                'feature_id': '111001_3',
            }
        },
    ],
}]


@patch('app.lib.sphinxapi.SphinxClient.RunQueries')
class TestFeatureSearchExactMatchBoost(BaseSearchTest):

    def test_exact_match_boosting_and_ranking(self, mock):
        """Test that exact matches get +10000 weight boost and are ranked higher"""
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
        self.assertEqual(
            exact_at_end['weight'], 12561, "Exact match at end should be boosted by 10000"
        )

        self.assertIsNotNone(exact_at_start, "Exact match at start should be in results")
        self.assertEqual(
            exact_at_start['weight'], 12550, "Exact match at start should be boosted by 10000"
        )

        self.assertIsNotNone(exact_in_middle, "Exact match in middle should be in results")
        self.assertEqual(
            exact_in_middle['weight'], 12540, "Exact match in middle should be boosted by 10000"
        )

        # Prefix match should not be boosted
        self.assertIsNotNone(prefix_match, "Prefix match should be in results")
        self.assertEqual(prefix_match['weight'], 2600, "Prefix match should not be boosted")

        # First result should be an exact match (highest boosted weight)
        self.assertIn(
            results[0]['attrs']['feature_id'], ['111001_0', '111001_2', '111001_3'],
            "First result should be an exact match"
        )

        # Prefix match should be ranked lower than exact matches
        prefix_match_index = next(
            (i for i, r in enumerate(results) if r['attrs']['feature_id'] == '11100130_0'), None
        )
        self.assertIsNotNone(prefix_match_index, "Prefix match should be in results")
        self.assertGreater(prefix_match_index, 0, "Prefix match should not be first")

    def test_no_boosting_when_no_exact_match(self, mock):
        """Test that results without exact matches don't get boosted"""
        mock_results = [{
            'matches': [{
                'id': 1,
                'weight': 2600,
                'attrs': {
                    'detail': 'via valle verzasca 7 6632 vogorno verzasca _ti_ 11100130',
                    'feature_id': '11100130_0',
                }
            }],
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
            'matches': [{
                'id': 1,
                'weight': 2500,
                'attrs': {
                    'detail': 'test abc123 example',
                    'feature_id': 'test_1',
                }
            }],
        }]

        mock.return_value = mock_results

        # Search with lowercase
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='ABC123',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        results = response.json['results']

        # Should be boosted despite case difference
        self.assertEqual(
            results[0]['weight'], 12500, "Case-insensitive exact match should be boosted"
        )

    def test_multiword_with_intervening_words(self, mock):
        """Test that multi-word searches boost results even with intervening words."""
        mock_results = [{
            'matches': [
                # Result with all search words in order but with intervening words
                # Search: "bahnhofstrasse 2 langenthal"
                # Detail has "bahnhofstrasse 2 4900 langenthal langenthal..."
                {
                    'id': 1,
                    'weight': 2500,
                    'attrs': {
                        'detail':
                            'bahnhofstrasse 2 4900 langenthal langenthal _be_ 1259385 100721941',
                        'feature_id': 'test_1',
                    }
                },
                # Result with only partial match
                {
                    'id': 2,
                    'weight': 2600,
                    'attrs': {
                        'detail': 'bahnhofstrasse 5 langenthal',
                        'feature_id': 'test_2',
                    }
                },
                # Result with exact consecutive match
                {
                    'id': 3,
                    'weight': 2400,
                    'attrs': {
                        'detail': 'bahnhofstrasse 2 langenthal _be_',
                        'feature_id': 'test_3',
                    }
                },
            ],
        }]

        mock.return_value = mock_results

        # Search with multi-word query
        response = self.app.get(
            url_for(
                'search_server',
                topic='ech',
                type='featuresearch',
                searchText='Bahnhofstrasse 2 Langenthal',
                features='ch.bfs.gebaeude_wohnungs_register'
            ),
            headers=self.origin_headers["allowed"]
        )

        self.assertEqual(response.status_code, 200)
        results = response.json['results']

        # Results should be reordered:
        # 1. Exact consecutive match (test_3): 2400 + 10000 = 12400
        # 2. All words in order but non-consecutive (test_1): 2500 + 5000 = 7500
        # 3. Partial match (test_2): 2600 (no boost)

        self.assertEqual(len(results), 3, "Should have all three results")

        # Verify the exact consecutive match is first
        self.assertEqual(results[0]['attrs']['feature_id'], 'test_3')
        self.assertEqual(
            results[0]['weight'], 12400, "Exact consecutive match should get +10000 boost"
        )

        # Verify the result with all words in order is second
        self.assertEqual(results[1]['attrs']['feature_id'], 'test_1')
        self.assertEqual(
            results[1]['weight'],
            7500,
            "All words in order (non-consecutive) should get +5000 boost"
        )

        # Verify the partial match is third
        self.assertEqual(results[2]['attrs']['feature_id'], 'test_2')
        self.assertEqual(results[2]['weight'], 2600, "Partial match should not be boosted")
