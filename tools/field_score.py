#!/usr/bin/env python3
"""Field score over time, projected to the ends of the project's weeks (owner, PROMPTS 39: "like in the previous year";
ported from battlecode24-vibe's tools/field-score.py and tools/progress-chart.py, which PROMPTS 40 lets us read).
   tools/field_score.py [--tau 1.0]   -> progress/field-score-1w.png, progress/field-score-4w.png, progress/progress.png

The field score (a build's expected score against every rated ladder bot, one game each) is a bounded percentage that
compresses as it rises, so it is not fitted directly. The RATING is: R(t) = R0 + a * ln(1 + t / tau), a
diminishing-returns curve (tau in days, default 1, t from the first submission), weighted least squares over the
submissions (the accepted builds of progress/ladder-state.json) with weights 1 / SE^2, and a 95% band from the fit's
covariance. Deviation from bc24: the covariance is scaled by the reduced chi-square when that exceeds 1 (the
submissions' ratings scatter more than their standard errors, and with a handful of points the unscaled band is too
narrow). The fitted and projected ratings are mapped to field score, vs higher and rank through tools/elolib.py
against the current ladder ratings, so the projection stays inside 0-100 by construction. Every build is a point
dated by its submission (the trial-start of a candidate, the init of the first validated build); rejected candidates
are hollow and not fitted. Times are PDT (owner, PROMPTS 28)."""
import argparse, datetime as dt, json, math, os, sys
_venv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv', 'bin', 'python')
if os.path.exists(_venv) and '.venv' not in sys.prefix and __name__ == '__main__': os.execv(_venv, [_venv] + sys.argv)
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import elolib

PDT = ZoneInfo('America/Los_Angeles'); UTC = dt.timezone.utc
# the project began 2026-10-07 (PROMPTS.md prompt 1); the horizons are the ends of its weeks (bc24 PROMPTS 46, 79)
START = dt.datetime(2026, 10, 7)                                   # naive PDT
HORIZONS = [(f'week {k}', START + dt.timedelta(days=7 * k)) for k in (1, 2, 3, 4)]
MIN_GAMES = 30
EXCLUDE = elolib.BASELINES   # stock bots submitted as 'us:' (smoke tests), not builds of ours


def fit_log(ts, rs, ses, tau=1.0):
    """Weighted least squares r = R0 + a ln(1 + t / tau). Returns (R0, a, cov) or None (fewer than 3 points)."""
    if len(ts) < 3:
        return None
    w = [1.0 / (s * s) if s > 0 else 1.0 for s in ses]
    x = [math.log1p(t / tau) for t in ts]
    S = sum(w); Sx = sum(a * b for a, b in zip(w, x)); Sxx = sum(a * b * b for a, b in zip(w, x))
    Sy = sum(a * b for a, b in zip(w, rs)); Sxy = sum(a * b * c for a, b, c in zip(w, x, rs))
    det = S * Sxx - Sx * Sx
    if det <= 0:
        return None
    a = (S * Sxy - Sx * Sy) / det
    r0 = (Sy * Sxx - Sx * Sxy) / det
    chi = sum(wi * (yi - r0 - a * xi) ** 2 for wi, xi, yi in zip(w, x, rs))
    k = max(1.0, chi / (len(ts) - 2)) if len(ts) > 2 else 1.0
    return r0, a, [[Sxx / det * k, -Sx / det * k], [-Sx / det * k, S / det * k]]


def predict(model, t, tau=1.0):
    """(rating, 95% half-width) of the fitted curve at t days after the first submission."""
    r0, a, cov = model
    x = math.log1p(t / tau)
    return r0 + a * x, 1.96 * math.sqrt(max(cov[0][0] + 2 * x * cov[0][1] + x * x * cov[1][1], 0.0))


def metrics(r, bots_r):
    """(field score, vs higher, bots above, rank) of a rating r against the rated ladder bots' ratings."""
    up = [b for b in bots_r if b > r]
    fs = sum(elolib.expected(r, b) for b in bots_r) / len(bots_r) if bots_r else 0.0
    vh = sum(elolib.expected(r, b) for b in up) / len(up) if up else float('nan')
    return fs, vh, len(up), 1 + len(up)


