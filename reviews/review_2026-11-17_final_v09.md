# Final critical QA: paper v0.9

17 November 2026. Baseline: clean commit `937fdf1`. Manuscript: 13 pages. Package SHA-256: `b127ae08208e4dc695722d1494c677744957aff40f0ddda7537e004a4410276d`.

## Submission judgement

**Proceed to submission preparation after a small, specific correction pass. I found no new numerical or methodological failure that overturns the central results.** The project has a publication-worthy core: an audited reconstruction, a scoped pre-specified extension, and concrete identification limits. This is not a guarantee of acceptance. Its strongest contribution is the combination of those elements, rather than a causal finding about adaptation.

The earlier comprehensive review remains part of this assessment. Since that review, the analysis measures and inference code have not changed; changes concern reporting, a figure title, packaging and provenance. I therefore reused the previous independent 10.6-million-submission and 125-competition accuracy checks, and freshly reran the statistical reporting stage and appendix generation in an isolated directory. I did not present reused checks as new runs.

I would fix findings 1–3 before submitting. They require wording and table changes, not a new research programme. Finding 4 is an operational submission condition. The remaining notes are minor.

## 1. The new practical recommendation overstates what per-example data identify

**Severity: substantive interpretation correction; not a failure of the existing results.**

Evidence: `paper/main.tex`, Conclusion, last sentence: releasing split assignments and per-example correctness “would let the within-team divergence be attributed.” The preceding sentence says settling these questions needs per-example predictions and split assignments. These are valuable additional data, but their release does not by itself establish attribution to feedback.

For example, a team can submit a predetermined sequence of models. Another team can use public feedback and happen to submit exactly that same sequence. Their recorded models, predictions, correctness matrices, submission times and split assignments can all be identical. Those records alone do not reveal which subsequent choices would have differed without feedback. Per-example data can expose composition effects, allow properly specified resplitting calculations and test a fixed-trajectory null under a verified randomization design. They do not automatically supply the counterfactual needed to separate every feedback mechanism from every alternative. Sampling submissions introduces further coverage limits.

**Fix:** retain the useful recommendation, but write, for example: “Platforms could release split assignments and per-example predictions for a documented sample of submissions, enabling stronger checks of sampling, composition and dependence. Causal attribution to feedback would additionally require a justified design, such as randomized feedback access, or explicit identifying assumptions.” Per-example correctness is particularly useful for accuracy; other metrics may need predictions and labels or sufficient scoring information.

This is a new overclaim in the practical consequences, not a reason to withdraw those consequences or collect new data for this paper.

## 2. S6 is still incompletely reported, and “unchanged” is literally inaccurate

**Severity: confirmed reporting defect.**

Evidence: `paper/appendix_secondary.tex` sends readers to Table 1 and the confirmatory section for S6. Table 1 contains only the full sample. The paragraph says “All four results are unchanged when flagged competitions are removed” and gives only 312/453 for H2. The qualitative conclusions survive, but the estimates and intervals do change. The plan's secondary section promises intervals; the CSV already contains them.

Fresh rerun of `scripts/stage3_tests.py` reproduces the S6 rows exactly:

| S6 outcome | E / O sample sizes | Effect | 95% interval | Holm p |
|---|---:|---:|---:|---:|
| Accuracy median-gap difference | 95 / 32 | −0.02599 pp | [−0.16609, 0.12453] pp | 1.00 |
| AUC median-gap difference | 73 / 38 | −0.000342 | [−0.003601, 0.001299] | 1.00 |
| Positive-drift share | 453 / — | 68.874% (312/453) | [64.459%, 73.068%] | 2.49 × 10⁻¹⁵ |
| Relative-drift median difference | 194 / 103 | 0.3315 percentage points of team spread | [−0.2954, 1.0684] points | 1.00 |

**Fix:** append these four rows, with units and their secondary status, and replace “results are unchanged” with “the qualitative conclusions are unchanged.” Correct the appendix's cross-reference. No statistical rerun is necessary to retrieve them.

The expanded appendix otherwise genuinely incorporates all 88 rows from `results_secondary.csv`, which resolves the major missing-S1/S2/S3 reporting concern from the previous review. However, the departure summary mentions only missing Spearman intervals. Positive-share intervals and the two added top-decile summaries also lack intervals. State this scope accurately rather than implying that Spearman correlations are the sole interval omission. It is acceptable to disclose the omission; it is unnecessary to invent a new confirmatory procedure now.

