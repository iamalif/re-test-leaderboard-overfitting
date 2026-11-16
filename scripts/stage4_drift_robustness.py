"""Stage 4 (EXPLORATORY, not in plan v1.0): does the drift result survive obvious alternative explanations?

Alternative A: teams start with trivial submissions (sample file, constant predictions) whose gap is ~0,
then submit real models that inherit the competition's gap level. That would create "drift" with the same
sign as the gap level, without any adaptation.
Alternative B: the gap scales with score level, and teams improve over time.

Checks, per competition:
  1. drift_late: third quarter versus fourth quarter of each team's submissions (teams with >= 8).
  2. drift_skip2: planned drift after dropping each team's first two submissions (teams with >= 6).
  3. slope_adj: within-team regression of gap on position (0..1), controlling for score level
     (mean of public and private score); coefficient on position.
  4. planned drift split by the sign of the competition's mean gap.

Run from the project root:  python scripts/stage4_drift_robustness.py
"""
import sys, duckdb, numpy as np, pandas as pd
from scipy.stats import binomtest
sys.path.insert(0, "scripts")
from stage2_measures import prepare_scores, oriented_gap

m = pd.read_csv("outputs/stage3/competition_measures.csv"); m = m[m.excluded.fillna("") == ""].set_index("CompetitionId")
con = duckdb.connect(); rows = []
for cid, r in m.iterrows():
    g = con.sql(f"select * from 'outputs/stage3/analysis_submissions.parquet' where CompetitionId={cid}").df()
    g = prepare_scores(g, r.Group); g["gap"] = oriented_gap(g, bool(r.higher_better))
    g = g.sort_values(["TeamId", "day", "Id"]); k = g.groupby("TeamId").cumcount(); n = g.groupby("TeamId").Id.transform("size")
    out = dict(CompetitionId=cid)
    # 1 late-only drift
    q = (4 * k // n)
    t = g[n >= 8].assign(q=q[n >= 8]).groupby(["TeamId", "q"]).gap.mean().unstack()
    out["drift_late"] = (t[3] - t[2]).mean() if len(t) else np.nan; out["late_teams"] = len(t)
    # 2 skip first two
    h = g[(n >= 6) & (k >= 2)]; kk = h.groupby("TeamId").cumcount(); nn = h.groupby("TeamId").Id.transform("size"); half = nn // 2
    d = h[kk >= nn - half].groupby("TeamId").gap.mean() - h[kk < half].groupby("TeamId").gap.mean()
    out["drift_skip2"] = d.mean() if len(d) else np.nan
    # 3 level-adjusted within-team slope
    h = g[n >= 4].copy(); h["pos"] = (k[n >= 4]) / (n[n >= 4] - 1); h["lvl"] = (h.pub + h.priv) / 2
    X = h[["pos", "lvl"]] - h.groupby("TeamId")[["pos", "lvl"]].transform("mean"); y = h.gap - h.groupby("TeamId").gap.transform("mean")
    sd = X.std()
    if len(h) > 50 and sd.pos > 0 and sd.lvl > 0 and np.isfinite(X.values).all() and np.isfinite(y.values).all():
        Xs = (X / sd).values; beta = np.linalg.lstsq(Xs, y.values, rcond=None)[0]; out["slope_adj"] = beta[0] / sd.pos
    rows.append(out)
x = m.join(pd.DataFrame(rows).set_index("CompetitionId")); x.to_csv("outputs/stage4/drift_robustness_per_competition.csv")

def share(v):
    v = v.dropna(); pos, nz = int((v > 0).sum()), int((v != 0).sum())
    return dict(n=len(v), positive=pos, share=pos / nz if nz else np.nan, sign_p=binomtest(pos, nz, .5).pvalue if nz else np.nan)
res = []
for coh in ("E", "O"):
    y = x[x.Cohort == coh]
    for name, sub in (("all", y), ("code-only", y[y.CodeOnly]), ("not code-only", y[~y.CodeOnly]),
                      ("mean gap > 0", y[y.mean_gap > 0]), ("mean gap < 0", y[y.mean_gap < 0]),
                      ("first-submission gap > 0", y[y.first_mean_gap > 0]), ("first-submission gap < 0", y[y.first_mean_gap < 0])):
        for col in ("drift_mean", "drift_late", "drift_skip2", "slope_adj"):
            res.append(dict(Cohort=coh, subset=name, measure=col, **share(sub[col])))
res = pd.DataFrame(res); res.to_csv("outputs/stage4/drift_robustness_summary.csv", index=False)
pd.set_option("display.width", 200); print(res.round(4).to_string(index=False))
