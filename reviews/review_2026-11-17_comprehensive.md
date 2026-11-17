# Comprehensive pre-submission QA

**Date:** 17 November 2026. **Reviewed baseline:** `7b6b8b1`, paper v0.7, 11-page `paper/main.pdf`. **Package:** SHA-256 `d78fa7345e0d2fc47545ca367612ed1c5f72135d78b4a4d5d3d09ca7c44afd70`.

## Verdict

**The project has a defensible, publication-worthy core. I found no numerical failure that overturns its principal findings. It is close to submission, but I recommend one bounded reporting/provenance revision first.** The central contribution is the audited reconstruction, the scoped later-cohort comparison and concrete demonstrations of what aggregate scores fail to identify. It should not try to regain a causal claim about adaptation.

The strongest fresh check in this review is an independent reconstruction of mean gaps and within-team drift from **all 10,598,147 retained pre-deadline submissions across 686 candidate competitions**. Both measures match the recorded outputs. I also independently recomputed the first-submission formal-test rejection fraction for **all 125 usable accuracy competitions**; all match exactly.

The remaining substantive concerns are completeness of planned secondary reporting, precise mathematical wording and access to the exact input snapshot. TMLR's AI-use policy is a separate venue-eligibility question; neither I nor a disclosure footnote can guarantee an editor's interpretation. I would not keep expanding the empirical analysis solely to make the paper more dramatic.

## Findings ranked by importance

### 1. Before submission: Appendix A still does not report all promised secondary quantities

**Type: confirmed reporting gap.** Section 6 says every pre-specified secondary quantity is listed; the appendix is titled “All pre-specified secondary quantities.” This is not yet accurate.

Examples against plan §7 and `outputs/stage3/results_secondary.csv`:

- S2 promises both absolute gaps and reference-adjusted top-decile gaps below/above 10,000, pooled and by cohort. The appendix gives the absolute-gap medians but omits the corresponding adjusted-gap medians and contrasts. For O+E the existing adjusted-gap contrast is -0.0784 percentage points, interval [-0.3073, 0.2719]. It is in the CSV, not the appendix.
- S1/S3 group medians and positive-drift shares are mostly shown without intervals, despite the plan's “reported with intervals” and the appendix's introductory description of medians with intervals. Many median intervals already exist in the CSV and can be included without rerunning the analysis.
- The six S2 Spearman estimates and two S4 estimates have p-values but no intervals even in the CSV. This is an implementation/reporting departure from the general interval promise, not something the new appendix resolves.
- The appendix gives an adjusted top-decile gap under S5 but not the top-decile p-value summary mentioned in plan §7. Either supply the promised pairing with its stated limitations, or explicitly log and explain the omission.
- Pooled S1 rows use the relative-drift subsets (124 regression, 307 classification). Raw drift is defined for 125 and 308 respectively. Relative-drift signs are unchanged when the scale exists, but missing spreads remove competitions. Label the reported share's denominator so readers do not assume it is the full raw-drift share.

**Fix:** provide a genuinely complete table keyed to S1–S6, with units, estimands, denominators and available intervals; mark unavailable intervals and deviations honestly. An expanded supplement is fine, but the paper must point to it accurately. Do not claim completeness while relying on readers to reconstruct missing items from a CSV. This is important in a pre-specified study even when omitted results do not reverse the headline.

### 2. Before submission: document a retrievable, immutable input snapshot

**Type: reproducibility/access gap, not a calculation error.** The package supplies input hashes and a download date, but tells reviewers to obtain Meta Kaggle from a daily-updating dataset and warns that a later download will not match. A hash verifies bytes already obtained; it does not let an outside reviewer obtain those bytes.

The recent clean runs establish reproduction from the retained local inputs. They do not establish that an unaffiliated reviewer can acquire the exact November 15 inputs. I did not find an immutable dataset-version identifier or a tested snapshot retrieval route in `ANON_README.md`.

**Fix:** record a version-specific Kaggle URL/API identifier if available and verify that it retrieves the recorded hashes; otherwise arrange a durable snapshot-access route consistent with the data terms. Keep author-identifying links out of the anonymous public package if necessary, but make access arrangements clear to the editor. State dataset provenance/licence and distinguish Meta Kaggle from the optional Allstate test file. Kaggle's own [Meta Kaggle Code announcement](https://www.kaggle.com/product-feedback/430422) states that Meta Kaggle moved to Apache 2.0; the actual snapshot's metadata and notices should be preserved rather than relying only on this announcement.

