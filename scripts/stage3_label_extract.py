"""Stage 3 (blind): pull the sentences of each competition description that bear on how the
public/private split was made. Reads description text only; no scores.

Run from the project root:  python scripts/stage3_label_extract.py
Output: outputs/stage3/split_evidence_sentences.csv
"""
import re, duckdb, pandas as pd
c = duckdb.connect()
df = c.sql("""select k.Cohort, k.HostSegmentTitle seg, k.CompetitionId id, k.Slug slug, k.MetricGroup, k.CodeOnly,
 coalesce(c.Overview,'') ov, coalesce(c.DatasetDescription,'') dd
 from 'outputs/stage1/cohort_per_competition.csv' k
 join read_csv('data/raw/Competitions.csv',header=true,all_varchar=true) c on c.Id::bigint=k.CompetitionId
 where k.n_pre_both_nonbench>=1000 and k.LeaderboardPercentage between 1 and 99
   and (k.Cohort in ('extension_candidate','original_120')
        or (k.Cohort='in_window_not_in_original' and k.MetricGroup like 'Regression%'))""").df()
STRONG = re.compile(r"private (leaderboard|test|lb|set|data|score)|public (leaderboard|test|lb|set|score)|"
                    r"(second|2nd|final) stage|stage (2|two)|two[- ]stage|future data|forecasting phase|"
                    r"evaluation phase|after the (final )?(submission )?deadline|"
                    r"random(ly)? (split|select|sampl|divid|chosen|assign|partition)|split (by|on|based|according)|"
                    r"(time|temporal|chronological)[- ](based )?split|"
                    r"(later|subsequent|following|future) (time )?(period|weeks?|months?|days?|dates?|years?)", re.I)
WEAK = re.compile(r"time[- ]series|forecast|test (set|data) (is|are|was|were|contains?|consists?|covers?|comes?|includes?)|"
                  r"held[- ]out|unseen", re.I)
rows = []
for r in df.itertuples():
    txt = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)|\(https?://[^)]*\)", " ", r.ov + " \n " + r.dd)
    sents = [re.sub(r"\s+", " ", s).strip() for s in re.split(r"(?<=[.!?])\s+|\n+", txt)]
    strong = [s for s in sents if STRONG.search(s)]
    weak = [s for s in sents if WEAK.search(s) and s not in strong]
    pick = (strong[:3] + weak[:1]) if strong else weak[:2]
    rows.append(dict(id=r.id, cohort=r.Cohort[:3], seg=r.seg[:4], slug=r.slug, text_len=len(txt),
                     evidence=" // ".join(s[:230] for s in pick)))
out = pd.DataFrame(rows).sort_values("id"); out.to_csv("outputs/stage3/split_evidence_sentences.csv", index=False)
print(len(out), "competitions;", int((out.evidence == "").sum()), "with no split-related sentence;",
      int(out.evidence.str.len().sum()), "characters of evidence")
print(out.groupby(["cohort", "seg"]).agg(n=("id", "size"), none=("evidence", lambda x: (x == "").sum())))
