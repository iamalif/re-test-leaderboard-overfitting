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

- 2026-11-16 about 03:20 Europe/Stockholm: plan v1.0, label table and hashes pushed to the public repository https://github.com/iamalif/re-test-leaderboard-overfitting as commit 0969d41 (the first local commit 0bf337b was re-stamped with a GitHub no-reply email before pushing; contents identical). Public visibility confirmed by the assistant from outside. Internet Archive snapshot: pending, to be made by the researcher (the assistant cannot reach web.archive.org). Extension scores remain sealed until the snapshot link is recorded here.

# UNSEALED (2026-11-16, 03:27 Europe/Stockholm)

- Internet Archive snapshots supplied by the researcher, both taken before any extension score was read:
  - plan: https://web.archive.org/web/20261116022305/https://github.com/iamalif/re-test-leaderboard-overfitting/blob/main/analysis_plan/stage2_analysis_plan_v1.0.md (02:23:05 UTC)
  - commit 0969d41: https://web.archive.org/web/20261116022522/https://github.com/iamalif/re-test-leaderboard-overfitting/commit/0969d41 (02:25:22 UTC)
- From this entry on, extension (E) and in-window regression (W) scores are read, strictly under plan v1.0. Any departure is logged below as a deviation.

# Stage 3 run under plan v1.0 (2026-11-16, about 03:30-03:50 Europe/Stockholm, Claude)

- Scripts: `scripts/stage3_extension.py` (extract and per-competition measures), `scripts/stage3_tests.py` (tests). Report: `outputs/stage3_report.md`.
- Analysed: O 114, E 487, W 51. Dropped under rule 4 (identical scores): O 3, E 29. Dropped under rule 3: E 2.
- Confirmatory, Holm-corrected: H1a accuracy gap level, no difference (E minus O -0.029 pp, 95% interval -0.172 to 0.121, p 0.59). H1b AUC, no difference (-0.0007, -0.0043 to 0.0011, p 0.24). H2 drift positive in 327 of 481 E competitions (68.0%, p 2e-15), significant. H3 relative drift E against O, no difference (p 0.92).
- Secondary: no regression/classification difference; absolute gap shrinks with test size but selection-adjusted top-decile gap does not; code-only competitions show far larger gap levels (median relative gap 30% against 0.7%) and higher drift; no time trend.
- Deviations/implementation notes 1-3 are listed in the report. None changes a confirmatory test.
- Decision: the code-only finding is NOT to be described as overfitting without follow-up; it is the main open question for stage 4.
- Next: commit and push results (researcher); stage 4 follow-up on code-only competitions (exploratory, marked as such); figures; paper draft.

# Stage 4 started: drift robustness (EXPLORATORY, 2026-11-16, Claude)

- Second commit pushed by the researcher (stage 3 results); seen in the local record of origin/main.
- Self-review raised two alternative explanations for H2 that the plan's simulation did not cover: (A) teams begin with trivial submissions whose gap is near zero and then inherit the competition's gap level; (B) the gap scales with score level and teams improve.
- Checks in `scripts/stage4_drift_robustness.py` (outputs in `outputs/stage4/`). Share of E competitions with positive drift: planned measure 68.0%; third versus fourth quarter of each team's submissions 63.3%; after dropping each team's first two submissions 65.4%; within-team slope controlling for score level 66.0% (all sign-test p < 1e-8). Where the first-submission gap is negative, so that explanation A predicts negative drift, the planned drift is still positive in 66.0% (140 of 212) and the late-only drift in 68.2%. In O: 67.5%, 61.1%, 71.9%, 68.4%.
- Conclusion: the drift result is not produced by A or B. These checks are exploratory and will be reported as such.
- Quality risks recorded for the researcher: plan designed and approved by the same assistant with no independent review; drift is a new measure validated by one simulation plus these checks; split labels are sparse and from one reader; novelty search not repeated since 15-16 November; the other assistant's stage 1 script has not been re-run in the stage 2 environment and three requirements files exist; RQ4 and notebook forking are not covered.

