import logging
import os
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

ALLOWED_DOMAINS = os.getenv('ALLOWED_DOMAINS', r'.*').split(',')
ALLOWED_DOMAINS_PATTERN = f"({format('|'.join(ALLOWED_DOMAINS))})"

# Proxy settings
FORWARED_ALLOW_IPS = os.getenv('FORWARED_ALLOW_IPS', '*')
FORWARDED_PROTO_HEADER_NAME = os.getenv('FORWARDED_PROTO_HEADER_NAME', 'X-Forwarded-Proto')
