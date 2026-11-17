#!/bin/bash
# Rebuild every pipeline table and figure from data/raw/. Python 3.14 with requirements.txt (or Python 3.12 with
# requirements-py312.txt). Stops at the first failure. The run's code and inputs are recorded in
# outputs/run_manifest.json and every stage in outputs/run_ledger.jsonl, under one run identifier.
#
# Result tables are tracked in the repository and stage 3 resumes from its row store, so a plain run REUSES
# earlier work. For a clean rebuild:   CLEAN=1 PY=.venv/bin/python bash run_all.sh
# CLEAN=1 moves the pipeline outputs (outputs/stage0_per_competition.csv, outputs/stage1-4, outputs/stage6, the
# ledger) to outputs_previous_<time>/ and recomputes them. Reports and review files elsewhere in outputs/ stay.
# Afterwards compare:   python scripts/compare_outputs.py outputs_previous_<time> outputs
set -euo pipefail
PY=${PY:-python}
if [ "${CLEAN:-0}" = "1" ]; then
  prev=outputs_previous_$(date +%Y%m%d_%H%M%S); mkdir -p "$prev"
  for p in outputs/stage0_per_competition.csv outputs/stage1 outputs/stage2 outputs/stage3 outputs/stage4 outputs/stage6 outputs/run_ledger.jsonl outputs/run_manifest.json; do
    if [ -e "$p" ]; then mv "$p" "$prev/"; fi
  done
  echo "moved pipeline outputs to $prev"
fi
mkdir -p outputs/stage1 outputs/stage2 outputs/stage3 outputs/stage4 outputs/stage6 paper/figures
export RUN_ID=${RUN_ID:-run_$(date -u +%Y%m%dT%H%M%SZ)}
"$PY" scripts/run_manifest.py
S() { "$PY" scripts/run_stage.py "$@"; }
S scripts/stage0_feasibility.py
S scripts/stage1_reproduce.py --project .
S scripts/stage1_cohort_counts.py
S scripts/stage2_pilot_original.py
S scripts/stage3_label_extract.py
S scripts/stage3_build_labels.py
while true; do
  set +e; out=$(S scripts/stage3_extension.py --max-seconds 100000); status=$?; set -e
  echo "$out" | tail -2
  if [ $status -ne 0 ]; then echo "stage 3 failed with exit $status" >&2; exit $status; fi
  if echo "$out" | grep -q '^DONE'; then break; fi
  if ! echo "$out" | grep -q '^PAUSED'; then echo "stage 3 ended without DONE or PAUSED" >&2; exit 1; fi
done
S scripts/stage3_tests.py
S scripts/stage4_drift_robustness.py
S scripts/stage4_code_only.py
S scripts/stage5_figures.py
S scripts/stage6_review_response.py
S scripts/stage6_verify_review_numbers.py
S scripts/stage6_split_size_symmetry.py
S scripts/stage6_dependence_and_strata.py
echo "ALL DONE"
