"""Local back end of the bc23 galaxy replica's Google Cloud stand-ins (standard library only).

siarnaq (galaxy f343088) runs unmodified with GCLOUD_ENABLE_ACTIONS=True. Every Google Cloud client it imports is
shadowed by a stand-in package under tools/galaxy/standins/google/, and those stand-ins keep their state here, on the
local disk of battlecode-dev. Nothing in this package opens a network connection except tokens' callers on loopback.

  config    paths, bucket/topic/queue names, service-account e-mails, the site host name
  fsutil    atomic file writes, safe path joins
  storage   Cloud Storage buckets as directories (objects + metadata sidecars)
  spool     Pub/Sub topics, Cloud Tasks queues and Cloud Scheduler jobs as spool directories (JSON files)
  tokens    OIDC-like ID tokens: HMAC-SHA256 with a key generated on the VM (stand-in for Google-signed tokens)
  cron      5-field cron matching for the recorded Cloud Scheduler jobs
  mail      an e-mail backend that never sends anything

Guide: docs/galaxy/README.md.
"""
