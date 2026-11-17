# Second pre-unsealing review: Addendum A v1.1

17 November 2026. Reviewed the v1.1 addendum, the response to the deadline review, and `scripts/stage7_deadline_contrast.py`. All checks below use synthetic data only. No actual post-deadline score was opened and no research analysis was run.

## Decision

The requested counterexample exists: a completely smooth, feedback-free cubic trajectory triggers both tests without any bend located specifically at the deadline. I recommend not running v1.1 as a test that detects a deadline-specific change. The author's proposed stopping criterion has been met. The main paper does not depend on this extension, so it is reasonable to stop this branch and complete the outstanding reproducibility and dependence work.

The revised equal windows do fix the unequal-window defect. The problem now is the interpretation of finite differences as detecting an interruption rather than ordinary higher-order curvature.

## 1. Constructive counterexample using the actual code

For each of 40 teams, predetermine 19 submissions indexed k=0,...,18. Put the deadline between indices 15 and 16, just as in the existing simulator. Define:

```
private(k) = 0.5 + k / 1024
gap(k)     = (2048*k - k^3) / 1048576
public(k)  = private(k) + gap(k)
```

There is one polynomial throughout: no conditional clause at the deadline, no feedback, and no change in the rule for generating models. Both scores and the gap increase over the observed range. The gap is smoothly concave throughout positive k. These are valid accuracy scores on fixed sets of 1,048,576 examples, with integer correct-answer counts; predetermined nested sets of corrected examples can realize the scores. The binary denominators also avoid floating-point cancellation as the explanation for the result.

Passing these data through the unmodified `team_windows` and `competition_row` gives:

| Quantity | Score units | Percentage points |
| --- | ---: | ---: |
| X | -0.000720977783203125 | -0.0720978 |
| Earlier placebo | -0.0005664825439453125 | -0.0566483 |
| Y | -0.0001544952392578125 | -0.0154495 |
| Private-score step before | +0.0029296875 | +0.292969 |
| Private-score step after | +0.0029296875 | +0.292969 |

For 20 synthetic competitions following this trajectory, the actual `sign_summary` returns 20/20 negative and two-sided p=0.00000190735 for **each** statistic. Both criteria in section 5 pass. The significance calculation illustrates the proposed decision rule; it is not evidence from real competitions. Distinct competitions can have different positive scales and baselines without changing either sign, so the construction does not depend on literal duplicate score sequences.

The earlier placebo is negative, but the specified decision rule does not veto a negative placebo. Instead, Y is intended to remove its curvature. It does not remove this cubic curvature. The private-score context shows exactly the same improvement before and after.

This example is not an assertion that cubic trajectories explain Kaggle. It establishes that the rule does not distinguish a deadline interruption from smooth feedback-free development.

## 2. Why the failure is structural

With consecutive equal-size windows, X is a second finite difference of window means and Y is a third finite difference:

```
X = P - 2B + A
Y = P - 3B + 3A - C
```

The third difference annihilates polynomials of degree at most two. It does not annihilate arbitrary smooth functions. For a cubic coefficient -a and window width w, Y=-6*a*w^3. Our a=1/1048576 and w=3 give the value above exactly. No discontinuity in value, slope or curvature is needed. The selected exponential saturation example has a favourable third-derivative sign; that is one curve, not coverage of smooth saturation or curvature generally.

The addendum itself accurately says Y is zero for quadratic trajectories. However, section 5 then says the rule “guards against smooth curvature,” and the response says “smooth curvature is handled.” Those broader statements are false. Smoothness/continuity and an exactly quadratic local course are different assumptions. A cubic is infinitely differentiable and violates the latter while satisfying the former.

The counterexample therefore does not refute a theorem explicitly conditioned on a quadratic trajectory; it shows why that restrictive assumption cannot be presented as ordinary continuity or justified by these simulations. With four window means, the data alone cannot decide between a smooth cubic and a quadratic course plus an interruption. Adding successively higher differences would move this problem to the next polynomial order rather than solve identification.

## 3. Two-test rule: conditional logic is sound, calibration remains missing

Requiring rejection of both component hypotheses can control the error rate for a conjunction claim if the component tests are valid for the corresponding composite nulls. No independence between the two tests is required for that basic intersection-union logic. I do not object merely because two tests are used without a standard multiple-testing correction.

But this does not give a 5% false-positive rate for the scientific null “no deadline-specific change.” The cubic example satisfies that scientific null and rejects both. A binomial sign test also needs fair signs under its stated null and appropriate independence across observational units. Acknowledging related competitions as a limitation does not supply that calibration. The unqualified claim that the combined rule keeps the overall error rate at 0.05 must specify the null and assumptions under which it holds.

## 4. Additional code and wording findings

**Empty eligibility crashes.** `team_windows` assumes the grouped pre-submission table contains all three window columns. If no team has 3w pre submissions, accessing `g[("gap", 0)]` raises `KeyError`. I reproduced this by applying w=6 to the synthetic data with 16 pre submissions. The same pathway can arise for the primary sample or w=5 sensitivity when all teams in a competition are below the corresponding threshold. The caller's `len(t) < MIN_TEAMS` check occurs too late. Return an empty table with the expected columns when there are no eligible pre teams. This is a code defect independent of whether the proposed statistical analysis is retained; I have not examined research outcomes to establish its frequency.

**Exposure uncertainty need not only dilute.** Section 8 says unverified exposure can dilute, but cannot create, a feedback effect. That requires a much more specific misclassification model. Exposure timing may correlate with competition type, model changes, scoring changes or who submits late. The deadline also bundles other changes. Replace the one-direction bias assertion with uncertainty about direction and magnitude. Similarly, “the two test sets stay the same” should be stated as an assumption within the verified scope, not a universal historical fact.

**Submission order is not calendar time.** Equal windows fix one defect, but a smooth calendar-time trajectory sampled at changing intervals can have changing differences in submission order. This remains another reason not to label the statistic a deadline-specific interruption without additional design assumptions.

## What is satisfactory

The window construction takes the final three consecutive pre windows and the first post window as stated when eligible data exist. Later extra submissions do not enter those windows. The removal of the outcome-selected “conservative” restriction, explicit tie reporting, admission that ongoing adaptation can be invisible, and descriptive framing are improvements. The proposal is also appropriately marked unfixed, so these problems were found without consuming the untouched outcomes.

## Handover and limits

Synthetic script and results: `outputs/review/deadline_v11/check.py` and `results.json`. These import only the measurement functions; they do not call `main()` or inspect raw research data. The review did not edit the plan, paper, existing results or analysis implementation, and did not commit, push or archive anything.

I did not repeat the platform search, rerun the entire author's simulation suite, verify the 211 eligibility count, or perform a novelty search. No new claim about novelty is made. The narrow question posed by the author is answered by the exact cubic counterexample.

Recommendation: preserve this design history, leave the post-deadline outcomes sealed, and finish the main paper's unresolved checks. A future explicitly descriptive plot or contrast could be useful, but the current sign-test rule should not be used to claim detection of a deadline-specific bend or evidence that separates feedback from smooth model-dependent change.
