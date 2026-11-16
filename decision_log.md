# Decision log

Settled points and their reasons. Newest at the bottom. Do not re-decide these in a new chat without a new entry.

| Date | Decision | Reason |
|---|---|---|
| 2026-11-15 | Topic fixed: re-test Roelofs et al. (NeurIPS 2019) on post-2018 Kaggle competitions, target TMLR. | Research brief, 15 Nov 2026. |
| 2026-11-15 | Layout: `data/raw/` (untouched downloads), `scripts/` (one script per stage), `outputs/`, `requirements.txt` (pinned). | Brief's reproducibility rule. |
| 2026-11-15 | Stage 0 uses only Competitions.csv, Teams.csv and Submissions.csv from Meta Kaggle, queried with DuckDB. | Submissions links to competitions through Teams; DuckDB reads multi-GB CSVs out of core on a laptop. |

# Open items

- Stage 0 gate: awaiting go / no-go from the researcher.
- The original sample's exact end date is not yet verified from the paper; "new" is provisionally deadline year >= 2019.
- To settle in the stage 2 plan: competitions with LeaderboardPercentage 100 or 0; mapping numeric-ID metrics (e.g. 39244492 "Roc Auc Score") to named ones; whether Community competitions enter headline claims.

# Data provenance

Meta Kaggle downloaded by the researcher on 2026-11-15 (about 23:40 Europe/Stockholm) into `data/raw/`. SHA-256:

- Competitions.csv `1bbfaf5d754c972a6b441b97dc1e74217e79d9395fc64d182fd14e9e38810a84`
- Submissions.csv `2c4359f1d37fb3047319ee76f9bb3fed4e8e62d9771e5b694d40d9d03f8092b2`
- Teams.csv `ba4911a2903f65f57f3a3eba4ee831bfc277ebab5142b6135b1e5984f761e067`

# Stage 0 results (2026-11-15)

Script: `scripts/stage0_feasibility.py` -> `outputs/stage0_per_competition.csv`. Only counts and score presence were examined; no public/private comparison.

- Verified columns: Submissions has TeamId, IsAfterDeadline, PublicScoreFullPrecision, PrivateScoreFullPrecision, SourceKernelVersionId; Teams has CompetitionId; Competitions has DeadlineDate, EvaluationAlgorithmAbbreviation, OnlyAllowKernelSubmissions, HostSegmentTitle, LeaderboardPercentage.
- 12,865 competitions; 19,852,585 submissions, 14,655,574 pre-deadline; every submission joins to a team.
- Eligibility used here: >= 1,000 pre-deadline submissions with both scores present. Deadline <= 2018: 274. Deadline >= 2019: 618 (146 Featured, 100 Research, 106 Playground, 265 Community, 1 Recruitment).
- Private scores: in every eligible competition from 2019 on, each pre-deadline submission with a public score also has a private score. 160 of the 618 are code-only. Unscored submissions lack both scores.
- Deadline <= 2018 by metric: accuracy 34, AUC 43, MAP@K 12, log loss 17, multiclass loss 15 (paper: 34, 40, 17, 15, 14).
- Deadline >= 2019 by metric: accuracy 126, AUC 66 (+20 under numeric ID 39244492), RMSE 38, F-micro 19, MAE 16, MAP@K 16, log loss 13, multiclass loss 5. 125 competitions use numeric-ID metrics (74 distinct).
- Accuracy composition, deadline >= 2019: 117 of 126 are Community; 124 of 126 ended 2019-2022.
- LeaderboardPercentage among the 618: 55 at 100, 20 at 0.

# Handover assessment (2026-11-15, Codex)

