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

HTTP_PORT = str(os.getenv('HTTP_PORT', "5000"))
LOGS_DIR = os.getenv('LOGS_DIR', str(BASE_DIR / 'logs'))
os.environ['LOGS_DIR'] = LOGS_DIR  # Set default if not set
LOGGING_CFG = os.getenv('LOGGING_CFG', 'logging-cfg-local.yml')
TRAP_HTTP_EXCEPTIONS = True
DEBUG = os.getenv('DEBUG', 'FALSE') == 'TRUE'
BOD_DB_NAME = str(os.getenv('BOD_DB_NAME', None))
BOD_DB_HOST = str(os.getenv('BOD_DB_HOST', None))
BOD_DB_PORT = int(os.getenv('BOD_DB_PORT', '5432'))
BOD_DB_USER = str(os.getenv('BOD_DB_USER', None))
BOD_DB_PASSWD = str(os.getenv('BOD_DB_PASSWD', None))
BOD_DB_CONNECT_TIMEOUT = int(os.getenv('BOD_DB_CONNECT_TIMEOUT', '10'))
BOD_DB_CONNECT_RETRIES = int(os.getenv('BOD_DB_CONNECT_RETRIES', '3'))

SEARCH_SPHINX_HOST = str(os.getenv('SEARCH_SPHINX_HOST', 'localhost'))
SEARCH_SPHINX_PORT = int(os.getenv('SEARCH_SPHINX_PORT', '9312'))

SCRIPT_NAME = os.getenv('SCRIPT_NAME', '')  # This is used by unicorn for route prefix

# geodata stagings can be dev, int or prod
GEODATA_STAGING = str(os.getenv('GEODATA_STAGING', 'prod'))

TESTING = strtobool(os.getenv('TESTING', 'False'))

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
