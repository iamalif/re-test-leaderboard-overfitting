"""Stage 3: confirmatory tests (H1a, H1b, H2, H3) and secondary analyses S1-S6 of plan v1.0.

Run from the project root:  python scripts/stage3_tests.py
Input : outputs/stage3/competition_measures.csv
Output: outputs/stage3/results_confirmatory.csv, results_secondary.csv, results_descriptive.csv
"""
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu, binomtest, spearmanr

rng = np.random.default_rng(20261116); B = 10_000
m = pd.read_csv("outputs/stage3/competition_measures.csv")
m["excluded"] = m.excluded.fillna("")
print(m.groupby(["Cohort", "excluded"]).size().unstack(fill_value=0))
d = m[m.excluded == ""].copy()
FIVE = ["Accuracy", "AUC", "MAP@K", "LogLoss", "MulticlassLoss"]
O, E, W = (d[d.Cohort == k] for k in "OEW")


def ci_median_diff(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    bs = [np.median(rng.choice(x, len(x))) - np.median(rng.choice(y, len(y))) for _ in range(B)]
    return np.median(x) - np.median(y), *np.percentile(bs, [2.5, 97.5])


def ci_stat(x, f):
    x = np.asarray(x, float)
    return f(x), *np.percentile([f(rng.choice(x, len(x))) for _ in range(B)], [2.5, 97.5])


def two_sample(name, e, o, scale=1.0, unit=""):
    e, o = e.dropna(), o.dropna()
    est, lo, hi = ci_median_diff(e * scale, o * scale)
    return dict(test=name, n_E=len(e), n_O=len(o), median_E=np.median(e) * scale, median_O=np.median(o) * scale,
                effect="median E minus median O" + unit, estimate=est, ci_lo=lo, ci_hi=hi,
                p=mannwhitneyu(e, o, alternative="two-sided").pvalue)


def sign(name, x):
    x = x.dropna(); pos, nz = int((x > 0).sum()), int((x != 0).sum())
    est, lo, hi = ci_stat((x > 0).astype(float), np.mean)
    return dict(test=name, n_E=len(x), effect="share with positive drift", estimate=est, ci_lo=lo, ci_hi=hi,
                p=binomtest(pos, nz, 0.5).pvalue, positive=pos, nonzero=nz)


def confirmatory(E, O):
    rows = [two_sample("H1a accuracy mean gap", E[E.Group == "Accuracy"].mean_gap, O[O.Group == "Accuracy"].mean_gap, 100, " (pp)"),
            two_sample("H1b AUC mean gap", E[E.Group == "AUC"].mean_gap, O[O.Group == "AUC"].mean_gap),
            sign("H2 drift exists in E (all metrics)", E.drift_mean),
            two_sample("H3 relative drift, five metric groups", E[E.Group.isin(FIVE)].rel_drift, O[O.Group.isin(FIVE)].rel_drift)]
    r = pd.DataFrame(rows)
    order = r.p.sort_values().index; k = len(r); adj = {}; running = 0
    for i, idx in enumerate(order):                                   # Holm
        running = max(running, min(1, (k - i) * r.p[idx])); adj[idx] = running
    r["p_holm"] = pd.Series(adj); r["significant_05"] = r.p_holm < 0.05
    return r

conf = confirmatory(E, O); conf.insert(0, "sample", "all")
unfl = confirmatory(E[~E.flagged], O[~O.flagged]); unfl.insert(0, "sample", "S6 not flagged")     # S6
pd.concat([conf, unfl]).to_csv("outputs/stage3/results_confirmatory.csv", index=False)

# descriptive companions
desc = []
for coh, x in (("O", O), ("E", E), ("W", W)):
    for grp, y in list(x.groupby("Group")) + [("ALL", x)]:
        dm = y.drift_mean.dropna(); rd = y.rel_drift.dropna(); rg = y.rel_mean_gap.dropna()
        row = dict(Cohort=coh, Group=grp, n=len(y), median_mean_gap=y.mean_gap.median(), share_gap_positive=(y.mean_gap > 0).mean(),
                   drift_n=len(dm), share_drift_positive=(dm > 0).mean() if len(dm) else np.nan,
                   median_rel_drift=rd.median(), median_rel_gap=rg.median(), q25_rel_drift=rd.quantile(.25) if len(rd) else np.nan,
                   q75_rel_drift=rd.quantile(.75) if len(rd) else np.nan, flagged=int(y.flagged.sum()))
        if grp == "Accuracy": row["share_gap_above_threshold"] = (y.mean_gap > 0.01).mean(); row["threshold"] = "1 pp"
        if grp == "AUC": row["share_gap_above_threshold"] = (y.mean_gap > 0.01).mean(); row["threshold"] = "0.01"
        desc.append(row)
pd.DataFrame(desc).to_csv("outputs/stage3/results_descriptive.csv", index=False)

sec = []
def add(analysis, label, x, col):
    x = x[col].dropna()
    if len(x) < 5: sec.append(dict(analysis=analysis, group=label, measure=col, n=len(x))); return
    est, lo, hi = ci_stat(x, np.median)
    sec.append(dict(analysis=analysis, group=label, measure=col, n=len(x), median=est, ci_lo=lo, ci_hi=hi, share_positive=(x > 0).mean()))
def contrast(analysis, label, a, b, col):
    a, b = a[col].dropna(), b[col].dropna()
    if min(len(a), len(b)) < 5: return
    est, lo, hi = ci_median_diff(a, b)
    sec.append(dict(analysis=analysis, group=label, measure=col, n=len(a), n_other=len(b), median=est, ci_lo=lo, ci_hi=hi,
                    p=mannwhitneyu(a, b, alternative="two-sided").pvalue))

# S1 regression vs classification
reg_all, cls_all = pd.concat([E, W])[lambda x: x.Group == "Regression"], pd.concat([E, O])[lambda x: x.Group.isin(FIVE)]
for col in ("drift_mean", "rel_drift", "rel_mean_gap"):
    add("S1", "regression E+W", reg_all, col); add("S1", "classification E+O", cls_all, col)
    add("S1", "regression E", E[E.Group == "Regression"], col); add("S1", "classification E", E[E.Group.isin(FIVE)], col)
for col in ("rel_drift", "rel_mean_gap"):
    contrast("S1", "regression minus classification, E+W vs E+O", reg_all, cls_all, col)
    contrast("S1", "regression minus classification, within E", E[E.Group == "Regression"], E[E.Group.isin(FIVE)], col)

# S2 test-set size (accuracy with inferred sizes)
acc = d[(d.Group == "Accuracy") & d.p05_all.notna()].copy(); acc["total"] = acc.n_pub + acc.n_priv; acc["abs_gap"] = acc.mean_gap.abs()
for lab_, x in (("O+E", acc), ("O", acc[acc.Cohort == "O"]), ("E", acc[acc.Cohort == "E"])):
    for col in ("abs_gap", "top10_gap_excess"):
        if len(x) >= 5:
            rho, p = spearmanr(x.total, x[col])
            sec.append(dict(analysis="S2", group=f"{lab_}: Spearman with total test size", measure=col, n=len(x), median=rho, p=p))
        small, big = x[x.total < 10_000], x[x.total >= 10_000]
        add("S2", f"{lab_}: under 10,000", small, col); add("S2", f"{lab_}: 10,000 or more", big, col)
        contrast("S2", f"{lab_}: under 10,000 minus 10,000 or more", small, big, col)

# S3 platform
for col in ("drift_mean", "rel_drift", "rel_mean_gap"):
    add("S3", "E code-only", E[E.CodeOnly], col); add("S3", "E not code-only", E[~E.CodeOnly], col)
    for seg in ("Featured", "Research", "Playground", "Community"): add("S3", f"E {seg}", E[E.Segment == seg], col)
for col in ("rel_drift", "rel_mean_gap"):
    contrast("S3", "E code-only minus not", E[E.CodeOnly], E[~E.CodeOnly], col)

# S4 time
for col in ("rel_drift", "rel_mean_gap"):
    x = E[[col, "DeadlineYear"]].dropna(); rho, p = spearmanr(x.DeadlineYear, x[col])
    sec.append(dict(analysis="S4", group="E: Spearman with deadline year", measure=col, n=len(x), median=rho, p=p))
    for y, z in E.groupby("DeadlineYear"): add("S4", f"E {y}", z, col)

# S5 formal accuracy test
for coh in ("O", "E"):
    x = acc[acc.Cohort == coh]
    for col in ("p05_all", "p05_first", "top10_gap_excess"):
        add("S5", coh, x, col)
    sec.append(dict(analysis="S5", group=f"{coh}: competitions with p05_first above 0.10", measure="p05_first", n=len(x), median=(x.p05_first > 0.10).mean()))
    sec.append(dict(analysis="S5", group=f"{coh}: accuracy competitions without usable inferred sizes", measure="count",
                    n=int(((d.Cohort == coh) & (d.Group == "Accuracy") & d.p05_all.isna()).sum())))
pd.DataFrame(sec).to_csv("outputs/stage3/results_secondary.csv", index=False)

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 30)
print(pd.concat([conf, unfl]).round(5).to_string(index=False)); print()
print(pd.DataFrame(desc).round(4).to_string(index=False))
