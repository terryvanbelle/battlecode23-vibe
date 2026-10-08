"""Stand-in for google.auth.exceptions."""


class GoogleAuthError(Exception):
    pass


class TransportError(GoogleAuthError):
    pass


class RefreshError(GoogleAuthError):
    pass


class DefaultCredentialsError(GoogleAuthError):
    pass


class MalformedError(DefaultCredentialsError, ValueError):
    pass


class InvalidValue(DefaultCredentialsError, ValueError):
    pass
