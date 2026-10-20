#!/usr/bin/env python3
"""Assemble a run of a panel's cells from finished runs that already played them (owner, PROMPTS 137-138: panel v3
mixes sides per line, and every v3 line is a v2 line ('+') or a v2b line ('-'), so the validated build's v3 controls
are its v2 and v2b games regrouped, with no new games). A cells line is taken whole from the source run whose own
cells file has the same opponent, the same map set and the same order; that opponent's results.csv and census.csv
rows, its requests.jsonl line and its replays are copied. The output is named without '-panel' so tools that glob
gauntlet/*-panel* (elo.py, attempts.py, sa_extract.py, causal_dag.py) never count the same games twice.
   tools/compose_run.py CELLS --from RUN [RUN...] --out gauntlet/<stamp>-ctl3-<package>"""
import argparse, csv, json, os, shutil, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools'))
import contest


def prov(run):
    """key=value pairs of a run's provenance.txt (the last value wins)."""
    with open(os.path.join(run, 'provenance.txt')) as fh:
        return dict(w.split('=', 1) for w in fh.read().split() if '=' in w)


def rows(path, key, value):
    if not os.path.exists(path):
        return [], None
    with open(path, newline='') as fh:
        r = csv.DictReader(fh)
        return [x for x in r if x.get(key) == value], r.fieldnames


def compose(cells, sources, out, repo=REPO):
    """Write the run `out` for `cells` from `sources`; raise ValueError when a line has no source or the sources
    played different packages."""
    want = contest.read_cells(cells if os.path.isabs(cells) else os.path.join(repo, cells))
    lines = {}
    pkgs = set()
    for run in sources:
        p = prov(run)
        if p.get('incomplete', '0') != '0':
            raise ValueError(f'{run} is incomplete')
        pkgs.add(p.get('package'))
        src = p['cells'] if os.path.isabs(p['cells']) else os.path.join(repo, p['cells'])
        for opp, maps, order in contest.read_cells(src):
            lines.setdefault((opp, frozenset(maps), order), run)
    if len(pkgs) != 1:
        raise ValueError(f'sources played {sorted(map(str, pkgs))}, not one package')
    os.makedirs(os.path.join(out, 'replays'))
    res, cen, req, fields = [], [], [], {}
    for opp, maps, order in want:
        run = lines.get((opp, frozenset(maps), order))
        if not run:
            raise ValueError(f'no source run played {opp} {order} on {",".join(maps)}')
        r, fields['results'] = rows(os.path.join(run, 'results.csv'), 'opponent', opp)
        if len(r) != len(maps):
            raise ValueError(f'{run}: {len(r)} games against {opp}, not {len(maps)}')
        res += r
        c, f = rows(os.path.join(run, 'census.csv'), 'cell_opponent', opp)
        cen += c
        fields['census'] = f or fields.get('census')
        with open(os.path.join(run, 'requests.jsonl')) as fh:
            req += [l for l in fh if json.loads(l).get('opponent') == opp]
        for m in sorted({x['match'] for x in r if x.get('match')}):
            f = os.path.join(run, 'replays', m + '.bc23')
            if os.path.exists(f):
                shutil.copy2(f, os.path.join(out, 'replays'))
    for name, data in (('results', res), ('census', cen)):
        if fields.get(name):
            with open(os.path.join(out, name + '.csv'), 'w', newline='') as fh:
                w = csv.DictWriter(fh, fieldnames=fields[name])
                w.writeheader()
                w.writerows(data)
    with open(os.path.join(out, 'requests.jsonl'), 'w') as fh:
        fh.writelines(req)
    first = prov(sources[0])
    keep = ' '.join(f'{k}={first[k]}' for k in ('team', 'team_id', 'site') if k in first)
    rel = os.path.relpath(os.path.abspath(cells), repo) if os.path.isabs(cells) else cells
    with open(os.path.join(out, 'provenance.txt'), 'w') as fh:
        fh.write(f'{keep} cells={rel} package={pkgs.pop()} composed_from='
                 + ','.join(os.path.relpath(os.path.abspath(s), repo) for s in sources) + '\n')
        fh.write('incomplete=0 unresolved_requests=-\n')
    return len(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cells')
    ap.add_argument('--from', dest='sources', nargs='+', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    if '-panel' in os.path.basename(a.out.rstrip('/')):
        sys.exit('the output name must not contain -panel (tools glob gauntlet/*-panel* and would count games twice)')
    if os.path.exists(a.out):
        sys.exit(f'{a.out} exists')
    try:
        n = compose(a.cells, a.sources, a.out)
    except ValueError as e:
        shutil.rmtree(a.out, ignore_errors=True)
        sys.exit(str(e))
    print(f'{a.out}: {n} games composed for {a.cells}')


if __name__ == '__main__':
    main()
