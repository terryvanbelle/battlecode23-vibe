"""Stand-in for google.oauth2.id_token: verifies the replica's own HMAC ID tokens (replica_gcp/tokens.py) instead
of Google-signed ones, without fetching any certificate. Used by siarnaq's GoogleCloudAuthentication."""
from google._standin import missing, unsupported
from replica_gcp import tokens

__getattr__ = missing(__name__)


def verify_token(id_token, request, audience=None, certs_url=None, clock_skew_in_seconds=0):
    if certs_url is not None:
        unsupported('verify_token(certs_url=...)')
    try:
        return tokens.verify(id_token.decode() if isinstance(id_token, bytes) else id_token, audience=audience,
                             clock_skew=clock_skew_in_seconds)
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f'cannot verify token: {e}') from None


def verify_oauth2_token(id_token, request, audience=None, clock_skew_in_seconds=0):
    """Claims of a valid token; ValueError otherwise (as google-auth raises for a bad Google token)."""
    return verify_token(id_token, request, audience=audience, clock_skew_in_seconds=clock_skew_in_seconds)


def fetch_id_token(request, audience):
    unsupported('google.oauth2.id_token.fetch_id_token')
