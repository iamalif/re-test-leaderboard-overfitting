"""Stage 3: apply analysis plan v1.0 to cohorts O, E and W.

Step 1 (extract): pre-deadline, non-benchmark submissions with finite public and private
scores, for every competition passing inclusion rules 1-2.
Step 2 (measure): per-competition measures from scripts/stage2_measures.py. Resumable.

Run from the project root, repeatedly until it prints DONE:
    python scripts/stage3_extension.py [--max-seconds 150]
Outputs: outputs/stage3/analysis_submissions.parquet, outputs/stage3/competition_measures.csv
"""
import argparse, os, sys, time
import duckdb, numpy as np, pandas as pd
sys.path.insert(0, "scripts")
from stage2_measures import (prepare_scores, competition_measures, infer_denominator, exact_pvalues,
                             null_top_decile_gap, first_per_team, top_decile)

ap = argparse.ArgumentParser(); ap.add_argument("--max-seconds", type=float, default=150); a = ap.parse_args()
t0 = time.time()
PARQ, OUT = "outputs/stage3/analysis_submissions.parquet", "outputs/stage3/competition_measures.csv"
REG_NAMES = {"Mean Squared Error", "Mean Absolute Error", "Mean Squared Log Error",
             "Root Mean Squared Error", "Root Mean Squared Log Error"}


def metric_group(metric, name):                      # plan section 4
    numeric = str(metric).isdigit()
    if metric == "CategorizationAccuracy" or (numeric and name == "Accuracy Score"): return "Accuracy"
    if metric == "AUC" or (numeric and name in ("Roc Auc Score", "sklearn_roc_auc_score")): return "AUC"
    if metric in ("MAP@{K}", "MAP@k", "MAP@3", "AP@{K}", "MAP@{K}_OLD"): return "MAP@K"
    if metric == "LogLoss": return "LogLoss"
    if metric in ("MulticlassLoss", "MulticlassLossOld"): return "MulticlassLoss"
    if metric in ("RMSE", "MAE", "MSE", "RMSLE") or (numeric and name in REG_NAMES): return "Regression"
    return "Other"


c = pd.read_csv("outputs/stage1/cohort_per_competition.csv")
s0 = pd.read_csv("outputs/stage0_per_competition.csv", usecols=["CompetitionId", "MetricIsMax"])
c = c.merge(s0, on="CompetitionId")
c["Group"] = [metric_group(m, n) for m, n in zip(c.Metric, c.MetricName)]
c["CohortCode"] = c.Cohort.map({"original_120": "O", "extension_candidate": "E", "in_window_not_in_original": "W"})
c = c[c.CohortCode.notna() & c.LeaderboardPercentage.between(1, 99)]            # rules 1 (in file) and 2
c = c[(c.CohortCode != "W") | c.Metric.isin(["RMSE", "MAE", "MSE", "RMSLE"])]
lab = pd.read_csv("outputs/stage3/split_labels.csv")[["CompetitionId", "split_label", "flagged"]]
c = c.merge(lab, on="CompetitionId", how="left").set_index("CompetitionId")

if not os.path.exists(PARQ):
    con = duckdb.connect(); con.execute("SET memory_limit='2GB'; SET temp_directory='/tmp/duck'")
    con.register("ids", pd.DataFrame({"CompetitionId": c.index.astype(str)}))
    con.execute(f"""COPY (
      SELECT t.CompetitionId::BIGINT CompetitionId, s.Id::BIGINT Id, s.TeamId::BIGINT TeamId,
             strptime(s.SubmissionDate, '%m/%d/%Y')::DATE AS day,
             try_cast(s.PublicScoreFullPrecision AS DOUBLE) pub, try_cast(s.PrivateScoreFullPrecision AS DOUBLE) priv
      FROM read_csv('data/raw/Submissions.csv', header=true, all_varchar=true) s
      JOIN read_csv('data/raw/Teams.csv', header=true, all_varchar=true) t ON s.TeamId = t.Id
      WHERE t.CompetitionId IN (SELECT CompetitionId FROM ids) AND s.IsAfterDeadline='False' AND t.IsBenchmark='False'
        AND isfinite(try_cast(s.PublicScoreFullPrecision AS DOUBLE)) AND isfinite(try_cast(s.PrivateScoreFullPrecision AS DOUBLE))
      ORDER BY 1, 2) TO '{PARQ}' (FORMAT parquet, ROW_GROUP_SIZE 100000)""")
    print("extracted", con.sql(f"select count(*), count(distinct CompetitionId) from '{PARQ}'").fetchall(), flush=True)

done = set(pd.read_csv(OUT).CompetitionId) if os.path.exists(OUT) else set()
con = duckdb.connect()
for cid, m in c.iterrows():
    if cid in done: continue
    if time.time() - t0 > a.max_seconds:
        print(f"PAUSED: {len(done)} of {len(c)} done"); sys.exit(0)
    g = con.sql(f"select * from '{PARQ}' where CompetitionId={cid}").df()
    g["day"] = pd.to_datetime(g.day)
    r = dict(CompetitionId=cid, Cohort=m.CohortCode, Group=m.Group, Metric=m.Metric, MetricName=m.MetricName,
             Segment=m.HostSegmentTitle, CodeOnly=bool(m.CodeOnly), DeadlineYear=int(m.DeadlineYear), Deadline=m.Deadline,
             split_label=m.split_label, flagged=bool(m.flagged), higher_better=bool(m.MetricIsMax), n_analysis=len(g))
    if len(g) < 1000:                                                           # rule 3
        r["excluded"] = "rule3_fewer_than_1000"
    else:
        hb = bool(m.MetricIsMax)
        raw = g
        g = prepare_scores(g, m.Group)
        r.update(competition_measures(g, hb))
        r["excluded"] = "rule4_identical_scores" if r["share_identical"] >= 0.99 else ""
        if m.Group == "Accuracy" and not r["excluded"]:
            npub, fpub = infer_denominator(raw.pub); npriv, fpriv = infer_denominator(raw.priv)
            r.update(n_pub=npub, n_priv=npriv, fit_pub=fpub, fit_priv=fpriv)
            in_range = bool(raw.pub.between(0, 1).all() and raw.priv.between(0, 1).all())
            r["scores_in_0_1"] = in_range
            if npub and npriv and fpub == 1 and fpriv == 1 and in_range:   # 'every score fits'
                g = raw.assign(p=exact_pvalues(raw.pub, raw.priv, npub, npriv))
                nm, ns = null_top_decile_gap(raw.pub, raw.priv, npub, npriv, seed=int(cid))
                r.update(p05_all=float((g.p <= .05).mean()), p05_first=float((first_per_team(g).p <= .05).mean()),
                         p05_top10=float((top_decile(g, True).p <= .05).mean()),
                         top10_gap_null=nm, top10_gap_null_sd=ns, top10_gap_excess=r["top10_mean_gap"] - nm)
    row = pd.DataFrame([r])
    if os.path.exists(OUT):
        old = pd.read_csv(OUT); pd.concat([old, row], ignore_index=True).to_csv(OUT, index=False)
    else:
        row.to_csv(OUT, index=False)
    done.add(cid)
print("DONE", len(done), "competitions")