# Stage 4 follow-ups, clean re-run, figures, first draft (2026-11-16, Claude)

- Researcher: go ahead; reviews are being handled by the researcher, the other assistant and outside experts.
- Code-only follow-up and prize-competition comparison (EXPLORATORY): `outputs/stage4_report.md`. Main points: the S3 code-only contrast is mostly composition; among Featured and Research competitions relative gap levels are higher after April 2019 (median 0.17 against 0.01, p 0.003), present from first submissions, with drift unchanged; mechanism not identified.
- DECISION: scope the headline. The 2019 conclusion is confirmed for accuracy and AUC competitions (now mostly in-class). The prize-competition pattern is reported as exploratory and open.
- Clean re-run of every script from raw files under Python 3.12 reproduced all tables. It exposed one reproducibility flaw: bootstrap intervals depended on row order. Fixed by sorting on competition ID in `scripts/stage3_tests.py`; interval bounds moved in the third significant digit (H1a upper bound 0.121 to 0.116; H3 upper 0.97 to 0.99); no estimate, p-value or conclusion changed. Logged as implementation note 4 in the stage 3 report.
- One environment now: `requirements.txt` (Python 3.12). The two earlier requirements files moved to `superseded/`.
- Figures: `scripts/stage5_figures.py` -> `paper/figures/` (four figures, PNG and PDF).
- First paper draft: `paper/draft_v0.1.md`, with open items marked TODO.

# Stage 5: literature check, label audit, TMLR draft (2026-11-16, about 04:05-04:40, Claude)

