import logging

import psycopg2 as psy

from flask import g

from app import cache
from app import settings

logger = logging.getLogger(__name__)


@cache.cached(key_prefix='get_topics_from_db')
def get_topics():
    '''Get a list with all topics from bod

    Returns:
        A List with the topics
    '''
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            # select records from DB
            cursor.execute("""
                SELECT topic FROM "re3".topics
                """)
            total_records = cursor.rowcount
            logger.debug("Found %s records", total_records)
            # iterate through table
            _topics = ['all'] + [record[0] for record in cursor]
    except psy.Error as error:
        logger.exception('Failed to retrieve topics: %s', error)
        _topics = settings.FALLBACK_TOPICS
        logger.error("Connection to the db could not be established." \
        " Using fallback %s", _topics)
    logger.debug(
        "Was not cached yet: get_topics_from_db: List of topics has been generated %s.", _topics
    )
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
    lang = lang if lang in ['de', 'fr', 'it', 'rm', 'en'] else 'de'
    query = f"SELECT {lang} FROM translations WHERE msg_id like '{msg_id}%'"
    logger.debug('function get_translation: not cached, with query %s', query)
    try:
        db_connection = get_db_connection()
        with db_connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            # if msg_id not in table translations
            if result is not None:
                translation = result[0]
            else:
                logger.warning(
                    'Missing translation for %s', msg_id, extra={"missing_translation": True}
                )
                translation = msg_id
    except psy.Error as error:
        logger.exception('Failed to retrieve translations: %s', error)
        logger.error('The label %s could not be translated', msg_id)
        translation = msg_id
    return translation


def get_db_connection():
    '''Returns the retrieved db connection

    Returns:
        db connection
    '''
    if 'db_connection' not in g:
        logger.debug('Connecting to %s db on host %s', settings.BOD_DB_NAME, settings.BOD_DB_HOST)
        try:
            g.db_connection = psy.connect( # pylint: disable=assigning-non-slot
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

    return g.db_connection
