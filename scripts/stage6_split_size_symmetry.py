"""Stage 6 (EXPLORATORY, after the follow-up review of 16 Nov 2026).

The follow-up review showed that a random split gives drift an expectation of zero but not a symmetric sign
unless the two sets have equal size. Two consequences are examined here:
 (a) drift sign by REPORTED (nominal) public share. Sign symmetry under a random split needs exactly equal scored sets,
     which a reported 50% does not verify;
 (b) mean (not sign) of drift for raw-score metrics, which has expectation zero under a random split whatever the sizes.
Uses unclipped drift from outputs/stage6/verify_review_numbers.csv for (b).

Run from the project root:  python scripts/stage6_split_size_symmetry.py
"""
import numpy as np, pandas as pd
from scipy.stats import binomtest
rng = np.random.default_rng(20261117)
m = pd.read_csv("outputs/stage3/competition_measures.csv"); m = m[m.excluded.fillna("") == ""]
m = m.merge(pd.read_csv("outputs/stage1/cohort_per_competition.csv")[["CompetitionId", "LeaderboardPercentage"]], on="CompetitionId")
m = m.merge(pd.read_csv("outputs/stage6/verify_review_numbers.csv")[["CompetitionId", "drift_raw"]], on="CompetitionId")
m["band"] = pd.cut(m.LeaderboardPercentage, [0, 39, 49, 50, 99], labels=["public under 40%", "public 40-49%", "public exactly 50%", "public over 50%"])
RAW = ["Accuracy", "AUC", "MAP@K"]
rows = []
def sign_row(label, x, col="drift_mean"):
    v = x[col].dropna(); pos, nz = int((v > 0).sum()), int((v != 0).sum())
    rows.append(dict(analysis="sign", subset=label, n=nz, positive=pos, share=pos / nz if nz else np.nan, p=binomtest(pos, nz, .5).pvalue if nz else np.nan))
for coh in ("E", "O", "O+E"):
    x = m[m.Cohort.isin(["O", "E"])] if coh == "O+E" else m[m.Cohort == coh]   # corrected 17 Nov: the pooled set wrongly included cohort W
    for b, y in x.groupby("band", observed=True): sign_row(f"{coh}, all metrics, {b}", y)
    for b, y in x[x.Group.isin(RAW)].groupby("band", observed=True): sign_row(f"{coh}, accuracy/AUC/MAP@K, {b}", y, "drift_raw")
def mean_row(label, x, scale):
    v = x.drift_raw.dropna().values * scale
    if len(v) < 8: return
    bs = [rng.choice(v, len(v)).mean() for _ in range(10000)]
    rows.append(dict(analysis="mean", subset=label, n=len(v), mean=v.mean(), ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5),
                     median=np.median(v), share=float((v > 0).mean())))
for coh in ("E", "O", "O+E"):
    x = m[m.Cohort.isin(["O", "E"])] if coh == "O+E" else m[m.Cohort == coh]   # corrected 17 Nov: the pooled set wrongly included cohort W
    mean_row(f"{coh}, accuracy, mean drift (pp)", x[x.Group == "Accuracy"], 100)
    mean_row(f"{coh}, AUC, mean drift (x100)", x[x.Group == "AUC"], 100)
    mean_row(f"{coh}, MAP@K, mean drift (x100)", x[x.Group == "MAP@K"], 100)
    mean_row(f"{coh}, accuracy, unflagged", x[(x.Group == "Accuracy") & ~x.flagged], 100)
    mean_row(f"{coh}, AUC, unflagged", x[(x.Group == "AUC") & ~x.flagged], 100)
r = pd.DataFrame(rows); r.to_csv("outputs/stage6/split_size_symmetry.csv", index=False)
pd.set_option("display.width", 220); print(r.round(4).to_string(index=False))
print(m.groupby(["Cohort", "band"], observed=True).size().unstack(fill_value=0))
