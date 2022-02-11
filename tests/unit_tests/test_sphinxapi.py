import unittest
from unittest.mock import patch

from nose2.tools import params

from app.lib import sphinxapi
from tests.unit_tests.sphinxapi_patch import patch_sphinx_server


class SpinxApiBaseTest(unittest.TestCase):

    @staticmethod
    def get_sphinx_client():
        api = sphinxapi.SphinxClient()
        api.SetServer('localhost', 9312)
        api.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        return api


class TestSphinxApi(SpinxApiBaseTest):

    def test_sphinx_api_error(self):
        api = self.get_sphinx_client()
        self.assertEqual(api.GetLastError(), '')

    def test_sphinx_api_warning(self):
        api = self.get_sphinx_client()
        self.assertEqual(api.GetLastWarning(), '')

    def test_sphinx_api_set_server(self):
        # pylint: disable=protected-access
        api = self.get_sphinx_client()
        host1 = 'unix://path1'
        port1 = 9312
        api.SetServer(host1, port1)
        self.assertEqual(api._host, 'localhost')
        self.assertEqual(api._port, port1)
        self.assertEqual(api._path, 'path1')

        host2 = '/totohost'
        port2 = 65535
        api.SetServer(host2, port2)
        self.assertEqual(api._host, 'localhost')
        self.assertEqual(api._port, port2)
        self.assertEqual(api._path, host2)

        host3 = 'my.domain.com'
        port3 = 65535
        api.SetServer(host3, port3)
        self.assertEqual(api._host, 'my.domain.com')
        self.assertEqual(api._port, port3)
        self.assertEqual(api._path, None)

    def test_sphinx_api_escape_string(self):
        api = self.get_sphinx_client()
        normal_str = 'bern'
        res2 = api.EscapeString(normal_str)
        self.assertEqual(res2, normal_str)

        esc_str = 'hi$toto'
        res3 = api.EscapeString(esc_str)
        self.assertEqual(res3, r'hi\$toto')