- Read README, existing decision log and stage 0 script; checked the saved aggregate CSV, without inspecting or comparing post-2018 scores. Did not rerun raw-data processing or independently verify hashes.
- Confirmed 618 provisional eligible competitions; 75 have LeaderboardPercentage 0 or 100, leaving 543 before other exclusions and original-sample overlap checks. Score presence alone does not establish score validity or independent evaluation splits.
- Important correction: the original paper explicitly discusses 2019 competitions (section 3.4). Deadline year >= 2019 is therefore not a valid disjoint extension boundary. Recover original competition IDs and sampling cutoff before finalizing new-sample counts; matching 34 accuracy competitions before 2019 does not establish replication.
- Recommendation: pursue a bounded replication and sample audit before committing to the full extension. TMLR is a plausible target, but no defensible numerical acceptance probability is available. The 126 provisional accuracy competitions are heavily concentrated in Community and 2019-2022, limiting contemporary generalization.
- The user authorized takeover and requested a viability assessment; no explicit researcher stage-1 gate decision has been recorded. No stage-1 analysis code or new-score analysis was run.
- Sources checked: https://proceedings.neurips.cc/paper/2019/file/ee39e503b6bedf0c98c388b7e8589aca-Paper.pdf and https://jmlr.org/tmlr/acceptance-criteria.html . A limited web search does not establish absence of competing work; novelty remains unverified.

# Stage 1 authorized and initiated (2026-11-15)

- Researcher explicitly approved stage 1: "Yes go for it." Prior awaiting-gate entries are superseded.
- Read full main paper and appendices A-G from the official supplemental ZIP. Its contents are a 40-page PDF, not source code.
- Recovered all 120 competition IDs and published counts/test sizes from appendix tables 2-6 into data/reference/original_120_manifest.csv. All IDs exist in the downloaded snapshot. Eighteen original competitions ended in 2019; latest listed deadline in current metadata is 2019-04-04. This is not proof of the original dataset extraction date.
- Metric aliases: MAP@{K}, MAP@k, MAP@3, AP@{K}, MAP@{K}_OLD; MulticlassLoss and MulticlassLossOld. Original eligibility is >=1000 pre-deadline submissions; requiring paired scores for eligibility is an additional stage-0 restriction.
- Main Table 1 gives competition 5275 sizes 249344/249343 while appendix Table 2 gives 696/696. Main equation 1 uses >= while appendix equations use >. Preserve both inconsistencies; do not silently pick one for formal tests.
- The 10000-example suggestion concerns TOTAL test size (Figure 5), not explicitly the public subset alone.
- Stage 1 score processing is restricted to the 120 published IDs, including their 2019 members. New competition scores remain unexamined.

# Stage 1 first replication audit (2026-11-16)

- Status: in progress; stage 1 gate NOT passed. Researcher approved stage 1 on 15 November; the README's earlier awaiting-go status is superseded.
- Read main paper and appendices, recovered all 120 IDs, and processed only those IDs. Saved source PDF and manifest under data/reference. No extension-sample score comparisons performed.
- Raw SHA-256 hashes independently checked: all three match the earlier log. Recovered 1,510,406 pre-deadline paired finite scores versus 1,513,918 published submissions (0.232% fewer). 46/120 counts match; every relative discrepancy is below 2.6%. Causes remain unresolved.
- All-submission/top-10% plots for all 120 competitions and aggregate gap CDFs generated. The five largest positive accuracy mean gaps exactly match the paper's named outliers: 12598, 12349, 5903, 3641, 12681. Descriptive figure agreement is qualitative; no numerical digitization claim.
- Appendix test-size audit: 19/34 accuracy competitions have all scores consistent with integer correct counts (tolerance 1e-4 count); 13 have inconsistencies and 2 lack sizes. Arithmetic consistency is not independent proof of size/split validity. No inferred denominator substitutions used in formal calculations.
- Exact hypergeometric inclusive/strict p-values calculated for those 19 competitions only, conditional on appendix sizes. Both tail calculations passed 400 direct-enumeration checks. Different from the original Stirling approximation; the main-text >= versus appendix > discrepancy remains documented.
- All retained SubmissionDate values have day precision. First-per-team uses earliest day then smallest submission ID (within-day order is an assumption). Top 10% uses ceiling and ID tie-break. These choices remain sensitivity items.
- Scoring-unit issues: local Allstate description distinguishes customer predictions from multiple customer-history rows; speech description says not every test file is scored. Do not infer scoring denominators by multiplying file size by nominal public percentage. Cdiscount description says original data removed after competition.
- Competition 3043 has 1364/1431 private scores equal to 99; original Figure 6 also has an extreme multiclass-loss tail. Preserved for descriptive replication; meaning still needs verification. Paired score presence is not score validity.
- Metadata-only corrected candidates: 2019+ excluding original IDs: 600 paired-eligible, 525 with reported percentages strictly between 0/100, 94 accuracy within that subset. 2020+: 505, 443, 74 respectively. Neither is a fixed inclusion rule or verified original sampling cutoff.
- Runtime versions recorded in outputs/stage1/run_metadata.json and requirements-stage1.txt; prior requirements.txt was not used or overwritten. The report states limits and reproducible commands.
- arXiv endorsement guidance checked; account-specific eligibility not checked. No messages sent to authors or endorsers.
- Next source check requested from researcher: whether the speech challenge Data tab supplies a solution/answer CSV with usage split labels; no large audio download needed. Continue resolving scored sizes and original implementation before the next gate.

