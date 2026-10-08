"""Stand-in for google.oauth2."""
from google._standin import missing

__getattr__ = missing(__name__)
