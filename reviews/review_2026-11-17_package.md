# Review of the actual anonymous ZIP

17 November 2026. Inspected `anonymous_review_package.zip`, the package builder, README, comparison implementation, rebuild report and response. No raw scientific analysis was run and no post-deadline scores were read.

## Verdict

Two reproducibility defects need correction before handing this package to reviewers. Neither establishes that a scientific result is wrong. The supplied comparison cannot currently establish its advertised level of agreement, and the documented direct shell invocation is not supported by the ZIP's file permissions.

## 1. High priority: comparison silently ignores nonnumeric values

`scripts/compare_outputs.py` says nonnumeric columns are compared by equality, but its implementation never compares them. It checks shape, numeric differences and numeric missingness only. Column names/schema are not explicitly checked either. It reports absent tables but does not count them as failures.

I extracted the actual script from the ZIP and passed it two one-row tables:

```
reference: CompetitionId,label,value = 1,RANDOM,0.5
new:       CompetitionId,label,value = 1,TIME,0.5
```

The script printed `same 1` and exited 0. This is a concrete false pass on a scientifically meaningful label change.

**Fix:** compare complete schemas, nonnumeric values and their missingness, as well as numeric values with a declared tolerance. Handle infinities explicitly. Align rows using explicit table keys or a documented deterministic policy rather than assuming the first three columns form a key whenever CompetitionId exists. Define which missing/extra tables are expected historical artifacts and fail on unexpected omissions. Validate the checker with deliberately changed text, numeric values, missingness, schema and omitted files, then regenerate the comparison report.

The current report can support numeric agreement within the fields actually checked, but “33 tables identical” is stronger than demonstrated. It also uses a numeric tolerance; use “equal within the stated tolerance” where bytes differ. Existing tables may in fact agree fully, but that has not been established by this checker.

## 2. Moderate: ZIP does not preserve runner execution permission

The ZIP entry `run_all.sh` has Unix permissions 0600, with no executable bit. The package builder constructs new ZipInfo entries without explicitly setting executable permissions. I reproduced `PermissionError` by extracting the runner bytes, applying the advertised mode and directly invoking it. No analysis code executed.

The documented command `CLEAN=1 PY=.venv/bin/python ./run_all.sh` can therefore fail immediately on an extractor respecting these permissions.

**Fix:** either preserve/set a regular executable-file mode for this entry, or document `CLEAN=1 PY=.venv/bin/python bash run_all.sh` consistently. Test the final ZIP after extraction, not just the working directory. The latter invocation fixes permission handling only; it does not fix the comparison defect above.

## 3. Package completeness and clarity

The ZIP contains 123 files and all entries listed in its SHA-256 manifest match their hashes. I did not find the author's account, project name or home-directory paths in the inspected packaged text search. Public third-party repository links appear in source-description evidence, which is not itself an author-identity leak. This was a targeted inspection, not a guarantee of anonymity against arbitrary cross-linking or every binary metadata field.

The builder intentionally drops files that match identity strings. That prevents some leaks but can silently remove required reproducibility material. Several independent-review scripts are absent, including later synthetic deadline checks, while the README broadly advertises reviewer counterexamples and checks. Prefer portable, sanitised versions of the relevant scripts, or list exactly which checks are supplied as results only. Add a required-file assertion so identity filtering cannot quietly remove an executable required by the documented pipeline.

Historical reports remain useful, but earlier withdrawn interpretations should be explicitly marked as superseded or indexed with their status in the anonymous chronology. The package should let a reviewer distinguish the current claims from preserved historical outputs without needing the omitted review exchange.

## What this review does not establish

I did not execute the full pipeline from the ZIP, independently reproduce the newly updated 10,000-draw intervals in this turn, audit all binary metadata, check current venue rules, or perform a literature/novelty search. Prior verification of the 4,000-draw intervals and label hash remains as previously documented. The stage-by-stage rebuild report is now present, which improves the record, but its comparison needs the repair above.

The package is close enough to repair directly. Have the other assistant fix the two concrete defects and regenerate its comparison before asking the researcher to spend time on the full wrapper run. No new research analysis is needed to address these findings.

Synthetic checker fixtures and extracted comparison script are under `outputs/review/package/`; they contain no research scores. Only this review and isolated verification artifacts were added by the reviewer.
