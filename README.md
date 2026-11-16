# Re-testing leaderboard overfitting on Kaggle

Re-test of Roelofs et al., "A Meta-Analysis of Overfitting in Machine Learning" (NeurIPS 2019) on later Kaggle competitions. Target venue: TMLR. The research brief (15 Nov 2026) is the governing document; ask the researcher for it if it is not in this folder.

## Current state (2026-11-16)

- Stage 0 metadata feasibility completed; its cohort boundary/counts were provisional and have been corrected in the stage 1 reports.
- The researcher authorized stage 1. It is in progress; its completion gate has not passed.
- Original-only descriptive replication recovered all 120 competitions and the five named accuracy outliers. Formal verification remains open because of scoring sizes, ordering and p-value-definition issues.
- Read `outputs/stage1_audit_update.md` first, then `outputs/stage1_report.md` and `decision_log.md`.
- Allstate test file verified; OpenReview lead confirmed unrelated. Read outputs/allstate_verification_note.md. Original analysis code/configuration remains missing. The researcher prefers no author contact: proceed via the independent reanalysis route in outputs/independent_reanalysis_route.md. The unused email draft must not be sent.
- No new-competition score comparisons have been performed.

### Update 16 Nov 2026, about 03:15 (Claude, back on the project)

- Reviewed and re-checked the other assistant's stage 1 work; see "Takeover review by Claude" in `decision_log.md`.
- Extension boundary is now provisional: deadline after 2019-04-04 23:59 (the original snapshot dates from about 5-9 April 2019), not in the 120. Counts: `outputs/stage1/cohort_counts.csv`, from `scripts/stage1_cohort_counts.py` (metadata only).
- Stage 1 closed on delegated authority (see log). Stage 2 plan drafted: `analysis_plan/stage2_analysis_plan_DRAFT.md`. Measures in `scripts/stage2_measures.py`, piloted on the original 120 by `scripts/stage2_pilot_original.py` (outputs in `outputs/stage2/`).
- Plan fixed: `analysis_plan/stage2_analysis_plan_v1.0.md` (hashes in `analysis_plan/SHA256SUMS.txt`). Split labels done blind: `outputs/stage3/split_labels.csv`.
- Plan posted and archived 16 Nov 2026 (links in the decision log); extension unsealed and stage 3 run. Results: `outputs/stage3_report.md`.
- (Superseded) Waiting on the researcher: post the plan publicly (e.g. OSF). Until then no extension score may be read. After posting: write and run `scripts/stage3_extension.py` using `scripts/stage2_measures.py`, exactly as the plan says.

## Rules for whoever works here next

- Do not compare public and private scores for competitions after the original sample until the stage 2 analysis plan is written, dated and posted publicly. Stage 0 looked only at counts and score presence.
- Log every decision and its reason in `decision_log.md`; append, do not rewrite earlier entries.
- One script per stage in `scripts/`, run from the project root. Never edit `data/raw/`.
- No paid services, cloud compute or human participants.

## Layout

- `analysis_plan/` - plan v1.0 (fixed and archived before unsealing) and hashes
- `data/raw/` - Meta Kaggle CSVs (not in the repository; hashes in the decision log)
- `data/reference/` - original 120 IDs, split-label decisions
- `scripts/` - one or more scripts per stage, named `stageN_*.py`, run from the project root in numeric order
- `outputs/` - tables per stage, plus `stage1_report.md`, `stage3_report.md`, `stage4_report.md`
- `paper/` - draft and figures
- `decision_log.md` - every decision, deviation and result, in order

## Run

Python 3.12 with `requirements.txt`. One command rebuilds everything from `data/raw/` in the right order and stops on any failure:

    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    PY=.venv/bin/python ./run_all.sh

## Status, 16 November 2026 (latest)

Stages 0 to 5 done. An independent review (`reviews/review_2026-11-16.md`) led to a major revision of the paper's claims: see `reviews/response_2026-11-16.md`. Current paper: `paper/main.pdf` (v0.2); the pre-review version is `paper/main_v0.1_before_review.tex`. Results: `outputs/stage3_report.md` (planned), `outputs/stage4_report.md` and `outputs/stage6/` (exploratory). Older status notes above are kept for the record.
