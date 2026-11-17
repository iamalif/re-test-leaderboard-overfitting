# Second review: revised paper and response — 16 November 2026

**Verdict: the revision substantially improves the paper, but I cannot yet sign off. A new central mathematical assertion is false as stated.** The descriptive findings remain useful. The next revision can resolve this by keeping H2 as the prespecified comparison with a 50% reference, while withdrawing its interpretation as a general test of random splitting plus no feedback.

Reviewed `paper/main.pdf` (9 pages), `reviews/response_2026-11-16.md`, stage-6 code/results, and `run_all.sh` at commit **517ee6f84cdf0222eaaa73c732ca3ef2287ade64**. PDF SHA-256: `4d2c4bfbafcc9de28551c29e8d53c9042a23886c5af1cfec987512b041835341`. New checks and audit records are in `outputs/review/revision/`. No existing tracked research file was changed.

## 1. Major: random splitting does not generally make the sign of drift a fair coin

The abstract (`paper/main.tex:21`) now says that under a random public–private split the divergence “could not arise” without feedback dependence. Methods (`:72`) says random splitting implies no preferred sign, and treats drift as testing exchangeable sets plus feedback-independent submissions. The response repeats this as a converse established by simulation. This is not valid for the unequal split sizes used by many competitions.

For a fixed sequence of models evaluated by ordinary accuracy, define each example's average late-minus-early correctness change as (z_i). Raw competition drift, with fixed team weights, is a difference of sample means:

\[
D=\overline z_{\rm public}-\overline z_{\rm private}.
\]

Uniform random assignment with fixed public/private sizes implies **E[D]=0**. It does **not** imply **P(D>0)=P(D<0)**. Equal expectation and sign symmetry are different properties. With unequal sizes, exchanging the labelled score vectors is not in general a distribution-preserving operation. A raw accuracy sign-symmetry argument does work for an equal-size uniform split, with feedback-independent trajectories, symmetric inclusion/processing, and appropriate treatment of ties. Those are additional assumptions, not consequences of arbitrary random splitting. Public-derived clipping additionally breaks the score-exchange symmetry used by such an argument.

### Exact counterexample, checked with the project's drift code

Five test examples; choose one uniformly for public and the other four for private. Every team makes a predetermined sequence: the early models get all five wrong; the later models correct examples 1–4, leaving example 0 wrong. No model consults either score.

| Which example is public? | Probability | Drift |
|---|---:|---:|
| One of the four corrected examples | 4/5 | 1 − 3/4 = **+1/4** |
| The unchanged example | 1/5 | 0 − 1 = **−1** |

Mean drift is zero, but **80% of random splits have positive drift without any feedback**. The script instantiates 100 teams with 12 predetermined submissions each, and enumerates every public assignment using `team_drift`. This is an exact calculation, not Monte Carlo uncertainty.

The issue is not restricted to tiny sets. With 10,000 examples, a uniformly random 2,000/8,000 split, and fixed models improving on 9,999 examples but not one, drift is positive with probability 0.8 (+1/8,000) and negative with probability 0.2 (−1/2,000). Its magnitude is small, but H2 uses only its sign. Independent competitions following this feedback-free construction would reject a 50/50 sign reference increasingly often as the number of competitions grows.

Outputs: `random_split_exact_counterexample.csv`, `followup_checks.json`; executable: `followup_checks.py`.

**What this does and does not establish.** It falsifies the proposed universal null calibration. It does not show that unequal-size skew explains the observed Kaggle result, nor invalidate the observed 327/481 count. The original review validated the numerical sign-test calculation, not this newly asserted justification; this follow-up identifies a further conceptual limitation. Even under a calibrated null, a finite observed divergence can arise by chance, so “could not arise” is too categorical.

**Required fix:** remove the new abstract assertion and the blanket random-split/no-preferred-sign statement. State separately the zero-expectation result for additive raw metrics and the stronger symmetry conditions needed for a sign test. Keep the archived H2 result, explicitly as a prespecified test against a 50% reference, without claiming that reference follows generally from nonadaptivity. Add this counterexample beside the first review's composition counterexample. The 300-run stage-6 simulation shows behavior of that generator; it cannot prove a general converse. This also weakens the first-submission sign test's proposed interpretation as evidence specifically for nonexchangeability or pre-first-submission adaptation, especially across clipped/nonlinear metrics.

