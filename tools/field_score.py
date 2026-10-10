#!/usr/bin/env python3
"""Field-score charts (owner, PROMPTS 39: "like in the previous year"; the design of bc20/bc24's field-score-1w/-4w
and progress.png, rebuilt here from their descriptions in the read room).

Every build of ours that played on the ladder is placed at its submission time (tools/ladder_policy.py history in
progress/ladder-state.json: a candidate's trial-start, the first validated build's init), with four panels:
  rating      the batch Bradley-Terry fit of progress/games.csv (tools/elolib.py), +- 95%
  field score expected score against every rated ladder bot, one game each
  vs higher   the same against only the ladder bots rated above the build
  rank        1 + the ladder bots rated above it, of (rated bots + 1)
Submissions (accepted builds) are filled and joined; rejected candidates are hollow. Once three submissions span half a
day, their ratings are fitted with R0 + a ln(1 + t / 1 day) (t from the project's first prompt, weights 1/SE^2) and
projected to the end of week 1 and of week 4 with a 95% band, mapped to field score, vs higher and rank through the
same ladder fit. Times are PDT (owner, PROMPTS 28).
   tools/field_score.py      # writes progress/field-score-1w.png, progress/field-score-4w.png, progress/progress.png
"""
import datetime, json, math, os, sys
# the charts need matplotlib, which lives in tools/.venv: re-exec there when it exists
_venv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
if os.path.exists(_venv) and '.venv' not in sys.prefix and __name__ == '__main__': os.execv(_venv, [_venv] + sys.argv)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import elolib

PDT = None
try:
    from zoneinfo import ZoneInfo
    PDT = ZoneInfo('America/Los_Angeles')
except Exception:
    PDT = datetime.timezone(datetime.timedelta(hours=-7))
START = datetime.datetime(2026, 10, 7, 7, 45, tzinfo=PDT)   # PROMPTS.md prompt 1
DAY = 86400.0
EXCLUDE = {'examplefuncsplayer'}                              # a sanity opponent, not a build


def fit_log(ts, rs, ses):
    """Weighted least squares of r = R0 + a ln(1 + t) (t in days). Returns (R0, a, cov 2x2) or None."""
    if len(ts) < 3:
        return None
    w = [1.0 / (s * s) if s > 0 else 1.0 for s in ses]
    x = [math.log(1.0 + t) for t in ts]
    S = sum(w); Sx = sum(wi * xi for wi, xi in zip(w, x)); Sxx = sum(wi * xi * xi for wi, xi in zip(w, x))
    Sy = sum(wi * yi for wi, yi in zip(w, rs)); Sxy = sum(wi * xi * yi for wi, xi, yi in zip(w, x, rs))
    det = S * Sxx - Sx * Sx
    if det <= 0:
        return None
    a = (S * Sxy - Sx * Sy) / det
    r0 = (Sy * Sxx - Sx * Sxy) / det
    # residual scale (reduced chi-square, at least 1) inflates the parameter covariance
    chi = sum(wi * (yi - r0 - a * xi) ** 2 for wi, xi, yi in zip(w, x, rs))
    scale = max(1.0, chi / (len(ts) - 2)) if len(ts) > 2 else 1.0
    cov = [[Sxx / det * scale, -Sx / det * scale], [-Sx / det * scale, S / det * scale]]
    return r0, a, cov


def predict(model, t):
    """(rating, 95% half-width) of the fitted curve at t days."""
    r0, a, cov = model
    x = math.log(1.0 + t)
    var = cov[0][0] + 2 * x * cov[0][1] + x * x * cov[1][1]
    return r0 + a * x, 1.96 * math.sqrt(max(var, 0.0))


def score_vs(r, bots_r):
    return sum(elolib.expected(r, b) for b in bots_r) / len(bots_r) if bots_r else 0.0


def metrics(r, bots_r):
    """(field score, vs higher, number above, rank) for a rating r against the rated bots' ratings."""
    up = [b for b in bots_r if b > r]
    return score_vs(r, bots_r), (score_vs(r, up) if up else float('nan')), len(up), 1 + len(up)


