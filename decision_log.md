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

# Addendum A withdrawn; definitions fixed for dependence and stratified checks (2026-11-17, about 02:15, Claude)

- Second pre-unsealing review (`reviews/review_2026-11-17_deadline_v11.md`): a smooth, feedback-free cubic gap trajectory makes both X and Y negative. I had asked for exactly such a case and said I would drop the test if one existed. DECISION: Addendum A's sign-test rule is WITHDRAWN and will not be run. Reason: with four window means, a deadline-located change cannot be told from ordinary third-order curvature; higher differences only move the problem up one order. Files moved to `superseded/`. Post-deadline scores remain unread by anyone on the project.
- Own finding: `outputs/stage3/split_labels.csv` had been built by an inline snippet, not by a script in the repository. Added `scripts/stage3_build_labels.py`; it reproduces the archived table byte for byte (SHA-256 edf340c3...).
- DEFINITIONS FIXED BEFORE LOOKING AT THE CONTRASTS BELOW (exploratory; crude by design):
  - Related-competition cluster: if the competition has an OrganizationId, the cluster is that organisation (338 of 652 analysed competitions; note organisation 4 hosts the whole Playground series and becomes one large cluster). Otherwise the cluster is the slug with all digits removed, cut to its first two hyphen-separated non-empty tokens (so `ml2019spring-hw2` and `ml2020spring-hw3` share a cluster). Known misses: course series whose slugs differ in words, not digits.
  - Dependence checks: (a) cluster bootstrap (resample clusters with replacement, 10,000 draws) for the H1a, H1b and H3 median differences and the H2 share; (b) one randomly chosen competition per cluster, repeated 2,000 times, giving the distribution of the H2 share and of its sign-test p-value.
  - Stratified O-versus-E comparison: accuracy and AUC mean gaps within host category collapsed to Community versus not Community; a stratum is reported only if both cohorts have at least 5 competitions; difference in medians with a bootstrap interval.
  - Tail summary for H1: 10th, 25th, 50th, 75th and 90th percentiles of the signed and of the absolute mean gap, by cohort, for accuracy and AUC.

# Dependence, strata, tails and clean re-run (2026-11-17, about 02:20-03:10, Claude)

- Results of the checks whose definitions are fixed in the previous entry: group bootstrap leaves all four confirmatory results unchanged (H1a -0.20 to 0.11 pp; H1b -0.0043 to 0.0019; H2 62.9% to 71.8%; H3 -0.0042 to 0.0099). One competition per group: H2 share 68.0%. 365 groups; the largest is organisation 4 with 113 competitions.
- Stratified comparisons: similar within Community accuracy and non-Community AUC; non-Community accuracy too small to say (13 against 8).
- NEW QUALIFICATION of H1 for the paper: absolute mean gaps for accuracy are larger in E (median 0.34 pp against 0.20; upper quartile 1.09 against 0.61) while signed medians are similar. For AUC absolute gaps are smaller in E.
- Clean re-run (Python 3.12, fresh directory, stage by stage in `run_all.sh` order): 34 tables compared, all identical after one fix. The fix: `scripts/stage6_split_size_symmetry.py` now sorts by competition ID before bootstrapping (same flaw as stage 3 earlier). `outputs/stage1/original_team_flags.csv` differs in size between a fresh run and the repository copy (all teams versus a shorter list); it only supplies the set of benchmark team IDs and nothing downstream differs. `run_all.sh` itself was not executed as a single process in my shell; its control flow was checked by the reviewer with stubs.
- `scripts/stage3_build_labels.py` added to `run_all.sh`, as was `stage6_dependence_and_strata.py`; stage 7 removed.
- Paper v0.5: paragraph on related competitions, strata and tails; limitations record the withdrawn deadline contrast; conclusion notes larger absolute gaps for accuracy. v0.4 kept as `paper/main_v0.4_before_dependence.tex`.
- Response: `reviews/response_2026-11-17_deadline_v11.md`.

# Review of v0.5 answered; reproducibility closed out; anonymised package (2026-11-17, about 02:45-03:20, Claude)

