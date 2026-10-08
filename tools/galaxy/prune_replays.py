# Replay retention for the galaxy replica (disk: the VM has 20 GB). Deletes the replay file of every FINISHED match
# (OK!, ERR, CAN) that our team did not play, created more than KEEP_HOURS ago. Its results are already in
# progress/games.csv (tools/galaxy/results.py), contestants cannot watch other teams' scrimmages, and our own
# matches' replays are always kept. Run inside siarnaq's Django context, as the replica user:
#   sudo -n bc23-galaxy-manage shell -c "exec(open('/home/terryvanbelle/projects/vibe/2023/tools/galaxy/prune_replays.py').read())"
# Installed in the operator's crontab on battlecode-dev every 6 hours at :30 (docs/galaxy/README.md).
import datetime
import os

from django.conf import settings
from django.utils import timezone
from siarnaq.api.compete.models import Match

KEEP_HOURS = 6     # results are exported every 2 hours (tools/galaxy/results.py); the VM disk is 20 GB
OURS = 'vibe23'
ROOT = os.environ.get('GALAXY_STORAGE_ROOT', '/srv/bc23-galaxy/storage')

cutoff = timezone.now() - datetime.timedelta(hours=KEEP_HOURS)
old = (Match.objects.filter(episode='bc23', status__in=['OK!', 'ERR', 'CAN'], created__lt=cutoff,
                            tournament_round__isnull=True)
       .exclude(participants__team__name=OURS))
n = freed = 0
for m in old.iterator():
    p = os.path.join(ROOT, settings.GCLOUD_BUCKET_SECURE, m.get_replay_path())
    if os.path.isfile(p):
        freed += os.path.getsize(p)
        os.remove(p)
        n += 1
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
print(stamp, f'prune-replays: {n} field-vs-field replays older than {KEEP_HOURS} h deleted, {freed / 1e6:.0f} MB freed')
