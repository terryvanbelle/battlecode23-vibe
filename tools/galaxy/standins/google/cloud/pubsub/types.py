"""Stand-in for google.cloud.pubsub.types (only PublisherOptions)."""
from google._standin import missing

__getattr__ = missing(__name__)


class PublisherOptions:
    def __init__(self, enable_message_ordering=False, flow_control=None, retry=None, timeout=None):
        self.enable_message_ordering = bool(enable_message_ordering)
        self.flow_control, self.retry, self.timeout = flow_control, retry, timeout
