"""Compare every CSV result table in two output trees, cell by cell, and write a file-by-file report.

    python scripts/compare_outputs.py REFERENCE_DIR NEW_DIR [REPORT.csv]
    python scripts/compare_outputs.py --selftest

A table passes only if: same column names in the same order; same number of rows; after aligning rows, every text
cell is identical (missing values included) and every numeric cell agrees within rtol 1e-9, atol 1e-12 (NaN must
match NaN, infinities must match exactly). Rows are aligned on a key: CompetitionId plus any of KEY_EXTRA present,
if that combination is unique in both tables; otherwise in file order (reported).
Tables in EXPECTED_NOT_REBUILT may be missing from NEW_DIR; any other missing or extra table is a failure.
KNOWN_EXCEPTIONS are reported with their reason and do not fail the comparison.
Exit status 1 on any failure. Version 2 (17 Nov 2026); version 1 compared numeric columns only.
"""
import sys, os, glob, fnmatch, hashlib, tempfile, numpy as np, pandas as pd

RTOL, ATOL = 1e-9, 1e-12
KEY_EXTRA = ["Cohort", "Metric", "Group", "subset", "side", "candidate_denominator", "measure", "analysis", "group", "quantity",
             "test", "sample", "band", "metric", "cohort", "gap", "case", "post_per_team", "split", "role", "table"]
EXPECTED_NOT_REBUILT = ["review/*", "review/*/*", "review/*/*/*", "rebuild/*", "stage7/*", "stage1/accuracy_size_evidence_register.csv",
                        "stage6/*metadata_only.csv", "stage6/dependence_and_strata_4000draws.csv"]
KNOWN_EXCEPTIONS = {"stage1/original_team_flags.csv":
                    "intermediate list of teams; a fresh run lists every team of the 120 competitions, the shipped copy a subset; "
                    "the 359 benchmark teams with submissions are identical; nothing downstream differs (outputs/rebuild/)"}


def _key(a, b):
    if "CompetitionId" not in a.columns: return None
    k = ["CompetitionId"] + [c for c in KEY_EXTRA if c in a.columns]
    for n in range(1, len(k) + 1):
        kk = k[:n]
        if not a.duplicated(kk).any() and not b.duplicated(kk).any(): return kk
    return None


def compare_tables(fa, fb):
    """fa = reference file, fb = new file. Returns (status, detail dict)."""
    if open(fa, "rb").read() == open(fb, "rb").read(): return "same", dict(alignment="bytes identical", max_abs_diff=0.0)
    a, b = pd.read_csv(fa, keep_default_na=True), pd.read_csv(fb, keep_default_na=True)
    if list(a.columns) != list(b.columns): return "DIFFERENT COLUMNS", dict(detail=f"{list(a.columns)} vs {list(b.columns)}"[:300])
    if len(a) != len(b): return "DIFFERENT ROW COUNT", dict(detail=f"{len(a)} vs {len(b)}")
    k = _key(a, b)
    if k:
        a = a.sort_values(k, kind="mergesort").reset_index(drop=True); b = b.sort_values(k, kind="mergesort").reset_index(drop=True); align = "key " + "+".join(k)
    else: align = "file order"
    problems, maxdiff = [], 0.0
    for c in a.columns:
        x, y = a[c], b[c]
        xn, yn = pd.api.types.is_numeric_dtype(x) and not pd.api.types.is_bool_dtype(x), pd.api.types.is_numeric_dtype(y) and not pd.api.types.is_bool_dtype(y)
        if xn and yn:
            X, Y = x.to_numpy(float), y.to_numpy(float)
            if not np.array_equal(np.isnan(X), np.isnan(Y)): problems.append(f"{c}: missing values differ"); continue
            if not np.array_equal(np.isinf(X) & (X > 0), np.isinf(Y) & (Y > 0)) or not np.array_equal(np.isinf(X) & (X < 0), np.isinf(Y) & (Y < 0)):
                problems.append(f"{c}: infinities differ"); continue
            fin = np.isfinite(X)
            if fin.any():
                d = np.abs(X[fin] - Y[fin]); maxdiff = max(maxdiff, float(d.max()))
                if not np.all(d <= ATOL + RTOL * np.abs(Y[fin])): problems.append(f"{c}: numbers differ (max abs {d.max():.3g})")
        elif xn != yn:
            problems.append(f"{c}: column type differs")
        else:   # text, or mixed text and numbers: cell by cell; cells that read as numbers on both sides use the tolerance
            nt = nn = 0
            for u, v in zip(x.tolist(), y.tolist()):
                um, vm = pd.isna(u), pd.isna(v)
                if um or vm:
                    nt += um != vm; continue
                try: fu, fv = float(u), float(v)
                except (TypeError, ValueError): nt += str(u) != str(v); continue
                if np.isfinite(fu) and np.isfinite(fv):
                    maxdiff = max(maxdiff, abs(fu - fv)); nn += abs(fu - fv) > ATOL + RTOL * abs(fv)
                else: nn += not (fu == fv or (np.isnan(fu) and np.isnan(fv)))
            if nt: problems.append(f"{c}: {nt} text values differ")
            if nn: problems.append(f"{c}: {nn} numeric cells in a text column differ")
    return ("same" if not problems else "DIFFERENT VALUES"), dict(alignment=align, max_abs_diff=maxdiff, detail="; ".join(problems)[:500])


