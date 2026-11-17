# Response to the follow-up review (`review_2026-11-16_followup.md`)

Author: Claude. Date: 17 November 2026. Reviewed baseline: commit 517ee6f. Paper now v0.3 (`paper/main.pdf`); v0.2 kept as `paper/main_v0.2_before_followup.tex`.

**Summary.** The follow-up is right on all five points. The converse I added in the first response was false as stated and has been withdrawn. My own simulation had already returned 44.7% positive under a random split; I treated that as noise instead of asking why it was not 50%.

| # | Finding | Position | What changed |
|---|---|---|---|
| 1 | A random split does not make the sign of drift a fair coin | Accepted | Abstract and methods corrected: zero expectation for example-averaged metrics; balanced sign only with equal sizes and unclipped scores. H2 is reported as a pre-specified test against a 50% reference, with no claim that the reference follows from non-adaptivity. The exact counterexample is in the paper. |
| 2 | The "first submissions fit the null" subgroup is not evidence of a random split | Accepted | Removed from the paper. Kept in `outputs/stage6/` with a label saying it is outcome-selected. Cohort composition of the five stated-random competitions (3 O, 2 E) now given. |
| 3 | Three invalid fits in the size tiers | Accepted | Tier inventory restricted to the 125 usable fits: A 1, B 21, C 96, D 7. The three unusable competitions are stated. "Usually right" wording removed; 21 of 21 described as corroboration within that subset only. |
| 4 | Full-text second-reader audit; code-only wording | Accepted with thanks | The paper reports the second reading and its limits (not blind to labels or results). "Scored by re-running submitted code" replaced by "accept submissions only from notebooks", with a note that not all re-run on hidden data. |
| 5 | Runner does not stop on a stage 3 failure | Accepted | `run_all.sh` now captures the exit status, fails on non-zero, retries only on PAUSED, and documents that cached rows are skipped. Not yet re-run end to end. |
| - | 1% magnitude tied to the wrong subset | Accepted | Abstract now gives 1.7% (all metrics) and 0.8% (five original groups). |
| - | "Two explanations can be set aside" | Accepted | Replaced by "the pattern survives three changes to the measure; these checks do not exclude every version of the mechanisms". |

## One new exploratory analysis prompted by finding 1

The unequal-size mechanism has a direction: the sign skews towards the smaller set's behaviour, so it should weaken or reverse when the public set is not the smaller one. `scripts/stage6_split_size_symmetry.py`, output `outputs/stage6/split_size_symmetry.csv`:

| Reported public share | All metrics, planned drift (O+E) | Accuracy/AUC/MAP@K, unclipped (O+E) |
|---|---|---|
| Under 40% | 263 of 394 (67%) | 92 of 140 (66%) |
| 40-49% | 36 of 46 (78%) | 7 of 10 (70%) |
| Exactly 50% | 95 of 151 (63%) | 58 of 90 (64%) |
| Over 50% | 37 of 55 (67%) | 22 of 30 (73%) |

- The share does not depend on which set is smaller. In the equal-size, unclipped subset, where a random split without feedback does give a balanced sign, drift is positive in 58 of 90 (sign test p = 0.008); E alone 37 of 61 (p = 0.12), O alone 21 of 29 (p = 0.02).
- Mean unclipped drift, whose expectation is zero under a random split for any sizes: accuracy, O+E, 0.10 pp (0.02 to 0.19); E alone 0.11 pp (-0.01 to 0.22). AUC, E: 0.0001 (-0.0020 to 0.0014).
- Reading: the unequal-size mechanism does not account for the pattern. This says nothing about the composition mechanism of the first review, which remains open. The analysis is exploratory, pools a fully examined cohort with the later one, and relies on the reported (nominal) public share. Please check it as critically as the rest.

## Still open

Series-level dependence between competitions; matched O-versus-E comparisons; fuller tail and absolute-gap summaries for H1; a clean end-to-end run of the revised `run_all.sh`; anonymised code package.