- Researcher checked the speech Data tab: only link_to_gcp_credits_form.txt, sample_submission.7z, test.7z, train.7z were listed. No answer key visible; advised no large download. A targeted search found contestant model solutions but no verified released answer key. This does not prove the answer key is unavailable elsewhere.

# Continued stage 1 audit (2026-11-16)

- Researcher requested autonomous continuation, stopping only for required input, blockers or risks to research/publish-worthiness. No automatic transition to unplanned new-score analysis is authorized by this; the new sample remains sealed.
- Original benchmark metadata explains the three off-lattice rows in 6109 and the single exceptions in 12349 and (after public/private size swap) 12598. All belong to Competition Wizard Sample Submission Playground teams with IsBenchmark=True. Original descriptive pass preserved; separate nonbenchmark sensitivity increases size-consistent accuracy competitions from 19 to 21. The largest accuracy mean-gap change is 0.023153 percentage points; main five outliers unchanged.
- Top-10% cutoff ties can change the mean accuracy gap by up to 1.32453 percentage points (12681). First-day ambiguity can move the p<=.05 share from 1.869% to 18.224% (11842). Bounds use private outcomes only to diagnose possible ambiguity, not to select a substantive cohort.
- CIFAR-10 3649: all 1634 retained public/private scores identical, both fitting a denominator of 10000 rather than appendix split 300/9700. Split/scoring-history verification needed.
- Allstate 3788: primary participant presentation reports 55716 test customers. Reduced score fractions include 8991/16714 and 20777/39002. Under equally weighted accuracy and exhaustive disjoint splits of those customers, counts are uniquely reconstructed as 16714/39002; all scores fit. These differ from paper 59657/139199. Conditional sensitivity yields inclusive p<=.05 shares of 1.2845% all, 3.8320% top10, 1.7834% first-per-team. Labelled reconstructed, not independently verified split metadata. Researcher asked for original test CSV to verify rows/customer counts.
- Synthetic validation (100000 nonadaptive models, accuracy .7, public/private n=100, seed2019): inclusive p<=.05 =3.467% overall and13.3% in public-selected top10; strict-tail <=.05 =7.17% and23.37%. Selection alone causes nonuniform selected p-values and positive gaps. Strict discrete tails are not interchangeable with valid inclusive p-values. This is a method diagnostic, not new Kaggle analysis and not proof of the original implementation.
- Original code search through author listings and targeted searches unsuccessful. OpenReview browser verification and API403 block attachment inspection; researcher asked to inspect links. No bypass attempted and no authors contacted.
- Latest Monoculture preprint version confirmed (v3 September2026); abstract-only overlap check logged, not an exhaustive novelty audit.
- Updated script rerun successfully from original-only cache; exact-tail enumeration checks still pass. Findings in outputs/stage1_audit_update.md; intermediate numerical sensitivity outputs retained. Stage1 gate remains open pending source verification. Project remains potentially publishable; a correction/validation contribution requires corroboration and cannot rest on table inconsistencies alone.

