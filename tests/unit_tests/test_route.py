import logging

from flask import url_for

from app.version import APP_VERSION
from tests.unit_tests.base_test import SearchTest

logger = logging.getLogger(__name__)


class CheckerTests(SearchTest):

    def test_checker(self):
        response = self.app.get(url_for('checker'), headers=self.origin_headers["allowed"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json, {"message": "OK", "success": True, "version": APP_VERSION})

    def test_checker_non_allowed_origin(self):
        response = self.app.get(url_for('checker'), headers=self.origin_headers["bad"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["error"]["message"], "Not allowed")
