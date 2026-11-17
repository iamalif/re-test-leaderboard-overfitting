# Independent review: parsing, regenerated results and package v2

17 November 2026. Requested scope: changes since f96fd05 through b84486c, including responses, rebuild-report addenda, score conversion, comparison v2, stage-3 regeneration and the actual anonymous ZIP. This review used synthetic fixtures, existing pre-deadline extracts and recorded result tables only. No post-deadline score was read. No recorded analysis output, plan or paper was edited.

## Overall assessment

I found no changed headline scientific result in the comparisons performed. The four reported original-sample changes are real and accurately identified; the confirmatory table and pilot competition-level drift tests agree with their earlier versions within numerical tolerance. ZIP permissions and manifest integrity are repaired.

However, comparison v2 still has false-pass cases, especially its unrestricted team-flags exception and its failure to protect decision-relevant signs and exact identifiers. The claim that reproducibility is completely closed is premature. These are repairable verification and provenance issues, not evidence that the paper's substantive conclusion has failed.

## 1. High priority: the known exception waives arbitrary team-flags corruption

**Confirmed error.** In `scripts/compare_outputs.py`, `run()` replaces *any* mismatch for `stage1/original_team_flags.csv` with a non-failing known-exception status. It does not check the claimed invariant (the same benchmark teams with submissions). Thus an explanation for one known difference becomes a permanent waiver for all future differences in that file.

I supplied otherwise identical one-row files with `TeamId=1`, changing `IsBenchmark=True` to `False`. The actual v2 tool printed a known exception and `RESULT: PASS`, exit 0. This would also waive a changed schema or an arbitrary different row count under that path.

**Fix:** replace the blanket exemption with a specific invariant check against the relevant submission-team set. Verify benchmark status on every submitted team, validate uniqueness/schema, and permit only documented extra registered teams. Alternatively pin the two explicitly reviewed file hashes and fail on any other mismatch. Preserve the explanation and invariant evidence in the comparison report. Downstream agreement is useful but does not substitute for validating a field used to filter observations.

## 2. High priority for a numerical audit: tolerances can hide different decisions

**Confirmed false passes.** The comparison applies float tolerance to identifiers and every numeric value, and converts text that looks numeric to floats. Its missing-value parser also conflates distinct literal text tokens. Actual fixture outcomes:

| Change | v2 result |
| --- | --- |
| `CompetitionId` 1000000000 → 1000000001 | same |
| `drift_mean` +1e-14 → -1e-14 | same |
| literal label `NA` → `NULL` | same |
| text code `001` → `1` in an otherwise mixed column | same |
| boolean flag True → False outside the exception | DIFFERENT VALUES (correct) |

The large-ID example illustrates the schema defect; I am not claiming current competition IDs are that large. The drift example is directly relevant because the analysis counts strict positive/negative signs. An absolute tolerance appropriate for reporting decimals is not enough to establish equality of a sign-test input. Similarly, a tiny perturbation can change a cutoff tie or a threshold decision.

**Fix:** define per-table keys and field types. Compare IDs, counts, booleans and categorical strings exactly; verify key sets exactly before aligning rows. Preserve literal text and distinguish its declared missing representation. Use a documented tolerance only for measured real-valued fields. Add exact decision-level comparisons for signs, finite/zero status, inclusion/exclusion flags, threshold classifications, and cutoff ties where they affect the analysis. Do not treat a generic tolerance comparison as proof these decisions are identical.

The existing 16-case self-test passes, and ordinary text changes, boolean changes, row reordering on a unique key and unexpected missing files are handled. The new fixtures extend rather than contradict those tests. `_key` falls back to file order when it cannot find a unique key; that is conservative for reordered duplicates. I did not establish a concrete wrong pairing caused by `_key` itself. The demonstrated identifier false pass occurs after alignment because key values are compared approximately.

