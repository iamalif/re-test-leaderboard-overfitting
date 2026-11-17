# Pre-unsealing review: deadline addendum A

17 November 2026. Reviewed `analysis_plan/addendum_A_deadline_contrast_v1.0.md`, `scripts/stage7_deadline_contrast.py`, the v0.3 response, and relevant v0.4 manuscript edits. No real post-deadline scores were read. Only synthetic inputs were passed to the proposed measure functions; the analysis entry point was not run.

## Recommendation

Do not archive and execute the current addendum as a confirmatory test of the proposed mechanism. The deadline is a potentially useful source of new descriptive evidence, and untouched post-deadline outcomes are worth preserving. However, the statistic confounds trajectory changes with unequal observation windows, and the two proposed explanations do not make opposite predictions without substantial additional assumptions. Pre-specification protects against some researcher flexibility; it does not establish identification or calibrate the null.

This is not a recommendation to abandon deadline research. Revise and stress-test the design while these outcomes remain untouched, then decide whether a carefully bounded descriptive extension merits the added scope.

## 1. Critical design failure: a linear feedback-free trajectory triggers the proposed signal

The code compares means of submission quarters before the deadline with the mean of **all** submissions afterward. Their spacing is different. These are not comparable steps even when the underlying trajectory is exactly linear and nothing changes at the deadline.

I passed the following deterministic synthetic data through the actual `team_steps` and `competition_row` functions. Forty teams each make 16 pre-deadline submissions, indexed k=0,...,15. Their private score is 0.600+0.002k and their public-minus-private gap is 0.001k. These fixed predictions improve on both sets without using feedback. Subsequent submissions continue the same trajectory. The scores are valid bounded accuracy values and can be represented by correct-answer counts on fixed sets of 1,000 examples. Both sets and all trajectories can be fixed in advance.

| Number of post submissions per team | X, percentage points | Placebo X | Public restriction passes | Private scores improve |
| --- | ---: | ---: | --- | --- |
| 1 | -0.15 | 0 | All 40 teams | Yes |
| 4 | 0 | 0 | All 40 teams | Yes |
| 8 | +0.20 | 0 | All 40 teams | Yes |

For the first case, Q3 averages indices 8–11 and Q4 indices 12–15. Their gap difference is 0.004. The first post submission is index 16, only 2.5 index units beyond the Q4 midpoint, giving J=0.0025. Hence X=-0.0015 despite an unchanged linear trajectory.

More generally, for pre-quarter size q and m post submissions on a linear gap trajectory of slope b, X=b(m-q)/2. Its sign can be determined by post-submission count alone. The existing simulator uses q=4 and m=8, building a positive X into its linear composition case. Its reported separation is therefore not a general discrimination result.

The placebo is exactly zero in the counterexample. Private scores continue improving; all teams satisfy the public-score restriction. Thus the proposed checks do not detect this failure. Replicating this trajectory across competitions can make the sign test arbitrarily significant without feedback or any deadline effect. This is a constructive invalidation of the proposed interpretation, not an assertion that this trajectory explains the real data.

**Required fix:** Define a common time/index scale and comparable observation windows before opening outcomes. Fixed equally sized submission windows remove this particular index-spacing artifact, but do not equalize calendar time or eliminate nonlinear learning trajectories and selection. A calendar-time slope design would address a different estimand and needs adequate time resolution and comparable local support. Explicitly choose the estimand rather than comparing arbitrary pooled means. Stress-test varying pre/post counts, calendar spacing, learning curvature, clipping, and stopping rules.

## 2. Major identification failure: composition need not produce a continuing linear gap

For another synthetic case, retain private score 0.600+0.002k but use gap 0.001 min(k,16). All models and their evaluations are predetermined; the model-dependent difference saturates. With eight post submissions, the actual functions return X=-0.0015, placebo=0, improving private scores (indeed a larger post step), and all 40 teams passing the restriction. The change could reflect exhaustion of an easy subpopulation or a preplanned model-family transition. No feedback is needed.

The example deliberately places a bend near the deadline to demonstrate nonidentification. It is not offered as the most probable explanation. But deadlines naturally coordinate effort, final ensembling, submission purposes and which models are produced. An earlier placebo does not exclude changes concentrated at the deadline. “Same test sets” does not imply the same rate or direction of a model-dependent gap.

Conversely, adaptation need not stop or reverse after the deadline. Participants may still optimize the public score, switch to an objective involving both scores, or continue an already selected trajectory. A persistent public-favouring gap is not a general refutation of prior adaptation. A negative change could reflect newly available private feedback without identifying what caused pre-deadline drift.