def submissions():
    """package -> (naive PDT submission time, accepted?) from tools/ladder_policy.py's history."""
    with open(elolib.STATE) as fh:
        hist = json.load(fh).get('history', [])
    out = {}
    for h in hist:
        pk, ev = h.get('package'), h.get('event', '')
        if not pk:
            continue
        at = dt.datetime.fromisoformat(h['at'].replace('Z', '+00:00'))
        at = (at if at.tzinfo else at.replace(tzinfo=UTC)).astimezone(PDT).replace(tzinfo=None)
        if ev in ('init', 'trial-start') and pk not in out:
            out[pk] = [at, ev == 'init']
        elif ev == 'accept' and pk in out:
            out[pk][1] = True
    return {k: tuple(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--tau', type=float, default=1.0)
    ap.add_argument('--outdir', default=os.path.join(elolib.REPO, 'progress')); o = ap.parse_args()
    import numpy as np
    rows = elolib.load(); R, SE, games, _ = elolib.fit(rows)
    rated = [b for b in elolib.ladder_bots() if games.get(b, 0) > 0]
    bots_r = [R[b] for b in rated]
    when = submissions()
    pts = sorted((when[elolib.build_of(p)][0], p) for p in R
                 if elolib.is_ours(p) and elolib.build_of(p) in when and elolib.build_of(p) not in EXCLUDE
                 and games.get(p, 0) >= MIN_GAMES)
    subs = [(d, p) for d, p in pts if when[elolib.build_of(p)][1]]
    cand = [(d, p) for d, p in pts if not when[elolib.build_of(p)][1]]
    if len(subs) < 2:
        sys.exit('field_score: fewer than two submissions')
    t0 = subs[0][0]
    def days(d): return (d - t0).total_seconds() / 86400
    def score(r): return 100 * metrics(r, bots_r)[0]
    def score_hi(r): return 100 * metrics(r, bots_r)[1]
    def rank_of(r): return metrics(r, bots_r)[3]
    def above(r): return metrics(r, bots_r)[2]
    FIT = len(subs) >= 3 and days(subs[-1][0]) >= 0.5
    model = fit_log([days(d) for d, _ in subs], [R[p] for _, p in subs], [SE[p] for _, p in subs], o.tau) if FIT else None
    FIT = model is not None
    def proj(t): return predict(model, t, o.tau) if FIT else (R[subs[-1][1]], 0.0)
    now = dt.datetime.now(PDT).replace(tzinfo=None); tn = days(now)
    ys = [R[p] for _, p in subs]
    print('submissions:', ', '.join(f'{elolib.build_of(p)} {R[p]:.0f}+-{1.96 * SE[p]:.0f} ({d:%m-%d %H:%M}) '
                                    f'{score(R[p]):.1f}%' for d, p in subs))
    if FIT:
        print(f'rating fit R = {model[0]:.0f} + {model[1]:.0f} ln(1 + t/{o.tau:g} d) (t in days from {t0:%Y-%m-%d %H:%M} PDT)')
        for name, when_ in [('now', now)] + HORIZONS:
            r, e = proj(days(when_))
            print(f'  {name} ({when_:%b %d}): rating {r:.0f} +- {e:.0f}  ->  field score {score(r):.1f}% '
                  f'[{score(r - e):.1f}%, {score(r + e):.1f}%], vs higher {score_hi(r):.1f}%, rank #{rank_of(r)}')
    else:
        print('no projection yet (needs 3 submissions spanning half a day): measured points only')

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

    def draw(weeks, path):
        HZ = HORIZONS[:weeks] if FIT else []
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9.5, 14.5), sharex=True)
        tt = np.linspace(0, days(HZ[-1][1]) + 0.3, 200) if FIT else np.array([])
        dates = np.array([t0 + dt.timedelta(days=float(t)) for t in tt])
        pr = [proj(float(t)) for t in tt]
        rr = np.array([p[0] for p in pr]); ee = np.array([p[1] for p in pr])
        past = tt <= tn
        # rating panel
        ax1.errorbar([d for d, _ in subs], ys, yerr=[1.96 * SE[p] for _, p in subs], fmt='o', color='tab:blue', ms=5,
                     capsize=2, label='submission (rating +- 95%)', zorder=3)
        if cand:
            ax1.plot([d for d, _ in cand], [R[p] for _, p in cand], 'o', mfc='white', mec='tab:gray', ms=4,
                     label='candidate (not fitted)')
        for d, p in cand:
            ax1.annotate(elolib.build_of(p), (d, R[p]), textcoords='offset points', xytext=(4, -9), fontsize=6, color='0.4')
        for d, p in subs:
            ax1.annotate(elolib.build_of(p), (d, R[p]), textcoords='offset points', xytext=(4, 5), fontsize=7)
        if FIT:
            ax1.plot(dates[past], rr[past], '-', color='tab:blue', lw=1.2,
                     label=f'fit: R = {model[0]:.0f} + {model[1]:.0f} ln(1 + t/{o.tau:g}d)')
            ax1.plot(dates[~past], rr[~past], '--', color='tab:blue', lw=1.2, label='projection')
            ax1.fill_between(dates, rr - ee, rr + ee, color='tab:blue', alpha=.12, label='95% band')
        ax1.axvline(now, color='0.6', lw=0.8, ls=':'); ax1.set_ylabel('rating (Bradley-Terry, Elo scale)')
        ax1.grid(alpha=.3); ax1.legend(fontsize=8, loc='lower right')
        ax1.set_title('Rating by submission with a diminishing-returns fit, and the field score it implies' if FIT
                      else 'Rating by submission (projection starts once 3 submissions span half a day)')
        # field-score panel
        ax2.plot([d for d, _ in subs], [score(R[p]) for _, p in subs], 'o', color='tab:blue', ms=5, zorder=3,
                 label='submission')
        if cand:
            ax2.plot([d for d, _ in cand], [score(R[p]) for _, p in cand], 'o', mfc='white', mec='tab:gray', ms=4,
                     label='candidate')
        if FIT:
            ss = np.array([score(r) for r in rr]); lo = np.array([score(r) for r in rr - ee]); hi = np.array([score(r) for r in rr + ee])
            ax2.plot(dates[past], ss[past], '-', color='tab:blue', lw=1.2)
            ax2.plot(dates[~past], ss[~past], '--', color='tab:blue', lw=1.2, label='projection (mapped rating)')
            ax2.fill_between(dates, lo, hi, color='tab:blue', alpha=.12, label='95% band')
        for name, d in HZ:
            r, e = proj(days(d)); ax2.plot([d], [score(r)], 's', color='tab:red', ms=6)
            ax2.annotate(f'{name} ({d:%b %d}): {score(r):.1f}% [{score(r - e):.0f}-{score(r + e):.0f}]', (d, score(r)),
                         textcoords='offset points', xytext=(-8, 8), fontsize=8, ha='right', color='tab:red')
        ax2.axvline(now, color='0.6', lw=0.8, ls=':')
        ax2.annotate('now', (now, ax2.get_ylim()[0]), textcoords='offset points', xytext=(3, 3), fontsize=7, color='0.4')
        ax2.set_ylabel('field score (%): expected score vs every rated ladder bot'); ax2.grid(alpha=.3)
        ax2.legend(fontsize=8, loc='lower right')
        # vs higher: only the ladder bots rated above the build (the set shrinks as the rating rises, so the curve steps
        # where a bot is passed)
        ax3.plot([d for d, _ in subs], [score_hi(R[p]) for _, p in subs], 'o', color='tab:purple', ms=5, zorder=3,
                 label='submission')
        if cand:
            ax3.plot([d for d, _ in cand], [score_hi(R[p]) for _, p in cand], 'o', mfc='white', mec='tab:gray', ms=4,
                     label='candidate')
        for d, p in subs:
            ax3.annotate(f"{elolib.build_of(p)} ({above(R[p])})", (d, score_hi(R[p])), textcoords='offset points',
                         xytext=(4, 5), fontsize=7)
        if FIT:
            sh = np.array([score_hi(r) for r in rr])
            ax3.plot(dates[past], sh[past], '-', color='tab:purple', lw=1.2)
            ax3.plot(dates[~past], sh[~past], '--', color='tab:purple', lw=1.2, label='projection (mapped rating)')
        for name, d in HZ:
            r, e = proj(days(d)); ax3.plot([d], [score_hi(r)], 's', color='tab:red', ms=6)
            ax3.annotate(f'{name}: {score_hi(r):.1f}% vs the {above(r)} above', (d, score_hi(r)),
                         textcoords='offset points', xytext=(-8, 8), fontsize=8, ha='right', color='tab:red')
        ax3.axvline(now, color='0.6', lw=0.8, ls=':')
        ax3.set_ylabel('field score vs higher (%): only bots rated above'); ax3.grid(alpha=.3)
        ax3.legend(fontsize=8, loc='lower right')
        # rank among the ladder bots (1 = above them all), by submission and along the fitted rating curve
        ax4.plot([d for d, _ in subs], [rank_of(R[p]) for _, p in subs], 'o', color='tab:green', ms=5, zorder=3,
                 label='submission')
        if cand:
            ax4.plot([d for d, _ in cand], [rank_of(R[p]) for _, p in cand], 'o', mfc='white', mec='tab:gray', ms=4,
                     label='candidate')
        for d, p in subs:
            ax4.annotate(f"{elolib.build_of(p)} #{rank_of(R[p])}", (d, rank_of(R[p])), textcoords='offset points',
                         xytext=(4, -10), fontsize=7)
        if FIT:
            rk = np.array([rank_of(r) for r in rr]); rlo = np.array([rank_of(r) for r in rr + ee])
            rhi = np.array([rank_of(r) for r in rr - ee])
            ax4.step(dates[past], rk[past], '-', where='post', color='tab:green', lw=1.2)
            ax4.step(dates[~past], rk[~past], '--', where='post', color='tab:green', lw=1.2, label='projection (mapped rating)')
            ax4.fill_between(dates, rlo, rhi, step='post', color='tab:green', alpha=.12, label='95% band')
        for name, d in HZ:
            r, e = proj(days(d)); ax4.plot([d], [rank_of(r)], 's', color='tab:red', ms=6)
            ax4.annotate(f'{name}: #{rank_of(r)} of {len(rated) + 1}', (d, rank_of(r)), textcoords='offset points',
                         xytext=(-8, -14), fontsize=8, ha='right', color='tab:red')
        ax4.axvline(now, color='0.6', lw=0.8, ls=':'); ax4.invert_yaxis()
        ax4.set_ylabel(f'rank among the {len(rated)} ladder bots (1 = top)')
        ax4.set_xlabel('submission (PDT); (n) = bots above'); ax4.grid(alpha=.3); ax4.legend(fontsize=8, loc='lower right')
        fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(path, dpi=120); plt.close(fig); print('wrote', path)

    for weeks in (1, 4):
        draw(weeks, os.path.join(o.outdir, f'field-score-{weeks}w.png'))

    # progress.png: rating (+- 95%) and field score of every accepted build, in accept order (bc24's progress-chart.py)
    fs = [score(R[p]) for _, p in subs]
    x = range(len(subs)); lab = [elolib.build_of(p) for _, p in subs]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    a1.errorbar(x, ys, yerr=[1.96 * SE[p] for _, p in subs], fmt='o-', color='#c0392b', capsize=4)
    a1.set_ylabel('ladder rating (BT, Elo scale)'); a1.grid(alpha=.3)
    a1.set_title(f'Accepted builds on the ladder ({len(rows)} games vs {len(rated)} rated ladder bots)')
    a2.plot(x, fs, 'o-', color='#2471a3'); a2.set_ylabel('expected field score %'); a2.set_ylim(0, 100); a2.grid(alpha=.3)
    a2.set_xticks(list(x)); a2.set_xticklabels(lab, fontsize=8)
    for i, v in enumerate(fs):
        a2.annotate(f'{v:.0f}%', (i, v), textcoords='offset points', xytext=(0, 6), ha='center', fontsize=8)
    fig.tight_layout(); out = os.path.join(o.outdir, 'progress.png'); fig.savefig(out, dpi=110); plt.close(fig)
    print('wrote', out)


if __name__ == '__main__':
    main()
