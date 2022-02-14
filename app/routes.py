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
    search = Search(request, topic)
    content_type_override = None

    if request.args.get('geometryFormat') == 'geojson':
        results = search.view_find_geojson()
        content_type_override = "application/geo+json"
    elif request.args.get('geometryFormat') == 'esrijson':
        results = search.view_find_esrijson()
    else:
        results = search.search()

    response = make_response(jsonify(results))

    callback = request.args.get('callback', None)
    if callback is not None:
        response.set_data(f"/**/{callback}({response.get_data(as_text=True)});")
        content_type_override = "application/javascript"

    if content_type_override:
        response.headers['Content-Type'] = content_type_override

    return response
