# Top-N autoscrim for the galaxy replica (owner, PROMPTS 29-30, 2026-10-08): galaxy's own autoscrim matchmaking
# (TeamQuerySet.autoscrim: 4-regular graph, shuffled sides, random maps, enqueued to saturn) run on a subset of teams,
# the N teams with the highest rating mean (galaxy's own autoscrim ordering), plus our team if it is outside them.
# Once the field's ordering was known, the owner asked for fewer field-vs-field games so that our candidates' games
# run sooner. Run inside siarnaq's Django context, as the replica user:
#   sudo -n bc23-galaxy-manage shell -c "exec(open('/home/terryvanbelle/projects/vibe/2023/tools/galaxy/autoscrim_top.py').read())"
# Installed as the operator's crontab entry on battlecode-dev, daily at 00:00 UTC = 17:00 PDT (docs/galaxy/README.md).
# Episode bc23's own autoscrim_schedule is null (disabled), so this is the only autoscrim.
import datetime

from siarnaq.api.episodes.models import Episode
from siarnaq.api.teams.models import Team

TOP_N = 24
OURS = 'vibe23'
BEST_OF = 3

ep = Episode.objects.get(pk='bc23')
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
if ep.frozen():
    print(stamp, 'autoscrim-top: episode frozen, no round')
else:
    pool = Team.objects.regular().with_active_submission().filter(episode=ep).order_by('-profile__rating__mean', 'pk')
    ids = list(pool.values_list('pk', flat=True)[:TOP_N])
    ours = pool.filter(name=OURS).values_list('pk', flat=True).first()
    if ours is not None and ours not in ids:
        ids.append(ours)
    Team.objects.filter(pk__in=ids).autoscrim(episode=ep, best_of=BEST_OF)
    names = list(Team.objects.filter(pk__in=ids).order_by('-profile__rating__mean').values_list('name', flat=True))
    print(stamp, f'autoscrim-top: {len(ids)} teams, best of {BEST_OF}:', ', '.join(names))
