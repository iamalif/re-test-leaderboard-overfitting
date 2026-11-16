# Analysis plan: re-testing leaderboard overfitting on Kaggle

**Version 1.0, fixed 16 November 2026.** Approved under authority the researcher delegated to the analysis assistant on 16 November 2026. It takes effect when it is posted publicly with a timestamp (for example on OSF). No public/private score of any extension competition may be read before that.

Study: a re-test and extension of Roelofs et al., "A Meta-Analysis of Overfitting in Machine Learning" (NeurIPS 2019). Data: Meta Kaggle, downloaded 15 November 2026 (SHA-256 hashes in `decision_log.md`).

## 1. What has and has not been looked at

- **Original 120 competitions (published IDs): fully examined.** All measures below were developed and piloted on them. Results on them are exploratory, not confirmatory.
- **Extension competitions: metadata only.** Counted: submissions per competition, whether score fields are filled, metric names, deadlines, host category, code-only flag, reported public share, and the length and keywords of description text. No score value has been read and no public/private comparison made.
- **In-window competitions not in the 120** (deadline on or before 4 April 2019): metadata only, same as above.

## 2. Cohorts

- **O (original):** the 120 competition IDs in the paper's appendix tables 2 to 6.
- **E (extension):** deadline after 2019-04-04 23:59 and on or before 2026-11-15; not in O. Reason for the boundary: the latest deadline in O is 2019-04-04, and the next competition meeting the paper's rule (deadline 2019-04-09) is absent from O.
- **W (in-window regression):** deadline on or before 2019-04-04 23:59, not in O, metric RMSE, MAE, MSE or RMSLE. Used only for the regression question (S1). The paper excluded regression by design.

Inclusion, applied identically to O, E and W:

