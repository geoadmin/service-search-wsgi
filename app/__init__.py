import gzip
import logging
import time

from flask_caching import Cache
from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import g
from flask import request

from app import settings
from app.helpers.utils import make_error_msg

logger = logging.getLogger(__name__)
route_logger = logging.getLogger('app.routes')

# Standard Flask application initialisation

app = Flask(__name__)
app.config.from_object(settings)

cache = Cache(app)


# NOTE it is better to have this method registered first (before validate_origin) otherwise
# the route might not be logged if another method reject the request.
@app.before_request
def log_route():
    g.setdefault('request_started', time.time())
    route_logger.debug('%s %s', request.method, request.path)


# Add CORS Headers to all request
@app.after_request
def add_cors_header(response):
    # Do not add CORS header to internal /checker endpoint.
    if request.endpoint == 'checker':
        return response

    response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


# Add Cache-Control Headers to all request except for checker
@app.after_request
def add_cache_control_header(response):
    # Do not add Cache-Control header to internal /checker endpoint.
    if request.endpoint == 'checker':
        return response

    response.headers['Cache-Control'] = settings.CACHE_CONTROL_HEADER
    return response


@app.after_request
def compress(response):
    accept_encoding = request.headers.get('accept-encoding', '').lower()

    if (
        response.status_code < 200 or response.status_code >= 300 or response.direct_passthrough or
        'gzip' not in accept_encoding or 'Content-Encoding' in response.headers
    ):
        return response

    content = gzip.compress(response.get_data(), compresslevel=settings.GZIP_COMPRESSION_LEVEL)
    response.set_data(content)
    response.headers['content-length'] = len(content)
    response.headers['content-encoding'] = 'gzip'
    return response


# NOTE it is better to have this method registered last (after add_cors_header) otherwise
# the response might not be correct (e.g. headers added in another after_request hook).
@app.after_request
def log_response(response):
    log_extra = {
        'response': {
            "status_code": response.status_code,
            "headers": dict(response.headers.items()),
        },
        "duration": time.time() - g.get('request_started', time.time())
    }
    if route_logger.isEnabledFor(logging.DEBUG):
        log_extra['response']['json'] = response.json if response.is_json else response.data
    route_logger.info("%s %s - %s", request.method, request.path, response.status, extra=log_extra)
    return response


# Register error handler to make sure that every error returns a json answer
@app.errorhandler(Exception)
def handle_exception(err):
    """Return JSON instead of HTML for HTTP errors."""
    if isinstance(err, HTTPException):
        if err.code >= 500:
            logger.exception(err)
        else:
            logger.error(err)
        return make_error_msg(err.code, err.description)

    logger.exception('Unexpected exception: %s', err)
    return make_error_msg(500, "Internal server error, please consult logs")


@app.teardown_appcontext
def close_db_connection(exception):
    if exception:
        logger.exception('Unexpected exception: %s', exception)
    # close db connection
    if hasattr(g, 'db_connection'):
        g.db_connection.close()


from app import routes  # isort:skip pylint: disable=wrong-import-position
