import logging

from flask import abort
from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.search import Search
from app.settings import SPHINX_BACKEND_READY
from app.version import APP_VERSION

logger = logging.getLogger(__name__)


@app.route('/checker', methods=['GET'])
def checker():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))


@app.route('/checker/ready', methods=['GET'])
def readiness():
    sphinx_ok_string = 'READY\n'
    try:
        with open(SPHINX_BACKEND_READY, 'r', encoding='utf-8') as fd:
            content = fd.read()
    except IOError as err:
        logger.critical('failed to open file %s error: %s', SPHINX_BACKEND_READY, err)
        content = ""

    if content != sphinx_ok_string:
        abort(503, 'Incomprehensible answer. sphinx is probably not ready yet.')
    return make_response(jsonify({'success': True, 'message': 'OK'}))


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
        content_type_override = request.accept_mimetypes.best_match(
            ["text/javascript", "application/javascript"],
            default="text/javascript",
        )

    if content_type_override:
        response.headers['Content-Type'] = content_type_override

    return response
