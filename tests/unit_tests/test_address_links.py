import unittest
from unittest.mock import patch

from app.helpers.validation_search import MapNameValidation
from app.search import Search

# Note: This test file directly tests the _parse_location_results internal method
# rather than using BaseSearchTest with the Flask test client. This approach allows
# for focused unit testing of the links generation logic without requiring a full
# Sphinx server mock setup.


class DummyAcceptLanguages:  # pylint: disable=too-few-public-methods

    def best_match(self, available):  # pylint: disable=unused-argument
        return 'de'


class DummyRequest:  # pylint: disable=too-few-public-methods

    def __init__(self, args=None):
        self.args = args or {}
        self.accept_languages = DummyAcceptLanguages()


@patch.object(MapNameValidation, 'has_topic', staticmethod(lambda topic: None))
class TestAddressLinksComprehensive(unittest.TestCase):
    """Test all scenarios for the address links feature."""

    def _make_search(self):
        """Create a Search instance for testing."""
        req = DummyRequest({'type': 'locations'})
        search = Search(req, 'all')
        search.bbox = None
        return search

    def _make_result(self, origin_name, **attrs):
        """Create a mock search result with given attrs."""
        default_attrs = {
            'origin': origin_name,
            'feature_id': f'fid_{origin_name}',
            'label': f'{origin_name} label',
            'geom_st_box2d': 'BOX(420000 30000,420000 30000)',
            'x': 600000,
            'y': 200000,
        }
        default_attrs.update(attrs)
        return {
            'id': hash(origin_name),
            'weight': 100,
            'attrs': default_attrs,
        }

    def test_address_with_both_egaid_and_egid_edid(self):
        """Address with both attrs: links should be added with both entries."""
        search = self._make_search()
        results = [self._make_result('address', egaid='EGAID_001', egid_edid='EGID_EDID_001')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertIn('links', result)
        self.assertEqual(len(result['links']), 2)

        titles = {link['title'] for link in result['links']}
        self.assertEqual(
            titles,
            {
                'ch.swisstopo.amtliches-gebaeudeadressverzeichnis',
                'ch.bfs.gebaeude_wohnungs_register',
            },
        )

        hrefs = {link['href'] for link in result['links']}
        self.assertIn(
            '/rest/services/ech/MapServer/'
            'ch.swisstopo.amtliches-gebaeudeadressverzeichnis/EGID_EDID_001',
            hrefs,
        )
        self.assertIn(
            '/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/EGID_EDID_001',
            hrefs,
        )

    def test_address_with_only_egaid(self):
        """Address with only egaid: no links section (both attrs required)."""
        search = self._make_search()
        results = [self._make_result('address', egaid='EGAID_001')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_address_with_only_egid_edid(self):
        """Address with only egid_edid: no links section (both attrs required)."""
        search = self._make_search()
        results = [self._make_result('address', egid_edid='EGID_EDID_001')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_address_with_neither_egaid_nor_egid_edid(self):
        """Address with no attrs: no links section."""
        search = self._make_search()
        results = [self._make_result('address')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_address_metaphone_with_both_attrs(self):
        """Address_metaphone with both attrs: links should be added."""
        search = self._make_search()
        results = [
            self._make_result(
                'address_metaphone',
                egaid='EGAID_002',
                egid_edid='EGID_EDID_002',
            )
        ]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertIn('links', result)
        self.assertEqual(len(result['links']), 2)

    def test_address_metaphone_with_only_egaid(self):
        """Address_metaphone with only egaid: no links section."""
        search = self._make_search()
        results = [self._make_result('address_metaphone', egaid='EGAID_002')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_address_metaphone_with_no_attrs(self):
        """Address_metaphone with no attrs: no links section."""
        search = self._make_search()
        results = [self._make_result('address_metaphone')]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_non_address_origin_no_links(self):
        """Non-address origin (zipcode): no links section even with attrs."""
        search = self._make_search()
        results = [self._make_result(
            'zipcode',
            egaid='EGAID_003',
            egid_edid='EGID_EDID_003',
        )]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        self.assertNotIn('links', result)

    def test_multiple_results_mixed_scenarios(self):
        """Mixed results: only those with both attrs and address origin get links."""
        search = self._make_search()
        results = [
            # Address with both attrs → has links
            self._make_result(
                'address',
                egaid='EGAID_A',
                egid_edid='EGID_EDID_A',
            ),
            # Address with only egaid → no links
            self._make_result(
                'address',
                egaid='EGAID_B',
            ),
            # Address_metaphone with both attrs → has links
            self._make_result(
                'address_metaphone',
                egaid='EGAID_C',
                egid_edid='EGID_EDID_C',
            ),
            # Zipcode with both attrs → no links (wrong origin)
            self._make_result(
                'zipcode',
                egaid='EGAID_D',
                egid_edid='EGID_EDID_D',
            ),
        ]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        results_list = search.results['results']
        self.assertEqual(len(results_list), 4)

        # First result: address with both attrs
        self.assertIn('links', results_list[0]['attrs'])

        # Second result: address with only egaid
        self.assertNotIn('links', results_list[1]['attrs'])

        # Third result: address_metaphone with both attrs
        self.assertIn('links', results_list[2]['attrs'])

        # Fourth result: zipcode with both attrs
        self.assertNotIn('links', results_list[3]['attrs'])

    def test_links_structure_and_content(self):
        """Validate the structure and content of generated links."""
        search = self._make_search()
        results = [
            self._make_result(
                'address',
                egaid='TEST_EGAID_VALUE',
                egid_edid='TEST_EGID_EDID_VALUE',
            )
        ]

        search._parse_location_results(results, limit=10)  # pylint: disable=protected-access

        result = search.results['results'][0]['attrs']
        links = result['links']

        for link in links:
            self.assertIn('rel', link)
            self.assertEqual(link['rel'], 'related')
            self.assertIn('title', link)
            self.assertIn('href', link)
            self.assertTrue(link['href'].startswith('/rest/services/ech/MapServer/'))

        # Verify gebaeude_wohnungs_register link
        egid_link = next((lnk for lnk in links if 'gebaeude_wohnungs_register' in lnk['title']),
                         None)

        self.assertIsNotNone(egid_link)
        self.assertEqual(
            egid_link['href'],
            '/rest/services/ech/MapServer/ch.bfs.gebaeude_wohnungs_register/'
            'TEST_EGID_EDID_VALUE',
        )


if __name__ == '__main__':
    unittest.main()