- Review `reviews/review_2026-11-17_v05.md`: no new major issue; three packaging items. All accepted (`reviews/response_2026-11-17_v05.md`).
- DEVIATION now logged: the group bootstrap first ran with 4,000 draws although the definition entry said 10,000. Re-run at 10,000 (first run kept as `outputs/stage6/dependence_and_strata_4000draws.csv`). H1b interval lower bound -0.0043 -> -0.0041; others unchanged at printed precision.
- `run_all.sh`: `CLEAN=1` moves `outputs/` aside before recomputing. `scripts/compare_outputs.py` added. Rebuild evidence in `outputs/rebuild/`.
- `outputs/stage4/prize_competitions_O_vs_E.csv` is now produced by `scripts/stage4_code_only.py` (it had been built inline); exact match with the earlier table.
- Paper v0.6: exact grouping rule and counts; grouping called one sensitivity analysis; host-category split said not to be matching. v0.5 not separately kept (changes are these three sentences and one interval bound).
- Anonymised package: `scripts/make_anonymous_package.py` -> `anonymous_package/`, `anonymous_review_package.zip` (not tracked in Git). Docs in `anonymous_package_docs/`.
- Remaining before submission: the researcher's read-through; smoke test of the package on the researcher's machine; arXiv endorsement; decide on preprint timing given double-blind review.

# Main environment moved to Python 3.14; exact score parsing (2026-11-17, about 14:10-14:40, Claude)

- Researcher's Mac has Python 3.14 and asked whether the project should use it. DECISION: Python 3.14 is the main documented environment (`requirements.txt`: DuckDB 2.0.0, pandas 3.1.1, NumPy 2.5.5, SciPy 1.18.1, Matplotlib 3.11.2); Python 3.12 kept as a second verified environment (`requirements-py312.txt`). Reason: longer support (to 2030), the researcher's and reviewer's machines already run it, and two verified environments are a stronger reproducibility claim than one.
- FINDING from the 3.14 rebuild: pandas 2.3's default CSV parser reads decimal numbers inexactly (10,387 of 41,739 public scores in competitions 8900 and 10200 were one rounding step off); pandas 3.1 is exact. Affects only `stage1_reproduce.py` and `stage2_pilot_original.py`; stage 3 onward reads scores with DuckDB, which is exact, so all confirmatory and later results were already identical across environments (within 1e-12).
- FIX: both scripts read scores as text and convert with Python's float(). Repository stage 1 and 2 tables regenerated under 3.14. Changed: `top10_mean_gap` and tie bounds for 8900 and 10200; team-level drift sign shares for 4493 and 5275. No number in the paper changed.
- After the fix: 3.14 rebuild 34 tables the same, 3.12 rebuild 33 the same; the only exception in both is the documented team-flags intermediate. Evidence and addendum in `outputs/rebuild/`.
- Paper v0.6 reproducibility sentence updated to mention both environments. Anonymised package rebuilt.

# Package review answered; stricter comparison; single-run stage 3 table (2026-11-17, about 15:10-15:40, Claude)

- Review `reviews/review_2026-11-17_package.md`: the comparison tool ignored text columns (concrete false pass shown); the zip dropped the run script's executable bit; identity filtering could silently drop needed files. All accepted; response `reviews/response_2026-11-17_package.md`.
- CORRECTION: earlier statements that the clean rebuild matched "33 tables" / "34 tables" were made with a tool that compared numbers only. Superseded by the version 2 comparison below.
- `scripts/compare_outputs.py` v2 (v1 in `superseded/`), with a 16-case self-test.
- v2 found `outputs/stage3/competition_measures.csv` had been built across two runs (column order; `scores_in_0_1` blank for 69 accuracy competitions from the first run). Regenerated in a single run under Python 3.14; `stage3_extension.py` now writes a fixed column order. Downstream stages 3 tests, 4, 5 figures, 6 re-run. Old copy in `superseded/outputs_before_single_run/`. No result or paper number changed.
- Both clean rebuilds (3.14 and 3.12) now PASS under v2; one known exception (team-flags intermediate).
- Package builder: explicit zip file modes, required-file assertion (26 files), README sections on report status and reviewer checks. Zip re-verified after extraction (modes, manifest hashes, comparison self-test).
- The researcher's smoke test is running from the earlier zip; its scripts produce the same tables, so its output is to be compared against the updated project outputs with the v2 tool.

# Package smoke test PASSED on the researcher's Mac (2026-11-17, 15:17, Claude)

- From the zip alone plus the public Meta Kaggle files, Python 3.14.2, fresh virtual environment, `CLEAN=1 bash run_all.sh` as a single process: ALL DONE. Comparison (tool v2) against the project: 34 same, 20 not rebuilt (expected), 1 known exception; RESULT: PASS. Recorded in `outputs/rebuild/clean_rebuild_report_2026-11-17.md`, addendum 3.
- This closes the reproducibility work. Remaining before submission: the researcher's own read-through of `paper/main.pdf`; arXiv endorsement; preprint timing under double-blind review; optional repeat of the literature search shortly before submitting.

# Review of post-v0.5 work answered; final ledgered runs (2026-11-17, about 15:30-16:40, Claude)

