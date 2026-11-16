> Superseded by `main.tex` / `main.pdf` (TMLR template). Kept for the record.

# Leaderboard overfitting on Kaggle, revisited: a pre-specified re-test with a within-team drift measure

**Draft v0.1, 16 November 2026. Working draft for the author; not yet in TMLR format.** Items marked [TODO] must be resolved before submission. Every number comes from the tables in `outputs/` and is traceable through `decision_log.md`.

## Abstract

Roelofs et al. (2019) compared public and private leaderboard scores in 120 Kaggle competitions and found little evidence of substantial adaptive overfitting. We re-test that conclusion on competitions that ended after their sample, with the analysis plan fixed and publicly archived before any new score was read. We first reconstruct the original study from Meta Kaggle: all 120 competitions are recovered and the five accuracy outliers reproduce, but the published test-set sizes are wrong or approximate for 11 of 32 accuracy competitions, and we show how to recover scoring sizes from the scores themselves. We then add a measure, within-team drift, that is unaffected by selection on public score and by fixed public/private differences. On 487 new competitions, the level of the public-private gap is unchanged for accuracy and AUC competitions (difference in medians -0.03 percentage points, 95% interval -0.17 to 0.12, and -0.0007, -0.0043 to 0.0011). Drift is positive in 68% of new competitions (327 of 481, p = 2e-15) and its size is the same as in the original sample: about 1% of the distance between a median and a top-decile team. Gap size falls with test-set size, but the part not explained by selection does not. Exploratory analyses show larger gap levels in recent prize competitions, present from teams' first submissions. The 2019 conclusion holds where it can be tested like for like; adaptation to the public leaderboard is real, systematic and small.

## 1. Introduction

- The public leaderboard is a test set reused thousands of times; the private leaderboard is used once. Their difference is the standard natural experiment on adaptive overfitting.
- The 2019 result is still cited as settled, while later sources disagree on whether Kaggle submissions overfit the public leaderboard. [TODO: cite the 2025 position paper, MLE-bench and the 2026 monoculture preprint after re-reading each; repeat the literature search and record its date. No peer-reviewed re-test was found in searches on 15-16 November 2026; this is not proof of absence.]
- Kaggle changed after 2019: code-only competitions, the Playground series, metrics defined per competition.
- Contributions:
  1. An independent reconstruction of the 2019 study, with documented discrepancies.
  2. Test-set sizes inferred from the score lattice, which extends the paper's formal test from 19 to 33 of its 34 accuracy competitions and to new competitions without hand collection.
  3. Two selection-aware measures: within-team drift, and a top-decile gap adjusted for selection under the paper's own null model.
  4. A pre-specified re-test on 487 later competitions.

## 2. The original study and its reconstruction

- **Sample.** The 120 competition IDs come from the paper's appendix. All are in the 15 November 2026 Meta Kaggle snapshot. We recover 1,510,406 pre-deadline submissions with both scores against 1,513,918 published; 46 of 120 counts match exactly and none differs by more than 2.6%.
- **Dating the snapshot.** The latest original deadline is 4 April 2019; the next eligible competition (9 April) is absent. The extension therefore starts after 4 April 2019.
- **Inclusion rule.** Applying the stated rule to today's data yields 28 further competitions in the original window. 26 of them report a public share of 0 or 100 percent, which suggests an unstated requirement of a real split.
- **Headline pattern.** The five largest mean accuracy gaps are the five outliers the paper names (12598, 12349, 5903, 3641, 12681).
- **Test-set sizes.** For 11 of the 32 accuracy competitions with published sizes, the sizes do not match the scores. The clearest case is Allstate (3788): the paper lists 59,657 and 139,199 examples, which sum to the 198,856 rows of the test file, but the task scores one prediction per customer and the file has 55,716 customers. The paper's text attributes this competition's small p-values to its "198,856 examples". With customer counts (16,714 and 39,002), 1.3% of submissions have p at or below 0.05; a normal approximation with the published counts gives 74.6%. We make no claim about what the original code computed.
- **Other discrepancies.** Day-precision dates, unspecified tie handling at the top-10% cutoff, and an inclusive tail in the main text against a strict one in the appendix. [TODO: one table listing each, from `outputs/stage1/reproduction_matrix.md`.]

## 3. Methods

