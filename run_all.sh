#!/bin/bash
# Rebuild every table and figure from data/raw/. Python 3.12 with requirements.txt. Stops at the first failure.
# Result tables are tracked in the repository and stage 3 skips competitions it finds already recorded, so a plain
# run in a checkout REUSES them. For a clean rebuild run:   CLEAN=1 PY=.venv/bin/python ./run_all.sh
# CLEAN=1 moves the existing outputs/ aside to outputs_previous_<time>/ and recomputes everything from data/raw/.
# Afterwards compare:   python scripts/compare_outputs.py outputs_previous_<time> outputs
set -euo pipefail
PY=${PY:-python}
if [ "${CLEAN:-0}" = "1" ]; then
  prev=outputs_previous_$(date +%Y%m%d_%H%M%S); mv outputs "$prev"; echo "moved existing outputs to $prev"
fi
mkdir -p outputs/stage1 outputs/stage2 outputs/stage3 outputs/stage4 outputs/stage6 paper/figures
$PY scripts/stage0_feasibility.py
$PY scripts/stage1_reproduce.py --project .
$PY scripts/stage1_cohort_counts.py
$PY scripts/stage2_pilot_original.py
$PY scripts/stage3_label_extract.py
$PY scripts/stage3_build_labels.py
while true; do
  set +e; out=$($PY scripts/stage3_extension.py --max-seconds 100000); status=$?; set -e
  echo "$out" | tail -2
  if [ $status -ne 0 ]; then echo "stage 3 failed with exit $status" >&2; exit $status; fi
  if echo "$out" | grep -q '^DONE'; then break; fi
  if ! echo "$out" | grep -q '^PAUSED'; then echo "stage 3 ended without DONE or PAUSED" >&2; exit 1; fi
done
$PY scripts/stage3_tests.py
$PY scripts/stage4_drift_robustness.py
$PY scripts/stage4_code_only.py
$PY scripts/stage5_figures.py
$PY scripts/stage6_review_response.py
$PY scripts/stage6_verify_review_numbers.py
$PY scripts/stage6_split_size_symmetry.py
$PY scripts/stage6_dependence_and_strata.py
echo "ALL DONE"
