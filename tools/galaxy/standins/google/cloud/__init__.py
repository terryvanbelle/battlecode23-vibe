"""Stand-in for google.cloud: storage, pubsub, tasks_v2, scheduler (and scheduler_v1), secretmanager."""
from google._standin import missing

__getattr__ = missing(__name__)
