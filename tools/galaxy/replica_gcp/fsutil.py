"""Atomic file writes and safe relative paths (no '..', no absolute paths, no hidden components)."""
import json
import os
import secrets

TMP_PREFIX = '.tmp-'


def safe_parts(name, what='name'):
    """Split a slash-separated relative name into path components, refusing anything that could leave its root."""
    if not isinstance(name, str) or not name:
        raise ValueError(f'empty {what}')
    if len(name.encode('utf-8')) > 1024:
        raise ValueError(f'{what} longer than 1024 bytes')
    if any(ord(c) < 32 or c == '\x7f' for c in name) or '\\' in name:
        raise ValueError(f'{what} has control characters or backslashes: {name!r}')
    parts = name.split('/')
    for p in parts:
        if p in ('', '.', '..') or p.startswith('.'):
            raise ValueError(f'{what} has an empty, dot or hidden component: {name!r}')
    return parts


def join_under(root, name, what='name'):
    path = os.path.join(root, *safe_parts(name, what))
    real_root = os.path.abspath(root)
    if not os.path.abspath(path).startswith(real_root + os.sep):
        raise ValueError(f'{what} escapes its root: {name!r}')
    return path


def _tmp_path(path):
    d, b = os.path.split(path)
    return os.path.join(d, f'{TMP_PREFIX}{os.getpid()}-{secrets.token_hex(6)}-{b}'[:250])


def atomic_write_bytes(path, data, mode=None):
    """Write data to path through a temporary file in the same directory and a rename (readers never see a part)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = _tmp_path(path)
    try:
        with open(tmp, 'wb') as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        if mode is not None:
            os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path, obj):
    atomic_write_bytes(path, (json.dumps(obj, indent=1, sort_keys=True) + '\n').encode())


class AtomicWriter:
    """A binary file object that becomes visible at `path` only when closed without error."""

    def __init__(self, path, on_commit=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path, self.on_commit = path, on_commit
        self._tmp = _tmp_path(path)
        self._fh = open(self._tmp, 'wb')
        self.size = 0

    def write(self, data):
        if isinstance(data, str):
            raise TypeError('binary writer: write bytes')
        n = self._fh.write(data)
        self.size += n
        return n

    def writable(self):
        return True

    def flush(self):
        self._fh.flush()

    @property
    def closed(self):
        return self._fh.closed

    def close(self):
        if self._fh.closed:
            return
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self._fh.close()
        os.replace(self._tmp, self.path)
        if self.on_commit:
            self.on_commit(self.size)

    def abort(self):
        if not self._fh.closed:
            self._fh.close()
        try:
            os.unlink(self._tmp)
        except FileNotFoundError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.close()
        else:
            self.abort()
        return False