1. At least 1,000 submissions before the deadline (the paper's rule).
2. Reported public leaderboard share between 1 and 99 percent.
3. At least 1,000 pre-deadline submissions that have finite public and private scores and come from non-benchmark teams. These are the analysis submissions.
4. Excluded as having no effective split: competitions where at least 99% of analysis submissions have identical public and private scores (checked mechanically after unsealing; in O this removes CIFAR-10, ID 3649).

Metadata-only counts under rules 1 to 3: O 117, E 516, W 51.

## 3. Score handling

- Gap = public minus private, signed so that positive means the public score looks better. Direction comes from `EvaluationAlgorithmIsMax`.
- Accuracy, AUC and MAP@K are analysed on raw scores. For every other metric, both scores are clipped to the 1st to 99th percentile range of the competition's public scores. The bounds never use private scores.
- Submission order within a team is (submission date, submission ID). Dates have day precision; in O, IDs never run against date order.
- Top 10% by public score keeps every submission tied at the cutoff.
- The competition is the unit of inference. Submissions within a competition are not treated as independent.

## 4. Metric groups

- Accuracy: `CategorizationAccuracy`, plus numeric-ID metrics named "Accuracy Score".
- AUC: `AUC`, plus numeric-ID metrics named "Roc Auc Score" or "sklearn_roc_auc_score".
- MAP@K: `MAP@{K}`, `MAP@k`, `MAP@3`, `AP@{K}`, `MAP@{K}_OLD`.
- LogLoss: `LogLoss`. MulticlassLoss: `MulticlassLoss`, `MulticlassLossOld`.
- Regression: `RMSE`, `MAE`, `MSE`, `RMSLE`, plus numeric-ID metrics named "Mean Squared Error", "Mean Absolute Error", "Mean Squared Log Error", "Root Mean Squared Error", "Root Mean Squared Log Error".
- Classification (for S1): the five groups above.
- Everything else: "other". Used only in all-metric analyses (H2, S3, S4).

## 5. Measures per competition

Code: `scripts/stage2_measures.py`.

- **Mean gap** over all analysis submissions (the paper's measure), in the metric's own units.
- **Team spread:** the distance between the median team and the top-decile team, on teams' median public score. A unit-free yardstick.
- **Relative gap** = mean gap / team spread.
- **Team drift:** for each team with at least 4 analysis submissions, the mean gap of the later half of its submissions minus the mean gap of the earlier half (the middle one dropped if the count is odd). The competition's drift is the mean over teams. No submission is selected by score, so selection on public score cannot create drift. A fixed public/private difference (for example a non-random split) cancels within team.
- **Relative drift** = drift / team spread.
- **Accuracy only, test-set sizes:** inferred from the scores as the smallest size on which every score is a whole count of correct answers, public and private separately. Used only when every score fits.
- **Accuracy only, null-model p-values:** exact two-sided inclusive tail under the paper's null model (a submission's correct answers split at random), with inferred sizes.
- **Accuracy only, selection-adjusted top-decile gap:** observed top-10% mean gap minus the top-10% mean gap expected under the same null model when the top 10% is chosen on simulated public scores (200 simulated splits).

## 6. Confirmatory hypotheses

Four tests, two-sided, Holm-corrected at an overall 0.05. Each is reported with an effect size and a 95% bootstrap interval (resampling competitions, 10,000 draws).

- **H1a. Accuracy level.** The distribution of mean gaps in E accuracy competitions differs from O. Mann-Whitney test; effect size: difference in medians, in percentage points.
- **H1b. AUC level.** Same for AUC competitions.
- **H2. Drift exists in E.** Across all E competitions (all metrics), the share with positive drift differs from one half. Sign test; effect size: the share, and the median relative drift.
- **H3. Drift changed.** Relative drift in E competitions of the five original metric groups differs from O. Mann-Whitney test; effect size: difference in medians.

Also always reported next to H1: the share of competitions with a mean gap above 1 percentage point (accuracy) and above 0.01 (AUC), per cohort.

A non-significant result is reported as such, with the interval; it is not described as evidence of no difference unless the interval excludes differences larger than the thresholds just named.

## 7. Secondary analyses (pre-specified, reported with intervals, not confirmatory)

- **S1. Regression versus classification (RQ2).** Share with positive drift, relative drift and relative gap; regression (E plus W) against classification (E plus O), and within E alone.
- **S2. Test-set size (RQ3).** Accuracy competitions with inferred sizes, O and E together and separately: absolute mean gap and selection-adjusted top-decile gap against total test size (Spearman), and below versus at-or-above 10,000 examples.
- **S3. Platform changes (RQ5).** Within E: code-only versus not, and Featured, Research, Playground, Community; drift and relative gap for each.
- **S4. Time.** Within E: relative drift and relative gap against deadline year (Spearman).
- **S5. Formal accuracy test.** Share of p-values at or below 0.05 for all submissions and for first-per-team submissions, per competition, with inferred sizes. Top-10% p-values are shown only next to the selection-adjusted gap.
- **S6. Split type.** H1 to H3 repeated on competitions not flagged as time-based, group-based or two-stage (labels in section 8).

## 8. Labels

Split-type labels were assigned on 16 November 2026 from competition description text only, before any extension score was read. Table: `outputs/stage3/split_labels.csv`, SHA-256 `edf340c395de553bb53086c811dc32ad3c4bb8d9313eb44f57455f155abab1b2`. Labels are not changed after unsealing.

- **Rubric.** A competition is flagged only when its description states that the private set differs from the public set in how it was drawn or scored:
  - TIME: public and private are separated by time, or private is a later period.
  - GROUP: public and private come from different subjects, sources, domains or categories, or are scored differently.
  - NEWDATA: the private score is computed on a second-stage, future or newly collected dataset.
  - RANDOM: the description states the public/private split is random. Not flagged.
  - UNSTATED: no such statement found. Not flagged. NO_TEXT: description under 200 characters. Not flagged.
- **Procedure.** `scripts/stage3_label_extract.py` pulls the sentences that mention the public or private set, stages, future data, forecasting or split wording. Those sentences were read for every competition; a second pattern pass over full descriptions caught five more statements. Decisions and reasons: `data/reference/split_label_decisions.py`.
- **Counts.** Flagged: O 12 of 117, E 44 of 516, W 4 of 51. Stated random: O 3, E 2.
- **Limits.** A difference between train and test data alone is not flagged. Labels reflect what hosts wrote; most descriptions say nothing, so UNSTATED is not evidence of a random split. One reader made the decisions. Before submission, the full descriptions of a random sample of 50 unflagged competitions are re-read and the agreement reported.
- Number of classes (RQ4) is exploratory and attempted only if it can be found for at least 70% of accuracy competitions.

## 9. Exploratory, clearly marked as such

- Number of classes and the gap (RQ4).
- Notebook forking and drift (needs the Meta Kaggle kernel tables; not yet downloaded).
- Rank changes between public and private leaderboards, from the team rank columns.
- Anything else suggested by the data after unsealing.

## 10. Known limits, stated in advance

- Drift is evidence of adaptation to the public set but is not a pure measure of it. It would also arise if a public/private difference grew with model quality. It is blind to adaptation that is already complete at a team's first submission, for example a forked public notebook.
- Mean gaps mix adaptation, selection and split design. A gap alone is never called adaptive overfitting.
- The null-model p-values assume each submission gets its own random split; real submissions share one split and are correlated.
- Formal accuracy tests rest mostly on Community (in-class) competitions in both cohorts: 25 of 34 in O, 85 of 94 in E. Only 2 E accuracy competitions ended in 2023 or later.
- Inferred test sizes assume ordinary unweighted accuracy.
- One snapshot of Meta Kaggle; submission counts for O differ from the paper's by up to 2.6%.

## 11. Deviations

Any departure from this plan after posting is logged in `decision_log.md` with its date and reason, and listed in the paper.

## Appendix: pilot on the original 120 (exploratory)

From `scripts/stage2_pilot_original.py`; outputs in `outputs/stage2/`. The pilot used all 120 competitions without inclusion rule 2 (three of them report a public share of 0 or 100); three competitions drop out for identical scores or an undefined team spread, leaving 117.

- **Simulation.** With no adaptation, drift averaged -0.02 percentage points whether or not the private set was 3 points harder; the top-10% gap was 0.75 and 3.75 points. With adaptation, drift was 1.18 points in both cases. Drift separated adaptation from split difference and from selection; the gap measures did not.
- **Drift in O.** Positive in 78 of 117 competitions (sign test p = 0.0004): AUC 31 of 40 (p = 0.0007), accuracy 17 of 33, MAP@K 12 of 17, LogLoss 9 of 13, MulticlassLoss 9 of 14. Median relative drift 0.6% of the team spread (AUC 1.4%).
- **Inferred sizes.** They equal the published sizes in 21 of the 32 accuracy competitions that have published sizes, and give sizes for the 2 that have none. Differences in the other 11: Allstate (customers, not rows); four off by one or with public and private swapped (3362, 9051, 12598, 13383); three with the same or nearly the same total but a different split (3428, 3641, 7115); two with much smaller scored totals (7042, 7634); and CIFAR-10 (3649), where both scores sit on 10,000 examples and are identical.
- **P-values.** An independent implementation matches the earlier stage 1 implementation on 68,552 submissions to within 1.5e-15.
- **Selection-adjusted top-decile gap.** Among the paper's five outliers, the top-10% gap is about what selection alone predicts for 5903 and 12681 (excess -0.23 and +0.06 points) and exceeds it for 12598 (+6.0), 3641 (+2.8) and 12349 (+1.2).