This is the main remaining obstacle to a strong claim of external reproducibility. It does not require more hypothesis tests.

### 3. Correct the mathematical scope of the denominator claims

**Type: methodological precision; no demonstrated failure on these competitions.** The manuscript calls inferred counts the smallest compatible sizes and states unconditionally that the true size is a multiple. That divisibility statement is exact for exact rational accuracies with the assumed scoring unit. The implementation works on floating-point values, rational approximation and tolerances:

- at least 20 distinct valid scores;
- denominator cap 5,000,000;
- rational approximation residual below 1e-11;
- count-grid tolerance below 1e-4;
- bounded LCM construction rather than a general exhaustive minimum search.

These details are not stated in the paper. A finite decimal score always has some rational representation, so “fits no lattice” also needs the cap/tolerance qualification.

I tested a deliberately extreme boundary example: true N=1,000,000,000,001 and scores `i*floor(N/100)/N`, i=0,...,19. The actual routine returns (100, fit=1), although N is not a multiple of 100. This is not a plausible claim about a particular Kaggle test set; it demonstrates why finite-precision compatibility is not an unconditional integer-identification theorem.

**Current-data reassurance:** across the 125 usable competitions, the maximum residual from the inferred integer counts is only 1.1642e-10 counts, far below the acceptance tolerance. The independent formal-test recomputation matches. I found no evidence that the approximation issue changes the reported results.

**Fix:** document the search bounds, distinct-score rule and tolerances, and make the multiple/lower-bound statement conditional on exact ordinary unweighted accuracy and adequate numerical representation. Prefer “minimum-compatible lattice candidates under the stated numerical convention” where necessary. Do not imply that the cap proves larger denominators impossible. This is a clarification of what the reconstruction establishes, not a request to change the archived plan or silently replace its algorithm.

### 4. Fix several remaining statements whose logic is broader than the evidence

**Type: interpretation/reporting, mostly sentence-level fixes.**

- **Introduction:** “the difference ... is a natural experiment on adaptive overfitting” conflicts with the paper's central nonidentification result. Call it an observational comparison using a withheld score. The private set is evaluated on many submissions; “used once” should refer specifically to its feedback/ranking role, not imply one numerical evaluation.
- **Abstract:** clarify that the signed-gap comparison covers **95 accuracy and 73 AUC competitions within the 487 later competitions**. The current opening can be read as extending that conclusion to all 487.
- **Methods:** “A team that tunes ... produces positive drift” is a mechanism, not a universal implication. Use “can produce.” Adaptation may be complete before observed submissions or continue without this diagnostic changing.
- **Limitations:** “a justified 50% reference only under equal-size random splits” is too restrictive as a necessity claim. Equal-size random splitting with the other symmetry assumptions is a sufficient guarantee; some unequal-size distributions also have symmetric signs. Say “is guaranteed under ...” and retain the fixed-trajectory/score-symmetric assumptions.
- **Formal test limitation:** shared splits do not invalidate each submission's marginal hypergeometric p-value under its null. They induce dependence across submissions and undermine independent-resplitting joint/reference interpretations. Separate these facts so the paper does not unnecessarily discredit its valid marginal calculation.
- **Time:** replace “there is no trend” with “we detect no monotone association.” S4's nonsignificant correlations do not prove zero trend.
- **Pre-specification wording:** “before any score ... was read” is mechanically stronger than the disclosed pipeline behavior of loading raw rows before filtering. State that extension outcomes were not examined or compared for analysis before archiving. Preserve the archived plan verbatim and clarify the operational meaning in the paper/provenance record.

None of these changes requires a different empirical conclusion.

### 5. The deviations paragraph conflates deviations, corrections and faithful implementation

**Type: confirmed mismatch with the plan.** The new paragraph lists the finite-score eligibility rule as a deviation, but plan §2 rule 3 already explicitly requires finite public/private scores. The two exclusions correct the metadata-stage approximation; they do not depart from the written rule.

