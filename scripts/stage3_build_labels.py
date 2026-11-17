"""Stage 3: build outputs/stage3/split_labels.csv from the extracted sentences and the recorded reading decisions.
The table archived on 16 Nov 2026 was produced by these same steps run inline; this script makes that step reproducible.

Run from the project root, after stage3_label_extract.py:  python scripts/stage3_build_labels.py [--check]
--check compares the result with the archived hash and does not overwrite the file.
"""
from csvio import read_csv_exact   # exact CSV reading under any pandas version
import sys, hashlib, io, importlib.util, pandas as pd
spec = importlib.util.spec_from_file_location("d", "data/reference/split_label_decisions.py"); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
FLAGS = d.FLAGS
ev = read_csv_exact("outputs/stage3/split_evidence_sentences.csv").fillna("")
assert set(FLAGS) <= set(ev.id)
ev["split_label"] = [FLAGS[i][0] if i in FLAGS else ("NO_TEXT" if l < 200 else "UNSTATED") for i, l in zip(ev.id, ev.text_len)]
ev["label_reason"] = [FLAGS[i][1] if i in FLAGS else "" for i in ev.id]
ev["flagged"] = ev.split_label.isin(["TIME", "GROUP", "NEWDATA"])
ev["cohort"] = ev.cohort.map({"ori": "O", "ext": "E", "in_": "W"})
out = ev[["id", "cohort", "slug", "split_label", "flagged", "label_reason", "evidence"]].rename(columns={"id": "CompetitionId"})
buf = io.StringIO(); out.to_csv(buf, index=False); h = hashlib.sha256(buf.getvalue().encode()).hexdigest()
ARCHIVED = "edf340c395de553bb53086c811dc32ad3c4bb8d9313eb44f57455f155abab1b2"
print("sha256", h, "| matches archived table:", h == ARCHIVED)
if "--check" not in sys.argv: out.to_csv("outputs/stage3/split_labels.csv", index=False)
sys.exit(0 if h == ARCHIVED else 1)
