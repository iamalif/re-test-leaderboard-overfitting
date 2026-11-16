"""Stage 4 (EXPLORATORY, not in plan v1.0): why do code-only competitions show larger relative gaps?

Separates three readings: (i) a yardstick artefact (team spread is compressed when many teams run the
same public notebook), (ii) a level difference present from the first submission (split or scoring design),
(iii) more adaptation (drift).

Run from the project root:  python scripts/stage4_code_only.py
"""
import numpy as np, pandas as pd
from scipy.stats import binomtest, mannwhitneyu, fisher_exact

x = pd.read_csv("outputs/stage4/drift_robustness_per_competition.csv")
x["prize"] = x.Segment.isin(["Featured", "Research"])
x["rel_first_gap"] = x.first_mean_gap / x.team_spread
x["spread_over_noise"] = x.team_spread / x.noise_sd_first.replace(0, np.nan)      # yardstick relative to first-submission gap noise
x["rel_drift_late"] = x.drift_late / x.team_spread
groups = {"O prize (none code-only)": x[(x.Cohort == "O") & x.prize],
          "E prize, not code-only": x[(x.Cohort == "E") & x.prize & ~x.CodeOnly],
          "E prize, code-only": x[(x.Cohort == "E") & x.prize & x.CodeOnly],
          "E Playground+Community": x[(x.Cohort == "E") & ~x.prize]}
rows = []
for name, g in groups.items():
    def sh(col):
        v = g[col].dropna(); return (v > 0).mean()
    rows.append(dict(group=name, n=len(g), flagged=int(g.flagged.sum()),
                     gap_positive=sh("mean_gap"), first_gap_positive=sh("first_mean_gap"), top10_gap_positive=sh("top10_mean_gap"),
                     drift_positive=sh("drift_mean"), drift_late_positive=sh("drift_late"),
                     med_rel_gap=g.rel_mean_gap.median(), med_rel_first_gap=g.rel_first_gap.median(),
                     med_rel_drift=g.rel_drift.median(), med_rel_drift_late=g.rel_drift_late.median(),
                     med_spread_over_noise=g.spread_over_noise.median(), med_teams=g.teams.median(), med_n=g.n.median()))
t = pd.DataFrame(rows); t.to_csv("outputs/stage4/code_only_summary.csv", index=False)
pd.set_option("display.width", 250); print(t.round(3).T.to_string())
a, b = groups["E prize, code-only"], groups["E prize, not code-only"]
tests = []
for col in ("mean_gap", "first_mean_gap", "drift_mean", "drift_late"):
    tab = [[int((a[col] > 0).sum()), int((a[col] <= 0).sum())], [int((b[col] > 0).sum()), int((b[col] <= 0).sum())]]
    tests.append(dict(measure=col + " > 0", code_only=f"{tab[0][0]}/{sum(tab[0])}", not_code_only=f"{tab[1][0]}/{sum(tab[1])}", fisher_p=fisher_exact(tab)[1]))
for col in ("rel_mean_gap", "rel_first_gap", "rel_drift", "rel_drift_late"):
    tests.append(dict(measure=col, code_only=a[col].median(), not_code_only=b[col].median(), mannwhitney_p=mannwhitneyu(a[col].dropna(), b[col].dropna()).pvalue))
# unflagged only
au, bu = a[~a.flagged], b[~b.flagged]
tests.append(dict(measure="rel_mean_gap, unflagged only", code_only=au.rel_mean_gap.median(), not_code_only=bu.rel_mean_gap.median(), mannwhitney_p=mannwhitneyu(au.rel_mean_gap.dropna(), bu.rel_mean_gap.dropna()).pvalue))
tt = pd.DataFrame(tests); tt.to_csv("outputs/stage4/code_only_tests.csv", index=False); print(tt.round(4).to_string(index=False))
print(pd.crosstab(x[x.Cohort == "E"].Group, [x[x.Cohort == "E"].prize, x[x.Cohort == "E"].CodeOnly]))
