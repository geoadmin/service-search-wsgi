import logging
import logging.config
from os import path

import psycopg2 as psy
import yaml

from flask import jsonify
from flask import make_response

from app import settings
from app.settings import ALLOWED_DOMAINS
from app.settings import LOGGING_CFG
from app.settings import LOGS_DIR
from app.settings import TESTING

logger = logging.getLogger(__name__)

ALLOWED_DOMAINS_PATTERN = f"({'|'.join(ALLOWED_DOMAINS)})"

topics = []


def make_error_msg(code, msg):
    return make_response(jsonify({'success': False, 'error': {'code': code, 'message': msg}}), code)


def get_logging_cfg():
    print(f"LOGS_DIR is {LOGS_DIR}")
    print(f"LOGGING_CFG is {LOGGING_CFG}")

    config = {}
    with open(LOGGING_CFG, 'rt', encoding='utf-8') as fd:
        config = yaml.safe_load(path.expandvars(fd.read()))

    logger.debug('Load logging configuration from file %s', LOGGING_CFG)
    return config


def init_logging():
    config = get_logging_cfg()
    logging.config.dictConfig(config)


def get_topics_from_db():
    '''Get a list with all topics from bod

    Returns:
        A List with the topics or an empty list
    '''
    # Connect to database
    if TESTING:
        return ['swisstopo', 'all', 'schnee', 'inspire', 'ech', 'api']
    logger.debug('Connecting to %s db on host %s', settings.BOD_DB_NAME, settings.BOD_DB_HOST)
    try:
        connection = psy.connect(
            dbname=settings.BOD_DB_NAME,
            user=settings.BOD_DB_USER,
            password=settings.BOD_DB_PASSWD,
            host=settings.BOD_DB_HOST,
            port=settings.BOD_DB_PORT,
            connect_timeout=5
        )
    except psy.Error as error:
        logger.error("Unable to connect: %s", error)
        if error.pgerror:
            logger.error('pgerror: %s', error.pgerror)
        if error.diag.message_detail:
            logger.error('message detail: %s', error.diag.message_detail)
        raise

    # Open cursor for DB-Operations
    cursor = connection.cursor()

    try:
        # select records from DB
        cursor.execute("""
            SELECT topic FROM "re3".topics
            """)
    except psy.Error as error:
        logger.exception('Failed to retrieve wms config from DB: %s', error)
        raise

    total_records = cursor.rowcount
    logger.info("Found %s records", total_records)

    # iterate through table
    _topics = ['all']
    for i, record in enumerate(cursor):
        logger.debug('topic in topics %d: %s', i, record)
        _topics.append(record[0])

    logger.info("List of topics has been generated")
    return _topics


topics = get_topics_from_db()
