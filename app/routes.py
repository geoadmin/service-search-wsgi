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
def search_server(topic='all'):
    request.matchdict = {}
    request.matchdict['topic'] = topic
    search = Search(request)
    if request.args.get('geometryFormat') == 'geojson':
        response = make_response(search.view_find_geojson())
        response.headers["Content-Type"] = "application/geo+json"
    elif request.args.get('geometryFormat') == 'esrijson':
        response = make_response(search.view_find_esrijson())
    else:
        response = make_response(search.search())

    # TODO: better - callback f.ex with a renderer
    if request.args.get('callback'):
        callback = request.args.get('callback')
        data = response.json
        response.headers["Content-Type"] = "application/javascript"
        response.data = f"/**/{callback}({data}));"

    return response
