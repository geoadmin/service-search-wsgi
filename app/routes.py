import logging
from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.search import Search
from app.version import APP_VERSION

logger = logging.getLogger(__name__)


@app.route('/checker', methods=['GET'])
def checker():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))


@app.route('/rest/services/<topic>/SearchServer', methods=['GET'])
def search_server(topic):
    request.matchdict = {}
    request.matchdict['topic'] = topic
    search = Search(request)
    if request.args.get('geometryFormat') == 'geojson':
        search_result = search.view_find_geojson()
    elif request.args.get('geometryFormat') == 'esrijson':
        search_result = search.view_find_esrijson()
    else:
        search_result = search.search()
    return make_response(search_result)
