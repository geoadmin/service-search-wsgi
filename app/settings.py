import logging
import os
from distutils.util import strtobool
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
ENV_FILE = os.getenv('ENV_FILE', None)
if ENV_FILE:
    from dotenv import load_dotenv
    print(f"Running locally hence injecting env vars from {ENV_FILE}")
    load_dotenv(ENV_FILE, override=True, verbose=True)

HTTP_PORT = os.getenv('HTTP_PORT', '5000')
LOGS_DIR = os.getenv('LOGS_DIR', str(BASE_DIR / 'logs'))
os.environ['LOGS_DIR'] = LOGS_DIR  # Set default if not set
LOGGING_CFG = os.getenv('LOGGING_CFG', 'logging-cfg-local.yml')
TRAP_HTTP_EXCEPTIONS = True
BOD_DB_NAME = os.getenv('BOD_DB_NAME', None)
BOD_DB_HOST = os.getenv('BOD_DB_HOST', None)
BOD_DB_PORT = int(os.getenv('BOD_DB_PORT', '5432'))
BOD_DB_USER = os.getenv('BOD_DB_USER', 'www-data')
BOD_DB_PASSWD = os.getenv('BOD_DB_PASSWD', None)
BOD_DB_CONNECT_TIMEOUT = int(os.getenv('BOD_DB_CONNECT_TIMEOUT', '1'))

FALLBACK_TOPICS = [
    'all',
    'verteidigung',
    'inspire',
    'emapis',
    'luftbilder',
    'geol',
    'ivs',
    'bfs',
    'nga',
    'cadastre',
    'mgdi',
    'schule',
    'api',
    'bafu',
    'energie',
    'ech',
    'gewiss',
    'swissmaponline',
    'meteoschweiz',
    'schneesport',
    'notruf',
    'wildruhezonen',
    'kgs',
    'isos',
    'swisstopo',
    'funksender',
    'sachplan',
    'milgeo',
    'astra',
    'geodesy',
    'blw',
    'are',
    'dev',
    'geothermie',
    'aviation',
    'vu'
]

SEARCH_SPHINX_HOST = os.getenv('SEARCH_SPHINX_HOST', 'localhost')
SEARCH_SPHINX_PORT = int(os.getenv('SEARCH_SPHINX_PORT', '9312'))

SCRIPT_NAME = os.getenv('SCRIPT_NAME', '')  # This is used by unicorn for route prefix

# geodata stagings can be dev, int or prod
GEODATA_STAGING = os.getenv('GEODATA_STAGING', 'prod')

# Flask-Caching
CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '86400'))  # 24 h

# SQL Alchemy
# pylint: disable=line-too-long
SQLALCHEMY_DATABASE_URI = \
    f"postgresql://{BOD_DB_USER}:{BOD_DB_PASSWD}@{BOD_DB_HOST}:{BOD_DB_PORT}/{BOD_DB_NAME}"

# SQL Alchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = strtobool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False'))

ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', r'.*').split(',')
ALLOWED_DOMAINS_PATTERN = f"({format('|'.join(ALLOWED_DOMAINS))})"

# Proxy settings
FORWARED_ALLOW_IPS = os.getenv('FORWARED_ALLOW_IPS', '*')
FORWARDED_PROTO_HEADER_NAME = os.getenv('FORWARDED_PROTO_HEADER_NAME', 'X-Forwarded-Proto')

# Cache-Control
CACHE_CONTROL_HEADER = os.getenv('CACHE_CONTROL_HEADER', 'public, max-age=600')
