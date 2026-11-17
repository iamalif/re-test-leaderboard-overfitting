"""Stage 2 pilot: run the planned measures on the ORIGINAL 120 competitions only,
and check them on simulated data. Reads no extension scores.

Run from the project root:  python scripts/stage2_pilot_original.py
Needs outputs/stage1/original_predeadline_submissions.csv.gz (from stage1_reproduce.py).
"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from stage2_measures import (prepare_scores, competition_measures, infer_denominator, exact_pvalues,
                             null_top_decile_gap, first_per_team, top_decile)
from scipy.stats import binomtest, wilcoxon

man = pd.read_csv("data/reference/original_120_manifest.csv").set_index("CompetitionId")
# Scores read as text and converted with Python's float() (correctly rounded under any pandas version). Added 17 Nov 2026.
d = pd.read_csv("outputs/stage1/original_predeadline_submissions.csv.gz",
                dtype={"PublicScoreFullPrecision": str, "PrivateScoreFullPrecision": str})
for _c in ("PublicScoreFullPrecision", "PrivateScoreFullPrecision"):
    d[_c] = [float(v) if isinstance(v, str) and v.strip() != "" else float("nan") for v in d[_c]]
flags = pd.read_csv("outputs/stage1/original_team_flags.csv")
bench = set(flags.loc[flags.IsBenchmark, "TeamId"])
d = d.rename(columns={"PublicScoreFullPrecision": "pub", "PrivateScoreFullPrecision": "priv"})
d["pub"] = pd.to_numeric(d.pub, errors="coerce"); d["priv"] = pd.to_numeric(d.priv, errors="coerce")
d = d[np.isfinite(d.pub) & np.isfinite(d.priv) & ~d.TeamId.isin(bench)].copy()
d["day"] = pd.to_datetime(d.SubmissionDate, format="%m/%d/%Y")

rows, den, pvals = [], [], []
for cid, m in man.iterrows():
    g = prepare_scores(d[d.CompetitionId == cid], m.PaperMetric)
    hb = m.PaperMetric not in ("LogLoss", "MulticlassLoss")
    r = dict(CompetitionId=cid, Metric=m.PaperMetric, **competition_measures(g, hb))
    # does submission Id order agree with day order?
    s = g.sort_values("Id"); r["id_day_inversions"] = float((s.day.diff().dt.days < 0).mean())
    rows.append(r)
    if m.PaperMetric == "Accuracy":
        npub, fpub = infer_denominator(g.pub); npriv, fpriv = infer_denominator(g.priv)
        e = dict(CompetitionId=cid, paper_pub=m.PaperPublicSize, paper_priv=m.PaperPrivateSize,
                 inferred_pub=npub, fit_pub=fpub, inferred_priv=npriv, fit_priv=fpriv,
                 share_identical=r["share_identical"])
        if npub and npriv and fpub == 1 and fpriv == 1 and r["share_identical"] < 0.99:
            g = g.assign(p=exact_pvalues(g.pub, g.priv, npub, npriv))
            pvals.append(g[["CompetitionId", "Id", "p"]])
            nm, ns = null_top_decile_gap(g.pub, g.priv, npub, npriv, seed=int(cid))
            e.update(p05_all=float((g.p <= .05).mean()), p05_first=float((first_per_team(g).p <= .05).mean()),
                     p05_top10=float((top_decile(g, True).p <= .05).mean()),
                     top10_gap=r["top10_mean_gap"], top10_gap_null=nm, top10_gap_null_sd=ns,
                     top10_gap_excess=r["top10_mean_gap"] - nm)
        den.append(e)
res = pd.DataFrame(rows); res.to_csv("outputs/stage2/pilot_original_measures.csv", index=False)
den = pd.DataFrame(den); den.to_csv("outputs/stage2/pilot_original_inferred_sizes.csv", index=False)
pv = pd.concat(pvals)
old = pd.read_csv("outputs/stage1/original_pvalues_consistent_sizes.csv.gz").merge(pv, on=["CompetitionId", "Id"])
print("cross-check against the stage 1 p-values (independent implementation):", len(old), "submissions in",
      old.CompetitionId.nunique(), "competitions; max abs difference", float((old.p - old.p_inclusive).abs().max()))
tests = []
for metric, x in list(res.groupby("Metric")) + [("All five", res)]:
    x = x[x.share_identical < 0.99]; dm = x.drift_mean.dropna(); pos = int((dm > 0).sum()); nz = int((dm != 0).sum())
    tests.append(dict(Metric=metric, competitions=len(dm), drift_positive=pos, sign_test_p=binomtest(pos, nz, .5).pvalue,
                      wilcoxon_p_rel_drift=wilcoxon(x.rel_drift.dropna()).pvalue, median_rel_drift=x.rel_drift.median(),
                      median_rel_gap=x.rel_mean_gap.median(), gap_positive=int((x.mean_gap > 0).sum())))
tests = pd.DataFrame(tests); tests.to_csv("outputs/stage2/pilot_original_drift_tests.csv", index=False)

# --- simulation: does team drift separate adaptation from shift and selection? ---
def simulate(adaptive, shift, seed, teams=300, steps=20, n_pub=1000, n_priv=1000, k=30):
    rng = np.random.default_rng(seed); recs = []
    for t in range(teams):
        acc0 = rng.uniform(0.6, 0.8)
        # correct/incorrect indicators; private set is harder by `shift`
        pub = rng.random(n_pub) < acc0; priv = rng.random(n_priv) < acc0 - shift
        val = rng.random(1000) < acc0                    # the team's own validation data
        for s in range(steps):
            cp, cq, cv = pub.copy(), priv.copy(), val.copy()
            for arr in (cp, cq, cv):                      # a proposed change re-draws k predictions
                idx = rng.choice(len(arr), k, replace=False)
                arr[idx] = rng.random(k) < (acc0 + 0.02 - (shift if arr is cq else 0))
            recs.append((t, s, cp.mean(), cq.mean()))    # every proposal is submitted
            keep = cp.mean() > pub.mean() if adaptive else cv.mean() > val.mean()
            if keep: pub, priv, val = cp, cq, cv
    g = pd.DataFrame(recs, columns=["TeamId", "Id", "pub", "priv"]); g["day"] = pd.Timestamp("2020-01-01")
    g["Id"] = np.arange(len(g)); g["gap"] = g.pub - g.priv
    return g
sim = []
for adaptive in (False, True):
    for shift in (0.0, 0.03):
        vals = [competition_measures(simulate(adaptive, shift, s), True) for s in range(20)]
        v = pd.DataFrame(vals)
        sim.append(dict(adaptive=adaptive, shift=shift, mean_gap_pp=100 * v.mean_gap.mean(),
                        top10_gap_pp=100 * v.top10_mean_gap.mean(), drift_pp=100 * v.drift_mean.mean(),
                        drift_pp_sd_across_runs=100 * v.drift_mean.std(), rel_drift=v.rel_drift.mean(),
                        share_runs_drift_positive=float((v.drift_mean > 0).mean())))
sim = pd.DataFrame(sim); sim.to_csv("outputs/stage2/pilot_simulation.csv", index=False)

pd.set_option("display.width", 250)
print(sim.round(3).to_string(index=False)); print()
print(tests.round(4).to_string(index=False)); print()
a = res[res.Metric == "Accuracy"].copy()
for c in ["mean_gap", "top10_mean_gap", "drift_mean", "drift_se", "noise_sd_first"]: a[c] = 100 * a[c]
print(a[["CompetitionId", "n", "teams", "drift_teams", "mean_gap", "top10_mean_gap", "noise_sd_first", "drift_mean", "drift_se", "rel_drift", "rel_mean_gap"]].round(3).to_string(index=False)); print()
for c in ["top10_gap", "top10_gap_null", "top10_gap_null_sd", "top10_gap_excess"]: den[c] = 100 * den[c]
print(den.drop(columns=["fit_pub", "fit_priv"]).round(3).to_string(index=False))