- Review `reviews/review_2026-11-17_post_v05.md`. All findings accepted; response `reviews/response_2026-11-17_post_v05.md`.
- CORRECTION OF RECORD: statements that "no post-deadline score has been read" are replaced by "no post-deadline score has been analysed". Pipeline steps load all submissions before filtering, and on 17 Nov a parser diagnostic without a deadline filter passed 14,733 post-deadline public-score strings of competitions 8900 and 10200 through a number-format comparison. No gap, private score or other quantity was computed from them. Earlier entries are left as written.
- CORRECTION: the earlier parser figure (10,387 of 41,739) used that unfiltered population. On the analysis population: pandas 2.3 misreads 7,544 public and 7,157 private of 26,985; pandas 3.1 none.
- CORRECTION: comparison v2 results (addenda 2-3 of the rebuild report) and the smoke-test comparison are superseded; v2 tolerated identifier changes and sign flips and waived any team-flags change.
- Changes: comparison v3; `scripts/csvio.py` exact reading everywhere; stage 3 JSON-lines row store; stage 1 team flags restricted to teams with retained submissions (exception removed); `scripts/run_stage.py` ledger; `CLEAN=1` moves pipeline outputs only; parser diagnostic saved under `scripts/diagnostics/`.
- Bug of my own caught by v3 before anything was stored: first `csvio.py` misread DuckDB's lowercase booleans. Fixed and checked against pandas on every table.
- Final fresh runs, one code version, all stages exit 0: Python 3.14.8/pandas 3.1.1 and Python 3.12.15/pandas 2.3.3. v3 PASS between them (2,441 decimal cells within tolerance; everything else identical). Project pipeline outputs replaced by the 3.14 run's (35 of 35 byte-identical). Ledgers and comparison reports in `outputs/rebuild/`. Paper numbers unchanged; archived hashes unchanged. Paper reproducibility sentence made precise.
- Remaining: the researcher's smoke test of the final zip.

# Final package smoke test PASSED (2026-11-17, 15:56, Claude)

- Researcher's Mac, final zip, Python 3.14.2, fresh environment, `CLEAN=1 bash run_all.sh` as one process: ALL DONE. Comparison v3 against the shipped tables: 35 match, 4 historical; RESULT: PASS; 663 decimal cells within tolerance, everything else identical. Rebuild report addendum 5.
- Reproducibility work closed. Remaining before submission: the researcher's read-through of `paper/main.pdf`; arXiv endorsement; preprint timing under double-blind review; a fresh literature search shortly before submitting; optionally, removing the researcher's name from search patterns in public scripts.
- CORRECTION (2026-11-17, 16:00): the rebuild report and my message to the researcher said the runs covered "two processor architectures". They did not: the assistant's Linux environment is a virtual machine on the researcher's Mac (arm64), so all three runs used the same Apple Silicon processor. Accurate statement: two operating systems (Linux VM, macOS) and two Python/pandas generations on one machine. No run on x86-64 has been done. Addendum 5 corrected.

# Review of v3 provenance answered (2026-11-17, about 16:20-17:10, Claude)

