import multiprocessing

from gunicorn.app.base import BaseApplication

from app import app as application
from app.helpers.utils import get_logging_cfg
from app.settings import FORWARDED_PROTO_HEADER_NAME
from app.settings import FORWARED_ALLOW_IPS
from app.settings import GUNICORN_WORKER_TMP_DIR
from app.settings import HTTP_PORT
from app.settings import SEARCH_SPHINX_TIMEOUT
from app.settings import SEARCH_WORKERS
from app.settings import WSGI_TIMEOUT


class StandaloneApplication(BaseApplication):  # pylint: disable=abstract-method

    def __init__(self, app, options=None):  # pylint: disable=redefined-outer-name
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


# We use the port 5000 as default, otherwise we set the HTTP_PORT env variable within the container.
if __name__ == '__main__':
    if SEARCH_WORKERS <= 0:
        SEARCH_WORKERS = (multiprocessing.cpu_count() * 2) + 1
    # Bind to 0.0.0.0 to let your app listen to all network interfaces.
    options = {
        'bind': f"0.0.0.0:{HTTP_PORT}",
        'worker_class': 'gevent',
        'workers': SEARCH_WORKERS,
        'worker_tmp_dir': GUNICORN_WORKER_TMP_DIR,
        'timeout': WSGI_TIMEOUT + SEARCH_SPHINX_TIMEOUT,
        'logconfig_dict': get_logging_cfg(),
        'forwarded_allow_ips': FORWARED_ALLOW_IPS,
        'secure_scheme_headers': {
            FORWARDED_PROTO_HEADER_NAME.upper(): 'https'
        }
    }
    StandaloneApplication(application, options).run()
