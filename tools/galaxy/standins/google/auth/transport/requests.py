"""Stand-in for google.auth.transport.requests: a transport that refuses every request (no network)."""
from google._standin import missing
from google.auth import exceptions

__getattr__ = missing(__name__)


class Request:
    def __init__(self, session=None):
        self.session = session

    def __call__(self, url, method='GET', body=None, headers=None, timeout=None, **kwargs):
        raise exceptions.TransportError(f'bc23 replica: no network access to {url!r}')
