# Stage 3 results: the extension, under analysis plan v1.0

16 November 2026. Plan: `analysis_plan/stage2_analysis_plan_v1.0.md`, public and archived before any of these scores were read (links in `decision_log.md`). Scripts: `scripts/stage3_extension.py`, `scripts/stage3_tests.py`. Tables: `outputs/stage3/`.

## Sample

| Cohort | Passed rules 1-2 | Dropped: under 1,000 finite scores | Dropped: identical public and private scores | Analysed |
|---|---:|---:|---:|---:|
| O, original | 117 | 0 | 3 | 114 |
| E, extension | 518 | 2 | 29 | 487 |
| W, earlier regression | 51 | 0 | 0 | 51 |

The 29 E competitions with identical scores are mostly simulation contests and tournament forecasts; 12 of them had been flagged NEWDATA or similar by the blind labels.

## Confirmatory tests (Holm-corrected)

| Test | E | O | Difference, E minus O (95% interval) | p | Holm p |
|---|---|---|---|---:|---:|
| H1a accuracy, median of competition mean gaps | 0.030 pp (n = 95) | 0.059 pp (n = 33) | -0.029 pp (-0.172 to 0.121) | 0.59 | 1.00 |
| H1b AUC, median of competition mean gaps | 0.0005 (n = 73) | 0.0012 (n = 40) | -0.0007 (-0.0043 to 0.0011) | 0.24 | 0.72 |
| H2 share of E competitions with positive drift | 327 of 481 = 68.0% (63.8 to 72.1) | | against 50% | 2e-15 | 9e-15 |
| H3 relative drift, five metric groups, median | 0.79% (n = 194) | 0.66% (n = 113) | 0.13 points (-0.33 to 0.97) | 0.92 | 1.00 |

- **H1: no detectable change in gap level.** The intervals exclude a shift as large as the pre-set thresholds (1 pp for accuracy, 0.01 for AUC), so this is evidence against a material change, not just a failure to detect one.
- **H2: drift exists.** In two thirds of new competitions, teams' later submissions have a larger public-over-private gap than their earlier ones. Median size: 1.7% of the distance between a median and a top-decile team (all metrics).
- **H3: drift did not change.** Its size in the five original metric groups is the same before and after April 2019.
- Share of competitions with a large mean gap: accuracy above 1 pp, O 15% (5 of 33), E 11% (10 of 95); AUC above 0.01, O 30%, E 18%.
- S6: restricted to competitions not flagged for split type, all four results are unchanged (H2: 312 of 453 = 68.9%).

## Secondary analyses (not confirmatory)

- **S1 regression versus classification.** No clear difference. Median relative drift: regression 0.5% (E+W, n = 124), classification 0.7% (E+O, n = 307); difference -0.2 points (-1.0 to 2.0). Within E: 2.1% against 0.8%, difference 1.3 points (-1.2 to 8.1).
- **S2 test-set size (accuracy, inferred sizes, n = 125).** The absolute mean gap falls with test size (Spearman -0.61): median 0.83 pp under 10,000 examples, 0.16 pp at 10,000 or more. The selection-adjusted top-decile gap does not vary with size (Spearman 0.12, p = 0.20; medians -0.07 and 0.01 pp). Small test sets make gaps noisier; there is no sign they add overfitting beyond what chance and selection produce.
- **S3 platform.** Code-only competitions have much larger gap levels: median relative gap 30% of the team spread (n = 129) against 0.7% elsewhere (n = 358), difference 29 points (8 to 52). Featured 15%, Research 17%, Playground 0.7%, Community 0.2%. Drift is also higher in code-only competitions: 4.3% against 1.2%, difference 3.1 points (0.8 to 4.6).
- **S4 time.** No trend in relative drift or relative gap across deadline years 2019 to 2026 (Spearman 0.03 and 0.01).
- **S5 formal accuracy test.** Usable for 33 of 33 O and 92 of 95 E accuracy competitions. Median share of first-per-team p-values at or below 0.05: O 1.7%, E 1.8%. Competitions where that share exceeds 10%: O 9%, E 11%. Median selection-adjusted top-decile gap: O -0.006 pp, E 0.009 pp.

## What this supports, and what it does not

- Supported: the 2019 conclusion about gap levels holds for accuracy and AUC competitions after April 2019.
- Supported: a small, systematic drift toward the public leaderboard exists in both periods, at about the same size, and does not depend on excluding flagged splits.
- Not established: that the large gap level in code-only competitions is adaptive overfitting. Gap level also reflects split design, and code competitions often score a hidden, larger private set. The higher drift there points the same way but is a secondary result. This needs follow-up before any claim.
- Limits from the plan still apply (section 10): drift is not a pure measure of adaptation; accuracy tests rest mostly on Community competitions (82 of 95 in E, 25 of 33 in O); labels reflect only what hosts wrote.

## Implementation notes and deviations

1. The formal accuracy test additionally requires all scores to lie in 0 to 1. One E competition reports scores outside that range; two more do not fit a lattice. This implements the plan's "used only when every score fits".
2. Rule 3 was applied to finite scores, which removed 2 E competitions that the metadata count had passed.
3. Relative measures have extreme values in a few competitions where more than 1% of public scores are astronomically large, so percentile clipping does not bound them. Every reported statistic is a median, rank or sign and is unaffected; means of relative measures must not be reported.
4. No other departure from plan v1.0.