## 2. Moderate: “first submissions fit the random-split null” is not evidence that their split is random

`scripts/stage6_review_response.py` selects competitions where at most 5% of first-submission p-values are at or below .05. The paper (`main.tex:149`) presents this as a subgroup whose first submissions fit the null; the response calls it support for random splitting.

This is a threshold on a noisy, dependent, often discrete and conservative rejection fraction, calculated using uncertain minimum sizes. Failure to reject individual submissions does not validate split randomization. The filter also uses score outcomes related to the drift outcome: selecting on first-submission gaps can itself affect early-versus-late comparisons. It is a post-outcome diagnostic subgroup, not a validated negative control. No calibrated competition-level goodness-of-fit test has been supplied.

The **94 competitions combine O and E: 23 original and 71 extension**. Likewise, the five RANDOM-labelled contests are **three original and two extension**. The user-facing table must not imply that either subset is purely later competitions. The reported 56/94 and p≈.079 are consistent with the stored calculation, but neither the subgroup selection nor a nonsignificant result establishes absence of adaptation or validates the sign null.

**Fix:** name the exact filter, label it exploratory and outcome-selected, report cohort composition and uncertain-size dependence, and remove language treating it as independent evidence for random splitting. It can be omitted if it distracts from the paper's defensible conclusions.

## 3. Moderate: the new size-evidence tiers include three invalid fits

`scripts/stage6_review_response.py` selects accuracy rows by `n_pub.notna()`, without requiring both lattice fits to equal one and scores to be in [0,1]. Consequently, three contests without usable formal tests are classified as tier C minimum-compatible sizes:

| ID | Public lattice-fit fraction | Private lattice-fit fraction | Problem |
|---|---:|---:|---|
| 14666 | 0.973008 | 0.977074 | Some scores do not fit |
| 22720 | 0.990366 | 0.985465 | Some scores do not fit |
| 23478 | 1.000000 | 1.000000 | Some scores outside [0,1] |

The stated tiers sum to **128**, while only **125** contests have usable minimum-based formal results. For usable cases the tier counts are **A=1, B=21, C=96, D=7**, not C=99. This does not change the existing stage-3 confirmatory results or the 125-case formal summaries; it is an error in the new evidence inventory and wording. See `ineligible_size_tiers.csv`.

**Fix:** add an explicit invalid/unresolved category or restrict the tier inventory to usable fits; retain all failures transparently. For older resumable rows, `scores_in_0_1` is missing even where results are usable, so do not treat missing as false without rechecking the raw scores. The review check uses the recorded fit fractions and successful formal-test indicator.

The 21/21 correspondence with published sizes is useful corroboration in that selected historical subset. It does not estimate how often a minimum is correct across new competitions with unverified units; avoid “usually right” as a general empirical conclusion. Published-size agreement is evidence, not independent verification of every count or the random-split model.

## 4. Full-text second-reader audit completed: no label changes under the original rubric

I read the **complete local Overview and DatasetDescription text** for the same seed-20261116 sample used by the first reader: **50 contests, 6 O and 44 E; 46 UNSTATED, 2 RANDOM, 2 NO_TEXT**. I did not use keyword-selected or length-truncated excerpts as the basis of final decisions. All 50 have individual reasons in `full_text_second_reader_audit.csv`; the raw text is preserved in `audit_full_source_text.json` with text hashes in the decision table. The export script records these manual reading decisions rather than assigning labels algorithmically.

**Result: 0 flag changes and 0 label changes.** The two RANDOM descriptions, Facebook check-ins (5186) and Santander product recommendations (5558), explicitly distinguish time-based train/test splits from random public/private splits. Several other descriptions give only split percentages. Train/test differences in CHAMPS (14313), Jigsaw (19018), Scrabble (39222), and BirdCLEF (91844) do not establish differences between leaderboard subsets.

Three cases deserve explicit ambiguity notes: **14774, 25914, 29653**. Their text distinguishes public/downloadable files, hidden files, licensing metadata, or validation/testing cohorts. It does not unambiguously state a different sampling or scoring mechanism between the two scored leaderboard subsets. Under the original positive-evidence rubric I retain UNSTATED, rather than treating “hidden” alone as proof of a nonrandom split. Other descriptions, such as NFL (30198), explicitly say downloadable mock files are not scored at all. This distinction is essential.

