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

- `data/raw/` — Meta Kaggle `Competitions.csv`, `Teams.csv`, `Submissions.csv` (downloaded 2026-11-15; SHA-256 in the decision log)
- `scripts/stage0_feasibility.py` — per-competition submission counts and score presence
- `outputs/stage0_per_competition.csv` — its output
- `requirements.txt` — pinned environment (Python 3.10, DuckDB, pandas)

## Run

    python -m venv .venv && .venv/bin/pip install -r requirements.txt
    .venv/bin/python scripts/stage0_feasibility.py

## Handover update — 16 November 2026

Stage 1 was explicitly authorized and is in progress; its completion gate has not passed. See `outputs/stage1_report.md` for findings and unresolved source checks. The original 120 IDs are in `data/reference/original_120_manifest.csv`. The official full paper is `data/reference/roelofs_2019_full.pdf`.

Run the original-only replication with `python3 scripts/stage1_reproduce.py --project .`; append `--from-cache` to reuse `outputs/stage1/original_predeadline_submissions.csv.gz`. Actual audit versions are recorded separately in `requirements-stage1.txt` and the run metadata. The original stage-0 requirements were not used for this run.

The original sample includes 18 competitions ending in 2019. Do not treat deadline year >= 2019 as a disjoint extension boundary. Continue to keep extension scores unexamined until the analysis plan is fixed and publicly posted.
