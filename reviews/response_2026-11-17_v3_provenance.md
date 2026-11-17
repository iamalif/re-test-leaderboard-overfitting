# Response to the review of comparison v3 and provenance (`review_2026-11-17_v3_provenance.md`)

Author: Claude. Date: 17 November 2026. All findings accepted. Finding 2 corrects a false statement of mine.

| # | Finding | What was done |
|---|---|---|
| 1 | Threshold changes and decimal-written counts could pass | Comparison v4: p-value columns must fall on the same side of 0.01, 0.05 and 0.10; columns whose reference values are all whole numbers below 2^53 are compared exactly however written. 28-case self-test including your fixtures. My first version applied exactness to every whole-looking decimal; it flagged values of about 1e94 from pathological custom-metric competitions that differ in the 16th digit, so the rule is now column-based. Underflow (1e-400) and nan/NaN spelling: documented, not changed. |
| 2 | Paper still said "unexamined" and "before reading any data" | You were right, and my response claiming the wording was corrected throughout was false. The paper now says the contrast was withdrawn without being run and that no post-deadline public and private scores were compared. Chronology states that the diagnostic counted parser disagreements on 14,733 post-deadline public-score strings of two original competitions, after the plan, and computed no gap, drift or deadline quantity. Your suggested wording, nearly verbatim. |
| 3 | "One part in 10^9" overstates the rule; no cell-level evidence | Paper and README state the rule as written. Cell-level difference reports now exist (`outputs/rebuild/final_v4/`): of 2,443 differing cells, 2,392 within 1e-14 relative, all but one within 3e-12; the one exception (2e-11, a cancellation) within 1.7e-7. The paper reports exactly this. The Mac run's outputs were not retained, so its 663-cell figure stays narrative and is labelled as such. |
| 4 | csvio overflow and other divergences | Integers outside int64 and underscore numbers stay text; type-changing options refused; documented as verified for this project's tables only. Re-verified against pandas on every project table under both versions. |
| 5 | Row store and team flags | Row store bound to a fingerprint of its code and inputs; stale resume refused. NaN tokens documented as Python-only. Team flags: thank you for checking the set; the 359 benchmark teams are retained. |
| 6 | Ledger limits | Run manifest at run start (all code, reference and raw-input hashes, versions, machine); ledger records carry the run identifier, the script hash taken before running, helper hashes and deleted files. Remaining limits (mtime/size detection, parquet not content-hashed) documented. |
| 7 | JSON and figures not compared | Three scientific JSON files are now compared field by field. Figures are drawn from compared tables and are not compared as images; stated. |

**Final runs** with all changes: both 15/15 stages exit 0; code and raw inputs verified against manifests; 193/193 outputs match ledgers; the 3.14 run equals the project outputs (38/38 files); 3.12 vs 3.14 PASS. No number in the paper changed apart from the reproducibility sentence itself.

Not done, by judgement: a general schema system for the reader, content hashing of parquet extracts, and image comparison of figures. Each is documented as a limit.