The broad `EXPECTED_NOT_REBUILT` patterns are acceptable for clearly separated historical artifacts today, but are not a durable specification of pipeline outputs. Explicitly list the expected outputs and allowed historical omissions so a future required file under `review/`, `rebuild/` or `stage7/` cannot disappear unnoticed. This is hardening advice; I did not find a currently required stage-3 result hidden by those patterns.

## 3. Moderate: score parsing is improved, but the full serialization path is not protected

The text-to-`float()` conversion is appropriate for ordinary decimal score strings. I tested the extracted conversion function without executing the analysis: empty strings, whitespace-only strings and missing values map to NaN; exponent notation, surrounding whitespace and numeric decimals work; `nan`, `inf` and `-inf` parse. Python floats are binary approximations, so “correctly rounded conversion” is more precise than saying the decimal scores are exact. Malformed nonempty tokens raise an exception; no evidence of such tokens in the analysed subset was found in this review.

I independently confirmed that the available default pandas parser can differ from `float()` on these score strings: among the **27,006** cached pre-deadline submissions for 8900 and 10200, pandas 3.0.1 differed on 7,556 public values. This is a demonstration in my environment, not reproduction of the report's pandas-2.3 figure. I did not have the claimed pandas 2.3/3.1 environments available and did not install them.

The statement that parsing affects “only” stages 1 and 2 is incomplete. Stage 3 initially extracts submission scores through DuckDB, but `stage3_extension.py:91` repeatedly reads and rewrites the entire accumulated result CSV after each competition, and `:98` reads it again before final column ordering. Stage 3 tests and later analyses also read CSV results with default parsing. Stage 1 rereads p-values before threshold comparisons. An exact raw extraction does not protect these later boundaries from re-parsing differences.

**Fix:** use a consistent round-trip-safe conversion for numeric result tables as well as raw scores, or retain a typed binary intermediate and export CSV for presentation. Then explicitly check the downstream decisions listed above. Keep archived measure definitions unchanged; document serialization fixes as implementation changes. In particular, avoid repeatedly changing old result values merely to append a row or reorder columns.

**Current impact:** I compared signs of `drift_mean`, `rel_drift` and `mean_gap` under default versus round-trip parsing of the current stage-3 table and found **zero sign changes**. Old versus regenerated stage-3 values also had no sign changes in those fields. This is reassuring evidence about current outputs, not a guarantee for every parser/environment or threshold.

## 4. Moderate provenance issue: the diagnostic count and two-environment claim need a precise record

The report states 10,387 of 41,739 public scores in 8900 and 10200 were misrounded. The current original-sample pre-deadline extract contains 5,681 + 21,325 = **27,006** rows for those competitions. I could not locate a saved diagnostic script or row-selection record explaining the 41,739 population.

**Fix:** retain the diagnostic code, exact input hash, parser versions and selection predicate. Explain the population difference without opening any additional post-deadline values. This discrepancy does **not** establish that post-deadline scores were read; it does mean the quoted diagnosis and its provenance cannot currently be reproduced from the described pre-deadline subset.

The report and the brief also leave uncertainty about which Python-3.12 stages were regenerated after the parsing and stage-3 serialization changes. A comparison of a directory containing outputs from different code states is not, by itself, evidence that the final code ran end to end in that environment. The recorded Mac smoke test is valuable, but the decision log says it used an earlier ZIP, compared against the later outputs. Label that accurately rather than implying the final ZIP itself was exercised.

**Fix:** retain a per-stage execution ledger with exact code/package hashes, environment versions, timestamps, exit status and output hashes. Either narrow the claim to the stages and code versions actually exercised or perform a final clean run of the supported secondary environment. A second environment need not block submission if it is explicitly optional and its verification is described honestly. After repairing the comparator, recompare the retained runs before claiming all supported environments produce the same decision-relevant results.

## 5. Regenerated stage 3: substantive agreement confirmed, literal identity overstated

I compared the superseded table with the current one using round-trip parsing and alignment by CompetitionId.

