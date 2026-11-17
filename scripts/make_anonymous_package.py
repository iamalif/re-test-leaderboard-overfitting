"""Build the anonymised review package: anonymous_package/ and anonymous_review_package.zip.

Copies code, plan, reference inputs and result tables; leaves out everything that names a person, account or machine
(decision log, README, reviews, superseded drafts, the unused author email); scans every copied text file for
identity strings and refuses to finish if any is found; writes a manifest with SHA-256 hashes.

Run from the project root:  python scripts/make_anonymous_package.py
"""
import os, re, shutil, hashlib, zipfile, sys
DEST = "anonymous_package"
INCLUDE = ["scripts", "run_all.sh", "requirements.txt", "analysis_plan/stage2_analysis_plan_v1.0.md", "analysis_plan/SHA256SUMS.txt",
           "data/reference/original_120_manifest.csv", "data/reference/split_label_decisions.py", "outputs", "paper/figures"]
EXCLUDE = re.compile(r"(__pycache__|\.DS_Store|\.parquet$|\.csv\.gz$|outputs/author_code_request\.md|scripts/make_anonymous_package\.py|"
                     r"outputs/stage1/[A-Za-z@]+_\d+\.png$|outputs/stage1/pvalues_\d+\.png$|outputs/stage5/label_audit_sentences\.txt)")
IDENT = re.compile(r"iamalif|re-test-leaderboard-overfitting|/Users/|/sessions/|Al Amin|alamin\.|@gmail|Codex", re.I)
DATA_OK = re.compile(r"outputs/stage0_per_competition\.csv|outputs/stage1/cohort_per_competition\.csv|outputs/stage3/split_|outputs/stage6/competition_clusters\.csv|"
                     r"outputs/stage1/original_sample_audit\.csv|outputs/review/revision/audit_full_source_text\.json|outputs/stage1/literature_check")   # public competition text / public links, not author identity
if os.path.exists(DEST): shutil.move(DEST, DEST + "_old_" + hashlib.md5(os.urandom(8)).hexdigest()[:6])
copied, dropped = [], []
for item in INCLUDE:
    files = [item] if os.path.isfile(item) else [os.path.join(r, f) for r, _, fs in os.walk(item) for f in fs]
    for f in sorted(files):
        if EXCLUDE.search(f): continue
        try: txt = open(f, encoding="utf-8").read()
        except UnicodeDecodeError: txt = None
        if txt is not None and IDENT.search(txt) and not DATA_OK.search(f):
            dropped.append((f, sorted(set(m.group(0) for m in IDENT.finditer(txt)))[:4])); continue
        os.makedirs(os.path.dirname(os.path.join(DEST, f)) or DEST, exist_ok=True); shutil.copy2(f, os.path.join(DEST, f)); copied.append(f)
for extra in ("ANON_README.md", "CHRONOLOGY.md"):
    shutil.copy2(os.path.join("anonymous_package_docs", extra), os.path.join(DEST, extra)); copied.append(extra)
with open(os.path.join(DEST, "MANIFEST_SHA256.txt"), "w") as m:
    for f in sorted(copied): m.write(hashlib.sha256(open(os.path.join(DEST, f), "rb").read()).hexdigest() + "  " + f + "\n")
# final scan of the package itself
bad = []
for r, _, fs in os.walk(DEST):
    for f in fs:
        p = os.path.join(r, f)
        try: t = open(p, encoding="utf-8").read()
        except UnicodeDecodeError: continue
        if IDENT.search(t) and not DATA_OK.search(p.replace(DEST + "/", "")): bad.append(p)
with zipfile.ZipFile("anonymous_review_package.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for r, _, fs in os.walk(DEST):
        for f in sorted(fs):
            p = os.path.join(r, f); zi = zipfile.ZipInfo(os.path.relpath(p, DEST), date_time=(2026, 11, 17, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(p, "rb").read())                       # fixed timestamps, no user or path metadata
print("copied", len(copied), "files; left out for identity strings:", len(dropped))
for f, why in dropped: print("  left out:", f, why)
print("identity strings remaining in package:", bad if bad else "none")
print("zip bytes:", os.path.getsize("anonymous_review_package.zip"))
sys.exit(1 if bad else 0)
