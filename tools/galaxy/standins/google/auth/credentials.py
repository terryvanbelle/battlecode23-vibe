"""Stand-in for google.auth.credentials: credential objects that can be constructed but never yield a token."""
from google._standin import missing
from google.auth import exceptions

__getattr__ = missing(__name__)


class Credentials:
    token = None
    expiry = None

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs

    @property
    def valid(self):
        return False

    @property
    def expired(self):
        return True

    def refresh(self, request):
        raise exceptions.RefreshError('bc23 replica: credentials cannot be refreshed (no Google access)')

    def before_request(self, request, method, url, headers):
        self.refresh(request)

    def apply(self, headers, token=None):
        self.refresh(None)


class AnonymousCredentials(Credentials):
    def refresh(self, request):
        return None

    def apply(self, headers, token=None):
        return None

    def before_request(self, request, method, url, headers):
        return None
