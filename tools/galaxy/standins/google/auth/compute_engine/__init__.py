"""Stand-in for google.auth.compute_engine (the metadata server is never contacted)."""
from google._standin import missing
from google.auth.compute_engine.credentials import Credentials  # noqa: F401

__getattr__ = missing(__name__)