- Review `reviews/review_2026-11-17_v3_provenance.md`: no changed scientific result; threshold changes could pass v3; the paper still said post-deadline scores were "unexamined" and the contrast was withdrawn "before reading any data" although my response claimed the wording was corrected throughout (it was not); "one part in 10^9" overstated the combined tolerance; csvio overflow; row-store, ledger and comparison-scope limits. All accepted; response `reviews/response_2026-11-17_v3_provenance.md`.
- CORRECTION OF RECORD (supersedes the 15:30 entry's wording): no post-deadline public and private scores have been compared, and no gap, drift or deadline quantity has been computed from post-deadline data. One number-format diagnostic (17 Nov, after the analysis plan, two original competitions) converted 14,733 post-deadline public-score strings with two parsers and counted disagreements. "Never analysed" was too broad for that.
- Changes: comparison v4; csvio v2; stage 3 row-store fingerprint; run manifest; richer ledger. Paper: deadline sentence and tolerance sentence made exact (now 10 pages after reflow). README and chronology corrected.
- Final runs (`outputs/rebuild/final_v4/`): both 15/15 exit 0, code and inputs verified against manifests, 193/193 outputs match ledgers; 3.14 run = project outputs (38/38 identical); 3.12 vs 3.14 PASS, 2,443 decimal cells in the last digits, all but one within 3e-12 relative.
- JUDGEMENT: the remaining csvio and row-store edge cases are defensive (no current input reaches them); I fixed the concrete ones (overflow, underscores, stale resume) and documented the reader's scope instead of building a general schema system. Figures are not compared as images; stated.

# Review v4 answered; stage 3 caches bound to raw inputs; byte-reproducible outputs; final runs (2026-11-17, about 17:20-18:30, Claude)

- Review `reviews/review_2026-11-17_v4.md`: no discrepancy in any scientific result; one caveat (stage 3 resume fingerprint omitted the score inputs) and two wording points. All accepted; response `reviews/response_2026-11-17_v4.md`.
- Fix: one fingerprint (`outputs/stage3/cache_fingerprint.json`) binds both stage 3 caches, the extracted scores and the row store, to SHA-256 of the stage 3 script, `stage2_measures.py`, `csvio.py`, the stage 0 and stage 1 metadata tables, the split labels, and raw `Submissions.csv` and `Teams.csv`. Computed on every start; if either cache exists and the stored fingerprint is missing or differs in any entry, the run stops and asks for CLEAN=1. Extraction writes to a temporary file and renames it, so an interrupted extraction leaves no cache that looks complete. Tested: unchanged inputs resume; a changed raw-file hash is refused; a cache without a fingerprint is refused. The old row-store fingerprint file moved to `superseded/stage3_old_fingerprint/`.
- Comparison tool header: the count rule is described as a heuristic inferred from reference values, and p-value protection as name-based. Behaviour unchanged; self-test passes.
- FOUND BY ME during the reruns: `stage0_per_competition.csv` and `stage1/cohort_per_competition.csv` were ordered by deadline only, so competitions sharing a deadline came out in varying order between runs; the comparison tool aligns rows by key, so earlier statements that runs gave "identical" tables meant identical cell by cell, not byte for byte. Ties are now broken by CompetitionId. The two gzip tables carried a timestamp and the figure PDFs a creation date; both removed. A repeat of those stages now reproduces every file byte for byte in the same environment. No result depended on row order (all analysis tables were cell-identical before and after).
- Final runs (`outputs/rebuild/final_v5/`), final code, run identifiers final_py314_20261117c and final_py312_20261117c. Stages were run with the same commands and order as `run_all.sh`, in several shell calls under one run identifier, because the assistant's shell stops background jobs and limits each call to three minutes. Both: 15 of 15 stages exit 0; all 31 code and reference files and the 3 raw inputs equal the manifests (including `make_anonymous_package.py`, which the final_v4 manifests predated); 193 of 193 outputs match the ledgers. 3.14 run vs project before copying: 38 of 38 result files same. 3.12 vs 3.14: PASS; the cell-level difference file is byte-identical to final_v4's (2,443 cells). Project pipeline outputs, ledger, manifest and figures are the 3.14 run's. Paper recompiled: text of all 10 pages unchanged.
- Earlier runs final_py314_20261117b / final_py312_20261117b (fingerprint fix only, before the ordering fix) passed the same checks; their outputs were replaced by the "c" runs and are not kept.
- Final anonymous package rebuilt after these changes: `anonymous_review_package.zip`, 167 files, 2,772,664 bytes, SHA-256 683ab08df0ee8fc10d18bbbfa3d3312ed8bb74243e372265706e0a21b6a04b8d; 32 required files present; no identity strings. The final-zip smoke test on the researcher's Mac is the next step and will be recorded as a new test of this file.

# Final-zip smoke test FAILED on one file; comparator fixed (2026-11-17, about 18:30-18:45, Claude)

- Researcher's Mac, zip 683ab08d..., Python 3.14, fresh environment, `CLEAN=1 bash run_all.sh`: ALL DONE. Comparison: 37 same, 4 historical, 1 MISSING FROM NEW: `stage1/allstate_file_verification.json`. RESULT: FAIL.
- Cause (my error): that file is built only when the Allstate competition test file `data/reference/test_v2.csv` is present. It is not shipped (it is a Kaggle competition file; the package README already lists it as optional). Comparison v4 added JSON comparison, and my own final runs could not catch the gap because their trees contained the test file. The earlier Mac smoke test passed because comparison v3 did not compare JSON files. No scientific result is affected: every other result file matched.
- Fix: comparison tool `OPTIONAL_INPUT`; the Allstate verification file may be absent from the new tree only when the test file is absent from that tree's project root (status "not rebuilt, optional input absent"); if the test file is present, the result must be rebuilt and match. Two self-test cases added (30 cases, all pass). Checked against a copy of the final run without that file: PASS. Package README updated.
- Zip 683ab08d... is superseded; the smoke test must be repeated on the rebuilt zip.
- Rebuilt zip: 167 files, 2,773,184 bytes, SHA-256 33a11b0b5df93331c11a0e80a9ec610e7bc40d88d4c31ec9132164e980171252; no identity strings. Note: `scripts/compare_outputs.py` now differs from its hash in the final_v5 run manifests; it is the comparison tool, not a pipeline stage, and no stage reads it. All 30 other code and reference files still equal the manifests.

# Final-zip smoke test PASSED (2026-11-17, about 18:50, Claude)

- Researcher's Mac, rebuilt zip (SHA-256 33a11b0b5df93331c11a0e80a9ec610e7bc40d88d4c31ec9132164e980171252, confirmed by the researcher's own `shasum` output; full log received), Python 3.14, fresh environment, `CLEAN=1 bash run_all.sh` as one process: ALL DONE. Comparison against the shipped tables: 37 same, 4 historical, 1 not rebuilt because the optional Allstate test file is absent; RESULT: PASS. 663 decimal cells differ within tolerance, largest relative difference 9.5e-13 (macOS vs Linux numerical libraries); every identifier, count, label, flag, missing value, sign and p-value threshold side identical.
- This is the smoke test of the final package. Remaining before submission: the researcher's read-through of `paper/main.pdf`; a fresh literature search; arXiv endorsement and preprint timing.

