"""Compare the pipeline's result tables (CSV) and result files (JSON) in two output trees, cell by cell.
Version 4 (17 Nov 2026).

    python scripts/compare_outputs.py REFERENCE_DIR NEW_DIR [REPORT.csv [DIFFERENCES.csv]]
    python scripts/compare_outputs.py --selftest

REPORT.csv lists every file with its status. DIFFERENCES.csv lists every decimal cell that is not textually identical
but passes: file, row key, column, both values, absolute and relative difference.

Scope: outputs/stage0_per_competition.csv and every CSV under the pipeline directories (PIPELINE_DIRS). Files in
HISTORICAL are kept results that the pipeline does not rebuild; they may be absent from either tree. Any other missing or
extra pipeline table fails. Everything outside the pipeline (review/, rebuild/, stage5/, stage7/) is not compared.

Every cell is read as literal text (no missing-value guessing). A table passes only if column names and order match,
the set of row keys matches exactly, and every cell matches:
  - identical text: match;
  - otherwise, if either cell is empty, or an integer, or not a number: mismatch (identifiers, counts, labels,
    booleans and missing values must be exactly equal);
  - otherwise both are decimals: they must have the same sign (negative / zero / positive) and finiteness; if either
    column holds only whole numbers below 2**53 in the reference (a count written as a decimal, e.g. "10.0"), they
    must be equal; in p-value columns (P_COLUMNS) they must fall on the same
    side of 0.01, 0.05 and 0.10; and |a - b| <= 1e-12 + 1e-9 * |b|. Note that this is a combined absolute and
    relative tolerance, not a pure relative bound: for |b| below 1e-3 the absolute term dominates.
JSON result files (JSON_RESULTS) are compared field by field under the same cell rules; fields that describe the
environment or the run (JSON_IGNORE) are skipped. Figures are not compared: they are drawn from compared tables.
Rows are aligned on CompetitionId plus the first further key columns that make each row unique; tables without such
a key are compared in file order.
"""
import sys, os, re, glob, tempfile, math
import pandas as pd

RTOL, ATOL = 1e-9, 1e-12
PIPELINE_DIRS = ["stage1", "stage2", "stage3", "stage4", "stage6"]
PIPELINE_FILES = ["stage0_per_competition.csv"]
HISTORICAL = {   # kept results that the pipeline does not regenerate; may be absent from a rebuild
    "stage1/accuracy_size_evidence_register.csv": "assembled during stage 1; superseded in the paper by stage 6 tiers",
    "stage6/deadline_design_eligibility_metadata_only.csv": "count table for the withdrawn deadline design",
    "stage6/post_deadline_counts_metadata_only.csv": "count table for the withdrawn deadline design",
    "stage6/dependence_and_strata_4000draws.csv": "first run of the group bootstrap, kept after the 10,000-draw rerun",
}
KEY_EXTRA = ["TeamId", "Cohort", "Metric", "Group", "subset", "side", "candidate_denominator", "measure", "analysis", "group",
             "quantity", "test", "sample", "band", "metric", "cohort", "gap", "case", "post_per_team", "split", "role"]
_INT = re.compile(r"^[+-]?\d+$")
P_COLUMNS = re.compile(r"(^p$|^p_|_p$|pvalue|p_value|p_holm|^p05)")
THRESHOLDS = (0.01, 0.05, 0.10)
JSON_RESULTS = ["stage1/allstate_file_verification.json", "stage1/allstate_reconstructed_size_sensitivity.json",
                "stage1/synthetic_selection_check.json"]
JSON_IGNORE = {"python", "pandas", "numpy", "matplotlib", "scipy", "test_file_sha256"}


def _num(t):
    try: return float(t)
    except ValueError: return None


def integer_column(values):
    """True if every non-empty cell is a whole number below 2**53 in magnitude (a count written as a decimal)."""
    seen = False
    for t in values:
        if t == "": continue
        f = _num(t)
        if f is None or not math.isfinite(f) or not f.is_integer() or abs(f) >= 2 ** 53: return False
        seen = True
    return seen


