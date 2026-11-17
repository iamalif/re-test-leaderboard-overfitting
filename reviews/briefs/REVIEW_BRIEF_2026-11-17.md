# Review brief: work since your v0.5 review

17 November 2026. Your review of v0.5 (`reviews/review_2026-11-17_v05.md`) covered the project up to commit `f96fd05`. Your package review (`reviews/review_2026-11-17_package.md`) looked at the zip built at `b1d807c`. Since then there are three commits, up to `b84486c`. The researcher asks for a critical, independent review of that work. As before, a real flaw found now is worth more than agreement.

## What changed

Read these first: `reviews/response_2026-11-17_v05.md`, `reviews/response_2026-11-17_package.md`, the decision log from "Review of v0.5 answered" onward, and `outputs/rebuild/clean_rebuild_report_2026-11-17.md` with its three addenda.

1. **Answers to your v0.5 review** (`b1d807c`). Group bootstrap re-run at the logged 10,000 draws (the 4,000-draw table is kept); paper states the exact grouping rule and the 365/247 counts; host-category split described as not matching; `run_all.sh` gained `CLEAN=1`; the Featured/Research table moved from an inline snippet into `scripts/stage4_code_only.py`; first anonymised package.
2. **Python 3.14 became the main environment** (`f36215a`). `requirements.txt` is now Python 3.14 with pandas 3.1, NumPy 2.5, SciPy 1.18 and DuckDB 2.0; `requirements-py312.txt` keeps the earlier set. The rebuild under 3.14 found that pandas 2.3's default CSV parser reads decimals inexactly (10,387 of 41,739 public scores in competitions 8900 and 10200 one rounding step off), while pandas 3.1 is exact. `stage1_reproduce.py` and `stage2_pilot_original.py` now read scores as text and convert with Python's `float()`. Four original-sample table rows changed; the claim is that no number in the paper did.
3. **Answers to your package review** (`b84486c`).
   - `scripts/compare_outputs.py` rewritten (v2; v1 in `superseded/`), with a 16-case `--selftest`.
   - Zip entries carry explicit file modes.
   - The package builder asserts that required files are present.
   - `ANON_README.md` gives the status of each historical report and lists which of your checks ship as results only.
4. **What the stricter comparison found** (`b84486c`). `outputs/stage3/competition_measures.csv` had been built across two runs of the stage 3 script, so its column order and the bookkeeping column `scores_in_0_1` depended on run history. It was regenerated in one run under 3.14 (old copy in `superseded/outputs_before_single_run/`), `stage3_extension.py` now writes a fixed column order, and downstream stages were re-run.
5. **Smoke test.** The researcher ran the zip on their own Mac (Python 3.14.2, fresh environment, `CLEAN=1 bash run_all.sh` as one process). Result: ALL DONE; comparison v2 PASS (34 same, 20 not rebuilt as expected, 1 known exception). Addendum 3 of the rebuild report.

## What most needs your scrutiny

- **The parsing finding and its fix.** Is the diagnosis right, and is it complete? Are there other places where pandas reads scores, or re-reads result tables, such that parser precision could still matter (signs of near-zero values, ties at a cutoff, the drift sign)? Does reading as text and calling `float()` handle every format in the raw files (empty strings, exponents, "nan", whitespace)?
- **The claim that no paper number changed.** Check the paper's numbers against the regenerated tables, especially anything from stages 1 and 2 (submission counts, outliers, inferred sizes, original-outlier reference gaps, pilot drift counts).
- **The regenerated stage 3 table.** Confirm that only column order and `scores_in_0_1` differ from the superseded copy, that the confirmatory results are unchanged, and that the fixed column order cannot drop or misplace a column.
- **Comparison tool v2.** Try to break it as you broke v1. In particular: key choice (`_key`) and whether it can align the wrong rows; mixed text-and-number columns; booleans; the tolerance; the `EXPECTED_NOT_REBUILT` patterns, which could hide a table that should have been rebuilt; and the `KNOWN_EXCEPTIONS` entry.
- **Two environments.** The rebuild report says 3.12 and 3.14 give the same tables. Is the evidence adequate, given that the 3.12 rebuild mixes stages run before and after the parsing fix (see the report)?
- **The package.** Does the zip still leak identity (code, CSV text, figure metadata, zip metadata)? Do the required-file assertion and the README's status tables match what is actually shipped?
- **Anything else** introduced in these three commits that weakens the record.

## Rules (unchanged)

- Do not edit `analysis_plan/`, recorded results, or the paper. Write your review to `reviews/review_<date>_<topic>.md` and any new outputs under `outputs/review/<topic>/`, labelled exploratory.
- Post-deadline scores remain unread; do not read them.
- No paid services, cloud compute, human participants, or contact with the original authors.
- Main environment: Python 3.14 with `requirements.txt`. Raw data in `data/raw/` (not in the repository).

## What to hand back

Findings ranked by severity. For each: what is wrong or unproven, the evidence (file, line, or a number you computed), and the fix. Separate errors from matters of judgement. Say plainly where you found nothing, and list what you did not check.