# Pre-submission QA by Claude; paper v0.7 (2026-11-17, about 19:00-20:15, Claude)

- Full QA: `reviews/qa_2026-11-17_claude.md`. Every number in the paper traced to its table; one stale count found (accuracy competitions in E after 2022: six, not two). Also: Burtch (2026) misdescribed (version drift, and a selection-bias remark wrongly attributed to it); plan deviations not listed in the paper although plan section 11 requires it; secondary results only partly reported; one overstated composition claim; minor wording.
- CRITICAL, author's decision: TMLR's FAQ expects "the ideas, claims and results found in submissions" to be "human-sourced, not produced by such tools". The work's design, code and drafting were done by LLM assistants. Options set out in the QA file. Recommended: ask the TMLR Editors-in-Chief before submitting, describing the division of work exactly.
- Applied: paper v0.7 (v0.6 kept as `paper/main_v0.6_before_qa.tex`), with an appendix of all pre-specified secondary quantities generated from `outputs/stage3/results_secondary.csv`, and accurate disclosure of the second LLM reviewer. No result changed. The rebuild report's time-zone name was removed from the package.
- Package rebuilt: SHA-256 d78fa7345e0d2fc47545ca367612ed1c5f72135d78b4a4d5d3d09ca7c44afd70. It differs from the smoke-tested zip (33a11b0b...) only in the text of `outputs/rebuild/clean_rebuild_report_2026-11-17.md`; code and tables are unchanged.

# AI-use disclosure revised on the author's account (2026-11-17, about 19:35, Claude)

- The author states: the research idea is the author's, found after the author's own search for novel questions; the author reviewed every step in depth; no review from the second assistant was passed on unchanged, all were substantially revised by the author. The QA's C1 concern was based on the assistant's partial view of the author's involvement and is revised accordingly.
- Author's instruction: the AI-use declaration follows the requirements of the target venue. For TMLR (a first-page footnote), the footnote now reads: the research question and direction are the authors'; LLM assistants implemented the analysis code, proposed and refined analysis designs and text, and were used for critical review; the authors reviewed, revised and approved the work at every stage and are responsible for all content. "Independent review" in the text now reads "a critical review carried out with a second LLM-based assistant".

# Comprehensive QA answered; paper v0.8 (2026-11-17, about 19:50-20:40, Claude)

- Review `reviews/review_2026-11-17_comprehensive.md` (second assistant; independent recomputation of gaps and drift for 686 competitions and of formal-test fractions for 125, all matching). All points accepted; response `reviews/response_2026-11-17_comprehensive.md`.
- CORRECTION: my v0.7 deviations paragraph listed the finite-score rule as a departure, but plan rule 3 already requires finite scores. Reclassified as an implementation note. My v0.7 appendix claimed completeness without being complete; it is now generated from all 88 rows of the secondary results table.
- Figure 2 title made neutral; Python 3.14 run final_py314_20261117d; every output byte-identical to the previous run except Figure 2.
- Burtch (2026) v3 count of 129 confirmed in its HTML (SI Fig. S7 caption and Table S5).
- Open, needs the researcher: an exact-snapshot retrieval route and the Meta Kaggle licence.
- Package rebuilt: SHA-256 b02087e27942fb390d6d8de0f73d3354d7e0bb123a7451b05b3b3abf0e5ab6b4. Changed since the smoke-tested zip: `stage5_figures.py` (title string), the new appendix script, Figure 2, the run ledger and manifest, the rebuild report text and review files. No analysis code changed.

