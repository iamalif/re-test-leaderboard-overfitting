"""Illustration for the paper (not an analysis of data): two simulated competitions whose within-team drift looks alike,
one produced by adaptation to public feedback, one by a feedback-free improvement path on public and private sets of
different composition. Deterministic (fixed seed). Writes paper/figures/fig5_identification.(pdf|png) and
outputs/illustration/identification_summary.csv.
Run from the project root:  python scripts/illustrate_identification.py
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(20261117)
N, PUB_SHARE, TEAMS, K = 5000, 0.3, 300, 12

def drift(gaps):                       # paper's definition: later half minus earlier half (K even)
    h = len(gaps) // 2
    return gaps[h:].mean() - gaps[:h].mean()

def scenario_adaptive():
    """Random public/private split. True accuracy never changes: each candidate resamples 150 predictions from the
    same 75% accuracy. The team keeps a candidate only if it raises the public score (feedback)."""
    public = np.zeros(N, bool); public[rng.choice(N, int(N * PUB_SHARE), replace=False)] = True
    pub, prv = np.zeros((TEAMS, K)), np.zeros((TEAMS, K))
    for t in range(TEAMS):
        base = rng.random(N) < 0.75; best = base[public].mean()
        for k in range(K):
            cand = base.copy(); idx = rng.choice(N, 150, replace=False); cand[idx] = rng.random(150) < 0.75
            pub[t, k], prv[t, k] = cand[public].mean(), cand[~public].mean()
            if pub[t, k] > best: base, best = cand, pub[t, k]
    return pub, prv

def scenario_composition():
    """No feedback: every team follows a fixed improvement path. Examples are of two kinds, A and B, predicted equally
    well at first; the public set holds 70% kind A, the private set about 41% (as when public and private come from
    different periods or sources). Later models improve mainly on kind A."""
    easy = rng.random(N) < 0.5
    pub_idx = np.concatenate([rng.choice(np.where(easy)[0], int(N * PUB_SHARE * 0.7), replace=False),
                              rng.choice(np.where(~easy)[0], int(N * PUB_SHARE * 0.3), replace=False)])
    public = np.zeros(N, bool); public[pub_idx] = True
    pub, prv = np.zeros((TEAMS, K)), np.zeros((TEAMS, K))
    for t in range(TEAMS):
        for k in range(K):
            p = np.where(easy, 0.72 + 0.004 * k, 0.72 + 0.0005 * k)
            c = rng.random(N) < p
            pub[t, k], prv[t, k] = c[public].mean(), c[~public].mean()
    return pub, prv

res = {"Adaptation to public feedback\n(random split, no real improvement)": scenario_adaptive(),
       "No feedback used\n(sets differ in composition, models improve)": scenario_composition()}
os.makedirs("outputs/illustration", exist_ok=True)
rows = []
INK, ORANGE, MUTED, GRID = "#1f1f1e", "#eb6834", "#6b6a63", "#e4e3dd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.titlesize": 9, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "legend.frameon": False, "figure.dpi": 200, "savefig.bbox": "tight", "font.family": "DejaVu Sans"})
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.9))
for ax, (name, (pub, prv)) in zip(axs, res.items()):
    gap = (pub - prv) * 100
    d = np.array([drift(g) for g in gap])
    first = gap[:, 0].mean()
    rows.append(dict(scenario=name.replace("\n", " "), teams=TEAMS, submissions=K, mean_gap_pp=gap.mean(),
                     first_gap_pp=first, drift_pp=d.mean(), share_teams_drift_positive=(d > 0).mean()))
    x = np.arange(1, K + 1)
    g = gap.mean(0)
    ax.plot(x, g, color=ORANGE, lw=2, marker="o", ms=4)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title(name, fontsize=8.5)
    ax.set_xlabel("Submission number within team")
    ax.set_ylabel("Public minus private accuracy (pp)")
    ax.text(0.03, 0.95, f"drift {d.mean():+.2f} pp\npositive for {100 * (d > 0).mean():.0f}% of teams",
            transform=ax.transAxes, va="top", fontsize=8, color=INK)
lo = min(a.get_ylim()[0] for a in axs); hi = max(a.get_ylim()[1] for a in axs)
for a in axs: a.set_ylim(lo, hi)
fig.tight_layout()
fig.savefig("paper/figures/fig5_identification.png"); fig.savefig("paper/figures/fig5_identification.pdf", metadata={"CreationDate": None})
pd.DataFrame(rows).to_csv("outputs/illustration/identification_summary.csv", index=False)
print(pd.DataFrame(rows).to_string(index=False))
