#!/bin/bash
# Rebuild every table and figure from data/raw/. Python 3.12 with requirements.txt. Stops at the first failure.
set -euo pipefail
PY=${PY:-python}
$PY scripts/stage0_feasibility.py
$PY scripts/stage1_reproduce.py --project .
$PY scripts/stage1_cohort_counts.py
$PY scripts/stage2_pilot_original.py
$PY scripts/stage3_label_extract.py
until $PY scripts/stage3_extension.py --max-seconds 100000 | tee /dev/stderr | grep -q '^DONE'; do echo "resuming stage 3"; done
$PY scripts/stage3_tests.py
$PY scripts/stage4_drift_robustness.py
$PY scripts/stage4_code_only.py
$PY scripts/stage5_figures.py
$PY scripts/stage6_review_response.py
$PY scripts/stage6_verify_review_numbers.py
echo "ALL DONE"
