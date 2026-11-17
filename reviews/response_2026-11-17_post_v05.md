# Response to the review of post-v0.5 work (`review_2026-11-17_post_v05.md`)

Author: Claude. Date: 17 November 2026. All findings accepted. Two go further than requested, and one correction is my own.

| # | Finding | What was done |
|---|---|---|
| 1 | The team-flags exception waived any change | Went to the cause instead of checking an invariant: the stage 1 script wrote every registered team (1,385,785) while the stored file held the 101,661 with retained pre-deadline submissions. The script now writes exactly those, sorted. The exception is deleted; the file is compared like any other and is byte-identical in the final runs. |
| 2 | Tolerances hid identifier changes and sign flips | Comparison v3: every cell read as literal text; integers, labels, booleans and empty cells must be identical; decimals must share sign, zero status and finiteness and agree within rtol 1e-9, atol 1e-12; row key sets checked exactly before alignment; explicit pipeline scope and an explicit list of 4 historical files instead of patterns; no exceptions. 22-case self-test including your five false passes. |
| 3 | Parsing protection incomplete; stage 3 re-parses its own table | Went to the root: `scripts/csvio.py` is used by every script for every table read, and was checked to reproduce pandas' column types and values on every project table under pandas 2.3 and 3.1. Stage 3 appends exact JSON lines and writes the CSV once, with required-column, uniqueness and row-count checks. |
| 4 | Diagnostic population; two-environment provenance | Your count was right. My query had no deadline or benchmark filter; the diagnostic is now a saved script on the analysis population (7,544 and 7,157 of 26,985 misread under pandas 2.3; 0 under 3.1). Correction disclosed: that query passed 14,733 post-deadline public-score strings of two original competitions through the format comparison. "Never read" is replaced by "never analysed" throughout. Provenance: `scripts/run_stage.py` ledger; two complete fresh runs with one final code version (addendum 4). |
| 5 | Stage 3 "only column order differed" overstated | Corrected in the report: 571 `drift_mean` cells (and others) differed at float precision because of the old re-parse-and-rewrite cycle; no sign changed. |
| 6 | Paper numbers | Re-checked against the final tables; unchanged. Agree that pilot 78/117 and the paper's 77/114 are different sets; the paper uses 77/114. |
| 7 | Package | Builder now also requires `csvio.py`, `run_stage.py`, the parser diagnostic and the ledger. Rebuilt and re-verified. |

## Found along the way

My first version of `csvio.py` recognised only "True"/"False". DuckDB writes lowercase "true"/"false", so the notebook-only flag was read as text, and Python treats the non-empty string "false" as true. Comparison v3 caught it in the first final run (548 cells), before any output was stored. Fixed, then checked against pandas on every table before re-running. I should have run that equivalence check before using the reader.

## Result

Final Python 3.14 run: project outputs are now exactly its outputs (35 of 35 byte-identical). Final Python 3.12 run: PASS against it; every identifier, count, label, boolean, missing value and sign identical; 2,441 decimal cells differ within one part in 10^9. No number in the paper changed.

Outstanding: the researcher's smoke test of the final zip.
