#!/bin/bash
if [[ "$1" == "scripts/stage3_extension.py" ]]; then
  if [[ ! -f "$REVIEW_FAILURE_MARKER" ]]; then
    touch "$REVIEW_FAILURE_MARKER"
    echo 'MOCK: fatal extraction error, exit 7' >&2
    exit 7
  fi
  echo 'DONE (mock only)'
fi
exit 0
