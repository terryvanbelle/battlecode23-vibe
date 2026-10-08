"""Python 3.10 behaviour that siarnaq (galaxy f343088, written for Python 3.10: backend/environment.yml) relies on and
that Python 3.11, the replica's interpreter (Debian 12), removed. Applied by replica_settings.py before siarnaq runs;
no siarnaq file is changed.

random.sample(population, k): Python 3.9 and 3.10 accept a set or a dict view (deprecated, converted with
tuple()); 3.11 raises TypeError("Population must be a sequence"). siarnaq samples the 3 maps of every ranked
scrimmage request that way (api/compete/serializers.py: random.sample(maps.keys(), 3)), so on 3.11 every ranked
request failed with HTTP 500 (found 2026-10-08). The patch restores 3.10's conversion exactly and nothing else.
"""
import collections.abc
import random

_PATCHED = '_bc23_py310_sample'


def apply():
    """Idempotent. Patches random.Random.sample and rebinds the module-level random.sample (bound to the hidden
    module instance at import time)."""
    if getattr(random.Random.sample, _PATCHED, False):
        return False
    orig = random.Random.sample

    def sample(self, population, k, *, counts=None):
        if isinstance(population, collections.abc.Set):     # Python 3.10, random.py: "Sampling from a set"
            population = tuple(population)
        return orig(self, population, k, counts=counts)
    sample.__doc__ = orig.__doc__
    setattr(sample, _PATCHED, True)
    random.Random.sample = sample
    random.sample = random._inst.sample
    return True
