"""Stage 5: audit sample for the split labels. Draws 50 unflagged O/E competitions (seed 20261116) and prints,
for each, every description sentence that mentions the test data, leaderboards, splitting, time or groups -
a much wider net than the one used for the original labelling.

Run from the project root:  python scripts/stage5_label_audit_sample.py > outputs/stage5/label_audit_sentences.txt
"""
import re, duckdb, pandas as pd
lab = pd.read_csv("outputs/stage3/split_labels.csv")
s = lab[(~lab.flagged) & lab.cohort.isin(["O", "E"])].sample(50, random_state=20261116).sort_values("CompetitionId")
tx = duckdb.connect().sql("select Id::bigint id, coalesce(Overview,'')||' \n '||coalesce(DatasetDescription,'') t from read_csv('data/raw/Competitions.csv',header=true,all_varchar=true)").df().set_index("id").t
WIDE = re.compile(r"test|leaderboard|private|public (score|lb|set)|split|held|hold-?out|future|later|stage|phase|unseen|subjects?|patients?|chronolog|time[- ]series|forecast", re.I)
for r in s.itertuples():
    t = re.sub(r"<[^>]+>|!\[[^\]]*\]\([^)]*\)|\(https?://[^)]*\)", " ", tx[r.CompetitionId])
    ss = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"(?<=[.!?])\s+|\n+", t)]
    hits = [x[:170] for x in ss if WIDE.search(x) and len(x) > 15]
    print(f"{r.CompetitionId}|{r.cohort}|{r.slug[:30]}|{r.split_label}|len={len(t)}|" + " // ".join(hits)[:800])
