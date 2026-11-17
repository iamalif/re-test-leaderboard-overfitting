"""Diagnostic (not part of the pipeline): how often does pandas' default CSV parser differ from Python's correctly
rounded float() on the score strings of competitions 8900 and 10200? Added 17 Nov 2026.

Population: pre-deadline submissions of non-benchmark teams with a non-empty public score - the rows the analysis uses.
(The figure first quoted on 17 Nov, 10,387 of 41,739, came from a query without these two filters and therefore also
passed 14,733 post-deadline public-score strings of these two original competitions through the parser comparison.
No gap or other quantity was computed from them; private scores were not involved.)

    python scripts/diagnostics/parser_precision_check.py
"""
import io, sys, hashlib, duckdb, pandas as pd
raw = duckdb.sql("""select s.PublicScoreFullPrecision p, s.PrivateScoreFullPrecision q
  from read_csv('data/raw/Submissions.csv', header=true, all_varchar=true) s
  join read_csv('data/raw/Teams.csv', header=true, all_varchar=true) t on s.TeamId = t.Id
  where t.CompetitionId in ('8900','10200') and s.IsAfterDeadline = 'False' and t.IsBenchmark = 'False'
    and s.PublicScoreFullPrecision <> '' and s.PrivateScoreFullPrecision <> ''""").df()
for col in ("p", "q"):
    csv = "x\n" + "\n".join(raw[col]) + "\n"
    exact = raw[col].map(float).values
    v = pd.read_csv(io.StringIO(csv)).x.values
    print(f"python {sys.version.split()[0]}, pandas {pd.__version__}: {'public' if col == 'p' else 'private'} scores, "
          f"{int((v != exact).sum())} of {len(v)} differ from Python's float()")
