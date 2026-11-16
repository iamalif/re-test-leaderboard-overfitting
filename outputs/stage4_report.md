# Stage 4: follow-up analyses (EXPLORATORY)

16 November 2026. Nothing here was in analysis plan v1.0. These analyses were chosen after seeing the stage 3 results and must be reported as exploratory. Scripts: `scripts/stage4_drift_robustness.py`, `scripts/stage4_code_only.py`. Tables: `outputs/stage4/`.

## 1. Does the drift result survive alternative explanations?

Two explanations that need no adaptation: (A) teams start with trivial submissions that have no gap, then inherit the competition's gap level; (B) the gap scales with score level and teams improve.

| Version of the drift measure | E: competitions with positive drift | O |
|---|---:|---:|
| Planned: later half minus earlier half | 327 of 481 = 68.0% | 77 of 114 = 67.5% |
| Third quarter versus fourth quarter of each team's submissions | 304 of 480 = 63.3% | 69 of 113 = 61.1% |
| After dropping each team's first two submissions | 314 of 480 = 65.4% | 82 of 114 = 71.9% |
| Within-team slope, controlling for score level | 317 of 480 = 66.0% | 78 of 114 = 68.4% |

Explanation A predicts negative drift where first submissions have a negative gap. In those E competitions the planned drift is positive in 140 of 212 (66.0%) and the late-only drift in 144 of 211 (68.2%). The drift result is not produced by A or B.

## 2. Why do code-only competitions show larger relative gaps (S3)?

Like-for-like comparison within E Featured and Research competitions:

| | Code-only (n = 127) | Not code-only (n = 57) | p |
|---|---:|---:|---:|
| Mean gap positive | 75.6% | 63.2% | 0.11 |
| First-submission gap positive | 67.7% | 61.4% | 0.41 |
| Drift positive | 71.3% | 75.0% | 0.72 |
| Median relative gap | 0.30 | 0.06 | 0.12 |
| Median relative gap, unflagged only | 0.19 | 0.02 | 0.03 |

- Most of the S3 contrast is composition: code-only competitions are almost all Featured or Research, and S3 compared them with a pool dominated by Playground and Community competitions.
- The gap is already present in teams' first submissions (median 0.18 of the team spread), and drift is no more common. This points to how the public and private sets are built or scored, not to more adaptation.
- The yardstick also differs: team spread relative to first-submission noise is 3.6 in code-only competitions, 5.6 in other E prize competitions and 12.2 in O prize competitions. Scores are more tightly packed, which inflates any gap expressed in team spreads.

## 3. Featured and Research competitions before and after April 2019

| | E (n = 184) | O (n = 68) | p |
|---|---:|---:|---:|
| Mean gap positive | 71.7% | 60.3% | 0.09 |
| First-submission gap positive | 65.8% | 54.4% | 0.11 |
| Top-10% gap positive | 81.5% | 66.2% | 0.02 |
| Drift positive | 72.5% | 70.6% | 0.75 |
| Median relative gap | 0.17 | 0.01 | 0.003 |
| Median relative first-submission gap | 0.08 | 0.01 | 0.007 |

Restricted to unflagged competitions the pattern is the same (median relative gap 0.09 against 0.003, p = 0.002). Only 23 of the 184 E competitions use one of the five original metrics.

**Reading.** In prize competitions, public scores sit further above private scores, relative to the spread between teams, than they did before April 2019. The difference is there from the first submission and drift is unchanged, so this looks like a change in competition design or in how tightly teams are packed, not a rise in adaptation. The confirmatory tests H1a and H1b could not see it, because prize competitions have largely left accuracy and AUC. The mechanism is not identified.

**Consequence for the paper.** The headline must be scoped: the 2019 conclusion holds for accuracy and AUC competitions, which are now mostly in-class. For prize competitions the paper reports this exploratory pattern as an open question, with the yardstick caveat.

## 4. Reproducibility check

All scripts from stage 0 to stage 4 were re-run from the raw files in a clean directory under Python 3.12. Every per-competition table and every result table matched the project's outputs (largest relative difference 9e-14) once the bootstrap ordering note in the stage 3 report was fixed.