- **Cohorts.** O: the original 120. E: deadline after 4 April 2019 and by 15 November 2026. W: earlier regression competitions, which the paper excluded by design. Inclusion: at least 1,000 pre-deadline submissions; public share between 1 and 99 percent; at least 1,000 scored submissions from non-benchmark teams; not identical public and private scores. Analysed: O 114, E 487, W 51.
- **Gap.** Public minus private score, signed so positive favours the public score. Competition mean gap as in the original.
- **Team spread.** Distance between the median team and the top-decile team on public score; gap and drift divided by it are unit-free.
- **Within-team drift.** For each team with at least four submissions, the mean gap of the later half minus the earlier half; averaged over teams. No submission is selected by score.
- **Inferred sizes.** For accuracy, the smallest test-set size on which every score is a whole count of correct answers.
- **Selection-adjusted top-decile gap.** Observed top-10% gap minus the gap expected when the top 10% is selected on public scores simulated under the paper's null model.
- **Validation.** Simulation: without adaptation drift is about 0 whether or not the private set is harder (top-10% gap 0.75 and 3.75 points); with adaptation drift is 1.18 points in both cases. Exact p-values agree with an independent implementation on 68,552 submissions.
- **Split labels.** Assigned from description text before unsealing; 44 of 516 E competitions flagged. Most descriptions say nothing about the split.
- **Pre-specification.** Plan v1.0 with four confirmatory tests (Holm-corrected) and six secondary analyses was committed to a public repository and archived on 16 November 2026, before any E or W score was read. [TODO: cite repository commit 0969d41 and the two archive links.] The measures were developed on O, which had been fully examined.

## 4. Confirmatory results

| Test | E | O | E minus O (95% interval) | Holm p |
|---|---|---|---|---:|
| H1a accuracy, median mean gap | 0.030 pp (n = 95) | 0.059 pp (n = 33) | -0.029 pp (-0.172 to 0.116) | 1.00 |
| H1b AUC, median mean gap | 0.0005 (n = 73) | 0.0012 (n = 40) | -0.0007 (-0.0043 to 0.0011) | 0.72 |
| H2 share of E competitions with positive drift | 68.0% (327 of 481; 63.8 to 72.1) | | against 50% | 9e-15 |
| H3 median relative drift, five metric groups | 0.79% (n = 194) | 0.66% (n = 113) | 0.13 points (-0.33 to 0.99) | 1.00 |

- Both H1 intervals exclude the pre-set thresholds for a material change (1 pp; 0.01).
- Results are unchanged when flagged competitions are removed.
- Figure 1: `figures/fig1_gap_level`. Figure 2: `figures/fig2_drift`.

## 5. Secondary results

- **Regression versus classification.** No clear difference in drift or relative gap (median relative drift 0.5% against 0.7%; difference -0.2 points, -1.0 to 2.1).
- **Test-set size** (Figure 3). Absolute mean gap falls with size (Spearman -0.61; median 0.83 pp below 10,000 examples, 0.16 pp at or above). The selection-adjusted top-decile gap does not (Spearman 0.12, p = 0.20). The 10,000 guideline is supported as protection against noise; we find no evidence that small test sets add overfitting beyond selection.
- **Time.** No trend in E, 2019 to 2026.
- **Formal accuracy test.** Median share of first-submission p-values at or below 0.05: O 1.7%, E 1.8%.
- **Platform.** Code-only competitions show larger relative gaps (median 0.30 against 0.007); see section 6.

## 6. Exploratory results

- **Robustness of drift.** Positive in 63.3% of E competitions using only the third and fourth quarters of each team's submissions, 65.4% after dropping each team's first two, 66.0% controlling for score level, and 66.0% where first submissions have a negative gap.
- **Selection explains two of the five original outliers.** For 5903 and 12681 the top-10% gap matches the selection-only expectation (excess -0.23 and +0.06 pp); for 12598, 3641 and 12349 it exceeds it (+6.0, +2.8, +1.2 pp).
- **Prize competitions** (Figure 4). Among Featured and Research competitions, the median relative gap is 0.17 in E against 0.01 in O (p = 0.003), already 0.08 against 0.01 at first submissions, with the share of positive drift unchanged (72.5% against 70.6%). Within E prize competitions, code-only and other formats do not differ clearly. Only 23 of 184 use an original metric, so H1 could not detect this. Teams are also more tightly packed, which inflates gaps measured in team spreads. Mechanism not identified.

## 7. Limitations

- Drift is evidence of adaptation, not a pure measure of it, and it misses adaptation complete before a team's first submission, such as a forked public notebook.
- The null model treats submissions as independently split; they share one split.
- Accuracy results rest mostly on in-class competitions in both periods (25 of 33; 82 of 95), and only two E accuracy competitions ended after 2022.
- Split labels reflect only what hosts wrote and come from one reader. [TODO: audit of 50 unflagged descriptions.]
- One Meta Kaggle snapshot; inferred sizes assume unweighted accuracy.
- Not studied: number of classes; notebook forking.

## 8. Reproducibility

Code, the analysis plan, the label table and all result tables are public. [TODO: repository link, licence, and a statement on redistributing Meta Kaggle extracts.] All scripts were re-run from the raw files in a clean Python 3.12 environment and reproduced every table.

## Before submission

- [TODO] Repeat and date the literature search; write related work.
- [TODO] Check TMLR's current policy on disclosing AI assistance and follow it. An AI assistant designed and ran these analyses under the author's direction.
- [TODO] Convert to the TMLR LaTeX template; confirm arXiv endorsement.
- [TODO] Independent review of the plan, the drift measure and section 6.
