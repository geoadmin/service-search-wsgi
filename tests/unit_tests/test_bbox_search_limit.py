import unittest
from unittest.mock import patch

from app.helpers.validation_search import MapNameValidation
from app.lib import sphinxapi
from app.search import Search

# Bounding box (EPSG:21781) used for the tests; all mocked matches sit inside it.
BBOX = '600000,200000,700000,300000'


class DummyAcceptLanguages:  # pylint: disable=too-few-public-methods

    def best_match(self, available):  # pylint: disable=unused-argument
        return 'de'


class DummyRequest:  # pylint: disable=too-few-public-methods

    def __init__(self, args=None):
        self.args = args or {}
        self.accept_languages = DummyAcceptLanguages()


def _match(match_id, origin, rank, weight, num):
    """A single Sphinx match located inside BBOX, carrying an internal @geodist."""
    return {
        'id': match_id,
        'weight': weight,
        'attrs': {
            'detail': f'bahnhofstrasse 1 {match_id} testcity',
            'origin': origin,
            'feature_id': f'{match_id}_0',
            'label': f'label {match_id}',
            'geom_st_box2d': 'BOX(650000 250000,650000 250000)',
            'x': 650000,
            'y': 250000,
            'rank': rank,
            'num': num,
            '@geodist': float(match_id),
        }
    }


def _mock_addresses(count):
    """`count` equally-weighted address matches inside BBOX."""
    return [{'matches': [_match(i + 1, 'address', 7, 100, 1) for i in range(count)]}]


@patch.object(MapNameValidation, 'has_topic', staticmethod(lambda topic: None))
@patch.object(sphinxapi.SphinxClient, 'RunQueries')
class TestBboxSearch(unittest.TestCase):
    """Location search within a bbox (HDG-79)."""

    @staticmethod
    def _search(sortbbox):
        req = DummyRequest({
            'type': 'locations',
            'searchText': 'bahnhofstrasse 1',
            'bbox': BBOX,
            'sortbbox': sortbbox
        })
        return Search(req, 'all')

    def test_sortbbox_false_returns_in_bbox_results(self, mock_run):
        # Core fix: sortbbox=false with a bbox must return the in-bbox matches, not an empty list
        mock_run.return_value = _mock_addresses(5)
        results = self._search('false').search()['results']
        self.assertEqual(len(results), 5)

    def test_sortbbox_false_uses_documented_order(self, mock_run):
        # Documented order: ascending rank, then weight DESC, then num ASC (scrambled on input)
        mock_run.return_value = [{
            'matches': [
                _match(1, 'address', 7, 100, 2),
                _match(2, 'gazetteer', 6, 100, 1),
                _match(3, 'address', 7, 50, 1),
                _match(4, 'address', 7, 100, 1),
            ]
        }]
        results = self._search('false').search()['results']
        self.assertEqual([r['id'] for r in results], [2, 4, 1, 3])

    def test_sortbbox_false_strips_geodist(self, mock_run):
        mock_run.return_value = _mock_addresses(3)
        results = self._search('false').search()['results']
        self.assertTrue(results)
        for result in results:
            self.assertNotIn('@geodist', result['attrs'])

    def test_sortbbox_false_caps_at_location_limit(self, mock_run):
        # 60 in-bbox matches, more than LOCATION_LIMIT (50)
        mock_run.return_value = _mock_addresses(60)
        results = self._search('false').search()['results']
        self.assertEqual(len(results), Search.LOCATION_LIMIT)

    def test_sortbbox_true_keeps_larger_cap(self, mock_run):
        # sortbbox=true keeps its pre-existing BBOX_SEARCH_LIMIT window and the @geodist attribute
        mock_run.return_value = _mock_addresses(60)
        results = self._search('true').search()['results']
        self.assertEqual(len(results), 60)
        self.assertIn('@geodist', results[0]['attrs'])
