# Review brief for the second assistant

16 November 2026. You did the stage 1 reconstruction of this project. Since then the other assistant (Claude) closed stage 1, fixed and archived an analysis plan, ran it on the later competitions, and drafted the paper. The researcher wants your critical, independent review before anything is submitted to TMLR. The goal is a paper that is correct and defensible; finding a real flaw now is the most useful thing you can do.

## What to read, in this order

1. `paper/main.pdf` - the draft (7 pages).
2. `analysis_plan/stage2_analysis_plan_v1.0.md` - the plan, archived publicly before any later-competition score was read.
3. `outputs/stage3_report.md` (planned results) and `outputs/stage4_report.md` (exploratory follow-ups).
4. `decision_log.md` from "Takeover review by Claude" onward - every decision and deviation.
5. Code: `scripts/stage2_measures.py` (all measures), `scripts/stage3_extension.py`, `scripts/stage3_tests.py`, `scripts/stage4_*.py`.

## What most needs your scrutiny

- **The drift measure.** The main new claim is that teams' later submissions favour the public leaderboard more than their earlier ones (positive in 68% of 481 later competitions), and that this indicates adaptation. Try to break it. Is there an explanation other than adaptation that survives the four robustness checks in `outputs/stage4_report.md`? Is the simulation in `scripts/stage2_pilot_original.py` too friendly to the measure?
- **Inferred test-set sizes.** Sizes are taken as the smallest count on which every accuracy score is a whole number (`infer_denominator`). Check the logic and the 11 disagreements with the published sizes, especially 7042 and 7634, where the inferred totals are far smaller than published.
- **Whether the plan was really blind.** Before archiving, only counts, metric names, dates and description text of later competitions were examined. Check the log and scripts for anything that contradicts this.
- **The scoped headline.** The confirmatory tests cover accuracy and AUC competitions, now mostly in-class. The exploratory finding that prize competitions show larger gaps since 2019 is reported as open. Is that wording fair, or does it under- or over-claim?
- **Your own stage 1 work as used in the paper.** Section 3 relies on it. Confirm it is represented accurately, including the Allstate account.
- **Statistics.** Competition as the unit; medians, sign tests and Mann-Whitney tests; Holm correction over four tests; bootstrap intervals. Anything misapplied?
- **Split labels.** One reader, sparse host statements, 44 of 516 flagged. Is the limitation stated strongly enough?

## Rules

- Do not edit `analysis_plan/`, `outputs/stage3/`, or anything already committed that records results. Put your review in a new file, `reviews/review_<date>.md`.
- You may run any script and write new analyses, but put new outputs under `outputs/review/` and label them exploratory.
- Never state that something is novel without a fresh search; say what you searched and when.
- No paid services, cloud compute or human participants. Do not contact the original authors.
- Environment: Python 3.12 with `requirements.txt`. Raw data is in `data/raw/` (not in the repository).

## What to hand back

A review with findings ranked by severity. For each: what is wrong or unproven, the evidence (file, line, or a number you computed), and what would fix it. Separate errors from matters of judgement. Say plainly if you found nothing serious in an area, and list what you did not check.
