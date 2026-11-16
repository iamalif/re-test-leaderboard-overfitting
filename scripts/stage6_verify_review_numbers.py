"""Stage 6 (EXPLORATORY): independent re-computation of two sensitivity numbers reported by the review.
(a) drift without percentile clipping; (b) first-submission rejection share when inferred sizes are doubled.
Run from the project root:  python scripts/stage6_verify_review_numbers.py
"""
import sys, duckdb, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from stage2_measures import oriented_gap, team_drift, exact_pvalues, first_per_team
m = pd.read_csv("outputs/stage3/competition_measures.csv"); m = m[m.excluded.fillna("") == ""]
con = duckdb.connect(); rows = []
for r in m.itertuples():
    g = con.sql(f"select * from 'outputs/stage3/analysis_submissions.parquet' where CompetitionId={r.CompetitionId}").df()
    g["day"] = pd.to_datetime(g.day); g["gap"] = oriented_gap(g, bool(r.higher_better)); d = team_drift(g)
    out = dict(CompetitionId=r.CompetitionId, Cohort=r.Cohort, drift_planned=r.drift_mean, drift_raw=d.mean() if len(d) else np.nan)
    if r.Group == "Accuracy" and pd.notna(r.p05_first):
        for k in (1, 2):
            p = exact_pvalues(g.pub, g.priv, int(r.n_pub) * k, int(r.n_priv) * k)
            out[f"p05_first_x{k}"] = float((first_per_team(g.assign(p=p)).p <= .05).mean())
    rows.append(out)
x = pd.DataFrame(rows); x.to_csv("outputs/stage6/verify_review_numbers.csv", index=False)
for c, y in x.groupby("Cohort"):
    v = y.drift_raw.dropna()
    print(c, "raw drift positive", int((v > 0).sum()), "of", len(v), "| sign flips vs planned", int(((y.drift_raw > 0) != (y.drift_planned > 0)).sum()),
          "| median p05_first x1", round(y.p05_first_x1.median(), 4), "x2", round(y.p05_first_x2.median(), 4))