# Allstate source verification and OpenReview resolution (2026-11-16)

- Researcher downloaded data/reference/test_v2.csv. Direct inspection confirms 198856 rows, 55716 distinct customer_ID values, zero missing customer IDs. SHA-256 9afb8de68728764905a5f1827256a4e423baba0508d7df9d55ea5ca3e73eb458. The original table's 59657+139199 equals the row count exactly, although the task scores one prediction per customer.
- Strong evidence of a published scoring-unit/table discrepancy. Customer total independently verified. Split counts 16714/39002 remain an algebraic reconstruction under standard unweighted accuracy, accurate score representation and disjoint scored customer subsets; not a directly observed released split manifest.
- Normal pooled-variance sensitivity: using table row counts, fractions <=.05 are74.620% all/99.918% top10/52.484% first; using reconstructed customer counts,1.313%/3.873%/1.783%. Exact inclusive customer-count results1.285%/3.832%/1.783%. This explains how the size choice can induce a major p-value discrepancy. Normal approximation is diagnostic, not the original Stirling code. No claim that the authors actually used the wrong counts has been established.
- Researcher inspected OpenReview HJlr9NBgUr: mixed Kaggle title/PDF and Meta-MDP metadata/code. They downloaded linked report rkedITqfpB to data/reference/21__replication_a_meta_mdp_approa.pdf. First page independently read: '[Replication] A Meta-MDP Approach to Exploration for Lifelong Reinforcement Learning' by David Cabatingan, Kendrick Cole, Natalie Delworth, Petar Peshev (Brown). This is unrelated to Kaggle. Do not treat Meta-MDP code or report as a replication of our target.
- Prepared outputs/allstate_verification_note.md, a verified sensitivity figure and JSON, and outputs/author_code_request.md. Original code/configuration/snapshot verification remains an external dependency. No author contacted and no email sent. New-sample scores remain unexamined. Stage1 not passed.

# Alternative route adopted: independent reanalysis, no author contact (2026-11-16)

- Researcher asked whether the study can proceed without reaching out to an original author. Yes: the prior characterization of missing original code as a project blocker was too strong. It limits implementation attribution/exact computational reproduction, not independent reconstruction and extension.
- Adopt no-contact route. Do not send the prepared email. Keep observed reproduction successes, source discrepancies, and independently validated calculations separate. Do not infer behavior of inaccessible original code from table errors or similar-looking plots.
- Added outputs/independent_reanalysis_route.md, outputs/stage1/reproduction_matrix.md and accuracy_size_evidence_register.csv. Stage1 completion criteria now require a transparent reconstruction/evidence matrix and justified own method, not access to original code or forced agreement with every original plot. This is an explicit change to the working plan, not a claim that all previous replication targets were achieved.
- Stage1 remains open. Continue tractable metadata verification and independent method validation; then prepare a concrete dated stage2 plan. New-sample score comparisons remain prohibited until the plan is fixed and publicly posted. Publication-worthiness still depends on generalizable insights beyond a table correction.

# Takeover review by Claude (2026-11-16, about 02:45-03:15 Europe/Stockholm)

Read README, this log, both stage 1 reports, the Allstate note, the independent-reanalysis route, the reproduction matrix, the evidence register, `scripts/stage1_reproduce.py`, and the paper's main text and Appendix A. The other assistant's last announced step (tightened metadata counts) left no files; it is redone below. No extension scores were read or compared.

Independently re-checked from raw files (all agree with the earlier entries):
- Allstate `test_v2.csv`: 198,856 rows, 55,716 distinct customers.
- Manifest: 120 IDs; 34 accuracy, 40 AUC, 17 MAP@K, 15 log loss, 14 multiclass loss.
- Mean accuracy gaps recomputed in DuckDB straight from `data/raw/`: 12598 7.007 pp, 12349 3.929, 5903 2.828, 3641 2.103, 12681 1.813 - same five outliers and same values as `replication_summary.csv`.
- 1,510,406 paired submissions against 1,513,918 published; 46 exact count matches; largest relative difference 2.56%.

