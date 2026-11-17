# Response to the pre-unsealing review of Addendum A (`review_2026-11-17_deadline.md`)

Author: Claude. Date: 17 November 2026. No post-deadline score has been read.

**Summary.** The review found a real defect and the design is changed. I accept findings 1, 3 and 4 in full and finding 2 in substance. I do not accept that the test should be dropped, and the review does not ask for that. Addendum v1.0 is withdrawn (never archived, never run). Version 1.1 is in `analysis_plan/addendum_A_deadline_contrast_v1.1.md`, marked not yet fixed, for a second pre-unsealing check.

| # | Finding | Position | What changed |
|---|---|---|---|
| 1 | Unequal windows: a linear feedback-free trajectory gives X = b(m - q)/2 | Accepted. A design error of mine. | Four equal, consecutive windows of 3 submissions (C, A, B before; P = first 3 after). On the review's counterexample X = 0 for 3, 8 and 30 post-deadline submissions. My v1.0 simulator had q = 4 and m = 8, which built the result in, as the review says. |
| 2 | Composition need not continue linearly; adaptation need not reverse | Accepted in substance | "Opposite predictions" withdrawn. The addendum now calls the analysis descriptive, states the smoothness assumption under which a change is read as consistent with feedback dependence, and fixes in advance that a null is not evidence against adaptation. |
| 3 | The deadline bundles changes; exposure is unverified | Accepted | Stated as limits. The analysis is no longer described as a feedback test. I have not verified exposure per competition and do not think it can be done for 211 historical competitions. |
| 4 | Ties; "conservative" restriction; null wording; dependence; clipping | Accepted | Zeros excluded from tests and counted; the public-score restriction is dropped; readings of non-significance fixed; O and E pooling and partial prior exposure stated. |

## Where I keep my own position

1. **Smooth curvature is handled, not just linear trends.** I added Y = X - X_placebo, which is zero for any quadratic trajectory, and require both X and Y to be significant and negative. In the suite, a concave quadratic gap and a smoothly saturating gap, both feedback-free, are not reported as changes.

2. **A bend placed exactly at the deadline cannot be excluded by any design on these data, and I say so.** The review's second counterexample is in the suite as case 4 and is reported as a known failure. I do not think that makes the analysis worthless. An interrupted series read under a stated continuity assumption is a standard, modest form of evidence; the paper will present it as that and no more.

3. **The asymmetry is real and now explicit.** If teams keep optimising the public score after the deadline, nothing changes and the design sees nothing (case 7). So only one outcome is informative. I still think it is worth running: the post-deadline scores exist, have not been used by anyone in this literature as far as our searches show (not a novelty claim), and the cost is small.

## Suite results (`outputs/stage7/selftest_suite.csv`)

Linear: X = Y = 0 at every post-deadline count. Concave quadratic: X = placebo, Y = 0. Smooth saturation: Y > 0. Saturation exactly at the deadline: X < 0 and Y < 0 (known failure). Adaptive then private-steered: X < 0 in 100%, Y < 0 in 93% of 60 simulated competitions. Adaptive then unsteered: 97% and 83%. Adaptive throughout: about half (blind). Noise: about half.

## Request

Please check v1.1 before it is fixed: the window construction in `team_windows`, the two-test rule, and whether any feedback-free trajectory other than a deadline-located bend produces both X < 0 and Y < 0. If you find one, I would rather drop the test than run it.
