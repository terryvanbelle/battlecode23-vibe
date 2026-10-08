"""Message types shared by the Cloud Tasks and Cloud Scheduler stand-ins (proto-plus look-alikes)."""
import enum


class HttpMethod(enum.IntEnum):
    HTTP_METHOD_UNSPECIFIED = 0
    POST = 1
    GET = 2
    HEAD = 3
    PUT = 4
    DELETE = 5
    PATCH = 6
    OPTIONS = 7


class _Message:
    _fields = ()

    def __init__(self, mapping=None, **kwargs):
        data = dict(mapping or {}, **kwargs)
        unknown = set(data) - set(self._fields)
        if unknown:
            raise TypeError(f'{type(self).__name__} has no field(s) {sorted(unknown)} in the bc23 replica stand-in')
        for f in self._fields:
            setattr(self, f, data.get(f, self._default(f)))

    def _default(self, f):
        return None

    def __repr__(self):
        return f'{type(self).__name__}({", ".join(f"{f}={getattr(self, f)!r}" for f in self._fields)})'


class OidcToken(_Message):
    _fields = ('service_account_email', 'audience')

    def _default(self, f):
        return ''


def coerce(cls, value):
    if value is None or isinstance(value, cls):
        return value
    if isinstance(value, dict):
        return cls(value)
    raise TypeError(f'expected {cls.__name__} or dict, got {type(value).__name__}')


def method_name(m):
    m = HttpMethod(m if m is not None else HttpMethod.POST)
    return 'POST' if m == HttpMethod.HTTP_METHOD_UNSPECIFIED else m.name