- Literature search repeated 16 Nov 2026. Queries: the 2019 title with "replication" and "re-analysis"; Kaggle public/private leaderboard shake-up and adaptive overfitting with Meta Kaggle 2026; the monoculture preprint; the position paper. No peer-reviewed re-test of the 2019 result on later competitions found. Not proof of absence.
- Read for related work: Burtch, arXiv:2607.13077 (Appendix G: 158 contests, each team's best public submission, standardized public minus private; the author notes the selection bias; reports a decline in 69% of contests). Bönisch and Losaria, arXiv:2511.06304 (normalised public-private discrepancy over time; no tests). Sculley et al., ICML 2025 position paper (cites the 2019 result as showing reuse was not the main problem).
- NOT verified and therefore not cited: the brief's statement that MLE-bench says Kaggle submissions sometimes overfit the public leaderboard (search snippets did not show it); the 2026 ecosystem survey (arXiv page rate-limited). Both remain TODO if wanted.
- TMLR policy on LLM use (jmlr.org/tmlr/faq.html, read 16 Nov 2026): allowed as assistive tools; authors fully responsible; use must be stated in a footnote on the first page. Footnote added to the draft. Secondary reports (September 2026) say a TMLR editor-in-chief has interviewed authors about their own papers and that per-author submission quotas and an AI-generated soundness review were introduced; not verified on TMLR's own pages.
- Split-label audit: 50 unflagged competitions re-read with a wider sentence filter; 0 labels changed (`outputs/stage5/label_audit_result.md`).
- Paper converted to the TMLR template: `paper/main.tex`, `paper/references.bib`, compiled to `paper/main.pdf` (7 pages, anonymised). `paper/draft_v0.1.md` is superseded by it.
- Remaining before submission: author reads and can defend every section; independent reviews; decide how to give anonymous access to code for double-blind review; arXiv endorsement; optional citations above.

# Independent review and major revision (2026-11-16, evening, Claude)

- The second assistant's review (`reviews/review_2026-11-16.md`, baseline commit 787131f) recommends major revision. Its three major findings are correct: (1) positive drift does not identify adaptation (a feedback-free counterexample passes all four stage 4 checks); (2) inferred sizes are minimum compatible denominators, not identified sizes; (3) the independent-resplitting adjustment is not an estimate of selection bias. Its confirmatory recomputation matched exactly and it found nothing contradicting the blind-plan record.
- DECISION: accept all seven findings. The causal claim "adaptation is real, systematic and small" is WITHDRAWN. Stage 4 report's sentence that the drift result "is not produced by A or B" stands only for those two specific alternatives; its implication that adaptation is established is withdrawn.
- DEVIATION from plan v1.0 section 8, now logged: the audit of 50 unflagged competitions used truncated excerpts and the same reader, not full descriptions. The 6% miss-rate bound in `outputs/stage5/label_audit_result.md` is withdrawn. The full-text audit by a second reader is still owed.
- CORRECTION: my statement to the researcher that accuracy and AUC competitions are "now mostly in-class" was wrong for AUC (29 of 73 E AUC competitions are Community).
- New exploratory work: `scripts/stage6_review_response.py`, `scripts/stage6_verify_review_numbers.py`, outputs in `outputs/stage6/`. Size tiers: A 1, B 21, C 99, D 7. Published sizes compatible with the scores equal the minimum in 21 of 21 cases. Under a random split, feedback-free simulated submissions give no excess of positive drift (44.7% of 300); with a composition-biased split, 100%. Where a random split is best supported in the data, drift is positive in 56 of 94 accuracy competitions (p 0.08) and 3 of 5 stated-random competitions. First-submission gaps are positive in 56% of E (p 0.007).
- Review's sensitivity numbers recomputed and confirmed (unclipped drift 307 of 481; doubled sizes 11.1% and 11.7%).
- Paper revised to v0.2 (`paper/main.tex`, 9 pages); pre-review version kept as `paper/main_v0.1_before_review.tex`. New title: "Leaderboard Overfitting on Kaggle, Revisited: A Pre-Specified Re-Test and the Limits of Aggregate Scores". Response: `reviews/response_2026-11-16.md`. `run_all.sh` added.
- Open: second-reader full-text label audit; series-level dependence; matched O/E comparisons; fuller tail summaries for H1; anonymised code package; arXiv endorsement.

# Follow-up review and second revision (2026-11-17, about 01:00-01:30, Claude)

- Follow-up review (`reviews/review_2026-11-16_followup.md`, baseline 517ee6f): the converse added in the first response ("under a random split drift has no preferred sign") is FALSE for unequal split sizes; exact counterexample with 80% positive drift and no feedback. Accepted and WITHDRAWN. Note for the record: my stage 6 simulation had returned 44.7% positive under a random split and I dismissed the departure from 50% as noise.
- Also accepted: the first-submission-fit subgroup is not evidence of a random split (removed from the paper); three invalid fits in the tier inventory (tiers now A 1, B 21, C 96, D 7 over 125 usable fits); "code-only" does not mean re-run on hidden data; runner did not stop on failure (fixed, not yet re-run end to end).
- The second assistant completed the full-text audit of the 50-competition sample as second reader: 0 label changes, three ambiguous cases (14774, 25914, 29653). This closes the audit owed under plan section 8; the earlier excerpt-based check remains logged as a deviation. The second reader was not blind to labels or results.
- New exploratory analysis (`scripts/stage6_split_size_symmetry.py`): share of positive drift does not depend on reported public share (under 40%: 67%; exactly 50%: 63%; over 50%: 67%; O+E, all metrics). Equal-size, unclipped, accuracy/AUC/MAP@K: 58 of 90 positive (p 0.008); E alone 37 of 61 (p 0.12). Mean unclipped accuracy drift O+E 0.10 pp (0.02 to 0.19). The unequal-size mechanism does not explain the pattern; the composition mechanism remains open.
- Paper revised to v0.3; v0.2 kept as `paper/main_v0.2_before_followup.tex`. Response: `reviews/response_2026-11-17_followup.md`.
- Standing position: descriptive and identification-limits framing. No causal claim about adaptation.

# Third review, v0.4, and Addendum A (2026-11-17, about 01:20-02:00, Claude)

- Review of v0.3 (`reviews/review_2026-11-17_v03.md`, baseline 1d44171). Accepted: (1) reported 50% is nominal, not verified equal size; (2) ERROR in `scripts/stage6_split_size_symmetry.py`: the pooled "O+E" rows included cohort W (51 competitions). Corrected all-metric rows: under 40% 244/357; 40-49% 35/45; exactly 50% 89/139; over 50% 36/54. The raw-metric column (58 of 90 etc.) was unaffected; (3) the share table cannot exclude unequal-size mechanisms in general; (4) residual overclaims on first-submission gaps and the abstract.
- Paper revised to v0.4; v0.3 kept as `paper/main_v0.3_before_third_review.tex`. Response: `reviews/response_2026-11-17_v03.md`.
- The researcher asked me to use my own judgement and not only follow the reviews. DECISION: stop post-hoc analyses of pre-deadline scores (agreeing with the reviewer), and add one NEW pre-specified test on untouched data: the deadline contrast. Reason: the deadline changes feedback while leaving both test sets fixed, and the feedback and composition explanations predict opposite behaviour of the gap there.
- Addendum A fixed at v1.0: `analysis_plan/addendum_A_deadline_contrast_v1.0.md`; code `scripts/stage7_deadline_contrast.py`; hashes `analysis_plan/SHA256SUMS_addendum_A.txt`. One confirmatory test T1 (share of competitions with X = J - Dq below zero, against one half), placebo, conservative restriction, limits stated.
- Post-deadline data examined so far: counts and score presence only (`outputs/stage6/post_deadline_counts_metadata_only.csv`, `deadline_design_eligibility_metadata_only.csv`). 338 competitions eligible (59 O, 279 E). NO post-deadline score value has been read.
- Self-test on synthetic data: adaptive 100% X<0; composition trend 0%; noise 50%. A first version of the simulator had an accidental composition trend (fixed number of changed predictions per set); corrected before fixing the addendum.
- UNVERIFIED ASSUMPTION: after the deadline a team sees both its public and private score for late submissions. A web search on 17 Nov did not return Kaggle documentation stating this. The researcher is asked to confirm.
- SEALED until the addendum is public and archived: all post-deadline scores. `scripts/stage7_deadline_contrast.py` must not be run without `--selftest` before then.

# Addendum A v1.0 withdrawn before use; v1.1 drafted (2026-11-17, about 02:05-02:40, Claude)

- Pre-unsealing review (`reviews/review_2026-11-17_deadline.md`) found the v1.0 statistic invalid: it compared quarter-means before the deadline with the mean of ALL post-deadline submissions, so a linear feedback-free trajectory gives X = b(m - q)/2, with a zero placebo. My v1.0 self-test had built the favourable case in (q = 4, m = 8). Accepted. v1.0 was never archived and never run on data; kept in `superseded/`.
- v1.1 (`analysis_plan/addendum_A_deadline_contrast_v1.1.md`, NOT YET FIXED): four equal consecutive windows of 3 submissions; X (zero for linear trajectories) and Y = X minus placebo (zero for quadratic); a change is reported only if both sign tests are significant and negative; analysis described as descriptive; exposure, bundled changes and the blind case stated as limits; public-score restriction dropped; ties counted.
- Synthetic suite saved (`outputs/stage7/selftest_suite.csv`), including both review counterexamples. Known failures recorded: a gap bend located exactly at the deadline (reported as a change), and adaptation that continues unchanged after the deadline (not detected).
- Metadata-only eligibility for v1.1: 211 competitions (41 O, 170 E) at window 3; 283 at window 2; 111 at window 5. Window 3 was chosen before these counts were produced; all three were then seen.
- STILL SEALED: all post-deadline scores. Not to be run until v1.1 has had a second pre-unsealing review, is marked fixed, and is public and archived.
- Response: `reviews/response_2026-11-17_deadline.md`.