- 2026-11-17 20:20: the researcher's screenshot of the Meta Kaggle dataset page (taken 17 Nov) shows License: Apache 2.0, expected update frequency Daily, 66.46 GB, 41 files. No version history is visible on the page. The paper now states the licence. Snapshot retrieval route still open.
- 2026-11-17 20:25: the dataset page's menu has no version history either (researcher's screenshot). DECISION (fallback set out to the researcher): the exact three files are offered to the editors during review, in a confidential note, and deposited with a persistent identifier (e.g. Zenodo, Apache 2.0 notice kept) on publication, not before, to preserve anonymity. Paper and package README now say this. TO DO at submission: confidential note to the action editor. TO DO on acceptance: the deposit. Package rebuilt: SHA-256 ab6528bbc622308e1f71c1ef2282ebb6ad1dee8e44c5d74d63f391a35ba7fc24.

# Project folder tidied (2026-11-17, about 20:35, Claude, at the researcher's request)

- Deleted (all rebuildable or obsolete, none tracked by git): 13 old package build folders, the package build folder, LaTeX build files, .DS_Store files, __pycache__.
- Moved, with history kept: review briefs to `reviews/briefs/`; earlier paper drafts to `paper/versions/`; `outputs/stage7/` (withdrawn deadline contrast, metadata only) to `superseded/outputs_stage7_withdrawn_deadline/`; the unused author email draft to `superseded/` (still ignored by git). Paths in earlier log entries refer to the old locations.
- README rewritten as a current guide; its earlier status notes are in this log.

# Deep QA pass and paper v0.9 (2026-11-17, about 20:40-21:00, Claude)

- Checked: TMLR style files byte-identical to the official repository (tmlr.sty, tmlr.bst, fancyhdr.sty); the template's optional sections; the non-adaptive counterexample (relative drift 1.07%, first-submission gap negative, all three robustness variants positive) and the positive-control simulation against their saved outputs; the drift definition against the code (odd counts drop the middle submission); the share-above-threshold definition (signed gap above +1 pp or +0.01).
- Paper v0.9: the intro's "published sizes allow 19" now says these are published sizes that fit every recorded score, benchmark submissions included (21 fit the non-benchmark scores; two more fail only on a few benchmark scores); the drift definition states the odd-count rule; the conclusion adds three practical consequences (verify sizes and scoring units; hosts state split design and size; platforms release split assignments for a sample); an optional Broader Impact Statement, as the TMLR template invites. No number changed.
- Package rebuilt: SHA-256 b127ae08208e4dc695722d1494c677744957aff40f0ddda7537e004a4410276d.

# Final critical QA of v0.9 answered; paper v0.10 (2026-11-17, about 20:45-21:10, Claude)

- Review `reviews/review_2026-11-17_final_v09.md` (second assistant): no error in any result. Three corrections, all accepted; two were my errors from v0.9 (an overclaim in the new practical recommendation; adjusted gaps placed under a "Share > 0" column). Response `reviews/response_2026-11-17_final_v09.md`.
- Appendix generator now also writes the S6 table (from `outputs/stage3/results_confirmatory.csv`) and a separate S5 top-decile table. It was revised after the production run manifest (final_py314_20261117d), which is kept unchanged. It is not a pipeline stage.
- SUBMISSION CHECKLIST (carried forward): confidential note to the action editor with a working route to the three exact Meta Kaggle files and to the plan's archive evidence; the deposit on acceptance; venue-specific AI-use declaration; the researcher's read-through.
- Package rebuilt: SHA-256 837c9be80055912e3e026e32021e027510aad4f9038021a97a0cbf9487da7f20.

# Presentation pass after external feedback; paper v0.11 (2026-11-17, about 21:15-21:45, Claude)

- Feedback from a third party (not the second assistant) on TMLR worthiness, plus the second assistant's comments on it. Agreed with both on substance: one clear argument; reconstruction and scoped re-test as the backbone; drift presented as a lesson about identification, not as the headline; the counterexamples made concrete; broader relevance stated as a methodological lesson, without claiming that Kaggle percentages transfer. Not adopted: the feedback's numerical scores and acceptance probabilities (no calibration), and a "theorem" that leaderboard data can never identify adaptation (counterexamples refute an implication; they do not prove impossibility).
- Changes (no result changed): the abstract now leads with the reconstruction (11 of 32; Allstate 1.3% against 74.6%; 33 instead of 19 testable competitions), then the re-test, then the divergence and its identification limits, and ends on the transferable lesson. The introduction gains a one-paragraph argument and a scope statement on other leaderboards, including LLM benchmarks. The contribution bullets name the Allstate consequence and the new figure. The conclusion opens with the reconstruction's two qualifications.
- New Figure 5, a simulation clearly labelled as such: `scripts/illustrate_identification.py` (fixed seed; not a pipeline stage; summary in `outputs/illustration/identification_summary.csv`). It shows adaptation on a random split without real improvement, against feedback-free improvement on sets of different composition: drift +0.56 against +0.66 pp, positive for 93% against 83% of teams.
- Package rebuilt: SHA-256 587b314085b98ee7a41549190895dc21769583900548f2f5fbcd543266cbb084.

