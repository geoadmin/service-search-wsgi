from unittest import TestCase

from numpy.testing import assert_almost_equal
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import mapping

from app.helpers.helpers_search import _round_bbox_coordinates
from app.helpers.helpers_search import _round_shape_coordinates
from app.helpers.helpers_search import _transform_coordinates
from app.helpers.helpers_search import _transform_point
from app.helpers.helpers_search import _transform_shape
from app.helpers.helpers_search import center_from_box2d
from app.helpers.helpers_search import escape_sphinx_syntax
from app.helpers.helpers_search import float_raise_nan
from app.helpers.helpers_search import format_search_text
from app.helpers.helpers_search import get_precision_for_proj
from app.helpers.helpers_search import get_proj_from_srid
from app.helpers.helpers_search import parse_box2d
from app.helpers.helpers_search import remove_accents
from app.helpers.helpers_search import round_geometry_coordinates
from app.helpers.helpers_search import transform_round_geometry

# pylint: disable=invalid-name


class Test_Helpers(TestCase):

    def test_format_search_text(self):
        testinput_str = 'Hallo!'
        result = format_search_text(testinput_str)
        self.assertEqual(result, 'Hallo\\!')

        testinput_str2 = 'über'
        result2 = format_search_text(testinput_str2)
        self.assertEqual(result2, 'ueber')

    def test_remove_accents(self):
        testinput_str = None
        result = remove_accents(testinput_str)
        self.assertEqual(result, None)

    def test_escape_sphinx_syntax(self):
        testinput_str = None
        result = escape_sphinx_syntax(testinput_str)
        self.assertEqual(result, None)

    def test_float_raise_nan(self):
        testval = 5
        result = float_raise_nan(testval)
        self.assertEqual(result, 5.0)
        with self.assertRaises(ValueError):
            float_raise_nan(float('nan'))

    def test_parse_box2d(self):
        strBox2d = 'BOX(1.1 2.2,3.3 4.4)'
        box2d = parse_box2d(strBox2d)
        self.assertEqual(box2d[0], 1.1)
        self.assertEqual(box2d[1], 2.2)
        self.assertEqual(box2d[2], 3.3)
        self.assertEqual(box2d[3], 4.4)

    def test_center_from_box2d(self):
        box2d = [1.1, 2.2, 3.3, 6.6]
        center = center_from_box2d(box2d)
        self.assertEqual(center[0], 2.2)
        self.assertEqual(center[1], 4.4)

    def test_center_from_box2d_wrong(self):
        box2d = [10.1, 2.2, 3.3, 6.6]
        with self.assertRaises(ValueError):
            center_from_box2d(box2d)
        box2d = [1.1, 2.2, 3.3]
        with self.assertRaises(ValueError):
            center_from_box2d(box2d)

    def test_get_proj_from_srid(self):
        srid = 21781
        proj = get_proj_from_srid(srid)
        self.assertFalse(proj.crs.is_geographic)
        # defined crs without ntv2 grid
        str_proj_lv03 = '+proj=somerc +lat_0=46.9524055555556 +lon_0=7.43958333333333 ' \
        '+k_0=1 +x_0=600000 +y_0=200000 +ellps=bessel +units=m +no_defs'
        self.assertEqual(proj.srs, str_proj_lv03)

    def test__transform_point(self):
        srid_from = 4326
        srid_to = 21781
        coords = _transform_point([7.37840, 45.91616], srid_from, srid_to)
        self.assertEqual(int(coords[0]), 595324)
        self.assertEqual(int(coords[1]), 84952)

    def get_precision_for_proj(self):
        # rounding all coordinates for to about 0.1 meter
        # Lat/Long proj -> precision of 7 decimals
        # Metric proj   -> precision of 1 decimal (obviously)
        self.assertEqual(get_precision_for_proj(2056), 1)
        self.assertEqual(get_precision_for_proj(3857), 1)
        self.assertEqual(get_precision_for_proj(21781), 1)
        self.assertEqual(get_precision_for_proj(4326), 7)

    def test__round_bbox_coordinates(self):
        bbox = [1.1111, 2.2222, 3.33333333, 4.44444444]
        self.assertEqual(_round_bbox_coordinates(bbox, precision=1), [1.1, 2.2, 3.3, 4.4])

    def test__round_shape_coordinates(self):
        point = Point(1.3456, 3.43434)
        point_rounded = _round_shape_coordinates(point, precision=1)
        polygon = Polygon([(0.231, 0.345), (1.4564, 1.1965), (1.38509, 0.97979)])
        polygon_rounded = _round_shape_coordinates(polygon, precision=2)

        self.assertEqual(mapping(point_rounded), {'type': 'Point', 'coordinates': (1.3, 3.4)})
        self.assertNotEqual(mapping(point), {'type': 'Point', 'coordinates': (1.3, 3.4)})
        self.assertEqual(
            mapping(polygon_rounded),
            {
                'coordinates': (((0.23, 0.34), (1.46, 1.2), (1.39, 0.98), (0.23, 0.34)),),
                'type': 'Polygon'
            }
        )
        self.assertNotEqual(mapping(polygon)['coordinates'][0], (0.231, 0.345))

    def test_round_geometry_coordinates(self):
        point = Point(1.3456, 3.43434)
        point_rounded = round_geometry_coordinates(point, precision=1)
        self.assertEqual(mapping(point_rounded), {'type': 'Point', 'coordinates': (1.3, 3.4)})

        bbox = [1.1111, 2.2222, 3.33333333, 4.44444444]
        self.assertEqual(round_geometry_coordinates(bbox, precision=1), [1.1, 2.2, 3.3, 4.4])

    def test__transform_coordinates(self):
        bbox = [2600000, 1200000, 2650000, 1250000]
        bbox_wgs84 = _transform_coordinates(bbox, 2056, 4326, rounding=False)
        bbox_wgs84_rounded = _transform_coordinates(bbox, 2056, 4326, rounding=True)

        self.assertEqual(bbox_wgs84_rounded, [7.438632, 46.951083, 8.100963, 47.398925])
        assert_almost_equal(
            bbox_wgs84,
            [7.438632420871815, 46.95108277187108, 8.100963474961302, 47.39892497922299],
            decimal=10
        )

    def test_transform_shape(self):
        point = Point(2600000, 120000)
        point_wgs84 = _transform_shape(point, 2056, 4326, rounding=False)
        point_wgs84_rounded = _transform_shape(point, 2056, 4326)

        self.assertEqual(
            mapping(point_wgs84_rounded), {
                'type': 'Point', 'coordinates': (7.438767, 37.274227)
            }
        )
        assert_almost_equal(point_wgs84.coords[0], (7.438767146513139, 37.27422679580366))

    def test_transform_round_geometry(self):

        bbox = [2600000, 1200000, 2650000, 1250000]
        bbox_wgs84 = transform_round_geometry(bbox, 2056, 4326, rounding=False)
        bbox_wgs84_rounded = transform_round_geometry(bbox, 2056, 4326, rounding=True)

        self.assertEqual(bbox_wgs84_rounded, [7.438632, 46.951083, 8.100963, 47.398925])
        assert_almost_equal(
            bbox_wgs84,
            [7.438632420871815, 46.95108277187108, 8.100963474961302, 47.39892497922299],
            decimal=10
        )

        point = Point(2600000, 120000)
        point_wgs84 = transform_round_geometry(point, 2056, 4326, rounding=False)
        point_wgs84_rounded = transform_round_geometry(point, 2056, 4326)

        self.assertEqual(
            mapping(point_wgs84_rounded), {
                'type': 'Point', 'coordinates': (7.438767, 37.274227)
            }
        )
        assert_almost_equal(
            point_wgs84.coords[0], (7.438767146513139, 37.27422679580366), decimal=10
        )
