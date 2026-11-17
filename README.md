# Re-testing leaderboard overfitting on Kaggle

A pre-registered re-test of Roelofs et al., "A Meta-Analysis of Overfitting in Machine Learning" (NeurIPS 2019), on Kaggle competitions that ended after the original sample. Target venue: TMLR.

## Status (17 November 2026)

- Paper: `paper/main.pdf` (v0.9, 13 pages including references and appendix; source `paper/main.tex`, generated appendix `paper/appendix_secondary.tex`).
- Analysis plan v1.0, fixed and archived publicly on 16 Nov 2026 before any later-competition score was examined: `analysis_plan/`.
- All results are rebuilt from the raw data by one command (below). Clean runs under Python 3.14 and 3.12 agree, and a smoke test of the review package passed on macOS (`outputs/rebuild/`).
- Remaining before submission: the researcher's read-through, and venue-specific preparation.

## Layout

- `analysis_plan/`: plan v1.0 and its SHA-256 hashes. Never edited after archiving.
- `data/raw/`: Meta Kaggle CSVs, downloaded 15 Nov 2026 (not in the repository; Apache 2.0; hashes in `decision_log.md` and the package README).
- `data/reference/`: the original 120 competition IDs and the split-label decisions (third-party PDFs and the optional Allstate test file are kept locally, not in the repository).
- `scripts/`: one script per stage (`stageN_*.py`), shared code (`stage2_measures.py`, `csvio.py`), run and provenance tools (`run_stage.py`, `run_manifest.py`, `compare_outputs.py`), package and appendix builders, `diagnostics/`.
- `outputs/`: result tables per stage; stage reports (`stage1_report.md`, `stage3_report.md`, `stage4_report.md`); `run_ledger.jsonl` and `run_manifest.json` of the run that produced them; `rebuild/` (reproducibility evidence); `review/` (checks run during review).
- `paper/`: manuscript, figures, bibliography, TMLR style files; `paper/versions/` keeps earlier drafts.
- `reviews/`: every critical review of the work and the response to it, plus the review briefs (`reviews/briefs/`). The paper refers to this review history; keep it.
- `anonymous_package_docs/`: README and chronology for the anonymised review package; `anonymous_review_package.zip` is built by `scripts/make_anonymous_package.py` (not in the repository).
- `superseded/`: withdrawn or replaced material, kept for the record (deadline addendum and its scripts, earlier comparison tools, the unused author email draft, which must not be sent).
- `decision_log.md`: every decision, deviation and correction, in order.

## Run

Python 3.14 with `requirements.txt` (or Python 3.12 with `requirements-py312.txt`). One command rebuilds every table and figure from `data/raw/` and stops on any failure:

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    CLEAN=1 PY=.venv/bin/python bash run_all.sh

Then `python scripts/compare_outputs.py outputs_previous_<time> outputs` compares the new tables with the previous ones. To rebuild the paper's appendix: `python scripts/make_appendix_secondary.py`; to build the review package: `python scripts/make_anonymous_package.py`.

## Rules for whoever works here next

- Do not edit `analysis_plan/`, `data/raw/` or archived results. Any departure from the plan is logged in `decision_log.md` and reported in the paper.
- Append to `decision_log.md`; never rewrite earlier entries.
- No post-deadline public and private scores are compared (the deadline contrast was withdrawn).
- No paid services, cloud compute or human participants. Do not contact the original authors.
