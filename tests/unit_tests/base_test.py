import unittest

from app import app


class SearchTest(unittest.TestCase):

    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()
        self.app = app.test_client()
        self.app.testing = True
        self.origin_headers = {
            "allowed": {
                "Origin": "some_random_domain"
            }, "bad": {
                "Origin": "big-bad-wolf.com"
            }
        }