def submission_times():
    """package -> (UTC datetime of submission, accepted?) from the ladder policy history."""
    p = os.path.join(elolib.REPO, 'progress', 'ladder-state.json')
    with open(p) as fh:
        hist = json.load(fh).get('history', [])
    out = {}
    for h in hist:
        pk, ev = h.get('package'), h.get('event', '')
        if not pk:
            continue
        at = datetime.datetime.fromisoformat(h['at'].replace('Z', '+00:00'))
        if at.tzinfo is None:
            at = at.replace(tzinfo=datetime.timezone.utc)
        if ev in ('init', 'trial-start') and pk not in out:
            out[pk] = [at, ev == 'init']
        elif ev == 'accept' and pk in out:
            out[pk][1] = True
    return {k: (v[0], v[1]) for k, v in out.items()}


def main():
    rows = elolib.load()
    R, SE, games, _ = elolib.fit(rows)
    bots = [b for b in elolib.ladder_bots() if games[b] > 0]
    bots_r = [R[b] for b in bots]
    when = submission_times()
    builds = []
    for p in R:
        if not elolib.is_ours(p) or games[p] == 0:
            continue
        b = elolib.build_of(p)
        if b in EXCLUDE or b not in when:
            continue
        t_utc, acc = when[b]
        fs, vh, nup, rank = metrics(R[p], bots_r)
        builds.append(dict(build=b, t=t_utc.astimezone(PDT), days=(t_utc - START).total_seconds() / DAY, r=R[p],
                           se=SE[p], fs=fs, vh=vh, rank=rank, acc=acc, n=games[p]))
    builds.sort(key=lambda d: d['t'])
    subs = [d for d in builds if d['acc']]
    model = None
    if len(subs) >= 3 and subs[-1]['days'] - subs[0]['days'] >= 0.5:
        model = fit_log([max(d['days'], 0.0) for d in subs], [d['r'] for d in subs], [d['se'] for d in subs])

    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt, matplotlib.dates as mdates
    nb = len(bots_r) + 1
    for tag, weeks in (('1w', 1), ('4w', 4)):
        end = START + datetime.timedelta(days=7 * weeks)
        fig, ax = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
        for d in builds:
            kw = dict(color='tab:blue', ms=6) if d['acc'] else dict(color='0.55', ms=5, mfc='white')
            ax[0].errorbar(d['t'], d['r'], yerr=1.96 * d['se'], fmt='o', capsize=2, **kw)
            ax[1].plot(d['t'], 100 * d['fs'], 'o', **kw)
            if not math.isnan(d['vh']):
                ax[2].plot(d['t'], 100 * d['vh'], 'o', **kw)
            ax[3].plot(d['t'], d['rank'], 'o', **kw)
        for i, key, f in ((0, 'r', 1), (1, 'fs', 100), (2, 'vh', 100), (3, 'rank', 1)):
            ax[i].plot([d['t'] for d in subs], [f * d[key] for d in subs], '-', color='tab:blue', lw=1, alpha=0.6)
        for d in subs:
            ax[0].annotate(d['build'], (d['t'], d['r']), textcoords='offset points', xytext=(4, 6), fontsize=7)
        if model:
            n = 120
            t0 = max(subs[0]['days'], 0.0)
            t1 = (end - START).total_seconds() / DAY
            ts = [t0 + (t1 - t0) * k / (n - 1) for k in range(n)]
            xs = [START + datetime.timedelta(days=t) for t in ts]
            pr = [predict(model, t) for t in ts]
            mid = [p[0] for p in pr]; lo = [p[0] - p[1] for p in pr]; hi = [p[0] + p[1] for p in pr]
            ax[0].plot(xs, mid, '--', color='tab:orange', lw=1.2, label='submissions: R0 + a ln(1 + t/1d), 95% band')
            ax[0].fill_between(xs, lo, hi, color='tab:orange', alpha=0.15)
            for i, j in ((1, 0), (2, 1), (3, 3)):
                f = 1 if j == 3 else 100
                m = [metrics(r, bots_r)[j] for r in mid]
                l_ = [metrics(r, bots_r)[j] for r in lo]
                h_ = [metrics(r, bots_r)[j] for r in hi]
                ax[i].plot(xs, [f * v for v in m], '--', color='tab:orange', lw=1.2)
                ax[i].fill_between(xs, [f * v for v in l_], [f * v for v in h_], color='tab:orange', alpha=0.15)
            pe, pw = predict(model, t1)
            fs_e, vh_e, _, rk_e = metrics(pe, bots_r)
            ax[1].annotate(f"{end:%b %d}: {100 * fs_e:.1f}% [{100 * metrics(pe - pw, bots_r)[0]:.1f}, "
                           f"{100 * metrics(pe + pw, bots_r)[0]:.1f}]", (end, 100 * fs_e), textcoords='offset points',
                           xytext=(-150, 8), fontsize=8, color='tab:orange')
            ax[3].annotate(f"rank {rk_e} of {nb}", (end, rk_e), textcoords='offset points', xytext=(-70, -12),
                           fontsize=8, color='tab:orange')
            ax[0].legend(loc='lower right', fontsize=8)
        ax[0].set_ylabel('rating (BT, Elo scale)'); ax[1].set_ylabel('field score %'); ax[2].set_ylabel('vs higher %')
        ax[3].set_ylabel(f'rank of {nb}'); ax[3].invert_yaxis()
        for a_ in ax:
            a_.grid(alpha=0.3)
            a_.axvline(START + datetime.timedelta(days=7), color='0.7', lw=0.8, ls=':')
        ax[3].set_xlim(START, end)
        ax[3].xaxis.set_major_formatter(mdates.DateFormatter('%b %d', tz=PDT))
        ax[3].set_xlabel('PDT')
        head = (f"Field score: {len(builds)} builds ({len(subs)} submissions filled, candidates hollow), "
                f"{len(bots_r)} rated ladder bots; projection to the end of week {weeks} ({end:%b %d})")
        fig.suptitle(head, fontsize=10)
        fig.tight_layout(rect=(0, 0, 1, 0.97))
        fig.savefig(os.path.join(elolib.REPO, 'progress', f'field-score-{tag}.png'), dpi=110)
        plt.close(fig)

    # progress.png: accepted builds only, rating and field score in submission order
    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    xs = list(range(len(subs)))
    ax[0].errorbar(xs, [d['r'] for d in subs], yerr=[1.96 * d['se'] for d in subs], fmt='o-', capsize=3)
    ax[1].plot(xs, [100 * d['fs'] for d in subs], 'o-', label='field score')
    ax[1].plot(xs, [100 * d['vh'] for d in subs], 's--', label='vs higher')
    for x, d in zip(xs, subs):
        ax[1].annotate(f"{100 * d['fs']:.1f}%", (x, 100 * d['fs']), textcoords='offset points', xytext=(0, 6),
                       ha='center', fontsize=8)
    ax[1].set_xticks(xs); ax[1].set_xticklabels([f"{d['build']}\n{d['t']:%m-%d %H:%M}" for d in subs], fontsize=7)
    ax[0].set_ylabel('rating (BT, Elo scale)'); ax[1].set_ylabel('%'); ax[1].legend(fontsize=8)
    for a_ in ax: a_.grid(alpha=0.3)
    fig.suptitle('Accepted builds (submission time, PDT)', fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(elolib.REPO, 'progress', 'progress.png'), dpi=110)
    plt.close(fig)
    if model:
        for tag, weeks in (('1w', 1), ('4w', 4)):
            t1 = (START + datetime.timedelta(days=7 * weeks) - START).total_seconds() / DAY
            pe, pw = predict(model, t1)
            print(f"projection end of week {weeks}: rating {pe:.0f} +- {pw:.0f}, field score {100 * metrics(pe, bots_r)[0]:.1f}%, "
                  f"rank {metrics(pe, bots_r)[3]} of {nb}")
    last = subs[-1] if subs else None
    if last:
        print(f"latest submission {last['build']}: rating {last['r']:.0f} +- {1.96 * last['se']:.0f}, field score "
              f"{100 * last['fs']:.1f}%, vs higher {100 * last['vh']:.1f}%, rank {last['rank']} of {nb}")


if __name__ == '__main__':
    main()
