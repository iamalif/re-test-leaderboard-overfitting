# Response to the review of the anonymous ZIP (`review_2026-11-17_package.md`)

Author: Claude. Date: 17 November 2026. All points accepted.

| Point | What was done |
|---|---|
| 1. Comparison ignored text values | Correct, and it mattered: "33 tables identical" was stronger than the tool could show. `compare_outputs.py` v2 checks schema, text, missingness, numbers with a declared tolerance, infinities, mixed columns; aligns rows on an explicit key or reports file order; classifies expected omissions; fails on unexpected ones. Self-test of 16 altered-table cases, including your RANDOM-to-TIME case, passes under pandas 2.3 and 3.1. v1 kept in `superseded/`. |
| 2. ZIP drops the executable bit | Zip entries now carry explicit modes (`run_all.sh` 755, others 644). All instructions use `bash run_all.sh` anyway. Checked on the extracted zip. |
| 3. Silent removal by identity filtering; status of historical reports | The builder now refuses to finish if any file the pipeline needs is missing (26 checked). `ANON_README.md` lists which reviewer checks ship with code and which as results only, and gives the status of each historical report. |

## What the stricter comparison found

Two things version 1 missed, neither a change in a result (details in `outputs/rebuild/clean_rebuild_report_2026-11-17.md`, addendum 2):

- `outputs/stage3/competition_measures.csv` had been built across two runs, so its column order and one bookkeeping column depended on run history. Regenerated in one run; the script now fixes the column order.
- A mixed text-and-number column in `outputs/stage4/code_only_tests.csv`, agreeing to about 1e-15.

After the fixes, Python 3.14 and Python 3.12 clean rebuilds both PASS against the project. No number in the paper changed.

Also done today and relevant to the package: Python 3.14 became the main environment, and the rebuild under it found that pandas 2.3 reads CSV numbers inexactly; two stage 1 and 2 scripts now read scores exactly (addendum 1 of the same report).

Outstanding: the researcher's own run of the package on their Mac, in progress.
