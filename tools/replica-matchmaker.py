#!/usr/bin/env python3
"""Keep the ladder replica busy the way the owner asked (PROMPTS 1): our current build challenges bots slightly better
and slightly worse than itself to ranked scrimmages; in the spare cycles random ladder bots do the same.

    python3 tools/replica-matchmaker.py [--target 6] [--ours 0.5] [--band 3] [--once]

Every --interval seconds: if fewer than --target matches are queued or running, file one ranked scrimmage request
(best of 3 on random public maps, shuffled order, as galaxy's ranked requests): with probability --ours the
challenger is our incumbent (tools/incumbent.txt, e.g. us:g_iter0), else a random field team; the opponent is drawn
from the --band teams ranked just above and the --band just below the challenger (by rating mean, as galaxy's
autoscrim orders teams). Requests go through the `bc23-replica` wrapper (runs as the locked-down user); the DB is read
read-only. Writes nothing else. Stop it by killing its process id."""
import argparse, os, random, sqlite3, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.environ.get('REPLICA_DB', '/home/bcreplica/replica/replica.db')


def ladder(conn):
    q = ("SELECT t.name, r.mean FROM team t JOIN rating r ON r.id = t.rating_id WHERE t.status = 'R' "
         "ORDER BY r.mean DESC, t.name")
    return [(n, m) for n, m in conn.execute(q)]


def busy(conn):
    return conn.execute("SELECT COUNT(*) FROM match WHERE status IN ('NEW','QUE','RUN','TRY')").fetchone()[0]


def pick(teams, challenger, band, rnd):
    names = [n for n, _ in teams]
    if challenger not in names:
        return None
    i = names.index(challenger)
    near = [names[j] for j in range(max(0, i - band), min(len(names), i + band + 1)) if j != i]
    return rnd.choice(near) if near else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', type=int, default=6)
    ap.add_argument('--ours', type=float, default=0.5)
    ap.add_argument('--band', type=int, default=3)
    ap.add_argument('--interval', type=int, default=30)
    ap.add_argument('--once', action='store_true')
    a = ap.parse_args()
    rnd = random.Random()
    while True:
        try:
            conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True, timeout=30)
            n = busy(conn)
            teams = ladder(conn)
            conn.close()
            inc = open(os.path.join(REPO, 'tools', 'incumbent.txt')).read().split()[0] \
                if os.path.exists(os.path.join(REPO, 'tools', 'incumbent.txt')) else ''
            for _ in range(max(0, a.target - n)):
                if inc and rnd.random() < a.ours:
                    by = inc
                else:
                    field = [t for t, _ in teams if not t.startswith('us:')]
                    by = rnd.choice(field) if field else None
                to = pick(teams, by, a.band, rnd) if by else None
                if not to:
                    continue
                r = subprocess.run(['bc23-replica', 'request', by, to, '--ranked'], capture_output=True, text=True)
                print(time.strftime('%H:%M:%S'), 'request', by, 'vs', to, 'rc', r.returncode, (r.stdout + r.stderr).strip()[:120],
                      flush=True)
        except Exception as e:      # a busy DB or a failed request must not kill the loop
            print('error', e, flush=True)
        if a.once:
            return 0
        time.sleep(a.interval)


if __name__ == '__main__':
    sys.exit(main())
