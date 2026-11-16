"""Stage 6 (EXPLORATORY, after the independent review of 16 Nov 2026).

1. Evidence tiers for inferred accuracy test-set sizes.
2. Simulation: what a random public/private split implies for drift when nobody uses feedback,
   even if the gap depends on the model (the review's counterexample mechanism).
3. Drift where the split is stated random, and where first submissions fit the random-split null.

Run from the project root:  python scripts/stage6_review_response.py
"""
import sys, numpy as np, pandas as pd
from scipy.stats import binomtest
sys.path.insert(0, "scripts")
from stage2_measures import team_drift

m = pd.read_csv("outputs/stage4/drift_robustness_per_competition.csv")
coh = pd.read_csv("outputs/stage1/cohort_per_competition.csv")[["CompetitionId", "LeaderboardPercentage", "Slug"]]
man = pd.read_csv("data/reference/original_120_manifest.csv")[["CompetitionId", "PaperPublicSize", "PaperPrivateSize"]]
m = m.merge(coh, on="CompetitionId").merge(man, on="CompetitionId", how="left")

# ---- 1. size tiers
a = m[(m.Group == "Accuracy") & m.n_pub.notna()].copy()
a["inferred_public_share"] = 100 * a.n_pub / (a.n_pub + a.n_priv)
a["share_matches_reported"] = (a.inferred_public_share - a.LeaderboardPercentage).abs() <= 1.0
a["published_equal"] = (a.n_pub == a.PaperPublicSize) & (a.n_priv == a.PaperPrivateSize)
def fits(n, pub):  # published size compatible with the lattice: a whole multiple of the minimum
    return pub.notna() & (pub % n == 0)
a["published_is_multiple"] = fits(a.n_pub, a.PaperPublicSize) & fits(a.n_priv, a.PaperPrivateSize)
def tier(r):
    if r.CompetitionId == 3788: return "A: total verified from the test file (Allstate)"
    if r.published_equal: return "B: equals the independently published size"
    if r.share_matches_reported: return "C: split ratio matches the reported public share; multiplier unverified"
    return "D: lattice only"
a["size_tier"] = a.apply(tier, axis=1)
a[["CompetitionId", "Cohort", "Slug", "n_pub", "n_priv", "PaperPublicSize", "PaperPrivateSize", "LeaderboardPercentage",
   "inferred_public_share", "size_tier", "p05_first", "usable" if "usable" in a else "p05_all"]].to_csv("outputs/stage6/size_evidence_tiers.csv", index=False)
print(pd.crosstab(a.size_tier, a.Cohort))
comp = a[a.published_is_multiple]
print("published sizes compatible with the score lattice:", len(comp), "; of these equal to the minimum:", int(comp.published_equal.sum()),
      "; proper multiples:", int((~comp.published_equal).sum()))
for t, x in a.groupby(a.size_tier.str[0]):
    print(t, "n", len(x), "median p05_first", round(x.p05_first.median(), 4), "share drift>0", round((x.drift_mean > 0).mean(), 3))

# ---- 2. simulation: exchangeable versus non-exchangeable sets, no feedback use
def simulate(random_split, seed, teams=60, steps=12, n=3000, clusters=6):
    rng = np.random.default_rng(seed)
    cl = rng.integers(0, clusters, n)                              # each example belongs to a cluster ("domain")
    growth = rng.uniform(0.0, 0.25, clusters)                      # clusters differ in how much later models gain on them
    base = rng.uniform(0.45, 0.7, clusters)
    if random_split: is_pub = rng.random(n) < 0.3
    else:            is_pub = np.isin(cl, np.argsort(-growth)[: clusters // 3])   # public = the clusters where later models gain most
    recs = []
    for t in range(teams):
        skill = rng.normal(0, 0.03)
        for s in range(steps):                                    # predetermined trajectory; no score is ever consulted
            p = np.clip(base[cl] + skill + growth[cl] * (s / (steps - 1)) ** rng.uniform(0.5, 2), 0, 1)
            correct = rng.random(n) < p
            recs.append((t, len(recs), correct[is_pub].mean(), correct[~is_pub].mean()))
    g = pd.DataFrame(recs, columns=["TeamId", "Id", "pub", "priv"]); g["day"] = pd.Timestamp("2020-01-01"); g["gap"] = g.pub - g.priv
    return team_drift(g).mean(), g.gap.mean()
sim = []
for random_split in (True, False):
    r = np.array([simulate(random_split, s) for s in range(300)])
    pos = int((r[:, 0] > 0).sum())
    sim.append(dict(split="random" if random_split else "by cluster, public = fastest-improving clusters", competitions=300,
                    share_positive_drift=pos / 300, sign_test_p=binomtest(pos, 300, .5).pvalue,
                    mean_drift_pp=100 * r[:, 0].mean(), mean_abs_drift_pp=100 * np.abs(r[:, 0]).mean(), share_positive_gap=float((r[:, 1] > 0).mean())))
sim = pd.DataFrame(sim); sim.to_csv("outputs/stage6/exchangeability_simulation.csv", index=False); print(sim.round(4).to_string(index=False))

# ---- 3. drift where a random split is stated or supported
rows = []
def add(label, x):
    v = x.drift_mean.dropna(); pos = int((v > 0).sum())
    rows.append(dict(subset=label, n=len(v), positive=pos, share=pos / len(v) if len(v) else np.nan, sign_p=binomtest(pos, len(v), .5).pvalue if len(v) else np.nan))
add("split stated random (O+E)", m[m.split_label == "RANDOM"])
acc = a
add("accuracy, O+E, all with sizes", acc)
add("accuracy, first submissions fit the null (share p<=0.05 at most 5%)", acc[acc.p05_first <= 0.05])
add("accuracy, first submissions do not fit (share above 5%)", acc[acc.p05_first > 0.05])
add("accuracy, tiers A-B only", acc[acc.size_tier.str[0].isin(["A", "B"])])
for coh_ in ("O", "E"):
    x = m[m.Cohort == coh_]; v = x.first_mean_gap; pos = int((v > 0).sum()); nz = int((v != 0).sum())
    rows.append(dict(subset=f"{coh_}: first-submission gap positive (level, not drift)", n=nz, positive=pos, share=pos / nz, sign_p=binomtest(pos, nz, .5).pvalue))
r = pd.DataFrame(rows); r.to_csv("outputs/stage6/drift_under_random_split_evidence.csv", index=False); print(r.round(4).to_string(index=False))
print(m[m.split_label == "RANDOM"][["CompetitionId", "Cohort", "Group", "drift_mean", "rel_drift", "mean_gap"]].round(5).to_string(index=False))