def cell_match(u, v, pcol=False, intcol=False):
    if u == v: return True, None
    if u == "" or v == "" or _INT.match(u) or _INT.match(v): return False, "exact"
    fu, fv = _num(u), _num(v)
    if fu is None or fv is None: return False, "text"
    if math.isnan(fu) or math.isnan(fv): return (math.isnan(fu) and math.isnan(fv)), "nan"
    if math.isinf(fu) or math.isinf(fv): return fu == fv, "infinity"
    if (fu > 0) != (fv > 0) or (fu < 0) != (fv < 0): return False, "sign"
    if intcol: return fu == fv, "integer column"
    if pcol and any((fu <= t) != (fv <= t) for t in THRESHOLDS): return False, "p-value threshold"
    return abs(fu - fv) <= ATOL + RTOL * abs(fv), "tolerance"


def _key(a, b):
    if "CompetitionId" not in a.columns: return None
    k = ["CompetitionId"] + [c for c in KEY_EXTRA if c in a.columns]
    for n in range(1, len(k) + 1):
        if not a.duplicated(k[:n]).any() and not b.duplicated(k[:n]).any(): return k[:n]
    return None


def compare_tables(fa, fb):
    if open(fa, "rb").read() == open(fb, "rb").read(): return "same", dict(alignment="bytes identical", cells_within_tolerance=0)
    rd = lambda f: pd.read_csv(f, dtype=str, keep_default_na=False, na_filter=False)
    a, b = rd(fa), rd(fb)
    if list(a.columns) != list(b.columns): return "DIFFERENT COLUMNS", dict(detail=f"{list(a.columns)} vs {list(b.columns)}"[:300])
    if len(a) != len(b): return "DIFFERENT ROW COUNT", dict(detail=f"{len(a)} vs {len(b)}")
    k = _key(a, b)
    if k:
        if set(map(tuple, a[k].values)) != set(map(tuple, b[k].values)): return "DIFFERENT KEYS", dict(detail="row keys differ: " + "+".join(k))
        a = a.sort_values(k, kind="mergesort").reset_index(drop=True); b = b.sort_values(k, kind="mergesort").reset_index(drop=True)
        align = "key " + "+".join(k)
    else: align = "file order"
    probs, tol, diffs = {}, 0, []
    keys = a[k].astype(str).agg("|".join, axis=1).tolist() if k else [f"row {i}" for i in range(len(a))]
    for c in a.columns:
        pcol, icol = bool(P_COLUMNS.search(c)), integer_column(a[c].tolist())
        for i, (u, v) in enumerate(zip(a[c].tolist(), b[c].tolist())):
            ok, why = cell_match(u, v, pcol, icol)
            if not ok: probs[(c, why)] = probs.get((c, why), 0) + 1
            elif why == "tolerance":
                tol += 1; fu, fv = float(u), float(v)
                diffs.append(dict(key=keys[i], column=c, reference=u, new=v, abs_diff=abs(fu - fv), rel_diff=abs(fu - fv) / max(abs(fu), abs(fv))))
    detail = "; ".join(f"{c}: {n} cells differ ({w})" for (c, w), n in probs.items())[:500]
    return ("same" if not probs else "DIFFERENT VALUES"), dict(alignment=align, cells_within_tolerance=tol, detail=detail,
                                                               max_abs_diff=max((d["abs_diff"] for d in diffs), default=0.0),
                                                               max_rel_diff=max((d["rel_diff"] for d in diffs), default=0.0), _diffs=diffs)


def _flatten(x, prefix=""):
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k in JSON_IGNORE: continue
            out.update(_flatten(v, f"{prefix}{k}."))
        return out
    if isinstance(x, list):
        out = {}
        for i, v in enumerate(x): out.update(_flatten(v, f"{prefix}{i}."))
        return out
    return {prefix[:-1]: "" if x is None else (repr(x) if isinstance(x, float) else str(x))}


def compare_json(fa, fb):
    import json
    a, b = _flatten(json.load(open(fa))), _flatten(json.load(open(fb)))
    if set(a) != set(b): return "DIFFERENT FIELDS", dict(detail=str(sorted(set(a) ^ set(b)))[:300])
    probs, tol, diffs = {}, 0, []
    for k in sorted(a):
        ok, why = cell_match(a[k], b[k], bool(P_COLUMNS.search(k.split(".")[-1])), integer_column([a[k]]))
        if not ok: probs[(k, why)] = 1
        elif why == "tolerance":
            tol += 1; fu, fv = float(a[k]), float(b[k])
            diffs.append(dict(key="", column=k, reference=a[k], new=b[k], abs_diff=abs(fu - fv), rel_diff=abs(fu - fv) / max(abs(fu), abs(fv))))
    detail = "; ".join(f"{k}: {w}" for (k, w) in probs)[:500]
    return ("same" if not probs else "DIFFERENT VALUES"), dict(alignment="fields", cells_within_tolerance=tol, detail=detail,
                                                               max_abs_diff=max((d["abs_diff"] for d in diffs), default=0.0),
                                                               max_rel_diff=max((d["rel_diff"] for d in diffs), default=0.0), _diffs=diffs)