**Required fix:** Withdraw the “opposite predictions” claim. Specify a narrower operational hypothesis and the assumptions connecting it to feedback. A deadline contrast can describe a behavioural/evaluation transition; identifying feedback as its cause additionally requires separating concurrent changes. Within-team comparisons remove stable team differences, not changing objectives or model composition.

## 3. The deadline bundles several changes; treatment timing is not established

On 17 November I searched Kaggle documentation, Kaggle-hosted discussions and the official CLI documentation for late submissions, private-score visibility and post-deadline behaviour.

- An indexed [Kaggle staff response about extending closed competitions](https://www.kaggle.com/competition-hosting/576369) says private scores have been revealed and daily submission limits are greatly relaxed.
- An indexed [Kaggle notebook-sharing announcement](https://www.kaggle.com/general/291540) says the sharing quiet period ends at the deadline.
- An indexed [hosting discussion](https://www.kaggle.com/competition-hosting/403715) says late submissions provide the submitter a score without changing the leaderboard.
- The [official CLI documentation](https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md) documents submission score access. The existence of public/private output fields is not a historical guarantee of the precise reveal time or coverage.

The discussion pages did not provide readable full text through the browser tool; the statements above were available in search indexing and should be treated with that retrieval limitation. Together they support the plausibility of post-deadline feedback changes and identify competing simultaneous changes. They do **not** establish that every sampled competition showed both scores immediately after its recorded deadline or retained identical scored sets.

One user's screenshot can demonstrate the interface for one competition, but cannot validate the historical mechanism for 338 heterogeneous competitions. Code reruns, reveal delays, host-specific behaviour and changed scoring data require competition-specific verification or explicit restrictions. `IsAfterDeadline` alone does not establish exposure to newly visible private feedback at model creation/submission time.

The first late model may already have been prepared before any private score was available. Pooling all late submissions, potentially over years, mixes very different feedback exposures and information environments. Same-team eligibility does not solve that problem.

**Required fix:** Verify the proposed exposure in the retained scope before presenting this as a feedback test. If verification is infeasible, a pre-specified descriptive post-deadline contrast is still possible, but “run either way with a caveat” cannot preserve the intended causal interpretation.

## 4. Statistical and specification issues

- The plan correctly acknowledges that a 50% sign reference needs assumptions. The unequal-window counterexample shows the proposed placebo does not validate them. A nonsignificant placebo is not an equivalence result or proof of exchangeability.
- The primary test excludes exact-zero X values (`sign_summary` uses the number of nonzero values), whereas the plan describes a share of competitions with X<0. Specify treatment of ties and report both total and nonzero counts. Noise-free equal trajectories can yield many ties.
- Selection on post public performance is not necessarily conservative for X. Public and private changes can be correlated; conditioning on public improvement can select larger private improvement and smaller gaps. No universal monotonic bias direction follows. Call it an outcome-selected sensitivity, not a conservative bound.
- “Not significant” should not be translated into absence of a deadline change; report uncertainty and power/precision limitations. The planned sign test concerns a direction frequency, not every possible deadline effect.
- Related-competition dependence still affects sign tests and bootstrap intervals. Pooling the previously examined O and E cohorts should be explicit, and the fresh-outcome status should not be presented as a completely untouched study.
- Public-based clipping can introduce saturation or asymmetric changes as models improve past pre-deadline bounds. The raw-score sensitivity is useful but does not make the clipped primary statistic mechanistically specific.

## 5. What is resolved in v0.4

The inspected manuscript now uses the corrected O+E table, nominal split terminology, a limited homogeneous-mechanism interpretation, and appropriately softened abstract and first-submission wording. These address the specific v0.3 findings checked here. I did not repeat a full manuscript audit or end-to-end reproduction.

## Practical next step

Keep real post-deadline scores sealed. Revise the design around a clearly descriptive estimand or obtain a defensible basis for a narrower feedback intervention. Before freezing it, require the synthetic suite to include the two counterexamples above and a wider range of feedback-free and adaptive trajectories; report failures as well as successes. Fix windows, exposure criteria, ties, clustering and reporting rules in the revised addendum. If the design cannot distinguish the mechanisms, state that and decide whether the descriptive contrast adds enough to justify inclusion.

I have not edited the addendum or run stage 7 on research data, pushed a commit, or archived a plan. No novelty claim is made; the web search checked platform behaviour, not the literature on novelty. The 338 eligibility count was taken from the proposal, not independently recomputed. Synthetic review artifacts are saved under `outputs/review/deadline/`.