## 3. The new top-decile rows use the wrong column and leave an orphan page

**Severity: confirmed table-label error; numerical values are correct.**

Evidence: `scripts/make_appendix_secondary.py`, final S5 rows, puts `median(top10_gap_excess)` in the column headed “Share > 0”. In the PDF, the original cohort therefore has a negative number in a share column. The parenthetical “adj. gap” does not make that heading correct. The later-cohort row alone occupies page 13, while its subsection heading and original-cohort row are on page 12. I inspected the rendered page.

**Fix:** use a small dedicated S5 table with explicit columns for cohort, n, median top-decile rejection fraction and median reference-adjusted gap. Keep the two rows and caption together. This both fixes the meaning and avoids the almost empty final page. Do not shrink the entire appendix to save a page.

Also clarify the appendix's estimate legend: rows labelled “competitions with p05_first above 0.10” contain a proportion, not a median, median difference or Spearman correlation. Those estimates are 3/33 and 10/92. The values are correct; the legend currently omits their type.

## 4. Exact-data access is a workable commitment, not yet demonstrated delivery

**Type: submission preparation, not a scientific error.**

The new manuscript and anonymous README explicitly offer the exact snapshot to editors during review and promise a persistent deposit on publication. The decision log records the researcher's licence check and unsuccessful search for version history. This is a reasonable resolution of the earlier access gap in principle; I do not require a public identifying deposit before double-blind submission.

At submission, make the confidential note and delivery route real: give the editor a functioning means to obtain the three exact files and the archived-plan timestamp evidence, and offer an anonymous reviewer-access arrangement if requested. Do not imply that downloading today's Meta Kaggle reproduces these results. Preserve the recorded hashes and dataset notices. I have not tested such a transfer and did not independently reopen the researcher's screenshot.

TMLR's [author guide](https://jmlr.org/tmlr/author-guide.html), checked 17 November 2026, limits uploaded supplementary material to 100 MB and encourages reproducibility materials. A separate arrangement for the raw files is therefore sensible. The current 174-file code/results ZIP is far smaller than that limit.

## Minor technical and presentation notes

- **Run provenance:** all 15 recorded stages exited zero and all 193 recorded output hashes match the project. The run manifest has one code-hash mismatch: `scripts/make_appendix_secondary.py`, whose current hash is `c736f4f2389523cf1c37f89ae2e0cfbaca0e1914d93dd154cdb802553b1109f2`. It is not a pipeline analysis stage, and I reproduced the current appendix byte for byte. Record that the appendix generator was revised after the production manifest. Preserve the historical manifest; do not relabel it as a run of later code. No full raw rebuild is justified by this difference.
- **Denominator wording:** the main methods now disclose the numerical convention and conditional interpretation, a substantial improvement. The implementation also caps intermediate LCMs at 5,000,000 and skips factors exceeding that cap; it is not an unrestricted LCM calculation. A short bounded-search qualification would make the methods exact. In Limitations, “lower bounds” should remain explicitly conditional on the stated scoring/precision assumptions. No failure on the observed competitions was found in the earlier independent check.
- **Package wording:** the anonymous README still says “before any ... score was read”, while the paper now uses “examined”. Use the same operationally accurate wording as the paper. The archived plan should remain untouched.
- **Rebuild instructions:** `run_all.sh` rebuilds the pipeline tables and figures, but does not build the appendix or manuscript PDF. The project README correctly gives the separate appendix command; mirror that distinction in the submission handoff if claiming one-command reproduction of the whole manuscript.
- **Intervals:** the general bootstrap description has an explicit Wilson exception in Figure 2. Say “unless otherwise specified” if desired. It is already identifiable from the caption and does not change inference.

## Areas where I found no new serious issue

**Core inference and code.** Fresh execution of the unchanged stage 3 test script produced all eight confirmatory/S6 rows with zero numerical differences, including 10,000-draw bootstrap intervals. All 88 secondary rows agree within 1.11 × 10⁻¹⁶ absolute difference; all 16 descriptive rows match exactly. This rerun checks reproducibility of the implementation; the previous independent recomputation supplies the separate implementation check. Mann–Whitney tests are correctly described as distribution comparisons with median differences as separate effect summaries; Holm is applied to the four tests. No new result warrants changing the principal statistical conclusions.

