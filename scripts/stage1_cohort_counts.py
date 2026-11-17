"""Stage 1 supplement: metadata-only cohort counts. Counts submissions and score
presence; never reads score values or compares public with private scores.

Run from the project root:  python scripts/stage1_cohort_counts.py
Outputs: outputs/stage1/cohort_per_competition.csv, outputs/stage1/cohort_counts.csv
"""
import duckdb
RAW = "data/raw"
ORIG_END = "2019-04-04 23:59:59"   # latest deadline among the 120 published IDs
SNAPSHOT = "2026-11-15"            # Meta Kaggle download date
con = duckdb.connect()
con.execute("SET memory_limit='2GB'; SET temp_directory='/tmp/duck'")
con.execute(f"""
CREATE TEMP TABLE cnt AS
SELECT t.CompetitionId::BIGINT AS CompetitionId,
       count(*) FILTER (s.IsAfterDeadline='False') AS n_pre,
       count(*) FILTER (s.IsAfterDeadline='False' AND t.IsBenchmark='False'
                        AND coalesce(s.PublicScoreFullPrecision,'')<>''
                        AND coalesce(s.PrivateScoreFullPrecision,'')<>'') AS n_pre_both_nonbench,
       count(DISTINCT t.Id) FILTER (s.IsAfterDeadline='False' AND t.IsBenchmark='False') AS n_teams_nonbench
FROM read_csv('{RAW}/Submissions.csv', header=true, all_varchar=true) s
JOIN read_csv('{RAW}/Teams.csv', header=true, all_varchar=true) t ON s.TeamId = t.Id
GROUP BY 1""")
con.execute(f"""
CREATE TEMP TABLE c AS
SELECT p.CompetitionId, p.Slug, p.HostSegmentTitle, p.Deadline, p.DeadlineYear, p.Metric, p.MetricName,
  CASE WHEN p.Metric='CategorizationAccuracy' THEN 'Accuracy'
       WHEN p.Metric='AUC' THEN 'AUC'
       WHEN p.Metric IN ('MAP@{{K}}','MAP@k','MAP@3','AP@{{K}}','MAP@{{K}}_OLD') THEN 'MAP@K'
       WHEN p.Metric='LogLoss' THEN 'LogLoss'
       WHEN p.Metric IN ('MulticlassLoss','MulticlassLossOld') THEN 'MulticlassLoss'
       WHEN p.Metric IN ('RMSE','MAE','MSE','RMSLE') THEN 'Regression (RMSE/MAE/MSE/RMSLE)'
       WHEN try_cast(p.Metric AS BIGINT) IS NOT NULL THEN 'Numeric-ID metric (unmapped)'
       ELSE 'Other named metric' END AS MetricGroup,
  p.OnlyAllowKernelSubmissions AS CodeOnly, p.LeaderboardPercentage,
  cnt.n_pre, cnt.n_pre_both_nonbench, cnt.n_teams_nonbench,
  CASE WHEN p.CompetitionId IN (SELECT CompetitionId FROM 'data/reference/original_120_manifest.csv') THEN 'original_120'
       WHEN p.Deadline <= TIMESTAMP '{ORIG_END}' THEN 'in_window_not_in_original'
       WHEN p.Deadline <= TIMESTAMP '{SNAPSHOT}' THEN 'extension_candidate'
       ELSE 'not_ended' END AS Cohort
FROM 'outputs/stage0_per_competition.csv' p JOIN cnt USING (CompetitionId)
WHERE cnt.n_pre >= 1000""")
con.execute("COPY (SELECT * FROM c ORDER BY Deadline, CompetitionId) TO 'outputs/stage1/cohort_per_competition.csv' (HEADER)")
con.execute("""COPY (
SELECT Cohort, MetricGroup, count(*) AS eligible_1000_pre,
       count(*) FILTER (n_pre_both_nonbench>=1000) AS paired_nonbench_1000,
       count(*) FILTER (n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99) AS interior_split,
       count(*) FILTER (n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99 AND HostSegmentTitle<>'Community') AS interior_non_community,
       count(*) FILTER (n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99 AND CodeOnly) AS interior_code_only,
       count(*) FILTER (n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99 AND DeadlineYear>=2023) AS interior_2023_on
FROM c GROUP BY ALL ORDER BY 1,3 DESC) TO 'outputs/stage1/cohort_counts.csv' (HEADER)""")
print(con.sql("SELECT * FROM 'outputs/stage1/cohort_counts.csv'").df().to_string(index=False))
print(con.sql("""SELECT Cohort, count(*) eligible, count(*) FILTER (n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99) interior FROM c GROUP BY 1 ORDER BY 1""").df().to_string(index=False))
print(con.sql("""SELECT HostSegmentTitle, count(*) n, count(*) FILTER (CodeOnly) code_only FROM c WHERE Cohort='extension_candidate' AND n_pre_both_nonbench>=1000 AND LeaderboardPercentage BETWEEN 1 AND 99 GROUP BY 1 ORDER BY 2 DESC""").df().to_string(index=False))