def _tables(root):
    out = {f for f in JSON_RESULTS if os.path.exists(os.path.join(root, f))}
    for f in PIPELINE_FILES:
        if os.path.exists(os.path.join(root, f)): out.add(f)
    for d in PIPELINE_DIRS:
        out |= {os.path.relpath(p, root) for p in glob.glob(os.path.join(root, d, "**", "*.csv"), recursive=True)}
    return out


def run(ref, new, report=None, diff_report=None):
    R, N = _tables(ref), _tables(new); rows = []; alldiffs = []
    for t in sorted(R | N):
        r = dict(table=t)
        if t not in N: r["status"] = "historical, not rebuilt" if t in HISTORICAL else "MISSING FROM NEW"
        elif t not in R: r["status"] = "historical, not rebuilt" if t in HISTORICAL else "ONLY IN NEW"
        else:
            st, d = (compare_json if t.endswith(".json") else compare_tables)(os.path.join(ref, t), os.path.join(new, t))
            for x in d.pop("_diffs", []): alldiffs.append(dict(file=t, **x))
            r.update(d); r["status"] = st
        rows.append(r)
    out = pd.DataFrame(rows)
    if report: out.to_csv(report, index=False)
    if diff_report: pd.DataFrame(alldiffs, columns=["file", "key", "column", "reference", "new", "abs_diff", "rel_diff"]).to_csv(diff_report, index=False)
    print(out.status.value_counts().to_string())
    bad = out[~out.status.isin(["same", "historical, not rebuilt"])]
    if len(bad): print("\nFAILURES:"); print(bad[[c for c in ("table", "status", "detail") if c in bad]].to_string(index=False)); return 1
    ntol = int(out.get("cells_within_tolerance", pd.Series([0])).fillna(0).sum())
    mx = out.get("max_rel_diff", pd.Series([0.0])).fillna(0).max(); ma = out.get("max_abs_diff", pd.Series([0.0])).fillna(0).max()
    print(f"\nRESULT: PASS ({int((out.status == 'same').sum())} result files match; {ntol} decimal cells differ within tolerance, "
          f"largest absolute difference {ma:.2g}, largest relative difference {mx:.2g})")
    return 0


