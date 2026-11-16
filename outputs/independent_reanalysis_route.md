# Independent reanalysis route — no author contact required

Decision date: 16 November 2026.

The researcher prefers an alternative to contacting the original authors. Original code is useful for implementation attribution but is not a prerequisite for rigorous research. The previous handover overstated it as a project blocker. No author has been contacted; the email draft is retained only as an unused artifact.

## What the project can establish

1. Reconstruct the published sample from its explicit competition IDs and reproduce descriptive findings on the available snapshot.
2. Evaluate whether the statistical model described in the paper is internally coherent and appropriate for the available data.
3. Independently implement and validate clearly specified calculations, documenting deviations from the published definitions and figures.
4. Extend a frozen, justified measurement protocol to genuinely new competitions after the analysis plan is publicly posted.

Exact reproduction of inaccessible source code is not required. Claims about what that inaccessible implementation actually did remain unavailable and must not be made.

## Stage 1 status and revised exit conditions

The descriptive reconstruction is encouraging: all 120 IDs are available, count drift is small, and the same five leading positive accuracy-gap outliers recur. This is a qualitative replication of the reported pattern, not an exact reproduction of every figure.

The formal reconstruction is partial. Published scoring-size conflicts, day-only timestamps, ties and conflicting tail definitions are documented findings, not reasons to force all plots into agreement. An implementation-level claim about the authors remains out of scope unless independent evidence later becomes available.

To close stage 1, complete and review:

- A reproduction matrix distinguishing reproduced descriptive results, unresolved results and justified departures from the published method.
- A metadata evidence register distinguishing directly observed counts, published counts that pass arithmetic checks, algebraically reconstructed counts and unresolved counts. Arithmetic agreement alone does not validate independent splits or unweighted scoring.
- A reproducible independent calculation with finite-population tests checked against enumeration, and method diagnostics showing discreteness and public-score selection effects.
- Explicit handling of benchmark teams, tied cutoffs, day-only dates and non-independent/unknown public-private splits.
- A frozen statement of which analyses can support descriptive generalization claims and which cannot identify adaptive model development.

These conditions replace the requirement to obtain original code or achieve visual agreement by using questionable metadata. They do not mark stage 1 complete automatically. The empirical extension remains sealed until the dated analysis plan is fixed and posted.

## Handling Allstate

Direct file evidence establishes 198,856 quote-history rows and 55,716 customers. The published size table sums to the row count. Under ordinary customer-level accuracy and disjoint public/private subsets, observed rational score denominators uniquely imply counts 16,714/39,002. Those split counts are algebraically reconstructed, not directly observed membership labels.

Keep the original descriptive score gaps unchanged. Present customer-count calculations with explicit assumptions and the row-count calculation as a sensitivity diagnostic. State the published-table inconsistency and its potential effect on uncertainty. Do not assert which counts the original code used, or that the overall original conclusion has been overturned.

## A manageable contribution

Prioritize a validated reanalysis of public/private score gaps and how their interpretation changes across competition types and eras. Keep the original study's sample distinct from the extension, and compare within metric and relevant competition/split strata. Report coverage and missingness rather than treating all competitions as interchangeable.

Formal uncertainty should be restricted to cases whose scoring units and split assumptions can be defended, with reconstructed-size cases reported separately. Do not interpret an excess of small p-values in public-selected submissions against an unconditional uniform reference as proof of adaptive development. Regression and other aggregate-score-only metrics can support descriptive analyses, but arbitrary normalization does not make them a common causal overfitting scale.

A substantial extension and useful generalizable lessons are still needed; a corrected table entry alone is not a sufficient publication case. Novelty, metadata coverage and the strength of claims remain active risks. No new method, positive effect or acceptance outcome is presumed.

## Next actions

Finish the reproduction matrix and evidence register using the original sample. Resolve tractable metadata issues from the existing competition descriptions and public sources; label the remainder unknown. Prepare a stage 2 plan around identifiable quantities, with secondary questions limited by available metadata. Ask the researcher to review and publish the concrete plan before any extension-score comparison.
