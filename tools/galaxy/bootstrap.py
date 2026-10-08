#!/usr/bin/env python3
"""Seed and inspect the replica's siarnaq database with siarnaq's own models (idempotent). Run as bcreplica with the
services' environment, i.e. through the wrapper:  bc23-galaxy-manage bootstrap <command>

  owner            superuser "owner"; the password is read from stdin (one line), never from the command line
  episode          episode bc23 (Battlecode 2023, java8, battlecode23 3.0.15) and its public maps (tools/maps.txt)
  service-user     the staff user siarnaq's GoogleCloudAuthentication maps saturn/Cloud Tasks callers to
  all              episode + service-user + owner (password on stdin)
  status           episode, map count, users, teams, submissions and matches by status (no secrets)
  audit            every host name or e-mail domain in the running settings and in the episode/user records;
                   anything that is not this site, localhost or a reserved .invalid name is listed as external
  purge-teams P    delete teams whose name starts with P, their members whose username starts with P, and
                   everything that references them (matches, requests, submissions, ratings, stored files)
Guide: docs/galaxy/README.md.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'replica_settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Replica')

import configurations  # noqa: E402

configurations.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402

from siarnaq.api.compete.models import Match, MatchParticipant, ScrimmageRequest, Submission  # noqa: E402
from siarnaq.api.episodes.models import Episode, Language, Map  # noqa: E402
from siarnaq.api.teams.models import Rating, Team  # noqa: E402
from siarnaq.api.user.models import User  # noqa: E402

from replica_gcp import storage as rstorage  # noqa: E402

UTC = datetime.timezone.utc
EPISODE = {
    'name_short': 'bc23',
    'name_long': 'Battlecode 2023',
    'blurb': '',
    'registration': datetime.datetime(2022, 12, 1, 0, 0, tzinfo=UTC),
    'game_release': datetime.datetime(2023, 1, 9, 19, 0, tzinfo=UTC),
    'game_archive': datetime.datetime(2099, 12, 31, 0, 0, tzinfo=UTC),   # far future: ranked play stays open
    'submission_frozen': False,
    # galaxy's own schedule is disabled (null): a daily top-N autoscrim at 17:00 PDT replaces it
    # (tools/galaxy/autoscrim_top.py, operator crontab; owner, PROMPTS 29-30: fewer field-vs-field games)
    'autoscrim_schedule': None,
    'language': Language.JAVA_8,
    'scaffold': 'https://github.com/battlecode/battlecode23-scaffold',
    'artifact_name': 'battlecode23',
    'release_version_client': '3.0.15',
    'release_version_public': '3.0.15',
    'release_version_saturn': '3.0.15',
    'is_allowed_ranked_scrimmage': True,
    # galaxy's default is 10 and 10; an accepted request counts twice (the request and its match), so 10 meant 5
    # requests an hour. Raised at the owner's request (PROMPTS 15-16, 2026-10-07): the VM, not the rule, is the limit.
    'ranked_scrimmage_hourly_limit': 20,
    'unranked_scrimmage_hourly_limit': 40,
}


def read_maps(path=None):
    path = path or os.path.join(REPO, 'tools', 'maps.txt')
    with open(path) as fh:
        return [l.strip() for l in fh if l.strip() and not l.startswith('#')]


def cmd_episode(maps_file=None):
    maps = read_maps(maps_file)
    with transaction.atomic():
        ep = Episode.objects.filter(pk=EPISODE['name_short']).first()
        if ep is None:
            ep = Episode(**EPISODE)
            ep.save()           # pre_save signal: Cloud Scheduler stand-in records the autoscrim job
            print(f'created episode {ep.pk}')
        else:
            changed = [k for k, v in EPISODE.items() if getattr(ep, k) != v and k != 'name_short']
            for k in changed:
                setattr(ep, k, EPISODE[k])
            if changed:
                ep.save()
            print(f'episode {ep.pk}: ' + (f'updated {", ".join(changed)}' if changed else 'unchanged'))
        have = set(Map.objects.filter(episode=ep).values_list('name', flat=True))
        new = [Map(episode=ep, name=m, is_public=True) for m in maps if m not in have]
        Map.objects.bulk_create(new)
        Map.objects.filter(episode=ep, name__in=maps, is_public=False).update(is_public=True)
    print(f'maps: {len(new)} added, {Map.objects.filter(episode=ep, is_public=True).count()} public in {ep.pk}')


def cmd_admin_email():
    """Migration user/0002 creates the superuser "admin" with the official contact address; give it a reserved
    .invalid address instead (e-mail is off anyway)."""
    n = User.objects.filter(username='admin').exclude(email='admin@bc23-replica.invalid').update(
        email='admin@bc23-replica.invalid')
    print('migration superuser admin: e-mail ' + ('set to admin@bc23-replica.invalid' if n else 'already a placeholder'))


def cmd_service_user():
    # exactly what GoogleCloudAuthentication.authenticate does on the first internal call
    user, created = User.objects.get_or_create(username=settings.GALAXY_ADMIN_USERNAME, is_staff=True)
    if created:
        user.set_unusable_password()
        user.save()
    print(f'service user {user.username}: ' + ('created' if created else 'exists') + f' (staff={user.is_staff})')


def cmd_owner():
    pw = sys.stdin.readline().rstrip('\n')
    if len(pw) < 12:
        raise SystemExit('bootstrap owner: no password on stdin (pipe the password file into this command)')
    user = User.objects.filter(username='owner').first()
    if user is None:
        user = User.objects.create_superuser(username='owner', email='owner@bc23-replica.invalid', password=pw,
                                             first_name='Replica', last_name='Owner')
        user.profile.country = 'US'
        user.profile.gender = '?'
        user.profile.save()
        print('created superuser owner')
    else:
        user.set_password(pw)
        user.is_staff = user.is_superuser = True
        user.save()
        print('superuser owner: password reset to the owner password, staff + superuser')


def cmd_status():
    ep = Episode.objects.filter(pk='bc23').first()
    print('episode:', ep and f'{ep.pk} {ep.name_long!r} frozen={ep.frozen()} autoscrim={ep.autoscrim_schedule!r} '
          f'release={ep.release_version_public} maps={ep.maps.filter(is_public=True).count()}')
    print('users:', ', '.join(f'{u.username}{"(staff)" if u.is_staff else ""}' for u in User.objects.order_by('pk')))
    print('teams:', Team.objects.count(), ', '.join(Team.objects.order_by('pk').values_list('name', flat=True)[:20]))
    for model in (Submission, Match):
        counts = {}
        for s in model.objects.values_list('status', flat=True):
            counts[s] = counts.get(s, 0) + 1
        print(f'{model.__name__.lower()}s:', counts or 'none')


HOST_RE = re.compile(r'(?i)(?:[a-z][a-z0-9+.-]*://|@)([a-z0-9.-]+\.[a-z]{2,})')


def _hosts_in(value):
    return {h.lower().rstrip('.') for h in HOST_RE.findall(repr(value))}


def cmd_audit():
    """List every host in the running configuration; 'external' ones could make something leave this machine."""
    own = settings.ALLOWED_HOSTS[0]
    found = {}
    for k in dir(settings):
        if k.isupper():
            v = getattr(settings, k)
            hosts = _hosts_in(v)
            if k in ('ALLOWED_HOSTS',):
                hosts |= {h.lower() for h in v}
            for h in hosts:
                found.setdefault(h, set()).add(f'settings.{k}')
    for ep in Episode.objects.all():
        for f in ('scaffold', 'blurb', 'name_long'):
            for h in _hosts_in(getattr(ep, f)):
                found.setdefault(h, set()).add(f'episode {ep.pk}.{f}')
    for u in User.objects.filter(is_staff=True):
        for h in _hosts_in(u.email):
            found.setdefault(h, set()).add(f'user {u.username}.email')
    external = []
    for h in sorted(found):
        if h == own or h.endswith('.invalid') or h in ('localhost', '127.0.0.1'):
            kind = 'own     '
        elif h == 'github.com' and all(w.endswith('.scaffold') for w in found[h]):
            kind = 'link    '     # the episode's scaffold repository, shown to contestants; saturn never fetches it
        else:
            kind = 'external'
            external.append(h)
        print(f'{kind} {h}: {", ".join(sorted(found[h]))}')
    print('external hosts:', ' '.join(external) or 'none')
    import google.auth
    import google.cloud.pubsub
    import google.cloud.scheduler
    import google.cloud.secretmanager
    import google.cloud.storage
    import google.cloud.tasks_v2
    import google.oauth2.id_token
    mods = [google.auth, google.oauth2.id_token, google.cloud.storage, google.cloud.pubsub, google.cloud.tasks_v2,
            google.cloud.scheduler, google.cloud.secretmanager]
    standin = all(os.sep + os.path.join('tools', 'galaxy', 'standins', 'google') + os.sep in m.__file__ for m in mods)
    print(f'stand-ins: {standin} ({len(mods)} google modules)')
    print(f'actions: GCLOUD_ENABLE_ACTIONS={settings.GCLOUD_ENABLE_ACTIONS} EMAIL_ENABLED={settings.EMAIL_ENABLED} '
          f'EMAIL_BACKEND={settings.EMAIL_BACKEND} DEBUG={settings.DEBUG}')


def _delete_blob(bucket, name):
    try:
        rstorage.delete(bucket, name)
        return 1
    except rstorage.NotFound:
        return 0


def cmd_purge_teams(prefix):
    if len(prefix) < 3:
        raise SystemExit('purge-teams: prefix must have at least 3 characters')
    teams = list(Team.objects.filter(name__startswith=prefix))
    users = list(User.objects.filter(username__startswith=prefix, is_staff=False, is_superuser=False))
    if not teams and not users:
        print(f'nothing starts with {prefix!r}')
        return
    blobs = []
    with transaction.atomic():
        matches = list(Match.objects.filter(participants__team__in=teams).distinct())
        others = MatchParticipant.objects.filter(match__in=matches).exclude(team__in=teams)
        if others.exists():
            raise SystemExit('purge-teams: refusing, some matches also involve other teams: '
                             + ', '.join(sorted({p.team.name for p in others})))
        sec, pub = settings.GCLOUD_BUCKET_SECURE, settings.GCLOUD_BUCKET_PUBLIC
        blobs += [(sec, m.get_replay_path()) for m in matches]
        rating_ids = set(MatchParticipant.objects.filter(match__in=matches).exclude(rating=None)
                         .values_list('rating_id', flat=True))
        MatchParticipant.objects.filter(match__in=matches).update(previous_participation=None)
        Match.objects.filter(pk__in=[m.pk for m in matches]).delete()
        ScrimmageRequest.objects.filter(requested_by__in=teams).delete()
        ScrimmageRequest.objects.filter(requested_to__in=teams).delete()
        for s in Submission.objects.filter(team__in=teams):
            blobs += [(sec, s.get_source_path()), (sec, s.get_binary_path())]
        Submission.objects.filter(team__in=teams).delete()
        for t in teams:
            prof = getattr(t, 'profile', None)
            if prof is not None and prof.pk:
                rating_ids.add(prof.rating_id)
                blobs += [(pub, f'team/{t.pk}/avatar.png'), (sec, prof.get_report_path())]
                prof.delete()
            t.delete()
        Rating.objects.filter(pk__in=rating_ids).delete()
        for u in users:
            prof = getattr(u, 'profile', None)
            if prof is not None and prof.pk:
                blobs += [(pub, f'user/{u.pk}/avatar.png'), (sec, prof.get_resume_path())]
                prof.delete()
            u.delete()
    files = sum(_delete_blob(b, n) for b, n in blobs)   # after the commit
    print(f'purged {len(teams)} team(s), {len(users)} user(s), {len(matches)} match(es), {files} stored file(s)')


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = argv[0]
    if cmd == 'episode':
        cmd_episode(argv[1] if len(argv) > 1 else None)
    elif cmd == 'service-user':
        cmd_service_user()
    elif cmd == 'owner':
        cmd_owner()
    elif cmd == 'all':
        cmd_episode()
        cmd_admin_email()
        cmd_service_user()
        cmd_owner()
    elif cmd == 'status':
        cmd_status()
    elif cmd == 'audit':
        cmd_audit()
    elif cmd == 'purge-teams' and len(argv) == 2:
        cmd_purge_teams(argv[1])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