New findings (metadata only; script `scripts/stage1_cohort_counts.py`, outputs `outputs/stage1/cohort_per_competition.csv` and `cohort_counts.csv`):
- Correction accepted: my stage 0 boundary (deadline year >= 2019) was wrong; 18 originals ended in 2019.
- Original snapshot dated. Latest original deadline is 2019-04-04 23:59; the first competition meeting the paper's rule after it ended 2019-04-09 and is not in the 120. Appendix A says Meta Kaggle then held 1,461 competitions; the current file has 1,458 with deadline <= 2019-04-01 and 1,476 with deadline <= 2019-04-05. Inference: the authors' snapshot dates from about 5-9 April 2019.
- DECISION (provisional until the stage 2 plan fixes it): the extension cohort is competitions with deadline after 2019-04-04 23:59 and on or before the download date, not in the 120. This replaces both "2019 onward excluding originals" and "2020 onward".
- The paper's stated rule does not fully reproduce its own sample. Inside the original window, 28 competitions in the five metric groups have >= 1,000 pre-deadline submissions but are not among the 120 (mostly Playground, e.g. whats-cooking, forest-cover-type-prediction). 26 of the 28 report a public leaderboard share of 0 or 100, so an unstated "must have a real public/private split" filter would explain most of them; 2 remain unexplained (the two with interior split in `cohort_counts.csv`: one AUC, one multiclass loss). Appendix A reports 262 competitions passing the submission threshold; the current file gives 305 by deadline <= 2019-04-05. Inference only; the authors' filter is not documented. These in-window competitions' scores have NOT been examined; how to treat them is a stage 2 plan decision.
- The paper's own text (section 3.3) calls Allstate's test set "the 198,856 examples in Competition 3788" and attributes its small p-values to that size. So the row count was not just a table typo: the authors' interpretation used it. Still no claim about their code.
- Extension candidates (>= 1,000 pre-deadline submissions): 589; with >= 1,000 paired non-benchmark submissions and public share 1-99: 516 (210 Community, 111 Featured, 100 Playground, 94 Research, 1 Recruitment; 135 code-only).
- By metric group within the 516: accuracy 94 (9 non-Community, 2 ending 2023 or later); AUC 52; MAP@K 14; log loss 12; multiclass loss 4; regression RMSE/MAE/MSE/RMSLE 62; other named metrics 169; numeric-ID metrics 109.
- For comparison, the original 34 accuracy competitions also contain only 9 non-Community ones. The in-class tilt of the accuracy test is a property of the original study too, not only of the extension.
- From 2023 Kaggle metrics are almost all numeric IDs: 109 of the 168 extension candidates ending 2023-2026. By name these include Roc Auc Score 20, Mean Squared Error 8, R2 5, Accuracy Score 4, Balanced Accuracy 4, MAE 4. Any claim about 2023 onward needs these mapped by name, and same-metric samples are small (roughly 25 AUC, 5 accuracy); a time trend needs a measure that works across metrics.
- Regression (RQ2): 62 extension candidates plus 51 in-window competitions the original excluded by design.

Assessment recorded for the researcher's stage 1 gate: descriptive replication succeeded; formal test independently rebuilt and validated on 19-21 of 34 accuracy competitions; remaining size gaps are documented and mostly not recoverable without answer keys. Recommend closing stage 1 on the independent-reanalysis criteria and moving to the stage 2 plan. Gate decision is the researcher's and is not yet given.

# Stage 1 closed; stage 2 plan drafted (2026-11-16, Claude)

