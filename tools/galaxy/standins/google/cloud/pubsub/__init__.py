"""Stand-in for google.cloud.pubsub (publisher side): every published message becomes one JSON file in the
topic's spool directory ($GALAXY_HOME/spool/pubsub/<topic>/ready/), written atomically; the saturn replacement
(tools/galaxy/saturn.py) is the subscriber.

siarnaq (gcloud/saturn.py, compete/managers.py) calls PublisherClient(credentials=, publisher_options=
types.PublisherOptions(enable_message_ordering=True), client_options={"api_endpoint": ...}), topic_path(), publish(
topic=, data=, ordering_key=) -> future.result() = message id, and resume_publish(). The api_endpoint is ignored:
nothing leaves the host. The ordering key is stored with the message; ids sort by publish time.
"""
import base64
import datetime
import threading
from concurrent.futures import Future

from google._standin import missing, unsupported
from google.cloud.pubsub import types  # noqa: F401
from replica_gcp import spool

__getattr__ = missing(__name__)


class PublisherClient:
    def __init__(self, batch_settings=(), publisher_options=(), credentials=None, client_options=None, **kwargs):
        opts = publisher_options if isinstance(publisher_options, types.PublisherOptions) else types.PublisherOptions()
        self.publisher_options = opts
        self._paused = set()
        self._lock = threading.Lock()

    @staticmethod
    def topic_path(project, topic):
        return f'projects/{project}/topics/{topic}'

    def publish(self, topic, data, ordering_key='', retry=None, timeout=None, **attrs):
        if not isinstance(data, bytes):
            raise TypeError('Data being published to Pub/Sub must be sent as a bytestring.')
        if ordering_key and not self.publisher_options.enable_message_ordering:
            raise ValueError('Cannot publish a message with an ordering key when message ordering is not enabled.')
        for k, v in attrs.items():
            if not isinstance(v, str):
                raise TypeError('All attributes being published to Pub/Sub must be sent as text strings.')
        future = Future()
        try:
            topic_id = spool.resource_id(topic, 'topics')
            with self._lock:
                if ordering_key and (topic_id, ordering_key) in self._paused:
                    raise RuntimeError(f'ordering key {ordering_key!r} is paused after an error; call resume_publish')
            q = spool.topic_queue(topic_id).ensure()
            msg_id = spool.new_id()
            q.put({'message_id': msg_id, 'topic': topic, 'ordering_key': ordering_key or '',
                   'attributes': dict(attrs), 'data': base64.b64encode(data).decode(),
                   'publish_time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   'delivery_attempt': 0}, msg_id)
            future.set_result(msg_id)
        except Exception as e:  # the client reports publish errors through the future
            if ordering_key:
                with self._lock:
                    try:
                        self._paused.add((spool.resource_id(topic, 'topics'), ordering_key))
                    except ValueError:
                        pass
            future.set_exception(e)
        return future

    def resume_publish(self, topic, ordering_key):
        with self._lock:
            try:
                self._paused.discard((spool.resource_id(topic, 'topics'), ordering_key))
            except ValueError:
                pass

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        unsupported(f'pubsub.PublisherClient.{name}')


class SubscriberClient:
    def __init__(self, *args, **kwargs):
        unsupported('pubsub.SubscriberClient (the subscriber is tools/galaxy/saturn.py)')
