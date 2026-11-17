# Review: comparison v3, exact reader, row store and final-run provenance

17 November 2026. Read the response to the post-v0.5 review, rebuild addenda 4–5, latest decision-log corrections, current implementations and packaged chronology. Checks used synthetic inputs and existing pre-deadline artifacts only. No post-deadline score was read or analysed by this review.

## Assessment

The previous concrete failures involving literal identifiers, sign changes, NA/NULL labels and the blanket team-flags exception are repaired. The retained execution evidence is substantially stronger. I found no new changed scientific result. Remaining findings concern decision-aware comparison, claims about precision and untouched data, and defensive handling of the new reader. They should be corrected without reopening the substantive analysis.

## 1. Material verification limitation: v3 still permits threshold changes

**Confirmed:** `cell_match('0.0499999999999', '0.0500000000001')` returns true. Both values have the same sign but are on opposite sides of p<=0.05. A generic sign check therefore does not establish that every decision is identical. The old false-pass cases are repaired; this is the further limitation explicitly identified in the brief.

The implementation also decides whether a field is an integer from its spelling, not its schema. `cell_match('10.0', '10.000000001')` passes. Thus an integer-valued count written with a decimal point is not protected by the claimed exact-count rule. Some result tables represent counts as decimals because other rows have missing entries.

**Fix:** retain tolerance for continuous estimates, but add table/column-specific invariants for IDs, counts and booleans regardless of formatting, and compare every decision used in downstream claims: thresholds, inclusion rules and relevant ties. For p-values, compare the boolean p<=0.05 (and adjusted-p rejection indicators where relevant) alongside numeric agreement. This does not require declaring all floating-point variation an error.

I found no evidence that a real current threshold decision changed; the fixtures show what PASS does not guarantee. The 22-case self-test passes. `_key` checks exact key sets and the no-unique-key fallback is conservative for row permutations; I found no demonstrated silent row misalignment.

Minor edge case: `1e-400` and `2e-400` pass because both underflow to binary zero. This is not known to occur in the present compared tables; it limits claims of exact zero status for arbitrary decimal strings. `nan` and `NaN` equality is reasonable for declared numeric missing values, but literal categorical strings require a schema if spelling itself is meaningful.

## 2. Material reporting correction: the untouched-data wording is not updated throughout

`paper/main.tex:190` still says the contrast was withdrawn “before reading any data” and “Post-deadline scores remain unexamined.” This conflicts with the disclosed parser comparison involving 14,733 post-deadline public-score strings. The response says the correction was made throughout; that is not true of the current manuscript source.

The decision log and packaged `CHRONOLOGY.md` disclose the incident, which is good. But “without computing anything from them” and an unqualified “never analysed” are too broad: conversion discrepancies were computed from those strings. That was a numerical-format diagnostic, not a gap, drift or deadline-hypothesis analysis. State that distinction directly rather than relying on an elastic definition of “analysed.”

**Suggested substance:** “The deadline analysis was withdrawn without being run. A later parser diagnostic processed post-deadline public-score strings from two original competitions; no post-deadline public–private comparison or deadline-effect analysis was performed.” Qualify ordering with the actual recorded chronology. Preserve earlier historical statements with the dated correction rather than rewriting history.

This does not itself invalidate the pre-specified later-competition analysis: the disclosed diagnostic concerns two original competitions and occurred after that plan. I found no evidence of a new pre-archive look at extension outcomes. The correction is about accurate provenance, not an allegation of compromised confirmatory results.

## 3. Precision claims exceed the evidence retained in the comparison reports

The acceptance rule is `abs(a-b) <= 1e-12 + 1e-9*abs(b)`. This is **not** a uniform relative error of one part in 10^9. For example, sufficiently small same-sign values can have a much larger relative difference while satisfying the absolute tolerance. The paper and addendum 5 use the stronger relative-only wording.

The saved Python-3.12 comparison reports **2,441** tolerated cells. I checked its distribution: 1,395 occur in the stage-4 per-competition table, 558 in stage 3, 247 in the raw-score verification table, and 90 in the pilot measures; the remaining 151 are scattered across summaries. This concentration is compatible with small numeric differences propagating into derived tables. The count alone does not establish their magnitude or source.

The report retains counts, not paired values or maximum absolute/relative errors. I did not locate the counterpart run directories or a saved cell-level difference file in the project, so I cannot independently calculate the requested largest relative differences. The 663-cell Mac claim is in the narrative; a corresponding retained cell-level report/ledger was not present among the inspected rebuild files. Attributing those differences specifically to operating-system/library rounding is plausible, not demonstrated by counts alone.

**Fix:** save a compact difference report with table, key, column, both values, absolute difference, relative difference (defined away from zero), sign and threshold agreement. Summarize maxima by table and preserve the Mac comparison output. Either verify the stronger relative bound empirically or state the actual combined tolerance in the paper. Hashes establish file identity, but cannot recover the missing values needed for this comparison.

## 4. New reader: useful for this dataset, not universally equivalent or exact

Synthetic tests of `csvio.read_csv_exact` in my available Python 3.14.2/pandas 3.0.1 environment show:

