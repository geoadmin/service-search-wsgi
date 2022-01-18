# -*- coding: utf-8  -*-

from app.lib import sphinxapi
from tests.unit_tests.base_test import BaseSearchTest


class TestSphinxApi(BaseSearchTest):

    @staticmethod
    def _get_sphinx_client():
        api = sphinxapi.SphinxClient()
        api.SetServer('localhost', 9312)
        api.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        return api

    def test_sphinx_error(self):
        api = self._get_sphinx_client()
        api.GetLastError()

    def test_sphinx_warning(self):
        api = self._get_sphinx_client()
        api.GetLastWarning()

    def test_sphinx_set_server(self):
        api = self._get_sphinx_client()
        host1 = 'unix://host1'
        port1 = 9312
        api.SetServer(host1, port1)

        host2 = '/totohost'
        port2 = 65535
        api.SetServer(host2, port2)

    def test_sphinx_api(self):
        api = self._get_sphinx_client()
        docs = [
            'this is my test text to be highlighted', 'this is another test text to be highlighted'
        ]
        words = 'test text'
        index = 'layers'
        opts = {
            'before_match': '<b>',
            'after_match': '</b>',
            'chunk_separator': ' ... ',
            'limit': 400,
            'around': 15
        }
        res = api.BuildExcerpts(docs, index, words, opts)
        self.assertFalse(res)

    def test_sphinx_api_searchquery(self):
        api = self._get_sphinx_client()
        query = 'weShouldNotFoundAnyResultOnThisQuery'
        res = api.Query(query)
        self.assertNotEqual(res['status'], sphinxapi.SEARCHD_OK)
        self.assertEqual(res['matches'], [])
        self.assertEqual(res['total'], 0)
        self.assertEqual(res['total_found'], 0)

    def test_sphinx_api_no_opts(self):
        api = self._get_sphinx_client()
        docs = [
            'this is my test text to be highlighted', 'this is another test text to be highlighted'
        ]
        words = 'test text'
        index = 'layers'
        res = api.BuildExcerpts(docs, index, words)
        self.assertFalse(res)

    def test_update_attributes(self):
        api = self._get_sphinx_client()
        index = 'layers'
        attrs = ['toto', 'tutu']
        values1 = {2: [123, 1000000000], 4: [456, 1234567890]}
        values2 = {
            2: [[123, 1000000000], [256, 1789789687]], 4: [[456, 1234567890], [789, 2034578990]]
        }

        res1 = api.UpdateAttributes(index, attrs, values1)
        self.assertIsNone(res1)

        res2 = api.UpdateAttributes(index, attrs, values2, True)
        self.assertIsNone(res2)

    def test_sphinx_api_query(self):  # pylint: disable=too-many-locals
        api = self._get_sphinx_client()
        query = 'doma'
        mode = sphinxapi.SPH_MATCH_EXTENDED

        index = 'swisssearch'
        filtercol = 'rank'
        filtervals = [1, 2]
        sortby = ''
        groupby = ''
        groupsort = '@rank ASC'
        limit = 1
        maxquerytime = 10
        testquerytime = 11
        minid = 1
        maxid = 2000

        api.ResetGroupBy()
        api.SetFieldWeights({'toto': 100})
        api.SetIndexWeights({'toto': 99})
        api.SetIDRange(minid, maxid)
        api.SetMatchMode(mode)
        if filtervals:
            api.SetFilter(filtercol, filtervals)
        if groupby:
            api.SetGroupBy(groupby, sphinxapi.SPH_GROUPBY_ATTR, groupsort)
        if sortby:
            api.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, sortby)
        if limit:
            api.SetLimits(0, limit, max(limit, 1000))
        if testquerytime:
            api.SetMaxQueryTime(maxquerytime)
        res = api.Query(query, index=index)
        self.assertIsInstance(res, dict)

    def test_sphinxapi_query2(self):
        api = self._get_sphinx_client()
        attribute = 'toto'
        name = 'bern'
        groupsort = '@group desc'
        sphtype = sphinxapi.SPH_ATTR_STRING
        count = 15
        min_ = 0.5
        max_ = 799.8
        values = {100: 'bern'}

        api.ResetOverrides()
        api.SetFilterFloatRange(attribute, min_, max_)
        if groupsort:
            api.SetGroupBy(attribute, sphinxapi.SPH_GROUPBY_ATTR, groupsort)
        if count:
            api.SetRetries(count)
        if sphtype:
            api.SetOverride(name, sphtype, values)
        if name:
            api.SetSelect(name)
        api.SetGroupDistinct(attribute)

    def test_query_build_keywords(self):
        api = self._get_sphinx_client()
        query = 'toto'
        index = 'layers'
        hits = 5
        res = api.BuildKeywords(query, index, hits)
        self.assertFalse(res)

        res2 = api.EscapeString(query)
        self.assertEqual(res2, query)

        esc_str = 'hi$toto'
        res3 = api.EscapeString(esc_str)
        self.assertEqual(res3, r'hi\$toto')
        api.Close()