- `scores_in_0_1` differs on 69 rows, as reported.
- Many other numeric cells differ at floating-point precision. For example, 571 `drift_mean` cells differ exactly, but none changes sign. All compared numeric fields agree within rtol=1e-9, atol=1e-12.
- Large absolute differences in a few custom-metric fields reflect their extreme scales; they are not evidence of large relative changes. They should not be reported without that context.
- The confirmatory result table agrees with its f96fd05 version at the same tolerance. I found no changed rejection decision or headline count.

Thus “only column order and bookkeeping differ” is true at the intended numerical tolerance, not literally for every stored number. Say so.

The new final `reindex(columns=COLUMN_ORDER)` aligns by name, so it does not shift values into another column. Its assertion rejects unexpected column names rather than silently dropping them. However, it permits missing columns and fills them with NaN, which is necessary for some optional quantities but should not silently repair missing mandatory identifiers/measures. Explicitly assert required columns and uniqueness separately. The ordering happens only on DONE, not before a PAUSED exit; that is acceptable for intermediate files if consumers wait for completion and the behavior is documented.

## 6. Paper-number check

Confirmed changes relative to f96fd05:

| Table field | Competition | Old | Current |
| --- | ---: | ---: | ---: |
| Stage-1 top10_mean_gap | 8900 | 0.02360644794371096 | 0.02355932052876918 |
| Stage-1 top10_mean_gap | 10200 | 0.0007934850427343285 | 0.0007935635383271904 |
| Pilot team drift_share_positive | 4493 | 0.6726190476190477 | 0.6666666666666666 |
| Pilot team drift_share_negative | 5275 | 0.524546660769571 | 0.5249889429455993 |

The pilot competition-level drift-test table is unchanged within tolerance, including its 78/117 positive count. That pilot count should not be confused with the final O-cohort 77/114: they use different final eligibility sets. The inferred-size pilot table is unchanged within tolerance, including the original-outlier reference gaps. The stage-1 submission total remains 1,510,406. I found no parsing-related number in the inspected manuscript claims requiring correction. The separately documented AUC bootstrap bound change to -0.0041 is an intended consequence of 10,000 draws, not of this parsing fix.

This was a targeted table-to-claim check, not an independent re-extraction of all raw observations or a fresh derivation of the original outlier identities. Earlier checks of those facts remain on record.

## 7. Package: repaired items and remaining limits

The actual ZIP inspected has 130 files. All manifest hashes verify, and `run_all.sh` has mode 0100755. The required-file list covers the explicit runner scripts and listed reference inputs. The README now distinguishes historical reports and results-only reviewer checks. These address the prior concrete packaging findings.

A targeted scan of every decodable ZIP entry found no listed author/account/home-path identifiers. I inspected metadata of packaged PDFs and PNGs: the figures contain Matplotlib version and creation-time information but no author name or home path in those fields. ZIP file modes and fixed timestamps are consistent with the builder. This is not a guarantee against reidentification from a searchable public plan, distinctive prose, external links or arbitrary binary content.

The main paper PDF is not part of this supplementary ZIP; its separate metadata should be checked on the final submission file. The builder's identity exemptions trust entire named source-data files and are broader than a semantic identity check; I found no actual author leak in the current entries. No new anonymity blocker was found.

## Handover

Priority order: repair comparison exception/schema/decision checks; recompare retained runs; document parser-diagnostic population and exact execution provenance; make serialization robust or narrow the cross-environment claim. Then regenerate the anonymous ZIP and record its hash. No new scientific hypothesis test is needed.

New exploratory verification artifacts are in `outputs/review/post_v05/`: `check.py`, `more.py`, JSON results and synthetic comparison fixtures. They use only already examined pre-deadline inputs and public result tables. My local environment was Python 3.14.2 with pandas 3.0.1; it was not the project's pinned main or secondary environment. I did not rerun the full raw pipeline, the new 10,000-draw bootstrap, or all paper figures, and did not repeat a literature search or make a novelty claim. No original author was contacted.
