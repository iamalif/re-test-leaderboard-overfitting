"""Run one pipeline stage and append a record to outputs/run_ledger.jsonl (added 17 Nov 2026).

    python scripts/run_stage.py scripts/stage3_tests.py [args...]

The record holds: the run identifier (RUN_ID), the stage script's SHA-256 taken before it runs and those of the
shared helpers, the arguments, the git commit if available, Python and package
versions, start and end time (UTC), exit status, and the SHA-256 of every file under outputs/ and paper/figures/
created or changed by the stage (detected by modification time and size), and files it deleted. Parquet extracts
are listed but not hashed. Intended for fresh, sequential runs; the run manifest (scripts/run_manifest.py) records all
code and input hashes once per run. The stage's own output is passed through unchanged; the exit status is the stage's.
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
script_hash_before = sha(script)   # hashed before running, so the record names the code that ran
before = snapshot(); t0 = time.time(); start = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
proc = subprocess.run([sys.executable, script] + args)
end = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"); after = snapshot()
changed = sorted(p for p, v in after.items() if before.get(p) != v)
HELPERS = ["scripts/csvio.py", "scripts/stage2_measures.py"]
rec = dict(run_id=os.environ.get("RUN_ID"), stage=os.path.basename(script), args=args, script_sha256=script_hash_before,
           helper_sha256={h: sha(h) for h in HELPERS if os.path.exists(h)}, commit=commit, python=platform.python_version(),
           packages=pk, start_utc=start, end_utc=end, seconds=round(time.time() - t0, 1), exit=proc.returncode,
           outputs_changed={p: sha(p) for p in changed if not p.endswith(".parquet")},
           outputs_deleted=sorted(set(before) - set(after)),
           large_outputs_changed=[p for p in changed if p.endswith(".parquet")])
os.makedirs("outputs", exist_ok=True)
with open(os.path.join("outputs", "run_ledger.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
sys.exit(proc.returncode)
