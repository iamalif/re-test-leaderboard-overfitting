"""Stage 2: measure definitions, shared by the pilot (original 120) and, later, the extension.

Every function takes one competition's scored, pre-deadline, non-benchmark submissions
as a DataFrame with columns Id, TeamId, day (datetime), pub, priv, and `higher_better`.
Gap is oriented so that positive = public score looks better than private score.
"""
from fractions import Fraction
from math import lcm
import numpy as np
import pandas as pd

MIN_TEAM_SUBS = 4          # a team needs this many scored submissions to enter the drift measure


RAW_SCORE_GROUPS = ("Accuracy", "AUC", "MAP@K")   # bounded metrics analysed on raw scores


def prepare_scores(g, metric_group):
    """For every metric outside RAW_SCORE_GROUPS, clip public and private scores to the
    1st-99th percentile range of the PUBLIC scores. Bounds never depend on private scores."""
    if metric_group in RAW_SCORE_GROUPS:
        return g
    lo, hi = g.pub.quantile([0.01, 0.99])
    return g.assign(pub=g.pub.clip(lo, hi), priv=g.priv.clip(lo, hi))


def oriented_gap(g, higher_better):
    return (g.pub - g.priv) if higher_better else (g.priv - g.pub)


def robust_sd(x):
    x = np.asarray(x, float)
    return 1.4826 * np.median(np.abs(x - np.median(x))) if len(x) else np.nan


def team_spread(g, higher_better):
    """Distance between a median team and a top-decile team, on teams' median PUBLIC score.
    Used as a unit-free yardstick: gap or drift divided by this spread."""
    t = g.groupby("TeamId").pub.median()
    if len(t) < 20:
        return np.nan
    return float(t.quantile(0.9) - t.quantile(0.5)) if higher_better else float(t.quantile(0.5) - t.quantile(0.1))


def first_per_team(g):
    return g.sort_values(["day", "Id"]).drop_duplicates("TeamId", keep="first")


def top_decile(g, higher_better):
    """Top 10% by public score, keeping every submission tied at the cutoff."""
    n = int(np.ceil(0.1 * len(g)))
    s = g.pub.sort_values(ascending=not higher_better)
    cut = s.iloc[n - 1]
    return g[g.pub >= cut] if higher_better else g[g.pub <= cut]


def team_drift(g):
    """Per team: mean gap of the later half of its submissions minus the earlier half.
    Order is (day, Id). Odd counts drop the middle submission. No selection on scores."""
    g = g.sort_values(["TeamId", "day", "Id"])
    k = g.groupby("TeamId").cumcount()
    n = g.groupby("TeamId").Id.transform("size")
    g = g[n >= MIN_TEAM_SUBS]
    k, n = k[g.index], n[g.index]
    half = n // 2
    early = g[k < half].groupby("TeamId").gap.mean()
    late = g[k >= n - half].groupby("TeamId").gap.mean()
    return (late - early).dropna()


def infer_denominator(scores, cap=5_000_000):
    """Smallest test-set size consistent with accuracy scores: LCM of the reduced
    denominators of the score values. Returns (n, share of scores on the n-lattice)."""
    u = np.unique(np.asarray(scores, float))
    u = u[np.isfinite(u) & (u >= 0) & (u <= 1)]
    if len(u) < 20:
        return None, np.nan
    dens = {}
    for v in u:
        f = Fraction(float(v)).limit_denominator(cap)
        if abs(float(f) - v) < 1e-11:
            dens[f.denominator] = dens.get(f.denominator, 0) + 1
    n = 1
    for d, _ in sorted(dens.items(), key=lambda kv: -kv[1]):
        m = lcm(n, d)
        if m <= cap:
            n = m
    fit = float(np.mean(np.abs(u * n - np.rint(u * n)) < 1e-4))   # within 0.0001 of a whole count
    return n, fit


def competition_measures(g, higher_better):
    g = g.copy()
    g["gap"] = oriented_gap(g, higher_better)
    first = first_per_team(g)
    top = top_decile(g, higher_better)
    s_c = robust_sd(first.gap)
    d = team_drift(g)
    out = dict(
        n=len(g), teams=g.TeamId.nunique(),
        mean_gap=g.gap.mean(), median_gap=g.gap.median(),
        first_mean_gap=first.gap.mean(), top10_mean_gap=top.gap.mean(), top10_n=len(top),
        noise_sd_first=s_c,
        share_identical=float((g.pub == g.priv).mean()),
        drift_teams=len(d), drift_mean=d.mean() if len(d) else np.nan,
        drift_se=d.std(ddof=1) / np.sqrt(len(d)) if len(d) > 1 else np.nan,
        drift_median=d.median() if len(d) else np.nan,
        drift_share_positive=float((d > 0).mean()) if len(d) else np.nan,
        drift_share_negative=float((d < 0).mean()) if len(d) else np.nan,
    )
    spread = team_spread(g, higher_better)
    out["team_spread"] = spread
    ok = spread is not None and np.isfinite(spread) and spread > 0
    out["rel_mean_gap"] = out["mean_gap"] / spread if ok else np.nan
    out["rel_drift"] = out["drift_mean"] / spread if ok else np.nan
    return out


def exact_pvalues(pub, priv, n_pub, n_priv):
    """Null model of the 2019 paper: a submission's correct answers are split at random
    between public and private sets of the given sizes. Two-sided, inclusive tail:
    P(|public acc - private acc| >= observed)."""
    from scipy.stats import hypergeom
    kp = np.rint(np.asarray(pub, float) * n_pub).astype(np.int64)
    kq = np.rint(np.asarray(priv, float) * n_priv).astype(np.int64)
    N, m = n_pub + n_priv, kp + kq
    # |kp/n_pub - kq/n_priv| >= eps  <=>  |kq*N - m*n_priv| >= observed distance
    centre, delta = m * n_priv, np.abs(kq * N - m * n_priv)
    lo = (centre - delta) // N                 # largest kq with kq*N <= centre - delta
    hi = -(-(centre + delta) // N)             # smallest kq with kq*N >= centre + delta
    p = hypergeom.cdf(lo, N, m, n_priv) + hypergeom.sf(hi - 1, N, m, n_priv)
    return np.minimum(1.0, p)


def null_top_decile_gap(pub, priv, n_pub, n_priv, reps=200, seed=0):
    """Top-decile mean gap expected from selection alone under the same null model.
    Returns (mean, sd) over simulated random splits, each submission split independently."""
    rng = np.random.default_rng(seed)
    kp = np.rint(np.asarray(pub, float) * n_pub).astype(np.int64)
    kq = np.rint(np.asarray(priv, float) * n_priv).astype(np.int64)
    m, N = kp + kq, n_pub + n_priv
    k = int(np.ceil(0.1 * len(m))); out = []
    for _ in range(reps):
        sp = rng.hypergeometric(m, N - m, n_pub)          # simulated public correct counts
        a_pub, a_priv = sp / n_pub, (m - sp) / n_priv
        cut = np.sort(a_pub)[-k]
        sel = a_pub >= cut
        out.append((a_pub[sel] - a_priv[sel]).mean())
    return float(np.mean(out)), float(np.std(out))
