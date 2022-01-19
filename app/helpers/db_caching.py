import logging

import psycopg2 as psy

from app import cache
from app import settings

logger = logging.getLogger(__name__)


@cache.cached(key_prefix='get_topics_from_db')
def get_topics_from_db():
    '''Get a list with all topics from bod

    Returns:
        A List with the topics or an empty list
    '''
    cursor = get_db_connection()

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

    logger.debug("get_topics_from_db: List of topics has been generated. No cache yet.")
    return _topics


@cache.memoize()
def get_translation(msg_id, lang):
    '''Get translation from bod table translations

    Args:
        msgi_id:
            String with the key to be translated
        lang:
            The lang to which will have to be translated

    Returns:
        String translated string or original string, if not in db

    '''
    # sanitize lang
    if lang not in ['de', 'fr', 'it', 'rm', 'en']:
        lang = 'de'
    query = f"SELECT {lang} FROM translations WHERE msg_id like '{msg_id}%'"
    logger.debug('function get_translation: not cached, with query %s', query)
    cursor = get_db_connection()
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        # if msg_id not in table translations
        if result is not None:
            translation = result[0]
        else:
            translation = msg_id
    except psy.Error as error:
        logger.exception('Failed to retrieve wms config from DB: %s', error)
        raise
    return translation


def get_db_connection():
    '''Connect to database and return a cursor

    Returns:
        db connection cursor
    '''
    logger.debug('Connecting to %s db on host %s', settings.BOD_DB_NAME, settings.BOD_DB_HOST)
    try:
        connection = psy.connect(
            dbname=settings.BOD_DB_NAME,
            user=settings.BOD_DB_USER,
            password=settings.BOD_DB_PASSWD,
            host=settings.BOD_DB_HOST,
            port=settings.BOD_DB_PORT,
            connect_timeout=settings.BOD_DB_CONNECT_TIMEOUT
        )
    except psy.Error as error:
        logger.error("Unable to connect: %s", error)
        if error.pgerror:
            logger.error('pgerror: %s', error.pgerror)
        if error.diag.message_detail:
            logger.error('message detail: %s', error.diag.message_detail)
        raise

    # Open cursor for DB-Operations
    return connection.cursor()
