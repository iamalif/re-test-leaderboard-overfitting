# Review brief: work since your post-v0.5 review

17 November 2026. Your last review (`reviews/review_2026-11-17_post_v05.md`) covered the project up to commit `b84486c`. Everything after it is unreviewed. The researcher asks for a critical, independent review of that work. As before, a real flaw found now is worth more than agreement.

## Read first

- `reviews/response_2026-11-17_post_v05.md`: the response to your review.
- `outputs/rebuild/clean_rebuild_report_2026-11-17.md`, addenda 4 and 5. Addendum 4 supersedes the comparisons in addenda 1-3.
- `decision_log.md` from "Review of post-v0.5 work answered" to the end, including two corrections of record.

## What changed

1. **Comparison v3** (`scripts/compare_outputs.py`; v2 in `superseded/`). Every cell is read as literal text. Integers, labels, booleans and empty cells must be identical. Decimals must share sign, zero status and finiteness, and agree within rtol 1e-9, atol 1e-12. Row key sets are checked exactly. Scope is explicit (`PIPELINE_DIRS`, `PIPELINE_FILES`), with a list of 4 historical files and no exceptions. A 22-case `--selftest` includes your five false passes.
2. **Team flags.** `stage1_reproduce.py` now stores exactly the teams with retained pre-deadline submissions (101,661), sorted; the comparison exception is deleted.
3. **Exact CSV reading everywhere** (`scripts/csvio.py`, used for every table read). It was checked to reproduce pandas' column types and values on every project table under pandas 2.3 and 3.1. A first version misread DuckDB's lowercase booleans; v3 caught this on the first final run, before anything was stored.
4. **Stage 3 row store.** `stage3_extension.py` appends exact JSON lines and writes the CSV once, sorted by competition, with checks on required columns, uniqueness and row count.
5. **Execution ledger** (`scripts/run_stage.py`; used by `run_all.sh`). Per stage it records the script hash, arguments, Python and package versions, times, exit status, and hashes of the changed files. `CLEAN=1` now moves only pipeline outputs.
6. **Parser diagnostic** saved as `scripts/diagnostics/parser_precision_check.py`, on the analysis population: under pandas 2.3, 7,544 public and 7,157 private scores of 26,985 are misread; under 3.1, none.
7. **Final runs.** Fresh folders, one final code version, each fully ledgered: Python 3.14.8/pandas 3.1.1 and Python 3.12.15/pandas 2.3.3. Comparison v3 PASS between them, with 2,441 decimal cells within tolerance. Project pipeline outputs were replaced by the 3.14 run's outputs, 35 of 35 byte-identical.
8. **Researcher's smoke test of the final zip** on macOS, Python 3.14.2, `CLEAN=1 bash run_all.sh` as one process: ALL DONE; v3 PASS, with 663 decimal cells within tolerance.
9. **Corrections of record.**
   - "No post-deadline score has been read" became "none has been analysed". Pipeline steps load all submissions before filtering, and the first parser check passed 14,733 post-deadline public-score strings of two original competitions through a format comparison without computing anything from them.
   - The runs cover two operating systems and two Python/pandas generations on ONE physical machine (Apple Silicon); the assistant's Linux environment is a virtual machine on the researcher's Mac. An earlier claim of "two processor architectures" was wrong.
10. **Paper:** the reproducibility sentence now says the two environments agree exactly in identifiers, counts, labels and signs, and in decimals to within 1e-9.

## What most needs your scrutiny

- **Comparison v3.** Try to break it as you broke v1 and v2. Gaps I know of:
  - figures (PNG/PDF) and JSON outputs such as `stage1/*.json` are not compared at all;
  - "nan" and "NaN" spellings count as equal;
  - `_key` falls back to file order for tables without a unique key;
  - the scope excludes `stage5/` and `stage7/`.

  Are any of these material? Is there a decision-relevant quantity that the sign rule plus tolerance can still miss, for example a threshold such as p <= 0.05 stored only as a decimal?
- **csvio.** Is "same types and values as pandas on every current table" enough? What inputs would make it diverge from pandas: dates, large integers, leading zeros, "inf", quoted numbers?
- **Stage 3 row store.** Resume behaviour after a PAUSED run; JSON handling of NaN, infinity and numpy types; the effect of the new row order on downstream scripts. Could the row-count assertion fail legitimately?
- **Team-flags filter.** At that point in `stage1_reproduce.py`, is `d` exactly the retained pre-deadline set? Could the filter drop a benchmark team that the analysis needs?
- **Ledger.** It detects changed files by modification time and size: can it miss a change or misattribute one? Is it adequate provenance for the claim in addendum 4?
- **Corrections of record.** Is "never analysed" accurate everywhere it now appears, in the log, the paper, `ANON_README.md` and `CHRONOLOGY.md`? Is anything else in the record overstated in the same way?
- **The tolerance counts.** Are 2,441 and 663 decimal cells within tolerance plausibly just floating-point rounding? A check of their largest relative differences, and of which tables they sit in, would help.
- **Anything else** in these commits that weakens the record or the package.

## Rules (unchanged)

- Do not edit `analysis_plan/`, recorded results or the paper. Write your review to `reviews/review_<date>_<topic>.md`, and any new outputs under `outputs/review/<topic>/`, labelled exploratory.
- Do not read, and certainly do not analyse, post-deadline scores.
- No paid services, cloud compute, human participants, or contact with the original authors.
- Main environment: Python 3.14 with `requirements.txt`. Raw data in `data/raw/` (not in the repository).

## What to hand back

Findings ranked by severity. For each: what is wrong or unproven, the evidence (file, line, or a number you computed), and the fix. Separate errors from matters of judgement. Say plainly where you found nothing, and list what you did not check.