@patch('app.lib.sphinxapi.SphinxClient._Connect')
class TestSphinxApiCommunication(SpinxApiBaseTest):

    def test_sphinx_api_build_excerpts(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_BUILD_EXCERPTS_SOCK
        api = self.get_sphinx_client()
        docs = [
            'this is my test text to be highlighted', 'this is another test text to be highlighted'
        ]
        words = 'test text'
        index = 'layers_de'
        opts = {
            'before_match': '<i>',
            'after_match': '</i>',
            'chunk_separator': ' ... ',
            'limit': 400,
            'around': 15
        }
        res = api.BuildExcerpts(docs, index, words, opts)
        self.assertListEqual(
            res,
            [
                'this is my <i>test</i> <i>text</i> to be highlighted',
                'this is another <i>test</i> <i>text</i> to be highlighted'
            ]
        )

    def test_sphinx_api_build_excerpts_no_opts(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_BUILD_EXCERPTS_NO_OPTS_SOCK
        api = self.get_sphinx_client()
        docs = [
            'this is my test text to be highlighted', 'this is another test text to be highlighted'
        ]
        words = 'test text'
        index = 'layers_de'
        res = api.BuildExcerpts(docs, index, words)
        self.assertListEqual(
            res,
            [
                'this is my <b>test</b> <b>text</b> to be highlighted',
                'this is another <b>test</b> <b>text</b> to be highlighted'
            ]
        )

    def test_sphinx_api_search_query(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_SEARCH_QUERY_SOCK
        api = self.get_sphinx_client()
        query = 'bern'
        res = api.Query(query)
        self.assertNotEqual(res['status'], sphinxapi.SEARCHD_OK)
        self.assertGreaterEqual(len(res['matches']), 10)
        self.assertGreaterEqual(res['total'], 10)
        self.assertGreaterEqual(res['total_found'], 10)
        self.assertEqual(
            res['matches'][0],
            {
                'attrs': {
                    'detail':
                        'waermeversorgung der ueberbauung weltpoststrasse bern, '
                        'mit eisspeicher-waermepumpe system unter nutzung von '
                        'solar- und abwasserwaerme waermeversorgung der '
                        'ueberbauung weltpoststrasse bern, mit '
                        'eisspeicher-waermepumpe system unter nutzung von solar- '
                        'und abwasserwaerme waermeversorgung der ueberbauung '
                        'weltpoststrasse bern, mit eisspeicher-waermepumpe system '
                        'unter nutzung von solar- und abwasserwaerme '
                        'waermeversorgung der ueberbauung weltpoststrasse bern, '
                        'mit eisspeicher-waermepumpe system unter nutzung von '
                        'solar- und abwasserwaerme',
                    'label':
                        'Wärmeversorgung der Überbauung Weltpoststrasse Bern, mit '
                        'Eisspeicher-Wärmepumpe System unter Nutzung von Solar- '
                        'und Abwasserwärme',
                    'origin': 'feature'
                },
                'id': 3981,
                'weight': 1884
            }
        )

    def test_update_attributes(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_UPDATE_ATTRIBUTES_SOCK
        api = self.get_sphinx_client()
        index = 'layers_de'
        attrs = ['toto', 'tutu']
        values1 = {
            2: [[123, 1000000000], [256, 1789789687]], 4: [[456, 1234567890], [789, 2034578990]]
        }

        res2 = api.UpdateAttributes(index, attrs, values1, True)
        self.assertEqual(res2, 1)

    @params(
        (patch_sphinx_server.MOCK_QUERY_SOCK_1, ('rank', [1, 2]), None, None, 1, 10),
        (patch_sphinx_server.MOCK_QUERY_SOCK_2, None, 'rank', None, None, None),
        (patch_sphinx_server.MOCK_QUERY_SOCK_3, None, None, 'rank ASC', None, None),
    )
    def test_sphinx_api_query(
        self, mocker, search_filter, group_by, sort_by, limit, query_time, mock_socket
    ):
        mock_socket.return_value = mocker
        api = self.get_sphinx_client()
        query = 'bern'
        mode = sphinxapi.SPH_MATCH_EXTENDED
        index = 'swisssearch'

        api.ResetGroupBy()
        api.SetFieldWeights({'detail': 100})
        api.SetIndexWeights({'address': 99})
        api.SetIDRange(1, 2000)
        api.SetMatchMode(mode)
        if search_filter is not None:
            api.SetFilter(*search_filter)
        if group_by is not None:
            api.SetGroupBy(group_by, sphinxapi.SPH_GROUPBY_ATTR, '@rank ASC')
        if sort_by is not None:
            api.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, sort_by)
        if limit is not None:
            api.SetLimits(0, limit, max(limit, 1000))
        if query_time is not None:
            api.SetMaxQueryTime(query_time)
        res = api.Query(query, index=index)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['status'], sphinxapi.SEARCHD_OK)

    def test_sphinxapi_query_overrides(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_QUERY_OVERRIDES_SOCK
        api = self.get_sphinx_client()
        query = 'bern'
        index = 'swisssearch'
        values = {100: 'test'}

        api.ResetOverrides()
        api.SetFilterFloatRange('x', 0.5, 799.8)
        api.SetOverride('label', sphinxapi.SPH_ATTR_STRING, values)
        api.SetGroupBy('label', sphinxapi.SPH_GROUPBY_ATTR, '@group DESC')
        api.SetSelect('label')
        api.SetRetries(3)

        api.SetGroupDistinct('label')
        res = api.Query(query, index=index)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['status'], sphinxapi.SEARCHD_OK)
        self.assertEqual(res['fields'], ['detail', 'geom_quadindex'])
        self.assertEqual(
            res['attrs'],
            [['feature_id', 7], ['detail', 7], ['origin', 7], ['geom_quadindex', 7],
             ['geom_st_box2d', 7], ['geom_st_box2d_lv95', 7], ['rank', 1], ['x', 5], ['y', 5],
             ['y_lv95', 5], ['x_lv95', 5], ['lat', 5], ['lon', 5], ['num', 1], ['zoomlevel', 1],
             ['label', 7], ['@groupby', 6], ['@count', 1], ['@distinct', 1]]
        )
        self.assertEqual(res['words'], [{'word': 'bern', 'docs': 63407, 'hits': 88901}])

    def test_query_build_keywords(self, mock_socket):
        mock_socket.return_value = patch_sphinx_server.MOCK_QUERY_BUILD_KEYWORDS_SOCK
        api = self.get_sphinx_client()
        query = 'Seftigenstrasse 264'
        index = 'address'
        hits = 5
        res = api.BuildKeywords(query, index, hits)
        self.assertEqual(
            res,
            [{
                'docs': 374,
                'hits': 374,
                'normalized': 'seftigenstrasse',
                'tokenized': 'seftigenstrasse'
            }, {
                'docs': 215,
                'hits': 215,
                'normalized': '264',
                'tokenized': '264',
            }]
        )