def run(ref, new, report=None):
    ref, new = ref.rstrip("/"), new.rstrip("/"); rows = []
    rel = lambda root: {os.path.relpath(f, root) for f in glob.glob(f"{root}/**/*.csv", recursive=True)}
    R, N = rel(ref), rel(new)
    for t in sorted(R | N):
        r = dict(table=t)
        if t not in N:
            exp = any(fnmatch.fnmatch(t, p) for p in EXPECTED_NOT_REBUILT)
            r["status"] = "not rebuilt (expected)" if exp else "MISSING FROM NEW"
        elif t not in R: r["status"] = "ONLY IN NEW"
        else:
            st, d = compare_tables(os.path.join(ref, t), os.path.join(new, t)); r.update(d)
            r["status"] = f"known exception: {KNOWN_EXCEPTIONS[t]}" if (st != "same" and t in KNOWN_EXCEPTIONS) else st
        rows.append(r)
    out = pd.DataFrame(rows)
    if report: out.to_csv(report, index=False)
    short = out.status.str.split(":").str[0]
    print(short.value_counts().to_string())
    bad = out[out.status.str.match(r"^[A-Z ]+$") & (out.status != "same")]
    if len(bad): print("\nFAILURES:"); print(bad[[c for c in ("table", "status", "detail") if c in bad]].to_string(index=False))
    else: print("\nRESULT: PASS (every rebuilt table matches; exceptions and expected omissions listed in the report)")
    return 0 if bad.empty else 1


def selftest():
    base = pd.DataFrame({"CompetitionId": [1, 2, 3], "label": ["RANDOM", "TIME", None], "value": [0.5, np.nan, np.inf], "n": [10, 20, 30]})
    cases = {
        "identical": (base, base.copy(), "same"),
        "rows reordered": (base, base.iloc[::-1], "same"),
        "tiny float difference": (base, base.assign(value=[0.5 + 1e-15, np.nan, np.inf]), "same"),
        "text changed": (base, base.assign(label=["TIME", "TIME", None]), "DIFFERENT VALUES"),
        "text missing vs present": (base, base.assign(label=["RANDOM", "TIME", "X"]), "DIFFERENT VALUES"),
        "number changed": (base, base.assign(value=[0.51, np.nan, np.inf]), "DIFFERENT VALUES"),
        "NaN vs number": (base, base.assign(value=[0.5, 0.0, np.inf]), "DIFFERENT VALUES"),
        "infinity sign": (base, base.assign(value=[0.5, np.nan, -np.inf]), "DIFFERENT VALUES"),
        "integer changed": (base, base.assign(n=[10, 20, 31]), "DIFFERENT VALUES"),
        "column renamed": (base, base.rename(columns={"n": "m"}), "DIFFERENT COLUMNS"),
        "column order": (base, base[["CompetitionId", "value", "label", "n"]], "DIFFERENT COLUMNS"),
        "row removed": (base, base.iloc[:2], "DIFFERENT ROW COUNT"),
        "mixed column, tiny diff": (base.assign(m=["96/127", "0.2988832674698108", None]), base.assign(m=["96/127", "0.29888326746981075", None]), "same"),
        "mixed column, text diff": (base.assign(m=["96/127", "0.29", None]), base.assign(m=["95/127", "0.29", None]), "DIFFERENT VALUES"),
        "mixed column, number diff": (base.assign(m=["96/127", "0.29", None]), base.assign(m=["96/127", "0.30", None]), "DIFFERENT VALUES"),
        "no key, order changed": (base.drop(columns="CompetitionId"), base.drop(columns="CompetitionId").iloc[::-1], "DIFFERENT VALUES"),
    }
    ok = True
    with tempfile.TemporaryDirectory() as d:
        for name, (x, y, want) in cases.items():
            fa, fb = os.path.join(d, "a.csv"), os.path.join(d, "b.csv"); x.to_csv(fa, index=False); y.to_csv(fb, index=False)
            got = compare_tables(fa, fb)[0]; ok &= got == want
            print(f"{'ok  ' if got == want else 'FAIL'} {name:28s} expected {want:20s} got {got}")
        for sub in ("r", "n"): os.makedirs(os.path.join(d, sub, "stage3")); os.makedirs(os.path.join(d, sub, "review"))
        base.to_csv(os.path.join(d, "r", "stage3", "t.csv"), index=False); base.to_csv(os.path.join(d, "n", "stage3", "t.csv"), index=False)
        base.to_csv(os.path.join(d, "r", "review", "x.csv"), index=False); base.to_csv(os.path.join(d, "r", "stage3", "u.csv"), index=False)
        print("-- tree with one expected and one unexpected missing table:")
        st = run(os.path.join(d, "r"), os.path.join(d, "n")); ok &= st == 1
    print("SELFTEST", "PASSED" if ok else "FAILED"); return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    sys.exit(run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))
