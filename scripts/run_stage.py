"""Run one pipeline stage and append a record to outputs/run_ledger.jsonl (added 17 Nov 2026).

    python scripts/run_stage.py scripts/stage3_tests.py [args...]

The record holds: the stage script and its SHA-256, the arguments, the git commit if available, Python and package
versions, start and end time (UTC), exit status, and the SHA-256 of every file under outputs/ and paper/figures/
created or changed by the stage. The stage's own output is passed through unchanged; the exit status is the stage's.
"""
import sys, os, json, time, hashlib, subprocess, platform, datetime
from importlib import metadata

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def snapshot():
    out = {}
    for root in ("outputs", "paper/figures"):
        for r, _, fs in os.walk(root):
            for f in fs:
                p = os.path.join(r, f)
                if p == os.path.join("outputs", "run_ledger.jsonl"): continue
                st = os.stat(p); out[p] = (st.st_mtime_ns, st.st_size)
    return out

script, args = sys.argv[1], sys.argv[2:]
try: commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
except Exception: commit = None
pk = {}
for name in ("duckdb", "pandas", "numpy", "scipy", "matplotlib", "pyarrow", "pypdf"):
    try: pk[name] = metadata.version(name)
    except metadata.PackageNotFoundError: pk[name] = None
before = snapshot(); t0 = time.time(); start = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
proc = subprocess.run([sys.executable, script] + args)
end = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"); after = snapshot()
changed = sorted(p for p, v in after.items() if before.get(p) != v)
rec = dict(stage=os.path.basename(script), args=args, script_sha256=sha(script), commit=commit, python=platform.python_version(),
           packages=pk, start_utc=start, end_utc=end, seconds=round(time.time() - t0, 1), exit=proc.returncode,
           outputs_changed={p: sha(p) for p in changed if not p.endswith(".parquet")},
           large_outputs_changed=[p for p in changed if p.endswith(".parquet")])
os.makedirs("outputs", exist_ok=True)
with open(os.path.join("outputs", "run_ledger.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
sys.exit(proc.returncode)
