"""Stand-in for google.auth: there are no Google credentials on the replica host, and default() says so."""
from google._standin import missing
from google.auth import credentials, exceptions  # noqa: F401

__version__ = '0+bc23replica'
__getattr__ = missing(__name__)


def default(scopes=None, request=None, quota_project_id=None, default_scopes=None):
    raise exceptions.DefaultCredentialsError('bc23 replica: no Google credentials exist on this host')
