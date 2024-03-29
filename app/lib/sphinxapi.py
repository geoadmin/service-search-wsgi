#
# $Id$
#
# Python version of Sphinx searchd client (Python API)
#
# Copyright (c) 2006, Mike Osadnik
# Copyright (c) 2006-2016, Andrew Aksyonoff
# Copyright (c) 2008-2016, Sphinx Technologies Inc
# All rights reserved
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License. You should
# have received a copy of the LGPL license along with this program; if you
# did not, you can find it at http://www.gnu.org/
#
# WARNING!!!
#
# As of 2015, we strongly recommend to use either SphinxQL or REST APIs
# rather than the native SphinxAPI.
#
# While both the native SphinxAPI protocol and the existing APIs will
# continue to exist, and perhaps should not even break (too much), exposing
# all the new features via multiple different native API implementations
# is too much of a support complication for us.
#
# That said, you're welcome to overtake the maintenance of any given
# official API, and remove this warning ;)
#

# pylint: disable=invalid-name,too-many-public-methods,too-many-locals,too-many-branches
# pylint: disable=too-many-statements,too-many-lines,too-many-instance-attributes

import logging
import re
import select
import socket
from struct import pack
from struct import unpack

logger = logging.getLogger(__name__)

# known searchd commands
SEARCHD_COMMAND_SEARCH = 0
SEARCHD_COMMAND_EXCERPT = 1
SEARCHD_COMMAND_UPDATE = 2
SEARCHD_COMMAND_KEYWORDS = 3
SEARCHD_COMMAND_PERSIST = 4
SEARCHD_COMMAND_STATUS = 5
SEARCHD_COMMAND_FLUSHATTRS = 7

# current client-side command implementation versions
VER_COMMAND_SEARCH = 0x11E
VER_COMMAND_EXCERPT = 0x104
VER_COMMAND_UPDATE = 0x103
VER_COMMAND_KEYWORDS = 0x100
VER_COMMAND_STATUS = 0x101
VER_COMMAND_FLUSHATTRS = 0x100

# known searchd status codes
SEARCHD_OK = 0
SEARCHD_ERROR = 1
SEARCHD_RETRY = 2
SEARCHD_WARNING = 3

# known match modes
SPH_MATCH_ALL = 0
SPH_MATCH_ANY = 1
SPH_MATCH_PHRASE = 2
SPH_MATCH_BOOLEAN = 3
SPH_MATCH_EXTENDED = 4
SPH_MATCH_FULLSCAN = 5
SPH_MATCH_EXTENDED2 = 6

# known ranking modes (extended2 mode only)
SPH_RANK_PROXIMITY_BM25 = 0  # default mode, phrase proximity major factor and BM25 minor one
SPH_RANK_BM25 = 1  # statistical mode, BM25 ranking only (faster but worse quality)
SPH_RANK_NONE = 2  # no ranking, all matches get a weight of 1
# simple word-count weighting, rank is a weighted sum of per-field keyword occurrence counts
SPH_RANK_WORDCOUNT = 3
SPH_RANK_PROXIMITY = 4
SPH_RANK_MATCHANY = 5
SPH_RANK_FIELDMASK = 6
SPH_RANK_SPH04 = 7
SPH_RANK_EXPR = 8
SPH_RANK_TOTAL = 9

# known sort modes
SPH_SORT_RELEVANCE = 0
SPH_SORT_ATTR_DESC = 1
SPH_SORT_ATTR_ASC = 2
SPH_SORT_TIME_SEGMENTS = 3
SPH_SORT_EXTENDED = 4
SPH_SORT_EXPR = 5

# known filter types
SPH_FILTER_VALUES = 0
SPH_FILTER_RANGE = 1
SPH_FILTER_FLOATRANGE = 2
SPH_FILTER_STRING = 3

# known attribute types
SPH_ATTR_NONE = 0
SPH_ATTR_INTEGER = 1
SPH_ATTR_TIMESTAMP = 2
SPH_ATTR_ORDINAL = 3
SPH_ATTR_BOOL = 4
SPH_ATTR_FLOAT = 5
SPH_ATTR_BIGINT = 6
SPH_ATTR_STRING = 7
SPH_ATTR_FACTORS = 1001
SPH_ATTR_MULTI = 0X40000001
SPH_ATTR_MULTI64 = 0X40000002

SPH_ATTR_TYPES = (
    SPH_ATTR_NONE,
    SPH_ATTR_INTEGER,
    SPH_ATTR_TIMESTAMP,
    SPH_ATTR_ORDINAL,
    SPH_ATTR_BOOL,
    SPH_ATTR_FLOAT,
    SPH_ATTR_BIGINT,
    SPH_ATTR_STRING,
    SPH_ATTR_MULTI,
    SPH_ATTR_MULTI64
)

# known grouping functions
SPH_GROUPBY_DAY = 0
SPH_GROUPBY_WEEK = 1
SPH_GROUPBY_MONTH = 2
SPH_GROUPBY_YEAR = 3
SPH_GROUPBY_ATTR = 4
SPH_GROUPBY_ATTRPAIR = 5


