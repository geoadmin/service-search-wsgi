import logging

from flask import jsonify
from flask import make_response
from flask import request

from app import app
from app.lib import sphinxapi
from app.search import Search
from app.settings import SEARCH_SPHINX_HOST
from app.settings import SEARCH_SPHINX_PORT
from app.settings import SEARCH_SPHINX_TIMEOUT
from app.version import APP_VERSION

logger = logging.getLogger(__name__)


@app.route('/checker', methods=['GET'])
def checker():
    return make_response(jsonify({'success': True, 'message': 'OK', 'version': APP_VERSION}))


@app.route('/checker/ready', methods=['GET'])
def readiness():
    # set up sphinx client
    sphinx = sphinxapi.SphinxClient()
    sphinx.SetServer(SEARCH_SPHINX_HOST, SEARCH_SPHINX_PORT)
    sphinx.SetConnectTimeout(SEARCH_SPHINX_TIMEOUT)
    sphinx.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)

    # run query
    result = sphinx.Query('nofx', 'swisssearch')
    sphinx_status = {
        'data': result if result is not None else 'ERROR or WARNING',
        'error_msg': sphinx.GetLastError(),
        'warning_msg': sphinx.GetLastWarning()
    }

    if result:
        return make_response(jsonify({'success': True, 'message': 'OK'}))

    logger.critical(sphinx_status)
    return make_response(jsonify({'success': False, 'status': sphinx_status}), 503)


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