# Second third-party feedback; paper v0.12 (2026-11-17, about 21:50, Claude)

- The same third party judged v0.11 much improved and raised three remaining concerns; all three addressed, none changes a result. (1) The exploratory paragraph heading now reads "Why the divergence does not identify adaptation". (2) Tension between H2's 50% reference and our argument that 50% is not justified in general: one sentence in the confirmatory results says H2 is reported as specified, and that its rejection shows the divergence is common, not that it departs from a justified no-adaptation reference. (3) Featured/Research result less prominent: its figure moved to Appendix B; the paragraph stays among the exploratory results. Its acceptance-probability estimates were not used.
- Package unchanged (SHA-256 587b3140...; it holds no manuscript source).

# Third third-party feedback; paper v0.13 (2026-11-17, about 22:00, Claude)

- The third party now judges the paper competitive. Remaining points: (1) over-cautious ending, so state positively what was established; (2) Featured/Research the least integrated part; (3) a theory-minded reviewer may ask for a formal statement on identification. Its probabilities were not used.
- (1) The conclusion now opens "This study establishes three things": the aggregate finding holds; part of the original evidence rests on sizes the scores contradict (scoring unit decides Allstate's formal test; testable competitions 19 to 33); the divergence is common but not attributable. No claim strengthened. (2) The Featured/Research paragraph ends by tying it to the same identification limit. (3) Proposition 1, deliberately narrow (Methods, proof in Appendix B). For an example-averaged, unclipped metric and submissions fixed in advance, team drift equals the mean over public examples minus the mean over private examples of the per-example improvement d(x). (a) Under a uniformly random split of fixed size, E[drift] = 0. (b) For a given split, drift is positive exactly when improvement is larger on public examples. So without feedback, drift measures whether improvement is concentrated on the public set. Not claimed: any general impossibility of identification. Stated: it does not apply to AUC or clipped scores, and (a) fixes the mean, not the sign. The Featured/Research figure is now Appendix C.
- Package unchanged (holds no manuscript source).

# Fourth third-party feedback; paper v0.14 (2026-11-17, about 22:05, Claude)

- No new substantive concern: the proposition is simple (accepted; its value is interpretive, as the paper says), Featured/Research is secondary (it stays exploratory), a theory-heavy reviewer might want a broader impossibility claim (deliberately not made). Probabilities not used.
- Found by me while checking the feedback's wording: the simulation paragraph said aggregate scores "cannot tell the two apart", more than the simulation shows (the two runs differ, for example, in first-submission gap). Now: "Within-team drift, the statistic our data allow, does not tell the two apart."
- Decision: stop presentation rounds here; next gate is the researcher's read-through.

# Fifth third-party feedback; paper v0.15 (2026-11-17, about 22:10, Claude)

- No new concern of substance. One wording suggestion adopted: the contribution bullet said the simulation shows drift "arises equally without feedback" (an overstatement). It now names "a formal characterisation (Proposition 1) and a simulation showing that positive drift is not specific to adaptation".
- Anticipating the expected reviewer question on recent competitions, the limitation on accuracy coverage now adds a descriptive count, computed from `outputs/stage3/competition_measures.csv` and not a pre-specified test: 156 of 487 later competitions ended in 2023-2026, and drift is positive in 114 of the 151 where it is defined.

# AI-use wording refined after the researcher's exchange with the third party (2026-11-17, about 22:15, Claude)

- Footnote now: LLM assistants "were used to assist with implementing the analysis code, with analysis design, with drafting the manuscript, and for critical review. The authors directed the study, evaluated every suggestion, reviewed and revised all analyses and text, and take full responsibility for the results and conclusions."
- Review wording, in two places, now says "a separate LLM-assisted review". In Reproducibility it re-implemented the confirmatory tests and the main per-competition measures and reproduced them to within 1e-10 relative, matching the comprehensive review's documented tolerance.
- The third party's proposed "the authors selected all analyses, preregistered the study design" was not used verbatim. The archived plan in the review package states it was "approved under authority the researcher delegated to the analysis assistant", and a reviewer reading both would see a contradiction. The adopted wording is consistent with the plan.

# Comprehensive QA of v0.16 answered; paper v0.17 (2026-11-17, about 22:20-22:45, Claude)

- Review `reviews/review_2026-11-17_v016.md` (second assistant): no numerical failure. Four interpretation and wording corrections, all to text I added during the presentation rounds (Proposition 1's interpretation and scope; the Allstate abstract comparison was not like-for-like; the simulation claim; the reproducibility scope). All accepted; response `reviews/response_2026-11-17_v016.md`.
- LESSON RECORDED: strengthening the presentation to answer outside feedback produced four overreaches in two hours. Further changes should be corrections only.
- Package rebuilt: SHA-256 9735c944e62826fe1e64ab4e0a510e80d6ca606c1152161e7c67747fbc5458f9.

# Researcher's read-through complete (2026-11-17, 22:01)

- The researcher has read the paper (v0.17) and found it in order. Question raised: the AI-use footnote says "the authors'" (plural). Intentional for double-blind review: the template's "Anonymous authors" line, and plural wording reveal nothing about the number of authors. TO DO at camera-ready, if the paper has a single author: change the footnote to "The research question and direction are the author's ... The author directed the study ..." ("we" in the body may stay, which is common in single-author papers).

# Venue and submission decisions (2026-11-17, about 22:20, Claude, on the researcher's delegation)

- Venue: TMLR first, submitted by the end of November 2026, because TMLR paused submissions from 2 Dec 2025 to 5 Jan 2026 and may pause again. No concurrent submission anywhere, and no splitting of the work into several papers. Allowed alongside: an arXiv preprint and non-archival workshops. If accepted: request the Journal-to-Conference and Reproducibility certifications are considered; J2C presentation at ICML or NeurIPS 2027. Not eligible: MLRC 2026 (it covers reproductions of papers from 2025 on). Fallbacks only after a TMLR rejection, one at a time: NeurIPS 2027 Evaluations & Datasets track, DMLR, JMLR.
- Authorship: sole author. AI systems are not authors; nobody who did not contribute is added.
- Data access for the editor: the three exact files plus archive links on a private cloud link, given only in an OpenReview comment readable by the action editor and Editors-in-Chief (who already see author identities). An anonymous copy if a reviewer asks.
- arXiv: no rush, since the work is already publicly timestamped (GitHub commit and Internet Archive snapshots). Post when an endorsement is obtained (ask a lecturer at the researcher's university who posts in cs.LG) or after TMLR acceptance, whichever comes first, using the TMLR "preprint" style option.
- URGENT for the researcher: an OpenReview profile with the university email (otherwise moderation takes up to two weeks).
- 2026-11-17 22:40: submission/EDITOR_README.txt written (hashes, licence, archive links) to go with the data files on the researcher's secondary Google Drive.
- 2026-11-18 00:42: OpenReview profile active (~Al_Amin_Alif1; du.se preferred, personal email as backup; ORCID 0009-0004-0751-6306 created and linked). Next: data upload to the secondary Google Drive.

# Submission kit frozen (2026-11-18, about 01:05, Claude)

- Second assistant's final QA of v0.17 (`reviews/review_2026-11-17_v017.md`): no outstanding correction; scientific QA closed. Its reviewed artefacts match the frozen files byte for byte: PDF baef9c1d..., ZIP 9735c944....
- Frozen copies in `submission/` (tmlr_submission_v0.17.pdf; supplementary_anonymous_package.zip, ignored by git). Kit: `submission/SUBMISSION_KIT.md` (form fields, plain-text abstract, recommended action editors from TMLR's board, declarations, confidential note, checklist).
- Data files uploaded by the researcher to the secondary Google Drive with EDITOR_README.txt. The link is kept by the researcher only and goes into the confidential comment.

# SUBMITTED to TMLR (2026-11-18, 01:10 Europe/Stockholm)

- OpenReview forum: https://openreview.net/forum?id=b3wKG8vniF ; TMLR submission number 14632; sole author ~Al_Amin_Alif1; regular submission; PDF `submission/tmlr_submission_v0.17.pdf` (SHA-256 baef9c1d...), supplementary `submission/supplementary_anonymous_package.zip` (SHA-256 9735c944...). Current readers: TMLR, Action Editors, Authors, AI Reviewer. Competing interests N/A; human subjects not applicable.
- Pending: confidential comment to the editors (data link, archive evidence), after checking its readers; action editor recommendation if TMLR asks for it; no confirmation email received (both inboxes checked); the submission is confirmed on OpenReview itself.
- 2026-11-18 01:24: confidential comment posted (note GMOxC2wDN1), readers Editors-in-Chief, Action Editors, Authors only; signed 'by Authors'. Email notification received at du.se. Remaining open: action editor recommendation, if TMLR asks under Tasks.
- 2026-11-18 01:35: post-submission brief for the second assistant: reviews/briefs/BRIEF_2026-11-18_post_submission.md