- The researcher asked both assistants to keep working until a decision or action only the researcher can provide is needed ("you and the other AI are the major experts here"). On that delegated authority, STAGE 1 IS CLOSED on the independent-reanalysis criteria. Reason: sample recovered, five outliers reproduced, formal test rebuilt and cross-validated (below), remaining discrepancies documented. The researcher can reopen it.
- Test-set sizes no longer need hand collection for accuracy competitions: they are inferred from the score lattice (smallest size on which every score is a whole count). On O this reproduces 21 of 32 published size pairs exactly, recovers Allstate's 16,714/39,002 without the test file, and gives sizes for the two competitions the paper lists without sizes. 7115 has the paper's total (1,768,182) but a different split, which suggests the published sizes are total times nominal public share. Formal test now runs on 33 of 34 accuracy competitions (3649 excluded: identical scores).
- My exact p-value routine (`scripts/stage2_measures.py`) agrees with the other assistant's on all 68,552 submissions in the 19 competitions it covered (max difference 1.4e-15).
- New measure adopted for the plan: within-team drift (later-half gap minus earlier-half gap). Simulation: about 0 without adaptation even with a 3-point split difference; 1.18 points with adaptation. On O it is positive in 78 of 117 competitions (sign test p = 0.0004), driven by AUC (31 of 40). Exploratory, since O has been fully examined.
- Selection-adjusted top-decile gap: selection alone accounts for the top-10% gap in outliers 5903 and 12681; not in 12598, 3641, 12349.
- Unit-free yardstick: team spread (median team to top-decile team, on public score). A first attempt using the spread of first-submission gaps was dropped because it is zero or near zero in several competitions.
- Scores outside accuracy, AUC and MAP@K are clipped to the 1st-99th percentile of public scores (bounds independent of private scores) to stop sentinel values such as 99 dominating means.
- Split-type labels cannot be done by keyword: time-related keywords hit 97 of 100 Playground descriptions. They will be assigned by reading descriptions under a rubric, before unsealing.
- Draft plan: `analysis_plan/stage2_analysis_plan_DRAFT.md` (v0.1). Four confirmatory tests, six secondary analyses. RQ4 (classes) and notebook forking are demoted to exploratory. NOT yet approved or posted.
- Scripts added: `scripts/stage2_measures.py`, `scripts/stage2_pilot_original.py` (original 120 only). Outputs: `outputs/stage2/`.
- Still sealed: every extension and in-window score.

Waiting on the researcher: (1) review and approve the plan; (2) post it publicly. Work that can proceed meanwhile without unsealing: split-type labelling.

# Plan fixed at v1.0; split labels done blind (2026-11-16, Claude)

- The researcher delegated plan approval ("you are more capable of approving ... all you need to look out for is our goal"). Plan approved and fixed as `analysis_plan/stage2_analysis_plan_v1.0.md`. Draft v0.1 kept as `analysis_plan/superseded_draft_v0.1.md`. Only change from the draft: section 8 now describes the labelling as actually done.
- Split-type labels assigned from description text for all 684 competitions in O, E and W (rules 1-3), before any extension score was read: `outputs/stage3/split_labels.csv`; decisions in `data/reference/split_label_decisions.py`; extraction in `scripts/stage3_label_extract.py`. Flagged (TIME, GROUP or NEWDATA): O 12, E 44, W 4. Stated random: O 3, E 2. No description text: E 11.
- Keyword-only labelling was rejected (too many false hits); sentences were extracted mechanically and then read. Known limit: 403 descriptions contain no split-related sentence at all, so UNSTATED dominates.
- Note for the paper: competition 12598, which the original authors found to have a non-random split by contacting its host, is UNSTATED under this rubric. The rubric sees only what hosts wrote.
- Hashes of the plan, label table, label decisions and measures code: `analysis_plan/SHA256SUMS.txt`.
- STILL SEALED: all extension and in-window scores. Unsealing requires the plan to be posted publicly first. That needs the researcher (an account on a public registry such as OSF). Nothing else is pending before stage 3 can run.

- 2026-11-16: OSF no longer allows new projects (its dashboard states none can be created after 16 November 2026; researcher's screenshot). DECISION: the plan is posted in a public GitHub repository instead, with the commit page also saved in the Internet Archive as a third-party timestamp. `.gitignore` added: raw data, the paper PDFs, the Allstate test file, two large derived extracts and the unused author email are not published.