class SphinxClient:

    def __init__(self):
        """
        Create a new client object, and fill defaults.
        """
        # pylint: disable=line-too-long
        self._host = 'localhost'  # searchd host (default is "localhost")
        self._port = 9312  # searchd port (default is 9312)
        self._path = None  # searchd unix-domain socket path
        self._socket = None
        self._offset = 0  # how much records to seek from result-set start (default is 0)
        self._limit = 20  # how much records to return from result-set starting at offset (default is 20)
        self._mode = SPH_MATCH_ALL  # query matching mode (default is SPH_MATCH_ALL)
        self._weights = []  # per-field weights (default is 1 for all fields)
        self._sort = SPH_SORT_RELEVANCE  # match sorting mode (default is SPH_SORT_RELEVANCE)
        self._sortby = b''  # attribute to sort by (defualt is "")
        self._min_id = 0  # min ID to match (default is 0)
        self._max_id = 0  # max ID to match (default is UINT_MAX)
        self._filters = []  # search filters
        self._groupby = b''  # group-by attribute name
        self._groupfunc = SPH_GROUPBY_DAY  # group-by function (to pre-process group-by attribute value with)
        self._groupsort = b'@group desc'  # group-by sorting clause (to sort groups in result set with)
        self._groupdistinct = b''  # group-by count-distinct attribute
        self._maxmatches = 1000  # max matches to retrieve
        self._cutoff = 0  # cutoff to stop searching at
        self._retrycount = 0  # distributed retry count
        self._retrydelay = 0  # distributed retry delay
        self._anchor = {}  # geographical anchor point
        self._indexweights = {}  # per-index weights
        self._ranker = SPH_RANK_PROXIMITY_BM25  # ranking mode
        self._rankexpr = b''  # ranking expression for SPH_RANK_EXPR
        self._maxquerytime = 0  # max query time, milliseconds (default is 0, do not limit)
        self._timeout = 1.0  # connection timeout
        self._fieldweights = {}  # per-field-name weights
        self._overrides = {}  # per-query attribute values overrides
        self._select = b'*'  # select-list (attributes or expressions, with optional aliases)
        self._query_flags = SetBit(0, 6, True)  # default idf=tfidf_normalized
        self._predictedtime = 0  # per-query max_predicted_time
        self._outerorderby = b''  # outer match sort by
        self._outeroffset = 0  # outer offset
        self._outerlimit = 0  # outer limit
        self._hasouter = False  # sub-select enabled

        self._error = ''  # last error message
        self._warning = ''  # last warning message
        self._reqs = []  # requests array for multi-query

    def __del__(self):
        if self._socket:
            self._socket.close()

    def GetLastError(self):
        """
        Get last error message (string).
        """
        return self._error

    def GetLastWarning(self):
        """
        Get last warning message (string).
        """
        return self._warning

    def SetServer(self, host, port=None):
        """
        Set searchd server host and port.
        """
        assert isinstance(host, str)
        self._host = host
        self._path = None
        if host.startswith('/'):
            self._path = host
            self._host = 'localhost'
        elif host.startswith('unix://'):
            self._path = host[7:]
            self._host = 'localhost'
        if port is not None:
            assert isinstance(port, int)
            assert 0 < port < 65536
            self._port = port

    def SetConnectTimeout(self, timeout):
        """
        Set connection timeout ( float second )
        """
        assert isinstance(timeout, (float, int))
        # set timeout to 0 make connection non-blocking that is wrong
        # so timeout got clipped to reasonable minimum
        self._timeout = max(0.001, timeout)

    def _Connect(self):
        """
        INTERNAL METHOD, DO NOT CALL. Connects to searchd server.
        """
        if self._socket:
            # we have a socket, but is it still alive?
            sr, sw, _ = select.select([self._socket], [self._socket], [], 0)

            # this is how alive socket should look
            if len(sr) == 0 and len(sw) == 1:
                return self._socket

            # oops, looks like it was closed, lets reopen
            self._socket.close()
            self._socket = None

        if self._path:
            af = socket.AF_UNIX
            addr = self._path
            desc = self._path
        else:
            af = socket.AF_INET
            addr = (self._host, self._port)
            desc = f'{addr[0]};{addr[1]}'
        try:
            sock = socket.socket(af, socket.SOCK_STREAM)
            sock.settimeout(self._timeout)
            sock.connect(addr)
        except socket.error as msg:
            if sock:
                sock.close()
            self._error = f'connection to {desc} failed ({msg})'
            return None

        v = unpack('>L', sock.recv(4))[0]
        if v < 1:
            sock.close()
            self._error = f'expected searchd protocol version, got {v}'
            return None

        # all ok, send my version
        sock.send(pack('>L', 1))
        return sock

    def _GetResponse(self, sock, client_ver):
        """
        INTERNAL METHOD, DO NOT CALL. Gets and checks response packet from searchd server.
        """
        (status, ver, length) = unpack('>2HL', sock.recv(8))
        response = b''
        left = length
        while left > 0:
            chunk = sock.recv(left)
            if chunk:
                response += chunk
                left -= len(chunk)
            else:
                break

        if not self._socket:
            sock.close()

        # check response
        read = len(response)
        if not response or read != length:
            if length:
                self._error = f'failed to read searchd response (status={status}, ver={ver},' \
                        f' len={length}, read={read})'
            else:
                self._error = 'received zero-sized searchd response'
            return None

        # check status
        if status == SEARCHD_WARNING:
            wend = 4 + unpack('>L', response[0:4])[0]
            self._warning = response[4:wend].decode()
            return response[wend:]

        if status == SEARCHD_ERROR:
            self._error = 'searchd error: ' + response[4:].decode()
            return None

        if status == SEARCHD_RETRY:
            self._error = 'temporary searchd error: ' + response[4:].decode()
            return None

        if status != SEARCHD_OK:
            self._error = f'unknown status code {status}'
            return None

        # check version
        if ver < client_ver:
            self._warning = f'searchd command v.{ver >> 8}.{ver & 0xff} older than client\'' \
                    f's v.{client_ver >> 8}.{client_ver & 0xff}, some options might not work'
        return response

    @staticmethod
    def _Send(sock, req):
        """
        INTERNAL METHOD, DO NOT CALL. send request to searchd server.
        """
        total = 0
        while True:
            sent = sock.send(req[total:])
            if sent <= 0:
                break

            total = total + sent

        return total

    def SetLimits(self, offset, limit, maxmatches=0, cutoff=0):
        """
        Set offset and count into result set, and optionally set max-matches and cutoff limits.
        """
        assert type(offset) in [int] and 0 <= offset < 16777216
        assert type(limit) in [int] and 0 < limit < 16777216
        assert maxmatches >= 0
        self._offset = offset
        self._limit = limit
        if maxmatches > 0:
            self._maxmatches = maxmatches
        if cutoff >= 0:
            self._cutoff = cutoff

    def SetMaxQueryTime(self, maxquerytime):
        """
        Set maximum query time, in milliseconds, per-index. 0 means 'do not limit'.
        """
        assert isinstance(maxquerytime, int) and maxquerytime > 0
        self._maxquerytime = maxquerytime

    def SetMatchMode(self, mode):
        """
        Set matching mode.
        """
        logger.info(
            'DEPRECATED: Do not call SetMatchMode() or, even better, use SphinxQL instead of an API'
        )
        assert mode in [
            SPH_MATCH_ALL,
            SPH_MATCH_ANY,
            SPH_MATCH_PHRASE,
            SPH_MATCH_BOOLEAN,
            SPH_MATCH_EXTENDED,
            SPH_MATCH_FULLSCAN,
            SPH_MATCH_EXTENDED2
        ]
        self._mode = mode

    def SetRankingMode(self, ranker, rankexpr=''):
        """
        Set ranking mode.
        """
        assert 0 <= ranker < SPH_RANK_TOTAL
        assert isinstance(rankexpr, str)
        self._ranker = ranker
        self._rankexpr = rankexpr.encode()

    def SetSortMode(self, mode, clause=''):
        """
        Set sorting mode.
        """
        assert mode in [
            SPH_SORT_RELEVANCE,
            SPH_SORT_ATTR_DESC,
            SPH_SORT_ATTR_ASC,
            SPH_SORT_TIME_SEGMENTS,
            SPH_SORT_EXTENDED,
            SPH_SORT_EXPR
        ]
        assert isinstance(clause, str)
        self._sort = mode
        self._sortby = clause.encode()

    def SetFieldWeights(self, weights):
        """
        Bind per-field weights by name; expects (name,field_weight) dictionary as argument.
        """
        assert isinstance(weights, dict)
        assert all(map(lambda key: isinstance(key, str), weights.keys()))
        assert all(map(AssertInt32, weights.values()))
        self._fieldweights = {key.encode(): value for key, value in weights.items()}

    def SetIndexWeights(self, weights):
        """
        Bind per-index weights by name; expects (name,index_weight) dictionary as argument.
        """
        assert isinstance(weights, dict)
        assert all(map(lambda key: isinstance(key, str), weights.keys()))
        assert all(map(AssertInt32, weights.values()))
        self._indexweights = {key.encode(): value for key, value in weights.items()}

    def SetIDRange(self, minid, maxid):
        """
        Set IDs range to match.
        Only match records if document ID is beetwen $min and $max (inclusive).
        """
        assert isinstance(minid, int)
        assert isinstance(maxid, int)
        assert minid <= maxid
        self._min_id = minid
        self._max_id = maxid

    def SetFilter(self, attribute, values, exclude=0):
        """
        Set values set filter.
        Only match records where 'attribute' value is in given 'values' set.
        """
        assert isinstance(attribute, str)
        assert iter(values)
        assert all(map(AssertInt32, values))

        self._filters.append({
            'type': SPH_FILTER_VALUES,
            'attr': attribute.encode(),
            'exclude': exclude,
            'values': values
        })

    def SetFilterString(self, attribute, value, exclude=0):
        """
        Set string filter.
        Only match records where 'attribute' value is equal
        """
        assert isinstance(attribute, str)
        assert isinstance(value, str)
        assert isinstance(exclude, int)

        self._filters.append({
            'type': SPH_FILTER_STRING,
            'attr': attribute.encode(),
            'exclude': exclude,
            'value': value.encode()
        })

    def SetFilterRange(self, attribute, min_, max_, exclude=0):
        """
        Set range filter.
        Only match records if 'attribute' value is beetwen 'min_' and 'max_' (inclusive).
        """
        assert isinstance(attribute, str)
        AssertInt64(min_)
        AssertInt64(max_)
        assert min_ <= max_
        assert isinstance(exclude, int)

        self._filters.append({
            'type': SPH_FILTER_RANGE,
            'attr': attribute.encode(),
            'exclude': exclude,
            'min': min_,
            'max': max_
        })

    def SetFilterFloatRange(self, attribute, min_, max_, exclude=0):
        assert isinstance(attribute, str)
        assert isinstance(min_, float)
        assert isinstance(max_, float)
        assert min_ <= max_
        assert isinstance(exclude, int)
        self._filters.append({
            'type': SPH_FILTER_FLOATRANGE,
            'attr': attribute.encode(),
            'exclude': exclude,
            'min': min_,
            'max': max_
        })

    def SetGeoAnchor(self, attrlat, attrlong, latitude, longitude):
        assert isinstance(attrlat, str)
        assert isinstance(attrlong, str)
        assert isinstance(latitude, float)
        assert isinstance(longitude, float)
        self._anchor['attrlat'] = attrlat.encode()
        self._anchor['attrlong'] = attrlong.encode()
        self._anchor['lat'] = latitude
        self._anchor['long'] = longitude

    def SetGroupBy(self, attribute, func, groupsort='@group desc'):
        """
        Set grouping attribute and function.
        """
        assert isinstance(attribute, str)
        assert isinstance(groupsort, str)
        assert func in [
            SPH_GROUPBY_DAY,
            SPH_GROUPBY_WEEK,
            SPH_GROUPBY_MONTH,
            SPH_GROUPBY_YEAR,
            SPH_GROUPBY_ATTR,
            SPH_GROUPBY_ATTRPAIR
        ]

        self._groupby = attribute.encode()
        self._groupfunc = func
        self._groupsort = groupsort.encode()

    def SetGroupDistinct(self, attribute):
        assert isinstance(attribute, str)
        self._groupdistinct = attribute.encode()

    def SetRetries(self, count, delay=0):
        assert isinstance(count, int) and count >= 0
        assert isinstance(delay, int) and delay >= 0
        self._retrycount = count
        self._retrydelay = delay

    def SetOverride(self, name, _type, values):
        logger.info('DEPRECATED: Do not call SetOverride(). Use SphinxQL REMAP() function instead.')
        assert isinstance(name, str)
        assert _type in SPH_ATTR_TYPES
        assert isinstance(values, dict)
        assert all(map(AssertUInt64, values.keys()))

        if _type == SPH_ATTR_STRING:
            assert all(map(lambda value: isinstance(value, str), values.values()))
            values = {key: value.encode() for key, value in values.items()}

        self._overrides[name] = {'name': name.encode(), 'type': _type, 'values': values}

    def SetSelect(self, _select):
        assert isinstance(_select, str)
        self._select = _select.encode()

    def SetQueryFlag(self, name, value):
        known_names = [
            "reverse_scan",
            "sort_method",
            "max_predicted_time",
            "boolean_simplify",
            "idf",
            "global_idf"
        ]
        flags = {
            "reverse_scan": [0, 1],
            "sort_method": ["pq", "kbuffer"],
            "max_predicted_time": [0],
            "boolean_simplify": [True, False],
            "idf": ["normalized", "plain", "tfidf_normalized", "tfidf_unnormalized"],
            "global_idf": [True, False]
        }
        assert name in known_names
        assert (
            value in flags[name] or
            (name == "max_predicted_time" and isinstance(value, int) and value >= 0)
        )

        if name == "reverse_scan":
            self._query_flags = SetBit(self._query_flags, 0, value == 1)
        if name == "sort_method":
            self._query_flags = SetBit(self._query_flags, 1, value == "kbuffer")
        if name == "max_predicted_time":
            self._query_flags = SetBit(self._query_flags, 2, value > 0)
            self._predictedtime = int(value)
        if name == "boolean_simplify":
            self._query_flags = SetBit(self._query_flags, 3, value)
        if name == "idf" and value in ("plain", "normalized"):
            self._query_flags = SetBit(self._query_flags, 4, value == "plain")
        if name == "global_idf":
            self._query_flags = SetBit(self._query_flags, 5, value)
        if name == "idf" and value in ("tfidf_normalized", "tfidf_unnormalized"):
            self._query_flags = SetBit(self._query_flags, 6, value == "tfidf_normalized")

    def SetOuterSelect(self, orderby, offset, limit):
        assert isinstance(orderby, str)
        assert isinstance(offset, int)
        assert isinstance(limit, int)
        assert offset >= 0
        assert limit > 0

        self._outerorderby = orderby.encode()
        self._outeroffset = offset
        self._outerlimit = limit
        self._hasouter = True

    def ResetOverrides(self):
        self._overrides = {}

    # jeg: added function
    def ResetFiltersOnly(self):
        """
        Clear filers only, not anchor as well
        """
        self._filters = []

    def ResetFilters(self):
        """
        Clear all filters (for multi-queries).
        """
        self._filters = []
        self._anchor = {}

    def ResetGroupBy(self):
        """
        Clear groupby settings (for multi-queries).
        """
        self._groupby = b''
        self._groupfunc = SPH_GROUPBY_DAY
        self._groupsort = b'@group desc'
        self._groupdistinct = b''

    def ResetQueryFlag(self):
        self._query_flags = SetBit(0, 6, True)  # default idf=tfidf_normalized
        self._predictedtime = 0

    def ResetOuterSelect(self):
        self._outerorderby = b''
        self._outeroffset = 0
        self._outerlimit = 0
        self._hasouter = False

    def Query(self, query, index='*', comment=''):
        """
        Connect to searchd server and run given search query.
        Returns None on failure; result set hash on success (see documentation for details).
        """
        assert len(self._reqs) == 0
        self.AddQuery(query, index, comment)
        results = self.RunQueries()
        self._reqs = []  # we won't re-run erroneous batch

        if not results or len(results) == 0:
            # len(results) == 0 is a failure we should have a least one entry in results,
            # this entry might contain an empty result though.
            return None
        self._error = results[0]['error']
        self._warning = results[0]['warning']
        if results[0]['status'] == SEARCHD_ERROR:
            return None
        return results[0]

    def AddQuery(self, query, index='*', comment=''):
        """
        Add query to batch.
        """
        logger.debug("Add Query; query='%s', index='%s', comment='%s'", query, index, comment)
        logger.debug(
            '_query_flags=%s, _ranker=%s, _weights=%s, _rankexpr=%s, _filters=%s, _fieldweights=%s',
            self._query_flags,
            self._ranker,
            self._weights,
            self._rankexpr,
            self._filters,
            self._fieldweights
        )

        # build request
        req = []
        req.append(
            pack('>5L', self._query_flags, self._offset, self._limit, self._mode, self._ranker)
        )
        if self._ranker == SPH_RANK_EXPR:
            req.append(pack('>L', len(self._rankexpr)))
            req.append(self._rankexpr)
        req.append(pack('>L', self._sort))
        req.append(pack('>L', len(self._sortby)))
        req.append(self._sortby)

        assert isinstance(query, str)
        query_encoded = query.encode()
        req.append(pack('>L', len(query_encoded)))
        req.append(query_encoded)

        req.append(pack('>L', len(self._weights)))
        for w in self._weights:
            req.append(pack('>L', w))
        assert isinstance(index, str)
        index_encoded = index.encode()
        req.append(pack('>L', len(index_encoded)))
        req.append(index_encoded)
        req.append(pack('>L', 1))  # id64 range marker
        req.append(pack('>Q', self._min_id))
        req.append(pack('>Q', self._max_id))

        # filters
        req.append(pack('>L', len(self._filters)))
        for f in self._filters:
            req.append(pack('>L', len(f['attr'])) + f['attr'])
            filtertype = f['type']
            req.append(pack('>L', filtertype))
            if filtertype == SPH_FILTER_VALUES:
                req.append(pack('>L', len(f['values'])))
                for val in f['values']:
                    req.append(pack('>q', val))
            elif filtertype == SPH_FILTER_RANGE:
                req.append(pack('>2q', f['min'], f['max']))
            elif filtertype == SPH_FILTER_FLOATRANGE:
                req.append(pack('>2f', f['min'], f['max']))
            elif filtertype == SPH_FILTER_STRING:
                req.append(pack('>L', len(f['value'])))
                req.append(f['value'])
            req.append(pack('>L', f['exclude']))

        # group-by, max-matches, group-sort
        req.append(pack('>2L', self._groupfunc, len(self._groupby)))
        req.append(self._groupby)
        req.append(pack('>2L', self._maxmatches, len(self._groupsort)))
        req.append(self._groupsort)
        req.append(pack('>LLL', self._cutoff, self._retrycount, self._retrydelay))
        req.append(pack('>L', len(self._groupdistinct)))
        req.append(self._groupdistinct)

        # anchor point
        if len(self._anchor) == 0:
            req.append(pack('>L', 0))
        else:
            attrlat, attrlong = self._anchor['attrlat'], self._anchor['attrlong']
            latitude, longitude = self._anchor['lat'], self._anchor['long']
            req.append(pack('>L', 1))
            req.append(pack('>L', len(attrlat)) + attrlat)
            req.append(pack('>L', len(attrlong)) + attrlong)
            req.append(pack('>f', latitude) + pack('>f', longitude))

        # per-index weights
        req.append(pack('>L', len(self._indexweights)))
        for indx, weight in self._indexweights.items():
            req.append(pack('>L', len(indx)) + indx + pack('>L', weight))

        # max query time
        req.append(pack('>L', self._maxquerytime))

        # per-field weights
        req.append(pack('>L', len(self._fieldweights)))
        for field, weight in self._fieldweights.items():
            req.append(pack('>L', len(field)) + field + pack('>L', weight))

        # comment
        comment_encoded = str(comment).encode()
        req.append(pack('>L', len(comment_encoded)) + comment_encoded)

        # attribute overrides
        req.append(pack('>L', len(self._overrides)))
        for v in self._overrides.values():
            req.extend((pack('>L', len(v['name'])), v['name']))
            req.append(pack('>LL', v['type'], len(v['values'])))
            for idU64, value in v['values'].items():
                req.append(pack('>Q', idU64))
                if v['type'] == SPH_ATTR_FLOAT:
                    req.append(pack('>f', value))
                elif v['type'] == SPH_ATTR_BIGINT:
                    req.append(pack('>q', value))
                elif v['type'] == SPH_ATTR_STRING:
                    req.append(value)
                else:
                    req.append(pack('>l', value))

        # select-list
        req.append(pack('>L', len(self._select)))
        req.append(self._select)
        if self._predictedtime > 0:
            req.append(pack('>L', self._predictedtime))

        # outer
        req.append(pack('>L', len(self._outerorderby)) + self._outerorderby)
        req.append(pack('>2L', self._outeroffset, self._outerlimit))
        if self._hasouter:
            req.append(pack('>L', 1))
        else:
            req.append(pack('>L', 0))

        # send query, get response
        req = b''.join(req)

        self._reqs.append(req)

    def RunQueries(self):
        """
        Run queries batch.
        Returns None on network IO failure; or an array of result set hashes on success.
        """
        if len(self._reqs) == 0:
            self._error = 'no queries defined, issue AddQuery() first'
            logger.error('Run queries: %s', self._error)
            return None

        sock = self._Connect()
        if not sock:
            logger.error('Run queries, connect failed: %s', self._error)
            return None

        logger.debug('Run %d queries', len(self._reqs))

        req = b''.join(self._reqs)
        length = len(req) + 8
        req = pack(
            '>HHLLL', SEARCHD_COMMAND_SEARCH, VER_COMMAND_SEARCH, length, 0, len(self._reqs)
        ) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_SEARCH)
        if not response:
            logger.error('Run queries, no response: %s', self._error)
            return None

        nreqs = len(self._reqs)

        # parse response
        max_ = len(response)
        p = 0

        results = []
        for _ in range(0, nreqs, 1):
            result = {}
            results.append(result)

            result['error'] = ''
            result['warning'] = ''
            status = unpack('>L', response[p:p + 4])[0]
            p += 4
            result['status'] = status
            if status != SEARCHD_OK:
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                message = response[p:p + length].decode()
                p += length

                if status == SEARCHD_WARNING:
                    result['warning'] = message
                else:
                    result['error'] = message
                    continue

            # read schema
            fields = []
            attrs = []

            nfields = unpack('>L', response[p:p + 4])[0]
            p += 4
            while nfields > 0 and p < max_:
                nfields -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                fields.append(response[p:p + length].decode())
                p += length

            result['fields'] = fields

            nattrs = unpack('>L', response[p:p + 4])[0]
            p += 4
            while nattrs > 0 and p < max_:
                nattrs -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                attr = response[p:p + length].decode()
                p += length
                type_ = unpack('>L', response[p:p + 4])[0]
                p += 4
                attrs.append([attr, type_])

            result['attrs'] = attrs

            # read match count
            count = unpack('>L', response[p:p + 4])[0]
            p += 4
            id64 = unpack('>L', response[p:p + 4])[0]
            p += 4

            # read matches
            result['matches'] = []
            while count > 0 and p < max_:
                count -= 1
                if id64:
                    doc, weight = unpack('>QL', response[p:p + 12])
                    p += 12
                else:
                    doc, weight = unpack('>2L', response[p:p + 8])
                    p += 8

                match = {'id': doc, 'weight': weight, 'attrs': {}}
                for attr in attrs:
                    if attr[1] == SPH_ATTR_FLOAT:
                        match['attrs'][attr[0]] = unpack('>f', response[p:p + 4])[0]
                    elif attr[1] == SPH_ATTR_BIGINT:
                        match['attrs'][attr[0]] = unpack('>q', response[p:p + 8])[0]
                        p += 4
                    elif attr[1] == SPH_ATTR_STRING:
                        slen = unpack('>L', response[p:p + 4])[0]
                        p += 4
                        match['attrs'][attr[0]] = ''
                        if slen > 0:
                            match['attrs'][attr[0]] = response[p:p + slen].decode()
                        p += slen - 4
                    elif attr[1] == SPH_ATTR_FACTORS:
                        slen = unpack('>L', response[p:p + 4])[0]
                        p += 4
                        match['attrs'][attr[0]] = ''
                        if slen > 0:
                            match['attrs'][attr[0]] = response[p:p + slen - 4].decode()
                            p += slen - 4
                        p -= 4
                    elif attr[1] == SPH_ATTR_MULTI:
                        match['attrs'][attr[0]] = []
                        nvals = unpack('>L', response[p:p + 4])[0]
                        p += 4
                        for _ in range(0, nvals, 1):
                            match['attrs'][attr[0]].append(unpack('>L', response[p:p + 4])[0])
                            p += 4
                        p -= 4
                    elif attr[1] == SPH_ATTR_MULTI64:
                        match['attrs'][attr[0]] = []
                        nvals = unpack('>L', response[p:p + 4])[0]
                        nvals = nvals / 2
                        p += 4
                        for _ in range(0, nvals, 1):
                            match['attrs'][attr[0]].append(unpack('>q', response[p:p + 8])[0])
                            p += 8
                        p -= 4
                    else:
                        match['attrs'][attr[0]] = unpack('>L', response[p:p + 4])[0]
                    p += 4

                result['matches'].append(match)

            result['total'], result['total_found'], result['time'], words = unpack(
                '>4L', response[p:p+16]
            )

            result['time'] = f'{result["time"] / 1000.0:.3f}'
            p += 16

            result['words'] = []
            while words > 0:
                words -= 1
                length = unpack('>L', response[p:p + 4])[0]
                p += 4
                word = response[p:p + length].decode()
                p += length
                docs, hits = unpack('>2L', response[p:p + 8])
                p += 8

                result['words'].append({'word': word, 'docs': docs, 'hits': hits})

        logger.debug('Run %d queries result', nreqs, extra={'query_results': results})

        self._reqs = []
        return results

    def BuildExcerpts(self, docs, index, words, opts=None):
        """
        Connect to searchd server and generate exceprts from given documents.
        """
        if not opts:
            opts = {}

        assert isinstance(docs, list)
        assert isinstance(opts, dict)

        sock = self._Connect()

        if not sock:
            return None

        # fixup options
        opts.setdefault('before_match', '<b>')
        opts.setdefault('after_match', '</b>')
        opts.setdefault('chunk_separator', ' ... ')
        opts.setdefault('html_strip_mode', 'index')
        opts.setdefault('limit', 256)
        opts.setdefault('limit_passages', 0)
        opts.setdefault('limit_words', 0)
        opts.setdefault('around', 5)
        opts.setdefault('start_passage_id', 1)
        opts.setdefault('passage_boundary', 'none')

        # build request
        # v.1.0 req

        flags = 1  # (remove spaces)
        if opts.get('exact_phrase'):
            flags |= 2
        if opts.get('single_passage'):
            flags |= 4
        if opts.get('use_boundaries'):
            flags |= 8
        if opts.get('weight_order'):
            flags |= 16
        if opts.get('query_mode'):
            flags |= 32
        if opts.get('force_all_words'):
            flags |= 64
        if opts.get('load_files'):
            flags |= 128
        if opts.get('allow_empty'):
            flags |= 256
        if opts.get('emit_zones'):
            flags |= 512
        if opts.get('load_files_scattered'):
            flags |= 1024

        # mode=0, flags
        req = [pack('>2L', 0, flags)]

        # req index
        assert isinstance(index, str)
        index_encoded = index.encode()
        req.append(pack('>L', len(index_encoded)))
        req.append(index_encoded)

        # req words
        assert isinstance(words, str)
        words_encoded = words.encode()
        req.append(pack('>L', len(words_encoded)))
        req.append(words_encoded)

        # options
        before_match_encoded = opts['before_match'].encode()
        req.append(pack('>L', len(before_match_encoded)))
        req.append(before_match_encoded)

        after_match_encoded = opts['after_match'].encode()
        req.append(pack('>L', len(after_match_encoded)))
        req.append(after_match_encoded)

        chunk_separator_encoded = opts['chunk_separator'].encode()
        req.append(pack('>L', len(chunk_separator_encoded)))
        req.append(chunk_separator_encoded)

        req.append(pack('>L', int(opts['limit'])))
        req.append(pack('>L', int(opts['around'])))
        req.append(pack('>L', int(opts['limit_passages'])))
        req.append(pack('>L', int(opts['limit_words'])))
        req.append(pack('>L', int(opts['start_passage_id'])))

        html_strip_mode_encoded = opts['html_strip_mode'].encode()
        req.append(pack('>L', len(html_strip_mode_encoded)))
        req.append(html_strip_mode_encoded)

        passage_boundary_encoded = opts['passage_boundary'].encode()
        req.append(pack('>L', len(passage_boundary_encoded)))
        req.append(passage_boundary_encoded)

        # documents
        req.append(pack('>L', len(docs)))
        for doc in docs:
            assert isinstance(doc, str)
            doc_encoded = doc.encode()
            req.append(pack('>L', len(doc_encoded)))
            req.append(doc_encoded)

        req = b''.join(req)

        # send query, get response
        length = len(req)

        # add header
        req = pack('>2HL', SEARCHD_COMMAND_EXCERPT, VER_COMMAND_EXCERPT, length) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_EXCERPT)
        if not response:
            return []

        # parse response
        pos = 0
        res = []
        rlen = len(response)

        for _ in range(len(docs)):
            length = unpack('>L', response[pos:pos + 4])[0]
            pos += 4

            if pos + length > rlen:
                self._error = 'incomplete reply'
                return []

            res.append(response[pos:pos + length].decode())
            pos += length

        return res

    def UpdateAttributes(self, index, attrs, values, mva=False, ignorenonexistent=False):
        """
        Update given attribute values on given documents in given indexes.
        Returns amount of updated documents (0 or more) on success, or -1 on failure.

        'attrs' must be a list of strings.
        'values' must be a dict with int key (document ID) and list of int values (new attribute
        values).
        optional boolean parameter 'mva' points that there is update of MVA attributes.
        In this case the 'values' must be a dict with int key (document ID) and list of lists of
        int values (new MVA attribute values).
        Optional boolean parameter 'ignorenonexistent' points that the update will silently ignore
        any warnings about trying to update a column which is not exists in current index schema.

        Example:
            res = cl.UpdateAttributes(
                'test1',
                ['group_id', 'date_added'],
                {2: [123,1000000000], 4: [456,1234567890]}
            )
        """
        assert isinstance(index, str)
        assert isinstance(attrs, list)
        assert isinstance(values, dict)
        assert all(map(lambda attr: isinstance(attr, str), attrs))
        assert all(map(AssertUInt32, values.keys()))

        def assertEntry(entry):
            assert isinstance(entry, list)
            assert len(attrs) == len(entry)
            if mva:
                assert all(
                    map(lambda val: isinstance(val, list) and all(map(AssertInt32, val)), entry)
                )
            else:
                assert all(map(AssertInt32, entry))
            return True

        assert all(map(assertEntry, values.values()))

        # build request
        index_encoded = index.encode()
        req = [pack('>L', len(index_encoded)), index_encoded]

        req.append(pack('>L', len(attrs)))
        ignore_absent = 0
        if ignorenonexistent:
            ignore_absent = 1
        req.append(pack('>L', ignore_absent))
        mva_attr = 0
        if mva:
            mva_attr = 1
        for attr in attrs:
            attr_encoded = attr.encode()
            req.append(pack('>L', len(attr_encoded)) + attr_encoded)
            req.append(pack('>L', mva_attr))

        req.append(pack('>L', len(values)))
        for docid, entry in values.items():
            req.append(pack('>Q', docid))
            for val in entry:
                val_len = val
                if mva:
                    val_len = len(val)
                req.append(pack('>L', val_len))
                if mva:
                    for vals in val:
                        req.append(pack('>L', vals))

        # connect, send query, get response
        sock = self._Connect()
        if not sock:
            return None

        req = b''.join(req)
        length = len(req)
        req = pack('>2HL', SEARCHD_COMMAND_UPDATE, VER_COMMAND_UPDATE, length) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_UPDATE)
        if not response:
            return None

        # parse response
        updated = unpack('>L', response[0:4])[0]
        return updated

    def BuildKeywords(self, query, index, hits):
        """
        Connect to searchd server, and generate keywords list for a given query.
        Returns None on failure, or a list of keywords on success.
        """
        assert isinstance(query, str)
        assert isinstance(index, str)
        assert isinstance(hits, int)

        # build request
        query_encoded = query.encode()
        req = [pack('>L', len(query_encoded)) + query_encoded]
        index_encoded = index.encode()
        req.append(pack('>L', len(index_encoded)) + index_encoded)
        req.append(pack('>L', hits))

        # connect, send query, get response
        sock = self._Connect()
        if not sock:
            return None

        req = b''.join(req)
        length = len(req)
        req = pack('>2HL', SEARCHD_COMMAND_KEYWORDS, VER_COMMAND_KEYWORDS, length) + req
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_KEYWORDS)
        if not response:
            return None

        # parse response
        res = []

        nwords = unpack('>L', response[0:4])[0]
        p = 4
        max_ = len(response)

        while nwords > 0 and p < max_:
            nwords -= 1

            length = unpack('>L', response[p:p + 4])[0]
            p += 4
            tokenized = response[p:p + length].decode()
            p += length

            length = unpack('>L', response[p:p + 4])[0]
            p += 4
            normalized = response[p:p + length].decode()
            p += length

            entry = {'tokenized': tokenized, 'normalized': normalized}
            if hits:
                entry['docs'], entry['hits'] = unpack('>2L', response[p:p + 8])
                p += 8

            res.append(entry)

        if nwords > 0 or p > max_:
            self._error = 'incomplete reply'
            return None

        return res

    def Status(self, session=False):
        """
        Get the status
        """

        # connect, send query, get response
        sock = self._Connect()
        if not sock:
            return None

        sess = 1
        if session:
            sess = 0

        req = pack('>2HLL', SEARCHD_COMMAND_STATUS, VER_COMMAND_STATUS, 4, sess)
        self._Send(sock, req)

        response = self._GetResponse(sock, VER_COMMAND_STATUS)
        if not response:
            return None

        # parse response
        res = []

        p = 8
        max_ = len(response)

        while p < max_:
            length = unpack('>L', response[p:p + 4])[0]
            key = response[p + 4:p + length + 4].decode()
            p += 4 + length
            length = unpack('>L', response[p:p + 4])[0]
            value = response[p + 4:p + length + 4].decode()
            p += 4 + length
            res += [[key, value]]

        return res

    ### persistent connections

    def Open(self):
        if self._socket:
            self._error = 'already connected'
            return None

        server = self._Connect()
        if not server:
            return None

        # command, command version = 0, body length = 4, body = 1
        request = pack('>hhII', SEARCHD_COMMAND_PERSIST, 0, 4, 1)
        self._Send(server, request)

        self._socket = server
        return True

    def Close(self):
        if not self._socket:
            self._error = 'not connected'
            return
        self._socket.close()
        self._socket = None

    @staticmethod
    def EscapeString(string):
        return re.sub(r"([=\(\)|\!@~\"&/\\\^\$\=\<\*])", r"\\\1", string)

    def FlushAttributes(self):
        sock = self._Connect()
        if not sock:
            return -1

        request = pack(
            '>hhI', SEARCHD_COMMAND_FLUSHATTRS, VER_COMMAND_FLUSHATTRS, 0
        )  # cmd, ver, bodylen
        self._Send(sock, request)

        response = self._GetResponse(sock, VER_COMMAND_FLUSHATTRS)
        if not response or len(response) != 4:
            self._error = 'unexpected response length'
            return -1

        tag = unpack('>L', response[0:4])[0]
        return tag


def AssertInt32(value):
    assert isinstance(value, int)
    assert -2**31 <= value <= 2**31 - 1
    return True


def AssertUInt32(value):
    assert isinstance(value, int)
    assert 0 <= value <= 2**32 - 1
    return True


def AssertInt64(value):
    assert isinstance(value, int)
    assert -2**63 <= value <= 2**63 - 1
    return True


def AssertUInt64(value):
    assert isinstance(value, int)
    assert 0 <= value <= 2**64 - 1
    return True


def SetBit(flag, bit, on):
    if on:
        flag += (1 << bit)
    else:
        reset = 255 ^ (1 << bit)
        flag = flag & reset

    return flag


#
# $Id$
#
