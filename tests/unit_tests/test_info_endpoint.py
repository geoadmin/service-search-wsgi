from flask import url_for

from tests.unit_tests.base_test import BaseSearchTest


class TestInfoEndpoint(BaseSearchTest):

    def test_info_endpoint(self):
        response = self.app.get(url_for('service_info'), headers=self.origin_headers["allowed"])
        self.assertEqual(response.status_code, 200)
        for item in response.json:
            self.assertIn('version', item)
            self.assertIn('name', item)
        self.assertCacheControl(response)
