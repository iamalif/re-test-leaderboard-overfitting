#!/bin/bash
if [[ "$1" == "scripts/stage3_extension.py" ]]; then
 case "$REVIEW_MODE" in
 fail) echo 'mock fatal error' >&2; exit 7 ;;
 missing) echo 'unexpected successful exit'; exit 0 ;;
 pause) if [[ ! -f "$REVIEW_MARKER" ]]; then touch "$REVIEW_MARKER"; echo 'PAUSED: mock'; exit 0; fi ;;
 esac
 echo 'DONE mock'
fi
exit 0
