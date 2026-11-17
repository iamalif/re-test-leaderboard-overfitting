"""EXPLORATORY runner test: replace Python with a harmless stub; run no research analyses."""
import argparse,os,subprocess,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
stub=a.out/'mock_python.sh'; marker=a.out/'mock_stage3_failed.marker'
marker.unlink(missing_ok=True)
stub.write_text('''#!/bin/bash
if [[ "$1" == "scripts/stage3_extension.py" ]]; then
  if [[ ! -f "$REVIEW_FAILURE_MARKER" ]]; then
    touch "$REVIEW_FAILURE_MARKER"
    echo 'MOCK: fatal extraction error, exit 7' >&2
    exit 7
  fi
  echo 'DONE (mock only)'
fi
exit 0
''');stub.chmod(0o755)
env=os.environ.copy();env['PY']=str(stub);env['REVIEW_FAILURE_MARKER']=str(marker)
r=subprocess.run(['bash','run_all.sh'],cwd=a.project,env=env,text=True,capture_output=True,timeout=10)
(a.out/'runner_failure_probe.txt').write_text('EXPLORATORY MOCK TEST: no analysis scripts executed.\n'+r.stdout+'\nSTDERR\n'+r.stderr+'\nEXIT '+str(r.returncode)+'\n')
assert marker.exists() and r.returncode==0 and 'resuming stage 3' in r.stdout
print('Confirmed: a simulated fatal stage-3 exit is retried and the runner eventually prints ALL DONE.')
