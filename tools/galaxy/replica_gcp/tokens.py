"""OIDC-like ID tokens for the replica's internal callers (stand-in for Google-signed service-account ID tokens).

siarnaq's GoogleCloudAuthentication (api/user/authentication.py) accepts a request whose User-Agent is
Galaxy-Saturn, Google-Cloud-Tasks or Google-Cloud-Scheduler when google.oauth2.id_token.verify_oauth2_token() accepts
its Bearer token and the token's e-mail is in GALAXY_ADMIN_EMAILS. In galaxy, Google signs those tokens. Here the
relay (relay.py) mints them with HMAC-SHA256 under a 256-bit key that exists only on the VM
($GALAXY_HOME/secrets/oidc-hmac.key, mode 600, user bcreplica), and the stand-in verify_oauth2_token() checks them.

Requests that carry a Bearer header skip Caddy's basic auth (the logged-in frontend's JWT), so this check is what
keeps the internet from posting match results: a token must carry a valid signature under that key, the issuer
below, an expiry in the future, and a verified e-mail. Format: a compact JWS (header.payload.signature, base64url).
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from . import config

ISSUER = 'bc23-replica-oidc'
ALG = 'HS256'
KEY_NAME = 'oidc-hmac.key'
MAX_LIFETIME = 3600


def key_path():
    return os.environ.get('GALAXY_OIDC_KEY_FILE') or config.secrets_dir(KEY_NAME)


def generate_key(path=None):
    """Create the key file (64 hex chars) if it is missing. Never prints it."""
    path = path or key_path()
    if os.path.exists(path):
        return path
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as fh:
        fh.write(secrets.token_hex(32) + '\n')
    return path


def _key():
    with open(key_path()) as fh:
        raw = fh.read().strip()
    key = bytes.fromhex(raw)
    if len(key) < 32:
        raise ValueError('OIDC key shorter than 256 bits')
    return key


def _b64e(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()


def _b64d(s):
    if not isinstance(s, str) or not s or any(c not in
                                              'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
                                              for c in s):
        raise ValueError('malformed token segment')
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def mint(email, audience, lifetime=MAX_LIFETIME, now=None):
    now = int(time.time() if now is None else now)
    header = {'alg': ALG, 'typ': 'JWT', 'kid': 'bc23-replica'}
    payload = {'iss': ISSUER, 'aud': audience, 'sub': email, 'email': email, 'email_verified': True,
               'iat': now, 'exp': now + int(min(lifetime, MAX_LIFETIME))}
    signing_input = _b64e(json.dumps(header, separators=(',', ':')).encode()) + '.' + \
        _b64e(json.dumps(payload, separators=(',', ':')).encode())
    sig = hmac.new(_key(), signing_input.encode(), hashlib.sha256).digest()
    return signing_input + '.' + _b64e(sig)


def verify(token, audience=None, now=None, clock_skew=0):
    """The token's claims, or ValueError. Checks signature, algorithm, issuer, expiry, issue time, verified e-mail
    and (when given) the audience."""
    if not isinstance(token, str) or token.count('.') != 2 or len(token) > 4096:
        raise ValueError('malformed token')
    h64, p64, s64 = token.split('.')
    sig = _b64d(s64)
    want = hmac.new(_key(), (h64 + '.' + p64).encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(sig, want):
        raise ValueError('bad token signature')
    try:
        header, claims = json.loads(_b64d(h64)), json.loads(_b64d(p64))
    except (ValueError, UnicodeDecodeError):
        raise ValueError('malformed token') from None
    if not isinstance(header, dict) or header.get('alg') != ALG or not isinstance(claims, dict):
        raise ValueError('unexpected token header')
    now = int(time.time() if now is None else now)
    skew = max(0, int(clock_skew))
    if claims.get('iss') != ISSUER:
        raise ValueError('wrong token issuer')
    exp, iat = claims.get('exp'), claims.get('iat')
    if not isinstance(exp, int) or not isinstance(iat, int):
        raise ValueError('token lacks exp/iat')
    if exp < now - skew:
        raise ValueError('token expired')
    if iat > now + skew + 30 or exp - iat > MAX_LIFETIME:
        raise ValueError('token issued in the future or lives too long')
    if audience is not None and claims.get('aud') != audience:
        raise ValueError('wrong token audience')
    if not claims.get('email') or claims.get('email_verified') is not True:
        raise ValueError('token has no verified e-mail')
    return claims
