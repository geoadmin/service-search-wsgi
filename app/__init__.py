import logging
import os
import re
import time

import psycopg2 as psy
from werkzeug.exceptions import HTTPException

from flask import Flask
from flask import abort
from flask import g
from flask import request

from app import settings
from app.helpers.utils import get_topics_from_db
from app.helpers.utils import make_error_msg

logger = logging.getLogger(__name__)
route_logger = logging.getLogger('app.routes')

# Standard Flask application initialisation

app = Flask(__name__)
app.config.from_object(settings)

# TODO: This will have to be discussed in a general manner.
# Right now the topics do not serve anything else than returning HTTP 400
# when the topic does not exist. No filtering is being done on it at all
# f.ex searching for lagefixpunkte in topic bafu, which is meaningless
# https://api3.geo.admin.ch/2111231107/rest/services/bafu/SearchServer?sr=2056&searchText=CH030000123112311020&lang=en&type=featuresearch&features=ch.swisstopo.fixpunkte-lfp1&timeEnabled=false&timeStamps=
try:
    topics = get_topics_from_db()
except psy.Error:
    topics = settings.FALLBACK_TOPICS
    logger.error("Connection to the db base could not be established." \
            " Using fallback %s", settings.FALLBACK_TOPICS)


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
    return response


# NOTE it is better to have this method registered last (after add_cors_header) otherwise
# the response might not be correct (e.g. headers added in another after_request hook).
@app.after_request
def log_response(response):
    route_logger.info(
        "%s %s - %s",
        request.method,
        request.path,
        response.status,
        extra={
            'response': {
                "status_code": response.status_code, "headers": dict(response.headers.items())
            },
            "duration": time.time() - g.get('request_started', time.time())
        }
    )
    return response


# Register error handler to make sure that every error returns a json answer
@app.errorhandler(Exception)
def handle_exception(err):
    """Return JSON instead of HTML for HTTP errors."""
    if isinstance(err, HTTPException):
        logger.error(err)
        return make_error_msg(err.code, err.description)

    logger.exception('Unexpected exception: %s', err)
    return make_error_msg(500, "Internal server error, please consult logs")


from app import routes  # isort:skip pylint: disable=wrong-import-position
