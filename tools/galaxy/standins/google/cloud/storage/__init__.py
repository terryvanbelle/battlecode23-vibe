"""Stand-in for google.cloud.storage: buckets are directories on the replica host (replica_gcp/storage.py).

What siarnaq (galaxy f343088) calls, and what this does:
  Client(credentials=...), Client(), Client.create_anonymous_client()   no connection; credentials are ignored
  client.bucket(name) / client.get_bucket(name)                         a Bucket (get_bucket: must exist)
  bucket.blob(name) / bucket.get_blob(name)                             a Blob (get_blob: None if missing)
  blob.open("wb", content_type=, predefined_acl=) / blob.open("rb")     atomic write / read of the object file
  blob.upload_from_string(data), upload_from_filename, upload_from_file the same, in one call
  blob.download_as_bytes() (download_as_string), download_to_filename   read
  blob.metadata (+ blob.patch())                                        custom metadata in a sidecar; a patch to
                                                                        Titan-Status: Unverified is marked Verified
  blob.generate_signed_url(expiration=, method="GET", credentials=)    /storage/<bucket>/<name> (same origin)
  blob.public_url                                                       /storage/<bucket>/<name>
Anything else raises NotImplementedError or AttributeError.
"""
import io
import os

from google._standin import missing, unsupported
from replica_gcp import storage as _fs

__getattr__ = missing(__name__)


class Client:
    def __init__(self, project=None, credentials=None, _http=None, client_info=None, client_options=None,
                 **kwargs):
        if _http is not None:
            unsupported('storage.Client(_http=...)')
        self.project = project or 'bc23-replica'
        self._credentials = credentials

    @classmethod
    def create_anonymous_client(cls):
        return cls(project='<none>')

    def bucket(self, bucket_name, user_project=None):
        return Bucket(self, bucket_name, user_project=user_project)

    def get_bucket(self, bucket_or_name, timeout=None, **kwargs):
        b = bucket_or_name if isinstance(bucket_or_name, Bucket) else self.bucket(bucket_or_name)
        if not b.exists():
            raise _fs.NotFound(f'bucket {b.name} does not exist')
        return b

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'storage.Client.{name}')


class Bucket:
    def __init__(self, client, name=None, user_project=None):
        self.client, self.name, self.user_project = client, _fs.check_bucket(name), user_project

    def blob(self, blob_name, chunk_size=None, encryption_key=None, kms_key_name=None, generation=None):
        if encryption_key is not None or kms_key_name is not None or generation is not None:
            unsupported('Bucket.blob(encryption_key/kms_key_name/generation)')
        return Blob(blob_name, self, chunk_size=chunk_size)

    def get_blob(self, blob_name, client=None, encryption_key=None, generation=None, timeout=None, **kwargs):
        blob = self.blob(blob_name)
        if not blob.exists():
            return None
        blob.reload()
        return blob

    def exists(self, client=None, timeout=None, **kwargs):
        return os.path.isdir(_fs.config.storage_root(self.name))

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'storage.Bucket.{name}')

    def __repr__(self):
        return f'<Bucket: {self.name}>'


