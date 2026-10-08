"""Stand-in for google.cloud.scheduler (siarnaq imports `google.cloud.scheduler as scheduler`): create_job,
update_job and delete_job record the job in $GALAXY_HOME/spool/scheduler/<job>.json. Nothing runs it unless the
operator enables bc23-galaxy-scheduler.timer, which fires recorded jobs whose cron schedule matches the current
minute (tools/galaxy/relay.py fire-jobs; docs/galaxy/README.md).

siarnaq (episodes/signals.py update_autoscrim_schedule) builds Job(name=, description=, http_target=HttpTarget(
uri=, http_method=POST, headers=, body=, oidc_token=OidcToken(service_account_email=)), schedule=, time_zone=) and
calls CloudSchedulerClient(credentials=).create_job(request=dict(parent=, job=)), update_job(request=dict(job=))
and delete_job(request=dict(name=)).
"""
import base64
import datetime
import os

from google._standin import missing, unsupported
from google.cloud._http_types import HttpMethod, OidcToken, _Message, coerce, method_name  # noqa: F401
from replica_gcp import cron, fsutil, spool

__getattr__ = missing(__name__)


class HttpTarget(_Message):
    _fields = ('uri', 'http_method', 'headers', 'body', 'oidc_token', 'oauth_token')

    def __init__(self, mapping=None, **kwargs):
        super().__init__(mapping, **kwargs)
        if self.oauth_token is not None:
            unsupported('scheduler.HttpTarget(oauth_token=...)')
        self.oidc_token = coerce(OidcToken, self.oidc_token)
        self.headers = dict(self.headers or {})
        self.body = self.body or b''
        self.http_method = HttpMethod(self.http_method if self.http_method is not None else HttpMethod.POST)


class Job(_Message):
    _fields = ('name', 'description', 'http_target', 'pubsub_target', 'app_engine_http_target', 'schedule',
               'time_zone', 'retry_config', 'attempt_deadline', 'state')

    def __init__(self, mapping=None, **kwargs):
        super().__init__(mapping, **kwargs)
        if self.pubsub_target is not None or self.app_engine_http_target is not None:
            unsupported('scheduler.Job with a Pub/Sub or App Engine target')
        self.http_target = coerce(HttpTarget, self.http_target)


def _job_id(name):
    return spool.resource_id(name, 'jobs')


def _record(job):
    job = coerce(Job, job)
    if job is None or job.http_target is None or not job.name:
        raise ValueError('scheduler: a named job with an HTTP target is required')
    cron.parse(job.schedule)        # Cloud Scheduler rejects an invalid schedule
    ht = job.http_target
    body = ht.body if isinstance(ht.body, bytes) else str(ht.body).encode()
    rec = {'name': job.name, 'description': job.description or '', 'schedule': job.schedule,
           'time_zone': job.time_zone or 'Etc/UTC',
           'http_target': {'uri': ht.uri, 'http_method': method_name(ht.http_method), 'headers': ht.headers,
                           'body': base64.b64encode(body).decode(),
                           'oidc_token': ({'service_account_email': ht.oidc_token.service_account_email,
                                           'audience': ht.oidc_token.audience} if ht.oidc_token else None)},
           'updated': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    os.makedirs(spool.scheduler_dir(), exist_ok=True)
    fsutil.atomic_write_json(spool.job_path(_job_id(job.name)), rec)
    return job


def _request(request, allowed):
    if not isinstance(request, dict):
        unsupported('CloudSchedulerClient request that is not a dict')
    unknown = set(request) - set(allowed)
    if unknown:
        unsupported(f'CloudSchedulerClient request fields {sorted(unknown)}')
    return request


class CloudSchedulerClient:
    def __init__(self, credentials=None, transport=None, client_options=None, client_info=None, **kwargs):
        if transport is not None:
            unsupported('CloudSchedulerClient(transport=...)')

    @staticmethod
    def job_path(project, location, job):
        return f'projects/{project}/locations/{location}/jobs/{job}'

    def create_job(self, request=None, *, parent=None, job=None, retry=None, timeout=None, metadata=()):
        if request is not None:
            r = _request(request, ('parent', 'job'))
            parent, job = r.get('parent'), r.get('job')
        job = coerce(Job, job)
        if parent is None or not job.name.startswith(parent + '/jobs/'):
            raise ValueError('scheduler: job name must be <parent>/jobs/<id>')
        return _record(job)

    def update_job(self, request=None, *, job=None, update_mask=None, retry=None, timeout=None, metadata=()):
        if request is not None:
            job = _request(request, ('job', 'update_mask')).get('job')
        return _record(job)

    def delete_job(self, request=None, *, name=None, retry=None, timeout=None, metadata=()):
        if request is not None:
            name = _request(request, ('name',)).get('name')
        try:
            os.unlink(spool.job_path(_job_id(name)))
        except FileNotFoundError:
            pass

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'scheduler.CloudSchedulerClient.{name}')
