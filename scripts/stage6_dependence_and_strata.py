"""Stage 6 (EXPLORATORY): dependence between related competitions, stratified O-versus-E comparisons, and tail
summaries for H1. Definitions were written in decision_log.md (17 Nov 2026) before this script was run.
First run used 4,000 group-bootstrap draws instead of the logged 10,000 (kept as dependence_and_strata_4000draws.csv);
this version uses 10,000 as specified.

Run from the project root:  python scripts/stage6_dependence_and_strata.py
"""
from csvio import read_csv_exact   # exact CSV reading under any pandas version
import re, duckdb, numpy as np, pandas as pd
from scipy.stats import binomtest
rng = np.random.default_rng(20261117)
m = read_csv_exact("outputs/stage3/competition_measures.csv"); m = m[m.excluded.fillna("") == ""].sort_values("CompetitionId")
meta = duckdb.connect().sql("select Id::bigint CompetitionId, Slug, OrganizationId from read_csv('data/raw/Competitions.csv',header=true,all_varchar=true)").df()
m = m.merge(meta, on="CompetitionId")
def cluster(r):
    if pd.notna(r.OrganizationId) and str(r.OrganizationId) != "": return f"org:{r.OrganizationId}"
    toks = [t for t in re.sub(r"\d", "", r.Slug.lower()).split("-") if t]
    return "slug:" + "-".join(toks[:2])
m["cluster"] = m.apply(cluster, axis=1)
m[["CompetitionId", "Cohort", "Segment", "Slug", "cluster"]].to_csv("outputs/stage6/competition_clusters.csv", index=False)
FIVE = ["Accuracy", "AUC", "MAP@K", "LogLoss", "MulticlassLoss"]
O, E = m[m.Cohort == "O"], m[m.Cohort == "E"]
print("clusters:", m.cluster.nunique(), "for", len(m), "competitions; largest:", m.cluster.value_counts().head(4).to_dict())

def cluster_boot(df, stat, B=10000):
    """Resample whole groups with replacement. `stat` receives a DataFrame. Row positions are gathered with arrays
    (same draws as concatenating group frames, far faster)."""
    df = df.reset_index(drop=True); groups = [g.index.values for _, g in df.groupby("cluster")]; out = []
    for _ in range(B):
        idx = rng.integers(0, len(groups), len(groups)); out.append(stat(df.iloc[np.concatenate([groups[i] for i in idx])]))
    return np.nanpercentile(out, [2.5, 97.5])
rows = []
def med_diff(col, grp, scale=1.0):
    sub = m[m.Group.isin(grp) & m.Cohort.isin(["O", "E"]) & m[col].notna()]
    f = lambda d: (d[d.Cohort == "E"][col].median() - d[d.Cohort == "O"][col].median()) * scale
    lo, hi = cluster_boot(sub, f); return f(sub), lo, hi, sub.cluster.nunique()
for name, col, grp, sc in (("H1a accuracy median gap, E minus O (pp)", "mean_gap", ["Accuracy"], 100), ("H1b AUC median gap, E minus O", "mean_gap", ["AUC"], 1),
                           ("H3 median relative drift, E minus O", "rel_drift", FIVE, 1)):
    est, lo, hi, k = med_diff(col, grp, sc); rows.append(dict(analysis="cluster bootstrap", quantity=name, estimate=est, ci_lo=lo, ci_hi=hi, clusters=k))
e = E[E.drift_mean.notna()]
lo, hi = cluster_boot(e, lambda d: (d.drift_mean > 0).mean())
rows.append(dict(analysis="cluster bootstrap", quantity="H2 share of E competitions with positive drift", estimate=(e.drift_mean > 0).mean(), ci_lo=lo, ci_hi=hi, clusters=e.cluster.nunique()))
shares, ps = [], []
for _ in range(2000):
    one = e.groupby("cluster").sample(1, random_state=int(rng.integers(1e9))); pos = int((one.drift_mean > 0).sum())
    shares.append(pos / len(one)); ps.append(binomtest(pos, len(one), .5).pvalue)
rows.append(dict(analysis="one competition per cluster, 2000 draws", quantity="H2 share positive", estimate=np.median(shares), ci_lo=np.percentile(shares, 2.5), ci_hi=np.percentile(shares, 97.5), clusters=e.cluster.nunique()))
rows.append(dict(analysis="one competition per cluster, 2000 draws", quantity="H2 sign-test p-value (median; 97.5th percentile in ci_hi)", estimate=np.median(ps), ci_lo=np.percentile(ps, 2.5), ci_hi=np.percentile(ps, 97.5), clusters=e.cluster.nunique()))
o = O[O.drift_mean.notna()]
rows.append(dict(analysis="by cluster type", quantity="E share positive drift, organisation clusters only", estimate=(e[e.cluster.str.startswith("org")].drift_mean > 0).mean(), clusters=e[e.cluster.str.startswith("org")].cluster.nunique()))
rows.append(dict(analysis="by cluster type", quantity="E share positive drift, excluding organisation 4 (Playground host)", estimate=(e[e.cluster != "org:4"].drift_mean > 0).mean(), clusters=e[e.cluster != "org:4"].cluster.nunique()))
# stratified O versus E
m["stratum"] = np.where(m.Segment == "Community", "Community", "not Community")
for grp, sc, unit in (("Accuracy", 100, "pp"), ("AUC", 1, "")):
    for st in ("Community", "not Community"):
        a, b = E[(E.Group == grp) & ((E.Segment == "Community") == (st == "Community"))].mean_gap * sc, O[(O.Group == grp) & ((O.Segment == "Community") == (st == "Community"))].mean_gap * sc
        if min(len(a), len(b)) < 5: rows.append(dict(analysis="stratified", quantity=f"{grp}, {st}: too few (E {len(a)}, O {len(b)})")); continue
        bs = [np.median(rng.choice(a.values, len(a))) - np.median(rng.choice(b.values, len(b))) for _ in range(10000)]
        rows.append(dict(analysis="stratified", quantity=f"{grp}, {st}: median gap E ({len(a)}) minus O ({len(b)}) {unit}", estimate=a.median() - b.median(), ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5),
                         median_E=a.median(), median_O=b.median()))
res = pd.DataFrame(rows); res.to_csv("outputs/stage6/dependence_and_strata.csv", index=False)
tails = []
for grp, sc in (("Accuracy", 100), ("AUC", 1)):
    for coh, d in (("O", O), ("E", E)):
        v = d[d.Group == grp].mean_gap * sc
        for lab, x in (("signed", v), ("absolute", v.abs())):
            tails.append(dict(metric=grp, cohort=coh, gap=lab, n=len(v), **{f"p{q}": x.quantile(q / 100) for q in (10, 25, 50, 75, 90)}))
tails = pd.DataFrame(tails); tails.to_csv("outputs/stage6/h1_tail_summary.csv", index=False)
pd.set_option("display.width", 230); print(res.round(4).to_string(index=False)); print(tails.round(4).to_string(index=False))
