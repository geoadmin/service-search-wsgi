import unittest

from gatilegrid import getTileGrid

from app import app
from app.helpers.helpers_search import parse_box2d
from app.helpers.validation_search import SUPPORTED_OUTPUT_SRS
from app.settings import CACHE_CONTROL_HEADER


class BaseSearchTest(unittest.TestCase):

    def setUp(self):
        self.context = app.test_request_context()
        self.context.push()
        self.app = app.test_client()

        # an origin header has to be set
        self.origin_headers = {"allowed": {"Origin": "unittesting"}}
        self.grids = {
            '21781': getTileGrid(21781),
            '2056': getTileGrid(2056),
            '3857': getTileGrid(3857),
            '4326': getTileGrid(4326)
        }

    def assertGeojsonFeature(self, feature, srid, has_geometry=True, has_layer=True):
        self.assertIn('id', feature)
        self.assertIn('properties', feature)
        self.assertNotIn('attributes', feature)
        if has_layer:
            self.assertIn('layerBodId', feature)
            self.assertIn('layerName', feature)
        if has_geometry:
            self.assertIn('geometry', feature)
            self.assertIn('type', feature)
            self.assertIn('type', feature['geometry'])
            self.assertIn('bbox', feature)
            self.assertBBoxValidity(feature['bbox'], srid)

    def assertEsrijsonFeature(self, feature, srid, has_geometry=True, has_layer=True):
        self.assertIn('id', feature)
        self.assertNotIn('properties', feature)
        self.assertIn('attributes', feature)
        if has_layer:
            self.assertIn('layerBodId', feature)
            self.assertIn('layerName', feature)
        if has_geometry:
            self.assertIn('geometry', feature)
            self.assertIn('bbox', feature)
            self.assertEqual(feature['geometry']['spatialReference']['wkid'], srid)
            self.assertBBoxValidity(feature['bbox'], srid)

    def assertBBoxValidity(self, bbox, srid):
        self.assertIn(srid, SUPPORTED_OUTPUT_SRS)
        grid = self.grids[str(srid)]
        minx, miny, maxx, maxy = bbox

        self.assertLessEqual(maxx, grid.MAXX)
        self.assertLessEqual(maxy, grid.MAXY)
        self.assertGreaterEqual(minx, grid.MINX)
        self.assertGreaterEqual(miny, grid.MINY)

    def assertAttrs(self, type_, attrs, srid, return_geometry=True, spatial_order=False):
        self.assertIn('detail', attrs)
        self.assertIn('origin', attrs)
        self.assertIn('label', attrs)
        if type_ in ('locations'):
            self.assertIn('geom_quadindex', attrs)
            if return_geometry:
                self.assertIn('lon', attrs)
                self.assertIn('lat', attrs)
                if srid == 21781:
                    self.assertLess(attrs['y'], self.grids['2056'].MINX)
                    self.assertLess(attrs['x'], self.grids['2056'].MINY)
                if srid in (2056, 4326, 3857):
                    self.assertGreater(attrs['y'], self.grids[str(srid)].MINX)
                    self.assertGreater(attrs['x'], self.grids[str(srid)].MINY)
            else:
                self.assertNotIn('lon', attrs)
                self.assertNotIn('lat', attrs)
                self.assertNotIn('geom_st_box2d', attrs)
                self.assertNotIn('x', attrs)
                self.assertNotIn('y', attrs)
        elif type_ == 'layers':
            self.assertIn('lang', attrs)
            self.assertIn('staging', attrs)
            self.assertIn('title', attrs)
            self.assertIn('topics', attrs)
        elif type_ == 'featuresearch':
            self.assertIn('lon', attrs)
            self.assertIn('lat', attrs)
            self.assertIn('geom_quadindex', attrs)
            self.assertIn('featureId', attrs)
            self.assertIn('layer', attrs)

        if type_ in ('locations', 'featuresearch') and return_geometry:
            if hasattr(attrs, 'geom_st_box2d'):
                bbox = parse_box2d(attrs['geom_st_box2d'])
                self.assertBBoxValidity(bbox, srid)
            if spatial_order:
                self.assertIn('@geodist', attrs)
            else:
                self.assertNotIn('@geodist', attrs)
        self.assertNotIn('x_lv95', attrs)
        self.assertNotIn('y_lv95', attrs)
        self.assertNotIn('geom_st_box2d_lv95', attrs)

    def assertCacheControl(self, response):
        self.assertIn('Cache-Control', response.headers)
        self.assertEqual(response.headers['Cache-Control'], CACHE_CONTROL_HEADER)
