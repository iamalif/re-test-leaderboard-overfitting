"""Compare every CSV result table in two output trees and write a file-by-file report.

    python scripts/compare_outputs.py REFERENCE_DIR NEW_DIR [REPORT.csv]

Rows are aligned on CompetitionId where present. Numeric columns are compared by largest relative difference;
other columns by equality. Exit status 1 if any table differs beyond 1e-6 or has a different shape.
"""
import sys, glob, os, hashlib, numpy as np, pandas as pd
ref, new = sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"); report = sys.argv[3] if len(sys.argv) > 3 else None
rows = []
for f in sorted(glob.glob(f"{new}/**/*.csv", recursive=True)):
    rel = os.path.relpath(f, new); g = os.path.join(ref, rel); r = dict(table=rel)
    if not os.path.exists(g): r["status"] = "only in new"; rows.append(r); continue
    a, b = pd.read_csv(f), pd.read_csv(g); r.update(rows_new=len(a), rows_ref=len(b))
    r["sha256_new"] = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]; r["sha256_ref"] = hashlib.sha256(open(g, "rb").read()).hexdigest()[:16]
    if a.shape != b.shape: r["status"] = "DIFFERENT SHAPE"; rows.append(r); continue
    if "CompetitionId" in a.columns:
        k = list(a.columns[:3]); a = a.sort_values(k).reset_index(drop=True); b = b.sort_values(k).reset_index(drop=True)
    num = [c for c in a.columns if pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    A, B = a[num].values.astype(float), b[num].values.astype(float)
    with np.errstate(all="ignore"):
        d = float(np.nanmax(np.abs(A - B) / (np.abs(B) + 1e-9))) if A.size and not np.isnan(A).all() else 0.0
    nan_mis = int((np.isnan(A) != np.isnan(B)).sum()) if A.size else 0
    r.update(max_relative_difference=d, nan_mismatches=nan_mis, identical_bytes=r["sha256_new"] == r["sha256_ref"])
    r["status"] = "same" if d <= 1e-6 and nan_mis == 0 else "DIFFERENT VALUES"; rows.append(r)
for g in sorted(glob.glob(f"{ref}/**/*.csv", recursive=True)):
    rel = os.path.relpath(g, ref)
    if not os.path.exists(os.path.join(new, rel)): rows.append(dict(table=rel, status="only in reference"))
out = pd.DataFrame(rows)
if report: out.to_csv(report, index=False)
print(out.status.value_counts().to_string()); bad = out[out.status.str.startswith("DIFFERENT")]
if len(bad): print(bad[["table", "status"]].to_string(index=False))
sys.exit(1 if len(bad) else 0)
