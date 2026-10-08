"""Cloud Storage buckets as local directories.

Object data:      $GALAXY_STORAGE_ROOT/<bucket>/<object name>            (Caddy serves it read-only at /storage/...)
Object metadata:  $GALAXY_HOME/storage-meta/<bucket>/<object name>.json  (never served: content type, ACL, custom
                                                                          metadata such as Titan-Status)
URLs: an object's public URL and every "signed" URL are the same-origin path /storage/<bucket>/<object name>. Caddy
puts the whole site behind basic auth, so these URLs are as private as the site (docs/galaxy/README.md).
"""
import base64
import datetime
import hashlib
import json
import os
import re
import urllib.parse

from . import config, fsutil

BUCKET_RE = re.compile(r'^[a-z0-9][a-z0-9._-]{1,220}[a-z0-9]$')
URL_PREFIX = '/storage/'


class NotFound(Exception):
    """The object does not exist (google.api_core.exceptions.NotFound in the real client)."""


def check_bucket(bucket):
    if not isinstance(bucket, str) or not BUCKET_RE.match(bucket) or '..' in bucket:
        raise ValueError(f'bad bucket name {bucket!r}')
    return bucket


def object_path(bucket, name):
    return fsutil.join_under(config.storage_root(check_bucket(bucket)), name, 'object name')


def meta_path(bucket, name):
    return fsutil.join_under(config.galaxy_home('storage-meta', check_bucket(bucket)), name, 'object name') + '.json'


def public_url(bucket, name):
    fsutil.safe_parts(name, 'object name')
    return URL_PREFIX + check_bucket(bucket) + '/' + urllib.parse.quote(name, safe='/')


def exists(bucket, name):
    return os.path.isfile(object_path(bucket, name))


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def load_meta(bucket, name):
    """The object's properties (GCS JSON API names), or None when the object does not exist."""
    path = object_path(bucket, name)
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return None
    meta = {}
    try:
        with open(meta_path(bucket, name)) as fh:
            meta = json.load(fh)
    except (FileNotFoundError, ValueError):
        meta = {}
    meta.update(bucket=bucket, name=name, size=str(st.st_size))
    meta.setdefault('contentType', 'application/octet-stream')
    meta.setdefault('metadata', None)
    meta.setdefault('updated', datetime.datetime.fromtimestamp(st.st_mtime, datetime.timezone.utc)
                    .isoformat(timespec='milliseconds').replace('+00:00', 'Z'))
    return meta


def save_meta(bucket, name, meta):
    keep = {k: v for k, v in meta.items() if k not in ('bucket', 'name', 'size')}
    fsutil.atomic_write_json(meta_path(bucket, name), keep)


def _md5_b64(path):
    h = hashlib.md5()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return base64.b64encode(h.digest()).decode()


def _committed(bucket, name, content_type, predefined_acl, metadata=None):
    def commit(size):
        old = load_meta(bucket, name) or {}
        gen = int(old.get('generation') or 0) + 1
        meta = {'contentType': content_type or 'application/octet-stream', 'acl': predefined_acl,
                'metadata': metadata, 'updated': _now(), 'generation': str(gen),
                'md5Hash': _md5_b64(object_path(bucket, name))}
        save_meta(bucket, name, meta)
    return commit


def writer(bucket, name, content_type=None, predefined_acl=None):
    """A file object; the object (and new metadata, custom metadata reset as on a GCS upload) appears on close."""
    return fsutil.AtomicWriter(object_path(bucket, name),
                               on_commit=_committed(bucket, name, content_type, predefined_acl))


def write_bytes(bucket, name, data, content_type=None, predefined_acl=None):
    with writer(bucket, name, content_type, predefined_acl) as w:
        w.write(data)


def write_file(bucket, name, src_path, content_type=None, predefined_acl=None):
    with writer(bucket, name, content_type, predefined_acl) as w, open(src_path, 'rb') as r:
        for chunk in iter(lambda: r.read(1 << 20), b''):
            w.write(chunk)


def read_bytes(bucket, name):
    try:
        with open(object_path(bucket, name), 'rb') as fh:
            return fh.read()
    except FileNotFoundError:
        raise NotFound(f'No such object: {bucket}/{name}') from None


def open_read(bucket, name):
    try:
        return open(object_path(bucket, name), 'rb')
    except FileNotFoundError:
        raise NotFound(f'No such object: {bucket}/{name}') from None


def patch_metadata(bucket, name, metadata):
    """blob.patch() of custom metadata (None clears it). Then Titan's stand-in runs (titan_scan)."""
    meta = load_meta(bucket, name)
    if meta is None:
        raise NotFound(f'No such object: {bucket}/{name}')
    meta['metadata'] = dict(metadata) if metadata is not None else None
    meta['updated'] = _now()
    meta['metageneration'] = str(int(meta.get('metageneration') or 1) + 1)
    save_meta(bucket, name, meta)
    titan_scan(bucket, name)
    return load_meta(bucket, name)


def titan_scan(bucket, name):
    """Stand-in for Titan (galaxy/titan: ClamAV over Eventarc on metadata updates). Titan scans an object whose
    custom metadata says Titan-Status: Unverified and sets Verified or Malicious. No virus scanner runs here; the
    only uploads (resumes, team reports) come from the owner, so the object is marked Verified at once."""
    meta = load_meta(bucket, name)
    if meta and (meta.get('metadata') or {}).get('Titan-Status') == 'Unverified':
        meta['metadata'] = dict(meta['metadata'], **{'Titan-Status': 'Verified'})
        meta['updated'] = _now()
        save_meta(bucket, name, meta)


def delete(bucket, name):
    try:
        os.unlink(object_path(bucket, name))
    except FileNotFoundError:
        raise NotFound(f'No such object: {bucket}/{name}') from None
    try:
        os.unlink(meta_path(bucket, name))
    except FileNotFoundError:
        pass


def list_names(bucket, prefix=''):
    root = config.storage_root(check_bucket(bucket))
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for f in filenames:
            if f.startswith('.'):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), root).replace(os.sep, '/')
            if rel.startswith(prefix):
                out.append(rel)
    return sorted(out)