Likewise plan §8 promised full-description re-reading but did not require blindness or forbid a second reader. The actual deviation was the initial truncated same-reader audit, subsequently replaced by the full-text review. Calling the final nonblind second reading itself a plan departure obscures the history.

**Fix:** distinguish true deviations from implementation fixes and planned checks completed later. Include the missing secondary intervals/reporting noted above. Do not edit the historical plan; correct the paper's summary and append to the log if needed.

### 6. TMLR AI-use policy: decision for the author, not an automatic rejection finding

**Type: venue judgement. Checked official sources on 17 November 2026.** The [editorial policy](https://jmlr.org/tmlr/editorial-policies.html) allows general-purpose assistive LLM use and assigns responsibility to human authors. The [FAQ](https://jmlr.org/tmlr/faq.html) additionally expects human-sourced ideas, claims and results and requires a first-page disclosure. These statements leave an interpretation question for extensive assistant participation in design and critical review.

The current footnote is materially more transparent than the earlier generic description. The author's account of originating the question, directing the work and substantively revising it should be represented accurately; I cannot independently audit that account or decide venue eligibility. A brief editor inquiry describing the actual division of work would reduce uncertainty if TMLR remains the target. I have not contacted anyone, and such an inquiry is a recommendation, not a tool-imposed approval requirement.

TMLR's [acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html) explicitly emphasize supported claims and audience interest, allow useful reproducibility work, and do not require a state-of-the-art or novelty claim. That makes the paper's narrower contribution potentially suitable. It is not a prediction of acceptance. A preprint is not inherently incompatible with their double-blind process according to the FAQ. The author should make the venue/preprint decision using the current policy, not assumptions about arXiv being categorically forbidden.

## Fresh numerical QA: what passed

The following checks were performed independently in this turn, rather than merely accepting the other assistant's report:

1. Recomputed competition mean gaps and within-team drift from the pre-deadline Parquet extract, using separate review code, for all 686 candidates and 10,598,147 submissions. No mismatch at rtol=1e-10/atol=1e-12, including the clipped metrics.
2. Checked the no-effective-split exclusion on raw versus clipped scores: no competition changes exclusion status in this dataset.
3. Reproduced all four raw confirmatory p-values: 0.5896954866, 0.2404757632, 2.2129261612e-15 and 0.9208851543. Holm implementation is correct on inspection. No exact-zero later drift creates a sign-test denominator ambiguity here.
4. Independently recomputed the first-submission p<=0.05 fraction for all 125 usable accuracy competitions, using a public-count hypergeometric formulation rather than the implementation's private-count formulation. Maximum fraction difference: **0**.
5. Exhaustively checked the formal tail calculation on 1,225 small public/private count configurations. Maximum error versus direct probability enumeration: **3.33e-16**.
6. Recovered final cohort counts O=114, E=487, W=51 and confirmed six later accuracy competitions ended after 2022.
7. Verified all four archived hashes: analysis plan, measure code, label decisions and label table.
8. Checked both final_v5 ledgers: 15 successful stages each; run identifiers match. All 193 retained main-run output hashes match. The only changed manifest-listed code is the subsequently revised comparator, as documented.
9. Verified all entries in the current 167-file ZIP against its manifest. Its SHA-256 matches the latest recorded package. The targeted account/home-path scan found no author identifier leak.

This is strong evidence that the recorded descriptive results are implemented and reproduced correctly. It is not proof of causal identification, representativeness of the competition sample, true test sizes, or unrestricted portability to any future software/data version.

## Design/statistics assessment

- Competition-level inference is preferable to treating submissions as independent observations. The organisation/slug grouping is a useful sensitivity, and its limitations are now stated. Shared users, tasks and course series can still create dependence across groups; this remains a limitation rather than a newly discovered computational error.
- H1/H3 Mann–Whitney tests concern distributions/ranks, not solely median equality. The manuscript now labels the test and separately gives median-difference intervals. Keep that distinction; the median interval, not a nonsignificant Mann–Whitney result, supports the scoped small-shift reading.
- The material-gap margins and unadjusted confidence-interval caveat are disclosed. Do not promote these into an omnibus equivalence result for all metrics or entire distributions.
- Selection-adjusted language has appropriately been replaced by an independent-resplitting reference. The current formal-size sensitivity and related-competition checks add genuine value without identifying adaptation.
- The rise in absolute accuracy gaps usefully qualifies the stable signed-median finding. Preserve it prominently; cancellation in signed gaps is important to the audience.
- Allstate remains a strong reconstruction contribution, with appropriate restraint about what the unavailable original code actually computed. Its exact file check is optional in the distributed runner; the comparator's narrowly conditioned omission rule is reasonable and does not waive unrelated mismatches.
- The deadline proposal is retired from the active workflow. No reason emerged to revive it as a causal rescue analysis.

## Literature, presentation and package QA

**Fresh search:** searched the original title with replication/extension terms, Kaggle leaderboard overfitting and 2026, and the two cited later studies on 17 November. I found the original NeurIPS work, Kaggle Chronicles and Burtch's current arXiv version, but did not identify a directly matching peer-reviewed re-test. This limited search is not proof of novelty or exhaustive absence.

I verified Burtch's current v3 title and revision date on the [arXiv record](https://arxiv.org/abs/2607.13077). The 35 MB PDF exceeded the web tool's fetch limit, and a separate network download failed, so I did **not** independently confirm the newly quoted 129-competition number from its full text. Preserve the exact page/table evidence used by the other assistant before submission. The [Kaggle Chronicles text](https://arxiv.org/html/2511.06304v1) supports treating its leaderboard comparison as descriptive rather than a direct re-test of Roelofs et al.

I rendered and inspected the 11-page manuscript at page/contact-sheet scale and extracted all page text. No gross clipping, missing figure or broken reference was apparent. The second page of the appendix lacks repeated column headers, and its opening claim about intervals is not matched by most rows. Repeat headers in the long table and prioritize readable complete reporting rather than a page-count target. Figure 2's title still asserts a direction broadly across groups; a neutral title such as “Share of competitions with positive within-team drift” is preferable. These are presentation fixes, not reasons to rerun the whole pipeline. TMLR's [author guide](https://jmlr.org/tmlr/author-guide.html) permits variable length and requires the template; it does not impose a nine-page target.

The stronger AI-use disclosure and explicit second-assistant review attribution are appropriate. Avoid presenting this review history as independent human peer review. The reproducibility paragraph could be shortened and move the 2,443-cell arithmetic to the supplement; it is accurate but takes space better used for scientific assumptions.

The anonymous package hash/identity checks pass in the scope tested. Confirm editor-only access to the public archive evidence: the plan hash alone proves content identity, not the date of public deposit. The public snapshot, code licence and data notices should be explicit in the release plan. I did not modify the package or contact editors/authors.

## Finite submission checklist

1. Complete/correct Appendix A and its interval/deviation statements.
2. Tighten the mathematical and interpretive wording in findings 3–5.
3. Provide an exact-snapshot retrieval route and preserve the relevant licence/provenance metadata.
4. Resolve the author's venue-policy judgement with an accurate account of the human and assistant contributions; an editor inquiry is an option.
5. Retain precise source evidence for the updated Burtch statistic, render the final revised PDF, and freeze PDF/ZIP hashes. Another full raw rebuild is unnecessary for prose-only edits; rerun affected checks if code or generated numerical tables change.

After those steps I would support submission preparation. I would not recommend months of new exploratory analyses, nor promise acceptance. The scientific value lies in correcting a specific influential reconstruction and showing that stable signed aggregate gaps, temporal divergence and causal adaptation are different claims.

## Artifacts and limitations of this QA

Authoritative review: `reviews/review_2026-11-17_comprehensive.md`. New exploratory checks: `outputs/review/comprehensive/` contains `recompute.py`, `recomputed_measures.csv`, `recompute_summary.json`, `size_audit.py`, `formal_accuracy_check.csv`, `extra_checks.py`, `extra_summary.json`, and `final_v5_audit.json`.

The review reused the existing pre-deadline extract; it did not independently re-extract 10.6 million rows from the raw Submissions file or open any post-deadline scores. It did not rerun every bootstrap interval, every exploratory regression or the entire pinned-environment pipeline. Prior interval checks remain documented. It did not independently verify every original-paper appendix transcription, every host description, every citation, the third-party archive timestamp or the author's involvement. These are explicit limits, not implied completion claims. The local review environment is Python 3.14.2 with pandas 3.0.1, not either pinned production environment. No existing plan, scientific result or manuscript was edited.
