# Addendum A to analysis plan v1.0: the deadline contrast

**Version 1.1, 17 November 2026. NOT YET FIXED: awaiting a second pre-unsealing review.** It takes effect only when it is posted publicly with a third-party timestamp. Until then no post-deadline score may be read. Version 1.0 was never archived or run; a pre-unsealing review found its statistic invalid (unequal observation windows) and it is kept in `superseded/` for the record.

## 1. What this is, and what it is not

A pre-specified **descriptive** contrast: does the course of the public-minus-private gap change at the competition deadline, beyond what its own prior course predicts?

It is motivated by the fact that feedback changes at the deadline while the two test sets stay the same. It is **not** a test that identifies adaptation. The deadline also changes submission limits, sharing rules, incentives and what teams choose to submit, and a model-dependent gap could change course at the deadline for reasons unrelated to feedback. The result is read under one stated assumption (section 5) and its limits are fixed here in advance (section 8).

## 2. What has and has not been looked at

- Post-deadline submissions: counted only (scored submissions per team and competition: `outputs/stage6/post_deadline_counts_metadata_only.csv`, `outputs/stage6/deadline_design_eligibility_metadata_only.csv`, `outputs/stage7/eligibility_v1.1_metadata_only.csv`). No post-deadline score value has been read by anyone on this project, including during both design reviews.
- Pre-deadline scores of O and E have been fully examined. The pre-deadline windows used below are therefore not new data; only the post-deadline window is. This is not a fully untouched study.
- Window size was chosen as 3 before the eligibility counts for 2, 3 and 5 were produced; all three counts were then seen.

## 3. Sample and windows

Code: `scripts/stage7_deadline_contrast.py`. Its `--selftest` uses synthetic data only.

- Competitions: those analysed under plan v1.0 in cohorts O and E, pooled.
- Submissions: non-benchmark teams, finite public and private scores; score handling as in plan v1.0 section 3, with clipping bounds taken from pre-deadline public scores and applied to both periods.
- For each team, in time order (date, then submission ID), with window size w = 3:
  - B = its last 3 pre-deadline submissions; A = the 3 before those; C = the 3 before those.
  - P = its first 3 post-deadline submissions.
  - Eligible team: at least 9 scored pre-deadline and at least 3 scored post-deadline submissions.
- All four windows have the same size and are consecutive in submission order, so the statistic does not depend on how many post-deadline submissions a team made beyond the first three.
- A competition enters with at least 20 eligible teams. Metadata count: 211 competitions (41 O, 170 E), about 10,000 teams.

## 4. Quantities

Per team, with each letter standing for the mean gap in that window:

- X = (P - B) - (B - A): the change of step at the deadline. Zero for any gap trajectory that is linear in submission order.
- X_placebo = (B - A) - (A - C): the same statistic one window earlier, involving no deadline.
- Y = X - X_placebo. Zero for any gap trajectory that is quadratic in submission order.

Per competition: the mean over eligible teams.

## 5. Primary analysis

Two sign tests across the pooled O and E competitions, each two-sided at 0.05: the share of competitions with X < 0, and the share with Y < 0, each against one half. Competitions with a value of exactly zero are excluded from a test and their number reported.

**A deadline-specific downward change is reported only if both are significant with shares above one half.** Requiring both keeps the overall error rate at 0.05 and guards against smooth curvature, which moves X and the placebo together.

Reported alongside: counts negative, positive and zero; medians of X and Y in team spreads with 95% bootstrap intervals over competitions.

**Assumption under which a downward change is read as consistent with dependence on public feedback:** absent a change in feedback, the gap would have continued on a course that is smooth across the deadline (at most quadratic over the four windows). This cannot be verified.

Fixed readings:

- Both significant and negative: the gap's course bends downward at the deadline. Consistent with dependence on public feedback under the assumption; not proof of it.
- Both significant and positive: the gap rises faster after the deadline.
- Otherwise: no deadline-specific change detected. This is **not** evidence against adaptation: teams may keep optimising the public score after the deadline, in which case nothing changes (section 6, case 7). Reported with intervals, not as "no change".

## 6. Synthetic suite (run before unsealing; `outputs/stage7/selftest_suite.csv`)

| Case | X | Placebo | Y | Outcome under the rule |
|---|---|---|---|---|
| 1. Linear gap, feedback-free (review counterexample 1), 3, 8 or 30 post-deadline submissions | 0 | 0 | 0 | No change reported |
| 2. Concave quadratic gap, feedback-free | negative | equal to X | 0 | No change reported |
| 3. Gap saturating smoothly, feedback-free | negative | more negative | positive | No change reported |
| 4. **Gap saturating exactly at the deadline, feedback-free (review counterexample 2)** | negative | 0 | negative | **Change reported: the design cannot tell this from feedback** |
| 5. Adaptive before; private score steers after | negative in 100% of 60 simulated competitions | about half | negative in 93% | Change reported |
| 6. Adaptive before; unsteered changes after | negative in 97% | about half | negative in 83% | Change reported |
| 7. **Adaptive before and after (public score still steers)** | 63% | 65% | 50% | **No change reported: the design is blind to this** |
| 8. No feedback use, noise only | 52% | 47% | 53% | No change reported |

Cases 4 and 7 are the design's known failures and are part of the result's interpretation.

## 7. Secondary and sensitivity analyses (not confirmatory)

- X and Y separately for E and O; unflagged competitions; competitions that are not notebook-only; accuracy, AUC and MAP@K only; competitions with positive pre-deadline drift.
- Window sizes 2 and 5.
- Unclipped scores.
- Post-deadline window restricted to submissions within 30 days after the deadline.
- Context: the gap steps P - B and B - A themselves, and the change in private score across the deadline and in the last pre-deadline step.

## 8. Limits fixed in advance

- **Exposure is not verified.** It is assumed that after the deadline teams can see private scores. Search results on 17 November 2026 support this for Kaggle in general but not for each of the 211 competitions at each date, and a team's first late submissions may have been prepared before it saw any private score. If the assumption fails, a real feedback effect is diluted, not created.
- **The deadline bundles changes:** private scores revealed, submission limits relaxed, sharing restrictions lifted, incentives gone. A change at the deadline cannot be attributed to any one of them.
- **Self-selection and purpose:** teams that submit after the deadline choose to, and may submit different kinds of models. The contrast is within team, which removes stable team differences only.
- **Windows are equal in submissions, not in calendar time.**
- **Sign tests have a justified 50% reference only if steps are exchangeable absent a deadline effect.** The placebo checks this one window earlier; a non-significant placebo does not prove it.
- **Competitions are not independent draws.**
- A downward change, if found, says nothing about how much of the pre-deadline drift is adaptation.

## 9. Deviations

Logged in `decision_log.md` with date and reason, and listed in the paper.
