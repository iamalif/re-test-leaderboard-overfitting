"""Stage 0: feasibility gate.

Counts, per competition, the pre-deadline submissions in Meta Kaggle and whether
public and private scores are present. It never compares public with private
scores, so it reveals no post-2018 results.

Run from the project root:  python scripts/stage0_feasibility.py
Inputs : data/raw/{Competitions,Teams,Submissions}.csv
Outputs: outputs/stage0_per_competition.csv
"""
import duckdb

RAW = "data/raw"
con = duckdb.connect()
con.execute("SET memory_limit='2GB'; SET temp_directory='/tmp/duck'; SET preserve_insertion_order=false;")

con.execute(f"""
CREATE TEMP TABLE sub AS
SELECT TeamId::BIGINT AS TeamId,
       count(*)                                                        AS n_all,
       count(*) FILTER (pre)                                           AS n_pre,
       count(*) FILTER (pre AND pub <> '')                             AS n_pre_pub,
       count(*) FILTER (pre AND priv <> '')                            AS n_pre_priv,
       count(*) FILTER (pre AND pub <> '' AND priv <> '')              AS n_pre_both,
       count(*) FILTER (pre AND kv <> '')                              AS n_pre_from_kernel
FROM (SELECT TeamId, IsAfterDeadline = 'False' AS pre,
             coalesce(PublicScoreFullPrecision,'')  AS pub,
             coalesce(PrivateScoreFullPrecision,'') AS priv,
             coalesce(SourceKernelVersionId,'')     AS kv
      FROM read_csv('{RAW}/Submissions.csv', header=true, all_varchar=true))
GROUP BY 1
""")

con.execute(f"""
COPY (
SELECT c.Id::BIGINT AS CompetitionId, c.Slug, c.Title, c.HostSegmentTitle,
       try_strptime(c.DeadlineDate, '%m/%d/%Y %H:%M:%S') AS Deadline,
       year(try_strptime(c.DeadlineDate, '%m/%d/%Y %H:%M:%S')) AS DeadlineYear,
       c.EvaluationAlgorithmAbbreviation AS Metric, c.EvaluationAlgorithmName AS MetricName,
       c.EvaluationAlgorithmIsMax AS MetricIsMax,
       c.OnlyAllowKernelSubmissions, c.LeaderboardPercentage, c.HasLeaderboard,
       c.TotalTeams, c.TotalSubmissions,
       count(t.Id) AS n_teams_in_teams_csv,
       coalesce(sum(s.n_all),0)::BIGINT AS n_all, coalesce(sum(s.n_pre),0)::BIGINT AS n_pre,
       coalesce(sum(s.n_pre_pub),0)::BIGINT AS n_pre_pub,
       coalesce(sum(s.n_pre_priv),0)::BIGINT AS n_pre_priv,
       coalesce(sum(s.n_pre_both),0)::BIGINT AS n_pre_both,
       coalesce(sum(s.n_pre_from_kernel),0)::BIGINT AS n_pre_from_kernel
FROM read_csv('{RAW}/Competitions.csv', header=true, all_varchar=true) c
LEFT JOIN read_csv('{RAW}/Teams.csv', header=true, all_varchar=true) t ON t.CompetitionId = c.Id
LEFT JOIN sub s ON s.TeamId = t.Id::BIGINT
GROUP BY ALL ORDER BY Deadline
) TO 'outputs/stage0_per_competition.csv' (HEADER)
""")
print(con.execute("SELECT count(*), sum(n_all), sum(n_pre) FROM 'outputs/stage0_per_competition.csv'").fetchall())
print("orphan submissions (team not in Teams.csv):",
      con.execute(f"SELECT coalesce(sum(n_all),0) FROM sub WHERE TeamId NOT IN (SELECT Id::BIGINT FROM read_csv('{RAW}/Teams.csv', header=true, all_varchar=true))").fetchone())