**Scope.** The abstract now clearly scopes the signed-gap comparison to 95 accuracy and 73 AUC competitions, describes 487 as the broader later cohort, and retains both relative-drift summaries. The paper distinguishes signed from absolute gaps and names the predominantly in-class accuracy sample and weak recent-year coverage. H1's margins and unadjusted interval status are explicit. H3 does not claim equivalence. These qualifications are substantive and should remain.

**Adaptation and robustness.** The paper preserves the feedback-free counterexamples, unequal-size sign issue, stopping caveat, clipping sensitivity and limits of the split-label audit. The 68% result is presented as descriptive, with its prespecified test retained transparently. The new conclusion sentence in finding 1 is the exception that needs correction. The withdrawn deadline analysis remains withdrawn; no need to resurrect it.

**Original reconstruction.** The Allstate claim remains carefully separated from any claim about what unavailable original code did. The 19-versus-21 compatible-size distinction is now explained by benchmark inclusion. I found no new inconsistency in its representation. This round did not re-count the Allstate raw file.

**Dependence and comparisons.** The grouping sensitivity is described as crude and incomplete, and category stratification is not called task matching. Selection/reference calculations are qualified as independent resplitting, not real-world selection estimates. These do not remove all observational limitations, but the paper acknowledges them.

**Package.** All manifest-listed ZIP members hash correctly; every ZIP member with a same-named project file matches it. A targeted scan found no `iamalif`, `/Users/alif`, `/sessions/` or project-name identity strings. This is a targeted check, not proof against every indirect identification route. The ZIP's SHA-256 matches the last decision-log entry. Existing archived plans/results were not edited.

**Visual review.** Rendered all 13 pages; inspected the overall layout and the final appendix page. No gross clipping or missing figure was apparent. The appendix headers now repeat. The S5 column/orphan-page problem is identified above. This was not a professional typography audit of every glyph.

## Publication judgement and finite stopping point

TMLR's [acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html), checked 17 November 2026, emphasize supported claims and reader interest, and explicitly allow useful reproducibility work with generalizable lessons. The paper's combination of scoring-unit verification, later-cohort comparison and identification counterexamples is a plausible fit. Reviewers may still question how much the restricted cohort comparison adds, how well the ad hoc dependence groups represent dependence, or whether the presentation makes the lessons clear. Those are real limitations and judgements, not presently demonstrated fatal errors.

The author has made and documented the AI-disclosure decision. I have no new evidence to reopen it; the earlier distinction between scientific validity and venue policy remains. Do not describe assistant-based checks as independent human peer review.

A limited fresh search on 17 November used the original paper title with replication/Kaggle/2026 terms and separately searched the Burtch identifier plus “129”. It did not establish an overlooked directly matching study, but it was not exhaustive and supports no new novelty claim. The Burtch v3 HTML still failed to load for this reviewer; the other assistant's reported primary-source verification is in the response, but I did not independently replicate it. Keep that source evidence available.

**Stopping rule:** fix the causal-recommendation sentence, complete S6 reporting and repair the S5 table; arrange the confidential data/archive handoff; render the revised PDF and rebuild/check the ZIP. Then proceed to submission discussion. No additional exploratory analysis, raw-data rerun or repeated general QA is required unless those edits change calculations or reveal a new discrepancy. Acceptance remains uncertain, but indefinite polishing would not resolve the study's inherent identification limits.

## Evidence and limits of this round

Review baseline and diffs, full current manuscript source, plan, response/log, methods/test code, appendix generator, package builder, run wrapper and documentation were inspected. Fresh statistical and appendix runs were isolated from project outputs. `outputs/review/final_v09/` contains the fresh tables, execution logs and verification summaries. This review is saved as `reviews/review_2026-11-17_final_v09.md`.

Not freshly repeated: extraction from raw Meta Kaggle, the complete 15-stage pinned-environment run, the 10.6-million-row independent measure reconstruction, all 125 formal-test recomputations, original-reference transcription, all host descriptions, every citation or third-party archive timestamp, external raw-file delivery, or actual submission. Those earlier checks retain their documented scopes. No post-deadline scores were opened, no original author/editor contacted, and no plan, manuscript or existing result changed.