class Blob:
    def __init__(self, name, bucket, chunk_size=None, encryption_key=None, kms_key_name=None, generation=None):
        if encryption_key is not None or kms_key_name is not None or generation is not None:
            unsupported('Blob(encryption_key/kms_key_name/generation)')
        _fs.object_path(bucket.name, name)   # validates the name
        self.name, self.bucket, self.chunk_size = name, bucket, chunk_size
        self._properties = {}
        self._changes = set()
        self.content_type = None

    # ---- properties
    @property
    def metadata(self):
        return self._properties.get('metadata')

    @metadata.setter
    def metadata(self, value):
        self._properties['metadata'] = dict(value) if value is not None else None
        self._changes.add('metadata')

    @property
    def size(self):
        s = self._properties.get('size')
        return int(s) if s is not None else None

    @property
    def public_url(self):
        return _fs.public_url(self.bucket.name, self.name)

    @property
    def path(self):
        return f'/b/{self.bucket.name}/o/{self.name}'

    # ---- metadata calls
    def exists(self, client=None, timeout=None, **kwargs):
        return _fs.exists(self.bucket.name, self.name)

    def reload(self, client=None, projection='noAcl', timeout=None, **kwargs):
        meta = _fs.load_meta(self.bucket.name, self.name)
        if meta is None:
            raise _fs.NotFound(f'No such object: {self.bucket.name}/{self.name}')
        self._properties = dict(meta)
        self.content_type = meta.get('contentType')
        self._changes.clear()

    def patch(self, client=None, timeout=None, **kwargs):
        unknown = self._changes - {'metadata'}
        if unknown:
            unsupported(f'Blob.patch of {sorted(unknown)}')
        meta = _fs.patch_metadata(self.bucket.name, self.name, self.metadata)
        self._properties = dict(meta)
        self._changes.clear()

    # ---- data
    def open(self, mode='r', chunk_size=None, ignore_flush=None, encoding=None, errors=None, newline=None,
             content_type=None, predefined_acl=None, **kwargs):
        if kwargs:
            unsupported(f'Blob.open({", ".join(sorted(kwargs))}=...)')
        if mode in ('wb', 'w'):
            w = _fs.writer(self.bucket.name, self.name, content_type or self.content_type
                           or ('text/plain' if mode == 'w' else None), predefined_acl)
            if mode == 'wb':
                return w
            return io.TextIOWrapper(_WriterAdapter(w), encoding=encoding or 'utf-8', errors=errors, newline=newline)
        if mode in ('rb', 'r'):
            fh = _fs.open_read(self.bucket.name, self.name)
            return fh if mode == 'rb' else io.TextIOWrapper(fh, encoding=encoding or 'utf-8', errors=errors,
                                                            newline=newline)
        unsupported(f'Blob.open(mode={mode!r})')

    def upload_from_string(self, data, content_type='text/plain', client=None, predefined_acl=None, **kwargs):
        if isinstance(data, str):
            data = data.encode('utf-8')
        _fs.write_bytes(self.bucket.name, self.name, data, content_type, predefined_acl)

    def upload_from_file(self, file_obj, rewind=False, size=None, content_type=None, client=None,
                         predefined_acl=None, **kwargs):
        if rewind:
            file_obj.seek(0)
        data = file_obj.read() if size is None else file_obj.read(size)
        _fs.write_bytes(self.bucket.name, self.name, data, content_type or self.content_type, predefined_acl)

    def upload_from_filename(self, filename, content_type=None, client=None, predefined_acl=None, **kwargs):
        _fs.write_file(self.bucket.name, self.name, filename, content_type or self.content_type, predefined_acl)

    def download_as_bytes(self, client=None, start=None, end=None, raw_download=False, **kwargs):
        data = _fs.read_bytes(self.bucket.name, self.name)
        if start is not None or end is not None:
            data = data[start or 0:(end + 1) if end is not None else None]
        return data

    download_as_string = download_as_bytes

    def download_as_text(self, client=None, start=None, end=None, encoding=None, **kwargs):
        return self.download_as_bytes(start=start, end=end).decode(encoding or 'utf-8')

    def download_to_filename(self, filename, client=None, **kwargs):
        with open(filename, 'wb') as fh:
            fh.write(_fs.read_bytes(self.bucket.name, self.name))

    def download_to_file(self, file_obj, client=None, **kwargs):
        file_obj.write(_fs.read_bytes(self.bucket.name, self.name))

    def delete(self, client=None, timeout=None, **kwargs):
        _fs.delete(self.bucket.name, self.name)

    def generate_signed_url(self, expiration=None, api_access_endpoint=None, method='GET', content_md5=None,
                            content_type=None, response_disposition=None, response_type=None, generation=None,
                            headers=None, query_parameters=None, client=None, credentials=None, version=None,
                            service_account_email=None, access_token=None, virtual_hosted_style=False,
                            bucket_bound_hostname=None, scheme='http'):
        """GCS would return a URL on Google's storage host, signed for `expiration`. The replica returns the
        object's same-origin path; Caddy's basic auth guards it (no per-URL signature, no expiry)."""
        if (method or 'GET').upper() != 'GET':
            unsupported(f'generate_signed_url(method={method!r})')
        if api_access_endpoint or bucket_bound_hostname or virtual_hosted_style:
            unsupported('generate_signed_url with a custom endpoint')
        return self.public_url

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'storage.Blob.{name}')

    def __repr__(self):
        return f'<Blob: {self.bucket.name}, {self.name}>'


class _WriterAdapter(io.RawIOBase):
    """Lets io.TextIOWrapper sit on an AtomicWriter (text-mode blob.open('w'))."""

    def __init__(self, w):
        super().__init__()
        self._w = w

    def writable(self):
        return True

    def write(self, b):
        return self._w.write(bytes(b))

    def close(self):
        if not self.closed:
            self._w.close()
        super().close()
