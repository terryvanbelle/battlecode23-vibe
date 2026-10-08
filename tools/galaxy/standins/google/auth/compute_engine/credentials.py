"""Stand-in for google.auth.compute_engine.credentials."""
from google._standin import missing
from google.auth import credentials

__getattr__ = missing(__name__)


class Credentials(credentials.Credentials):
    pass
