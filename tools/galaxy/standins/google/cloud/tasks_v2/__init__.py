"""Stand-in for google.cloud.tasks_v2: create_task() writes the task to $GALAXY_HOME/spool/tasks/<queue>/ and the
relay (tools/galaxy/relay.py) delivers its HTTP request to siarnaq on 127.0.0.1 with a replica ID token for the
task's service account, retrying with Cloud Tasks' default backoff (docs/galaxy/README.md).

siarnaq (compete/models.py Match.request_rating_update, episodes/models.py request_publish_to_bracket) builds
Task(http_request=HttpRequest(http_method=POST, url=, oidc_token=OidcToken(service_account_email=))) and calls
CloudTasksClient().queue_path(project, location, queue) and create_task(request=dict(parent=, task=)).
"""
import base64
import datetime

from google._standin import missing, unsupported
from google.cloud._http_types import HttpMethod, OidcToken, _Message, coerce, method_name  # noqa: F401
from replica_gcp import spool

__getattr__ = missing(__name__)


class HttpRequest(_Message):
    _fields = ('url', 'http_method', 'headers', 'body', 'oidc_token', 'oauth_token')

    def __init__(self, mapping=None, **kwargs):
        super().__init__(mapping, **kwargs)
        if self.oauth_token is not None:
            unsupported('tasks_v2.HttpRequest(oauth_token=...)')
        self.oidc_token = coerce(OidcToken, self.oidc_token)
        self.headers = dict(self.headers or {})
        self.body = self.body or b''
        self.http_method = HttpMethod(self.http_method if self.http_method is not None else HttpMethod.POST)


class Task(_Message):
    _fields = ('name', 'http_request', 'app_engine_http_request', 'schedule_time', 'dispatch_deadline',
               'create_time', 'dispatch_count', 'response_count')

    def __init__(self, mapping=None, **kwargs):
        super().__init__(mapping, **kwargs)
        if self.app_engine_http_request is not None:
            unsupported('tasks_v2.Task(app_engine_http_request=...)')
        self.http_request = coerce(HttpRequest, self.http_request)


class CloudTasksClient:
    def __init__(self, credentials=None, transport=None, client_options=None, client_info=None, **kwargs):
        if transport is not None:
            unsupported('CloudTasksClient(transport=...)')

    @staticmethod
    def queue_path(project, location, queue):
        return f'projects/{project}/locations/{location}/queues/{queue}'

    @staticmethod
    def task_path(project, location, queue, task):
        return f'projects/{project}/locations/{location}/queues/{queue}/tasks/{task}'

    def create_task(self, request=None, *, parent=None, task=None, retry=None, timeout=None, metadata=()):
        if request is not None:
            if parent is not None or task is not None:
                raise ValueError('If the `request` argument is set, then none of the individual field arguments '
                                 'should be set.')
            if not isinstance(request, dict):
                unsupported('create_task(request=<non-dict>)')
            unknown = set(request) - {'parent', 'task', 'response_view'}
            if unknown:
                unsupported(f'create_task request fields {sorted(unknown)}')
            parent, task = request.get('parent'), request.get('task')
        task = coerce(Task, task)
        if task is None or task.http_request is None:
            raise ValueError('create_task: an HTTP task is required')
        if task.schedule_time is not None or task.name:
            unsupported('create_task with schedule_time or a task name')
        queue_id = spool.resource_id(parent, 'queues')
        hr = task.http_request
        q = spool.task_queue(queue_id).ensure()
        task_id = spool.new_id()
        name = f'{parent}/tasks/{task_id}'
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        body = hr.body if isinstance(hr.body, bytes) else str(hr.body).encode()
        q.put({'name': name, 'queue': parent, 'create_time': now,
               'http_request': {'url': hr.url, 'http_method': method_name(hr.http_method),
                                'headers': hr.headers, 'body': base64.b64encode(body).decode(),
                                'oidc_token': ({'service_account_email': hr.oidc_token.service_account_email,
                                                'audience': hr.oidc_token.audience}
                                               if hr.oidc_token is not None else None)},
               'dispatch_count': 0, 'response_count': 0, 'last_attempt': None}, task_id)
        return Task(name=name, http_request=hr, create_time=now, dispatch_count=0, response_count=0)

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'tasks_v2.CloudTasksClient.{name}')
