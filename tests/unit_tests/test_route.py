import logging
from unittest.mock import patch

from flask import url_for

from app.version import APP_VERSION
from tests.unit_tests.base_test import BaseSearchTest
from tests.unit_tests.sphinxapi_patch import patch_search_layers_run_queries

logger = logging.getLogger(__name__)


class CheckerTests(BaseSearchTest):

    def test_checker(self):
        response = self.app.get(url_for('checker'), headers=self.origin_headers["allowed"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})


@patch('app.lib.sphinxapi.SphinxClient.RunQueries')
class TestSearchService(BaseSearchTest):

    def test_search_layers(self, mock):
        mock.return_value = patch_search_layers_run_queries.results
        response = self.app.get(
            url_for('search_server', topic='inspire', type='layers', searchText='wand'),
            headers=self.origin_headers["allowed"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        logger.debug('response %s', response.json)
        self.assertEqual(response.json['results'][0]['attrs']['lang'], 'de')
        self.assertAttrs('layers', response.json['results'][0]['attrs'], 21781)
        self.assertCacheControl(response)

    def test_search_layers_geojson(self, mock):
        mock.return_value = patch_search_layers_run_queries.results
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
        self.assertCacheControl(response)

    def test_search_layers_geojson_with_projection_one(self, mock):
        mock.return_value = patch_search_layers_run_queries.results
        projections = {
            '2056': [2420000.0, 1030000.0, 2900000.0, 1510000.0],
            '4326': [5.140299, 45.398122, 11.591427, 49.666411],
            '3857': [572215.4, 5684417.0, 1290351.8, 6388703.2],
            '21781': [420000, 30000, 900000, 510000]
        }
        for srid in list(projections.keys()):
            response = self.app.get(
                url_for(
                    'search_server',
                    topic='inspire',
                    type='layers',
                    searchText='wand',
                    geometryFormat='geojson',
                    sr=srid
                ),
                headers=self.origin_headers["allowed"]
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/geo+json')
            self.assertEqual(response.json['type'], 'FeatureCollection')
            self.assertEqual(response.json['bbox'], projections[srid])
            self.assertCacheControl(response)
