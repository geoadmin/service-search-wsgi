import os
import socket
import sys

from app.helpers import sphinxapi

# pylint: disable=invalid-name

sys.tracebacklimit = 0

searchText = '@(title,detail,layer) "wand" | @(title,detail,layer) "^wand" | @(title,detail,layer) "wand$" | @(title,detail,layer) "^wand$" | @(title,detail,layer) "wand"~5 | @(title,detail,layer) "wand*" | @(title,detail,layer) "^wand*" | @(title,detail,layer) "wand*"~5 | @(title,detail,layer) "*wand*" | @(title,detail,layer) "^*wand*" | @(title,detail,layer) "*wand*"~5 & @topics (inspire | ech) & @staging prod | @staging integration | @staging test'  # pylint: disable=line-too-long
topicFilter = '(inspire | ech)'
mapName = 'inspire'
index_name = 'layers_fr'
temp = []

sphinxhost = os.environ.get('SPHINXHOST', 'localhost')

sphinx = sphinxapi.SphinxClient()
sphinx.SetServer(sphinxhost, 9312)
sphinx.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)

sphinx.SetConnectTimeout(10.0)

resp = sphinx._Connect()  # pylint: disable=protected-access

if isinstance(resp, socket.socket):
    print(f"Connected to Sphinx server <{sphinxhost}>")
else:
    print(f"Cannot connect to Sphinx server <{sphinxhost}>. Exit")

temp = sphinx.Query(searchText, index=index_name)
temp = temp['matches'] if temp is not None else temp

if temp is not None and len(temp) > 0:
    print("Querying Sphinx server successful")
    for l in temp:
        print(l['attrs']['label'])
else:
    print("Not the expected result while querying Sphinx Server")
