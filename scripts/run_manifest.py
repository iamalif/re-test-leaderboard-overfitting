"""Write outputs/run_manifest.json at the start of a pipeline run (added 17 Nov 2026).

Records a run identifier, the SHA-256 of every file under scripts/, data/reference/, the requirements files and
run_all.sh, the SHA-256 and size of the three raw Meta Kaggle files, and the Python and package versions.
Each ledger record of the run carries the same run identifier (environment variable RUN_ID).

    RUN_ID=<id> python scripts/run_manifest.py
"""
import os, sys, json, glob, hashlib, platform, datetime
from importlib import metadata

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""): h.update(b)
    return h.hexdigest()

files = sorted(set(glob.glob("scripts/**/*.py", recursive=True) + glob.glob("data/reference/*.*") +
                   ["run_all.sh"] + glob.glob("requirements*.txt")))
files = [f for f in files if "__pycache__" not in f and os.path.isfile(f)]
raw = {f: dict(sha256=sha(f), bytes=os.path.getsize(f)) for f in sorted(glob.glob("data/raw/*.csv"))}
pk = {}
for name in ("duckdb", "pandas", "numpy", "scipy", "matplotlib", "pyarrow", "pypdf"):
    try: pk[name] = metadata.version(name)
    except metadata.PackageNotFoundError: pk[name] = None
m = dict(run_id=os.environ.get("RUN_ID") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
         started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
         python=platform.python_version(), machine=platform.machine(), system=platform.system(), packages=pk,
         code={f: sha(f) for f in files}, raw_inputs=raw)
os.makedirs("outputs", exist_ok=True)
json.dump(m, open("outputs/run_manifest.json", "w"), indent=1)
print("run", m["run_id"], "|", len(files), "code and reference files,", len(raw), "raw inputs hashed")