**Limits:** this was a second AI reader, after outcomes were unsealed, aware of the prior labels and results; not a blinded independent human reliability study. It covers the full stored text fields, not external links, contents of embedded images, or host verification. It checks application of the description-only rubric, not whether the true splits were random. Zero changes does not justify a 6% upper bound on the prevalence of nonrandom splits. The original excerpt-audit deviation should remain in the log; this later audit completes the outstanding full-text reading task without retroactively changing its timing. The archived label file remains untouched.

### Additional factual correction exposed by the audit

The revised paper calls the code-only category “Competitions scored by re-running submitted code” (`main.tex:129`). That is not what `OnlyAllowKernelSubmissions` establishes. Two analysed E contests in this sample, **18278 (Flower Classification)** and **19018 (Jigsaw Multilingual)**, explicitly say:

> Your code will not be re-run, as there is no completely hidden test set.

Both have `CodeOnly=True` in the analysis. **Fix:** use “competitions requiring notebook/code submissions.” A claim about hidden-data reruns needs a separate validated variable. This does not change the reported comparison, but changes its mechanism and interpretation.

## 5. Lower severity: the new runner does not stop at every failure

Dependency order in `run_all.sh` is improved. However, stage 3 is inside an `until ... | ...` condition. Bash's `set -e` does not stop execution for failure in that condition: a fatal stage-3 error is treated as a request to resume. Persistent errors can loop indefinitely.

I tested the actual runner with a harmless dummy interpreter that fails stage 3 once with exit 7, then prints DONE on retry. It prints “resuming stage 3”, continues, and ends **ALL DONE / exit 0**. No analysis scripts were executed in this test. Artifacts: `runner_failure_probe.py` and `runner_failure_probe.txt`.

**Fix:** capture the stage-3 exit status and fail on a nonzero status; only retry a successful run that explicitly reports PAUSED. Check completeness before downstream processing. A “clean rebuild” must also explicitly handle existing resumable outputs, since cached rows are otherwise skipped. I have not run a clean end-to-end rebuild of the revision.

## Disposition of the first review

| Original finding | Current assessment |
|---|---|
| Drift does not identify adaptation | Composition limitation accepted and explained; **new random-split converse needs withdrawal/correction** |
| Minimum denominator ≠ identified size | Main conceptual correction accepted; fix invalid tier entries and qualify generalization from 21/21 |
| Independent resplitting ≠ actual selection adjustment | Substantially resolved by reference-model wording and dependence caveat |
| Missing clipping | Resolved in methods with unclipped sensitivity; clipping also matters for the new symmetry argument |
| Truncated label audit | Deviation acknowledged; full local-text second-reader audit now complete, with limits above |
| Scope and statistical interpretation | H1/H3 and Featured/Research wording much improved; new diagnostic subset and random-split interpretation remain problematic |
| Attribution/boundary/reproduction instructions | Attribution and boundary resolved; runner failure handling still needs work |

One small remaining precision issue: the abstract couples the all-metric 68% count to an approximately 1%-of-spread magnitude. The E all-metric median relative drift is **1.683%**, whereas **0.788%** is the five-original-metric subset. Name the subset when quoting that magnitude. Also replace “two explanations can be set aside” with the narrower statement that the pattern survives the specified trimming and pooled linear adjustment; these checks do not exclude every version of those mechanisms.

## Recommended next step

Continue with the revised descriptive/identification-limits framing. Correct items 1–3 and the code-only wording before considering the mathematical story settled. Add the completed audit and runner repair. Matched comparisons and family-dependence checks remain worthwhile; I did not complete them in this follow-up and they should not be described as done. No fresh novelty search was performed in this follow-up, and I make no novelty claim.

The archived plan, measure code, labels, and recorded confirmatory results are unchanged from the relevant previous commits, as checked in `followup_checks.json`. The computations are reproducible, but interpretation still needs the above corrections. The research remains worth pursuing; the new counterexample strengthens the need for the paper's more careful framing rather than requiring abandonment.
