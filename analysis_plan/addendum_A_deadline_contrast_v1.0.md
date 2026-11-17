# Addendum A to analysis plan v1.0: the deadline contrast

**Version 1.0, fixed 17 November 2026.** It takes effect when it is posted publicly with a third-party timestamp. Until then no post-deadline score may be read. Plan v1.0 is unchanged; this addendum adds one confirmatory test on data that plan v1.0 did not use.

## 1. Why

Plan v1.0 found that teams' later pre-deadline submissions favour the public leaderboard more than their earlier ones (H2). Two independent reviews showed that this pattern does not establish adaptation: a model-dependent difference between the public and private sets can produce it without any use of feedback, and so can a random split of unequal sizes. More analysis of the same pre-deadline scores cannot settle this.

The deadline changes the feedback a team receives while leaving the two test sets unchanged. Before it, a team sees only its public score. After it, late submissions are still scored on both sets. The two explanations then make opposite predictions:

- **Dependence on public feedback** (tuning to the public score, or stopping after a favourable one): the pre-deadline rise in the gap should stop or reverse after the deadline.
- **Model-dependent difference between the sets:** the gap is a property of the model and the two sets, so it should continue on its course as teams keep changing their models.

## 2. What has and has not been looked at

- Post-deadline submissions: counted only (number per team and competition, and whether score fields are filled; `outputs/stage6/post_deadline_counts_metadata_only.csv`, `deadline_design_eligibility_metadata_only.csv`). No post-deadline score value has been read by anyone on this project. Every earlier script filters to pre-deadline submissions.
- Pre-deadline scores of O and E: fully examined. The pre-deadline quantities used below (drift between quarters) have been seen; the post-deadline quantities have not.

## 3. Assumption to verify before interpretation

After a competition's deadline, a team making a late submission is shown both its public and its private score. This is the mechanism by which feedback changes. If it cannot be confirmed from Kaggle documentation, the result is reported with that caveat. The test is run either way.

## 4. Sample and quantities

Code: `scripts/stage7_deadline_contrast.py` (hash in `SHA256SUMS_addendum_A.txt`). Its `--selftest` uses synthetic data only.

- Competitions: those analysed under plan v1.0 in cohorts O and E.
- Submissions: non-benchmark teams, finite public and private scores. Pre-deadline as in plan v1.0; post-deadline are those flagged `IsAfterDeadline`.
- Score handling as in plan v1.0 section 3; clipping bounds come from pre-deadline public scores and are applied to post-deadline scores as well.
- Eligible team: at least 8 scored pre-deadline submissions and at least 1 scored post-deadline submission.
- Per team, pre-deadline submissions in time order are cut into quarters. Q2, Q3, Q4 are the mean gaps of the second, third and fourth quarters; P is the mean gap of all the team's post-deadline submissions.
  - Step across the deadline: J = P - Q4.
  - Last step before the deadline: Dq = Q4 - Q3.
  - Change of step: X = J - Dq.
- Per competition: the mean of J and of Dq over eligible teams, and X as their difference. A competition enters if it has at least 20 eligible teams. Metadata count: 338 competitions (59 O, 279 E) before any further loss.

## 5. The one confirmatory test

**T1.** Across the O and E competitions together, the share with X < 0 differs from one half (two-sided sign test, alpha 0.05). Reported with the share, the median of X in team spreads, and a 95% bootstrap interval over competitions.

Interpretation fixed in advance:

- Share of X < 0 significantly above one half: the gap's course changes at the deadline in the direction that dependence on public feedback predicts.
- Significantly below one half: the gap rises faster after the deadline; evidence against the feedback explanation in this form.
- Not significant: no evidence that the deadline changes the gap's course; the pre-deadline drift is not shown to depend on feedback.

The 50% reference is exact only if, absent any deadline effect, consecutive steps are exchangeable. That is an assumption. The placebo in section 6 checks it on the same competitions.

## 6. Secondary analyses (reported with intervals, not confirmatory)

- T1 separately for E and for O.
- Share of competitions with J < 0, and median J in team spreads.
- **Placebo:** the same statistic one quarter earlier, X_placebo = Dq - (Q3 - Q2), which involves no deadline; and the paired difference X - X_placebo.
- **Conservative restriction:** only teams whose mean post-deadline public score is at least as good as their Q4 mean public score. Selecting on a high public score raises the post-deadline gap, so this works against finding X < 0.
- Unclipped scores; unflagged competitions; accuracy, AUC and MAP@K only; competitions with positive pre-deadline drift.
- Context: the change in private score across the deadline and in the last pre-deadline step, to show whether teams' models keep improving.

## 7. Known limits, stated in advance

- Teams that submit after the deadline select themselves, and their purposes change (experiments, write-ups, learning). The contrast is within team, but a change in what teams submit could move the gap for reasons other than feedback. The private-score context and the conservative restriction address this only in part.
- If models get worse after the deadline and the gap depends on model quality, X could be negative without any feedback effect. The context rows show whether models get worse.
- P pools all post-deadline submissions, which may span years.
- After the deadline a team may tune to the private score. A fall in the gap for that reason is still dependence on feedback, but it is not evidence about the size of pre-deadline overfitting.
- Competitions are treated as independent units.
- This is one further test on aggregate scores. It cannot identify how much of the pre-deadline drift is adaptation.

## 8. Deviations

Logged in `decision_log.md` with date and reason, and listed in the paper.
