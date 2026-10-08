"""Stand-in for google.auth.impersonated_credentials (titan.get_object builds one before signing a URL; the
storage stand-in's generate_signed_url ignores it)."""
from google._standin import missing
from google.auth import credentials

__getattr__ = missing(__name__)


class Credentials(credentials.Credentials):
    def __init__(self, source_credentials=None, target_principal=None, target_scopes=None, delegates=None,
                 lifetime=3600, quota_project_id=None, iam_endpoint_override=None, **kwargs):
        super().__init__()
        self.source_credentials, self.target_principal = source_credentials, target_principal
        self.target_scopes, self.lifetime = target_scopes, lifetime

    @property
    def service_account_email(self):
        return self.target_principal

    def sign_bytes(self, message):
        raise NotImplementedError('bc23 replica: no IAM signBlob; the storage stand-in needs no signature')
