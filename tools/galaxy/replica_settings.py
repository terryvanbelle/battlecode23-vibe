"""Django settings of the bc23 galaxy replica: siarnaq (galaxy f343088, unmodified) with local stand-ins.

Selected with DJANGO_SETTINGS_MODULE=replica_settings and DJANGO_CONFIGURATION=Replica (django-configurations).
PYTHONPATH must put tools/galaxy/standins first (the `google` stand-ins), then tools/galaxy, then galaxy's backend/.

What differs from siarnaq's Production class, and why (docs/galaxy/README.md, "Differences from galaxy"):
  * GCLOUD_ENABLE_ACTIONS=True with every Google client replaced by a stand-in (tools/galaxy/standins/google/).
  * The site is https://galaxy.<ip-with-dashes>.sslip.io/ (ALLOWED_HOSTS[0], CSRF, CORS, FRONTEND_ORIGIN); no
    setting names an official Battlecode host. The host is read at start from /etc/bc23-replica/hostname.
  * PostgreSQL 15 on the local unix socket (peer auth, no TCP), as galaxy's Cloud SQL Postgres.
  * Secrets (Django key, the migration-created admin's password) are files generated on the VM, never committed.
  * E-mail is off twice: EMAIL_ENABLED=False and a backend that drops every message (replica_gcp/mail.py).
  * Caddy terminates TLS and adds X-Forwarded-Proto/-For (SECURE_PROXY_SSL_HEADER, NUM_PROXIES=1).
"""
import os
from typing import Any

from siarnaq.settings import _LOGGING_COMMON, Base  # noqa: E402  (imports the google stand-ins)

from replica_gcp import config as rc

STANDINS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'standins')


def _secret(name, required=True):
    path = rc.secrets_dir(name)
    try:
        with open(path) as fh:
            value = fh.read().strip()
    except FileNotFoundError:
        if required:
            raise RuntimeError(f'bc23 replica: missing secret {path} (run tools/galaxy/deploy/galaxy-setup.sh secrets)')
        return None
    if len(value) < 32:
        raise RuntimeError(f'bc23 replica: secret {path} is too short')
    return value


def _check_standins():
    """Refuse to start unless every google.* module siarnaq uses comes from the stand-ins (fail closed)."""
    import google.auth
    import google.cloud.pubsub
    import google.cloud.scheduler
    import google.cloud.secretmanager
    import google.cloud.storage
    import google.cloud.tasks_v2
    import google.oauth2.id_token
    for m in (google.auth, google.oauth2.id_token, google.cloud.storage, google.cloud.pubsub, google.cloud.tasks_v2,
              google.cloud.scheduler, google.cloud.secretmanager):
        if not os.path.abspath(m.__file__).startswith(STANDINS_DIR + os.sep):
            raise RuntimeError(f'bc23 replica: {m.__name__} is not the stand-in ({m.__file__})')


class Replica(Base):
    GALAXY_HOST = rc.galaxy_host()
    ALLOWED_HOSTS = [GALAXY_HOST]          # [0] builds saturn's report URLs and the task/scheduler URLs
    CSRF_TRUSTED_ORIGINS = [f'https://{GALAXY_HOST}']
    CORS_ALLOWED_ORIGINS = [f'https://{GALAXY_HOST}']
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = False            # Caddy redirects http to https; the loopback relay speaks plain http
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    DEBUG = False

    GALAXY_ADMIN_EMAILS = list(rc.ADMIN_EMAILS)
    GALAXY_ADMIN_USERNAME = rc.ADMIN_USERNAME

    GCLOUD_SERVICE_EMAIL = rc.SERVICE_EMAIL
    GCLOUD_LOCATION = rc.LOCATION
    GCLOUD_ENABLE_ACTIONS = True
    GCLOUD_CREDENTIALS = None
    GCLOUD_PROJECT = rc.PROJECT
    GCLOUD_BUCKET_PUBLIC = rc.BUCKET_PUBLIC
    GCLOUD_BUCKET_SECURE = rc.BUCKET_SECURE
    GCLOUD_BUCKET_EPHEMERAL = rc.BUCKET_EPHEMERAL
    GCLOUD_TOPIC_COMPILE = rc.TOPIC_COMPILE
    GCLOUD_TOPIC_EXECUTE = rc.TOPIC_EXECUTE
    GCLOUD_ORDER_COMPILE = rc.ORDER_COMPILE
    GCLOUD_ORDER_EXECUTE = rc.ORDER_EXECUTE
    GCLOUD_SCHEDULER_PREFIX = rc.SCHEDULER_PREFIX
    GCLOUD_BRACKET_QUEUE = rc.QUEUE_BRACKET
    GCLOUD_RATING_QUEUE = rc.QUEUE_RATING

    EMAIL_ENABLED = False
    EMAIL_VERIFICATION_ENABLED = False
    EMAIL_VERIFICATION_REQUIRED = False
    EMAIL_BACKEND = 'replica_gcp.mail.DropEmailBackend'
    EMAIL_HOST = 'mail.invalid'
    EMAIL_HOST_USER = 'no-reply@bc23-replica.invalid'
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
    SERVER_EMAIL = EMAIL_HOST_USER
    ADMINS: list = []
    MANAGERS: list = []
    ANYMAIL = {'MAILJET_API_KEY': '', 'MAILJET_SECRET_KEY': ''}
    FRONTEND_ORIGIN = f'https://{GALAXY_HOST}'
    CHALLONGE_API_KEY = ''

    REST_FRAMEWORK = dict(Base.REST_FRAMEWORK, NUM_PROXIES=1)   # client address from Caddy's X-Forwarded-For

    STATIC_ROOT = os.environ.get('GALAXY_STATIC_ROOT', '/srv/bc23-galaxy/static')

    LOGGING: dict[str, Any] = {
        **_LOGGING_COMMON,
        'loggers': {
            'django': {'handlers': ['json'], 'level': 'INFO'},
            'django_structlog': {'handlers': ['json'], 'level': 'INFO'},
            'siarnaq': {'handlers': ['json'], 'level': 'DEBUG'},
        },
    }

    @property
    def DATABASES(self):
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('GALAXY_DB_NAME', 'siarnaq'),
                'USER': os.environ.get('GALAXY_DB_USER', 'bcreplica'),
                'HOST': os.environ.get('GALAXY_DB_HOST', '/var/run/postgresql'),   # unix socket: peer auth, no TCP
                'CONN_MAX_AGE': 60,
            }
        }

    @classmethod
    def pre_setup(cls):
        super().pre_setup()
        _check_standins()
        cls.SECRET_KEY = _secret('django-secret-key')
        # migration user/0002 creates the superuser "admin" with this password; nobody needs to know it
        cls.SUPERUSER_PASSWORD = _secret('admin-password')


class ReplicaTest(Replica):
    """For offline checks only (python3 -m test ...): SQLite in GALAXY_HOME, generated secrets."""

    @property
    def DATABASES(self):
        return {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': rc.galaxy_home('test.sqlite3')}}

