"""Stand-in for google.cloud.secretmanager: siarnaq's settings module imports it (Staging/Production read their
secrets from Secret Manager). The replica keeps its secrets in files on the VM; any use of this client raises."""
from google._standin import missing, unsupported

__getattr__ = missing(__name__)


class AccessSecretVersionRequest:
    def __init__(self, *args, **kwargs):
        unsupported('secretmanager.AccessSecretVersionRequest')


class SecretManagerServiceClient:
    def __init__(self, *args, **kwargs):
        unsupported('secretmanager.SecretManagerServiceClient (the replica has no Secret Manager)')
