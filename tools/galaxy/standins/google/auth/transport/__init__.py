"""Stand-in for google.auth.transport."""
from google._standin import missing

__getattr__ = missing(__name__)