def selftest():
    base = pd.DataFrame({"CompetitionId": [1, 2, 3], "label": ["RANDOM", "TIME", ""], "value": [0.5, float("nan"), float("inf")],
                         "n": [10, 20, 30], "flag": [True, False, True]})
    a = lambda **kw: base.assign(**kw)
    cases = {
        "identical": (base, base.copy(), "same"),
        "rows reordered": (base, base.iloc[::-1], "same"),
        "tiny decimal difference": (base, a(value=[0.5 + 1e-15, float("nan"), float("inf")]), "same"),
        "text changed": (base, a(label=["TIME", "TIME", ""]), "DIFFERENT VALUES"),
        "empty vs text": (base, a(label=["RANDOM", "TIME", "X"]), "DIFFERENT VALUES"),
        "literal NA vs NULL": (a(label=["NA", "TIME", ""]), a(label=["NULL", "TIME", ""]), "DIFFERENT VALUES"),
        "decimal changed": (base, a(value=[0.51, float("nan"), float("inf")]), "DIFFERENT VALUES"),
        "NaN vs number": (base, a(value=[0.5, 0.0, float("inf")]), "DIFFERENT VALUES"),
        "infinity sign": (base, a(value=[0.5, float("nan"), float("-inf")]), "DIFFERENT VALUES"),
        "sign flip within tolerance": (a(value=[1e-14, 1.0, 2.0]), a(value=[-1e-14, 1.0, 2.0]), "DIFFERENT VALUES"),
        "zero vs tiny": (a(value=[0.0, 1.0, 2.0]), a(value=[1e-15, 1.0, 2.0]), "DIFFERENT VALUES"),
        "integer changed": (base, a(n=[10, 20, 31]), "DIFFERENT VALUES"),
        "large identifier +1": (a(CompetitionId=[1000000000, 2, 3]), a(CompetitionId=[1000000001, 2, 3]), "DIFFERENT KEYS"),
        "boolean flipped": (base, a(flag=[False, False, True]), "DIFFERENT VALUES"),
        "code 001 vs 1": (a(label=["001", "x", ""]), a(label=["1", "x", ""]), "DIFFERENT VALUES"),
        "mixed column, tiny diff": (a(m=["96/127", "0.2988832674698108", ""]), a(m=["96/127", "0.29888326746981075", ""]), "same"),
        "mixed column, text diff": (a(m=["96/127", "0.29", ""]), a(m=["95/127", "0.29", ""]), "DIFFERENT VALUES"),
        "column renamed": (base, base.rename(columns={"n": "m"}), "DIFFERENT COLUMNS"),
        "column order": (base, base[["CompetitionId", "value", "label", "n", "flag"]], "DIFFERENT COLUMNS"),
        "row removed": (base, base.iloc[:2], "DIFFERENT ROW COUNT"),
        "no key, order changed": (base.drop(columns="CompetitionId"), base.drop(columns="CompetitionId").iloc[::-1], "DIFFERENT VALUES"),
        "p-value across 0.05": (a(p=[0.0499999999999, 0.5, 0.9]), a(p=[0.0500000000001, 0.5, 0.9]), "DIFFERENT VALUES"),
        "p-value same side": (a(p=[0.0400000000001, 0.5, 0.9]), a(p=[0.0400000000002, 0.5, 0.9]), "same"),
        "decimal-written count changed": (a(n=["10.0", "20.0", "30.0"]), a(n=["10.000000001", "20.0", "30.0"]), "DIFFERENT VALUES"),
        "team flag flipped (keyed by TeamId)": (pd.DataFrame({"TeamId": [1, 2], "CompetitionId": [5, 5], "IsBenchmark": [True, False]}),
                                                pd.DataFrame({"TeamId": [1, 2], "CompetitionId": [5, 5], "IsBenchmark": [False, False]}), "DIFFERENT VALUES"),
    }
    ok = True
    with tempfile.TemporaryDirectory() as d:
        for name, (x, y, want) in cases.items():
            fa, fb = os.path.join(d, "a.csv"), os.path.join(d, "b.csv"); x.to_csv(fa, index=False); y.to_csv(fb, index=False)
            got = compare_tables(fa, fb)[0]; ok &= got == want
            print(f"{'ok  ' if got == want else 'FAIL'} {name:36s} expected {want:20s} got {got}")
        for sub in ("r", "n"):
            for dd in ("stage3", "stage6", "review"): os.makedirs(os.path.join(d, sub, dd))
        for f in ("stage3/t.csv",): base.to_csv(os.path.join(d, "r", f), index=False); base.to_csv(os.path.join(d, "n", f), index=False)
        base.to_csv(os.path.join(d, "r", "stage3", "u.csv"), index=False)                                    # required, missing
        base.to_csv(os.path.join(d, "r", "stage6", "dependence_and_strata_4000draws.csv"), index=False)       # historical, missing
        base.to_csv(os.path.join(d, "r", "review", "x.csv"), index=False)                                     # outside scope
        print("-- tree: one table matches, one historical absent, one required table missing, one review file outside scope:")
        st = run(os.path.join(d, "r"), os.path.join(d, "n")); ok &= st == 1
        import json as _j
        ja, jb = os.path.join(d, "a.json"), os.path.join(d, "b.json")
        for name, (x, y, want) in {"json identical apart from versions": ({"python": "3.12", "rows": [{"n": 5, "p": 0.04}]}, {"python": "3.14", "rows": [{"n": 5, "p": 0.04}]}, "same"),
                                   "json p crosses 0.05": ({"rows": [{"p": 0.0499999999999}]}, {"rows": [{"p": 0.0500000000001}]}, "DIFFERENT VALUES"),
                                   "json count changed": ({"rows": [{"n": 5}]}, {"rows": [{"n": 6}]}, "DIFFERENT VALUES")}.items():
            _j.dump(x, open(ja, "w")); _j.dump(y, open(jb, "w")); got = compare_json(ja, jb)[0]; ok &= got == want
            print(f"{'ok  ' if got == want else 'FAIL'} {name:36s} expected {want:20s} got {got}")
    print("SELFTEST", "PASSED" if ok else "FAILED"); return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv: sys.exit(selftest())
    sys.exit(run(sys.argv[1].rstrip("/"), sys.argv[2].rstrip("/"), sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4] if len(sys.argv) > 4 else None))
