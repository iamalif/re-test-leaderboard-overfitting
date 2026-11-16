# Stage 1 follow-up: scoring units and statistical interpretation

16 November 2026. **Stage 1 remains open.** Subsequent source-file verification is recorded in `allstate_verification_note.md`; the Allstate test file is now received, and the OpenReview report is confirmed unrelated. The descriptive replication is stable, but the formal interpretation needs source verification. These findings do not show that the original paper's headline conclusion is false, and do not establish how its unpublished implementation worked.

## Findings that are now better understood

**Benchmark teams explain five exceptional rows.** The three off-lattice submissions in competition 6109, one in 12349, and one in 12598 all belong to teams flagged `IsBenchmark=True`, named Competition Wizard Sample Submission Playground. The 12598 scores additionally fit the published sizes when public and private sizes are swapped. Excluding benchmarks increases the number of accuracy competitions whose entire score sets fit the appendix sizes from 19 to 21; the swapped-size case is not counted as independently verified.

Across all original accuracy competitions, excluding benchmark teams changes any mean gap by at most 0.0232 percentage points. The same five competitions remain the largest positive outliers. The faithful first pass remains unchanged; the exclusion is a separate sensitivity analysis.

**Ties can matter.** For competition 12681, any exact-sized top-10% subset selected by public score can have a mean gap between 1.2965 and 2.6210 percentage points, depending on which equal-public-score submissions fill the cutoff. These are mathematical bounds, not recommended selection methods. The private score must never choose which tied submissions enter a substantive analysis. An inclusive-all-ties rule or a fixed outcome-independent tie-break should be declared in advance.

**Dates limit the first-submission analysis.** All retained submission dates have day precision. For competition 11842, choosing among submissions on each team's first day allows the fraction with p <= .05 to range from 1.87% to 18.22%. Smallest submission ID is a plausible proxy for order, not independent verification of chronology. Bounds and the proxy rule should be reported until original ordering can be established.

**Identical scores do not establish independent validation.** All 1,634 retained submissions in the original CIFAR-10 competition (3649) have identical public and private scores. Both score columns fit denominator 10,000, whereas the appendix lists a 300/9,700 split. This requires a scoring/split-history explanation; it cannot simply count as evidence against adaptive overfitting.

## Allstate: a source-supported reconstruction worth verifying

The paper lists 59,657 public and 139,199 private examples for competition 3788, totaling 198,856. A contemporary participant's [presentation, slide 7](https://speakerdeck.com/justmarkham/allstate-purchase-prediction-challenge-on-kaggle) identifies 55,716 test customers. His [project report](https://github.com/justmarkham/kaggle-allstate/blob/master/allstate-paper.md) describes one prediction per customer, correct only when all seven insurance options match. The local official competition description also distinguishes customer histories from the one prediction required per customer.

Recorded public and private scores include reduced fractions 8991/16714 and 20777/39002. Under ordinary equally weighted accuracy, a total of 55,716 distinct scored customers, and exhaustive disjoint splits, those denominators uniquely imply 16,714 public and 39,002 private customers. Every retained Allstate score fits these counts.

This is a supported reconstruction, not a released split manifest. Verification against the actual test file is pending. A file-row versus customer-count error is plausible but not yet established.

Conditional on these reconstructed counts, the exact inclusive hypergeometric test gives:

| Subset | Submissions | Fraction with p <= .05 |
|---|---:|---:|
| All submissions | 24,523 | 1.285% |
| Top 10% by public score | 2,453 | 3.832% |
| First per team, date then ID proxy | 1,570 | 1.783% |

These conditional results differ markedly from the visual concentration of small Allstate p-values in the original Figure 3. This is a formal-replication discrepancy to resolve, not an empirical finding about modern competitions. Directly matching original code would help distinguish table errors, implementation choices, approximation errors and snapshot changes.

## A synthetic check changes what the future tests can claim

We simulated 100,000 fixed models, each with the same 70% population accuracy, evaluated on independent public/private sets of 100 examples each (seed 2019). No model adapted to any test result. This is an intentionally simplified method diagnostic, not a model of the dependence structure of real Kaggle submissions.

| Subset | Mean public-minus-private gap | Inclusive p <= .05 | Strict-tail quantity <= .05 |
|---|---:|---:|---:|
| All fixed models | -0.00047 percentage points | 3.467% | 7.170% |
| Top 10% selected on public score | 7.8782 percentage points | 13.300% | 23.370% |

Two implications follow from this constructed example:

- Selecting submissions by public performance can produce a positive gap and an excess of small p-values without adaptive model development. The selected group's p-values cannot be judged against an unconditional uniform reference to establish adaptation.
- For discrete outcomes, a strict tail excludes the observed probability mass and need not be a valid conservative p-value. The inclusive tail and strict-tail quantity must not be treated interchangeably. The original main text and appendix differ on this inequality; which was actually implemented remains unknown.

These issues do not invalidate descriptive gap measurements. They constrain causal claims about adaptive overfitting. The eventual paper should distinguish public-score optimism, selection effects, distribution shift and evidence specifically attributable to adaptation. A table typo alone is unlikely to carry the intended contribution; a validated measurement pipeline and carefully delimited extension could.

## Source search and current dependencies

Checked the NeurIPS supplement, Sara Fridovich-Keil's project listing and public repositories, Rebecca Roelofs's public repositories, Vaishaal Shankar's public repository listing, and targeted title/code searches. No original analysis repository was located. This is not proof none is public. Two GitHub name matches inspected were older unrelated projects, not evidence of a recent reproduction.

OpenReview has a page for the paper at https://openreview.net/forum?id=HJlr9NBgUr. It presents a browser-verification page to the research tool; the public API attempt returned 403. The researcher has been asked to inspect its attachment links. No access check was bypassed, and no authors were contacted.

The other requested action is downloading the small Allstate test CSV into `data/reference/` so we can count rows and unique `customer_ID` values. No audio archive is needed.

## Recorded outputs

The original-only script now includes benchmark/tie sensitivities, first-day ambiguity bounds, a reproducible synthetic null check, and the conditional Allstate reconstruction. Numerical results are stored alongside the first-pass outputs. Main dependencies and input hashes remain recorded. The new competitions' score comparisons remain sealed.
