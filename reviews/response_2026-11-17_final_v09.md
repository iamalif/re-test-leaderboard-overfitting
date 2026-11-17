# Response to the final critical QA of v0.9 (`review_2026-11-17_final_v09.md`)

Author: Claude. Date: 17 November 2026. Paper v0.10. All points accepted. Findings 1 and 3 were my errors.

| # | Finding | What was done |
|---|---|---|
| 1 | The new recommendation overstated what per-example data identify | Rewritten. Per-example predictions and split assignments for a documented sample "would allow stronger checks of sampling, composition and dependence". Attributing the divergence to feedback "would still need a justified design, such as randomised access to feedback, or explicit identifying assumptions". |
| 2 | S6 incompletely reported; "unchanged" literally inaccurate | New Appendix Table 5 gives the four S6 estimates, intervals and Holm p-values, generated from `results_confirmatory.csv`. The main text now says "the qualitative conclusions of all four tests are unchanged" and points to it. The departure summary now covers every interval omission: Spearman correlations, shares of positive values and the top-decile summary. |
| 3 | Adjusted gaps under "Share > 0"; orphan page | The S5 top-decile summary is a separate small table (Table 4) with its own columns. The estimate legend now names proportions (rows "above 0.10"). |
| 4 | Data access must be operational at submission | Agreed. It is on the submission checklist in the decision log: a confidential note to the editor with a working delivery route for the three files and the archive evidence. |
| minor | Manifest predates the appendix generator | Recorded in the decision log. The generator is not a pipeline stage, and the historical manifest is kept as is. |
| minor | Denominator wording | Methods now say the multiple is built from the most frequent denominators, skipping any factor that would take it above 5,000,000. Limitations make "lower bounds" conditional on the convention. |
| minor | Package README said "read" | Now "examined", as in the paper. |
| minor | `run_all.sh` does not build the appendix or PDF | Already stated in the project README; the submission handoff will say the same. |
| minor | Interval convention | "Unless stated otherwise, intervals are 95% bootstrap intervals over competitions." |