- A column containing `9223372036854775808` becomes **-9223372036854775808** through the unconditional int64 cast; pandas instead returns the positive uint64 value. This is a concrete overflow defect in the new generic reader.
- An integer `9007199254740993` in a column with a missing cell becomes `9007199254740992.0`. Default pandas does this too, but “exact reading” is not accurate for such nullable identifiers.
- `1_000` becomes numeric 1000.0 through Python float parsing, whereas default pandas leaves it text.
- Dates remain textual by default, leading zeros are lost for all-integer columns as in pandas, and `inf` parses correctly. Quoting numeric CSV fields does not, by itself, declare a categorical type.

**Fix:** bounds-check integer conversion; use uint64, nullable integer or text/object storage as appropriate. Prefer an explicit schema for identifiers and flags. Describe this helper as round-trip-safe conversion for the supported project schema, not as universally identical to pandas across every version and input. Test `parse_dates` or other kwargs before advertising them: forced dtype=str followed by regex inference is not a general drop-in replacement for all pandas options.

I did not find current competition/team IDs near these limits or evidence that these examples corrupted the present results. This is a defensive implementation issue with potentially serious consequences on unsupported inputs, not a new paper-result failure. Current-table equivalence checks are useful regression coverage but cannot prove general equivalence.

## 5. Row store and team flags: checked, with bounded caveats

**Team flags:** at the filter point, `d` is the original competitions' pre-deadline submission extract; it has not been narrowed to Allstate or had benchmark teams removed. The resulting file contains exactly its 101,661 distinct teams, including 359 benchmark teams. I compared the team sets directly. This filter does not drop a benchmark team required by that retained population. Some score-validity filtering happens within competition-specific copies, so “teams in the pre-deadline extract” is the most precise description. Reusing a preexisting incomplete flag cache still would not restore missing flags; fresh CLEAN runs avoid that condition.

**JSON row store:** the retained store has 686 rows with 686 distinct competition IDs. Graceful PAUSED exits occur before the next competition is processed, and completed rows are appended once; ordinary resume behavior is sound on inspection. Python's json encoder/decoder round-trips the finite floats and accepts its own NaN tokens (143 in the current store). Those tokens are not strict interoperable JSON; use Python-only wording or null plus an explicit missing-value convention. NumPy scalar conversion through `.item()` is suitable for the scalar fields presently written.

An abrupt kill during a line append can leave a partial last line; resume then raises a JSON parse error. That is fail-stop, not silent corruption. A recoverable last-line/atomic-write policy would improve robustness. The cache has no input/config/code fingerprint, so a plain resume after changing data or measures can reuse stale rows. Require CLEAN after such changes or bind the cache to a run manifest.

The final assertions and name-based column ordering prevent duplicate rows and unexpected fields. A hypothetical run where every competition is excluded before measures are created would lack required measure columns and fail legitimately; the actual full cohort contains measured competitions and this is not a current failure. Sorting by CompetitionId is deterministic; no new ordering-sensitive result error was found.

## 6. Ledger: substantial evidence, not a complete content provenance system

I checked both retained final-run ledgers: **15 stages each, all exit 0**, with stage-script hashes matching the current files. For the main Python-3.14 ledger, all **192 retained hashed outputs** checked against their latest ledger entries match. That is strong improvement over the earlier narrative-only evidence.

Limits of `run_stage.py`:

- Change detection uses mtime and size, so a same-size modification preserving mtime is missed; deletion is not recorded.
- A concurrently changed unrelated output can be attributed to the running stage.
- The stage script is hashed after execution; imported helpers such as `csvio.py` and `stage2_measures.py` are not independently hashed in each record.
- Parquet changes are listed but not content-hashed.

For fresh, sequential, controlled runs these are reasonable engineering shortcuts; I found no evidence that they caused an actual misattribution here. A single immutable run-start manifest of all code, inputs and configuration, plus final output hashes and deleted-file reporting, would make the claim more precise without hashing every large file before every stage. The package manifest helps, but should be explicitly tied to the execution ledger's run identifier.

## 7. Comparison coverage and remaining scope

Not comparing stage-5 audit material or the retired stage-7 outputs is reasonable when clearly described as outside the active pipeline. A file-order fallback can produce a false failure on a harmless reorder, but does not warrant calling every such case a silent pass.

Excluding JSON and figures **does matter to the breadth of the claim**: Allstate file-verification JSON supports a paper statement, and figures are user-facing results. Do not equate agreement of 35 CSV tables with agreement of all artifacts. Compare scientific JSON fields while excluding documented environment/timestamp fields. For figures, verify source data and rendering rather than requiring identical PDF/PNG bytes across library versions. Current wording should explicitly name the CSV comparison scope.

## Conclusion and handover

The review does not find a new reason to abandon or reinterpret the scientific findings. Finish the narrow reporting corrections, add schema/threshold checks, and retain quantitative difference evidence. Avoid another blanket claim that every possible reproducibility issue has been closed.

Artifacts: `outputs/review/v3_provenance/check.py` and `results.json` contain exploratory fixtures and ledger checks. I did not install the two pinned environments, rerun the raw pipeline, open post-deadline scores, or independently recompute maxima from unavailable counterpart files. No novelty or venue-policy claim is made, and no original author was contacted. Existing analysis files, paper and results were left unchanged.
