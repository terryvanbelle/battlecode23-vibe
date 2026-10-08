"""Helpers shared by the stand-ins: fail-closed module attributes and the replica_gcp import."""
import os
import sys

_TOOLS_GALAXY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOLS_GALAXY not in sys.path:
    sys.path.insert(0, _TOOLS_GALAXY)


def missing(module):
    """A module-level __getattr__ that refuses every name the stand-in does not define."""
    def __getattr__(name):
        if name.startswith('__'):
            raise AttributeError(name)
        raise AttributeError(f'{module}.{name} is not implemented by the bc23 replica stand-in (fail closed)')
    return __getattr__


def unsupported(what):
    raise NotImplementedError(f'{what} is not implemented by the bc23 replica stand-in (fail closed)')
