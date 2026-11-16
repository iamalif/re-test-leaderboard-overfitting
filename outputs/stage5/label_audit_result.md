# Split-label audit (16 November 2026)

Sample: 50 unflagged competitions from O and E, drawn with seed 20261116 by `scripts/stage5_label_audit_sample.py`. For each, every description sentence mentioning test data, leaderboards, splitting, time, stages or groups was listed (`label_audit_sentences.txt`, first 800 characters of matches per competition) and read.

Result: 0 of 50 labels changed. No sampled description states that the private set was drawn or scored differently from the public set. Several describe a train/test difference (for example 14313 split by molecule, 39222 different opponents, 19018 different languages), which the rubric does not flag.

Limits: same reader as the original labelling; long descriptions were truncated at 800 characters of matching sentences. With 0 misses in 50, a miss rate above about 6% among unflagged competitions is unlikely (95% bound, 3/n rule).
