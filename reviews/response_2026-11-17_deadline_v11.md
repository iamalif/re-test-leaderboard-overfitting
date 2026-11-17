# Response to the second pre-unsealing review of Addendum A (`review_2026-11-17_deadline_v11.md`)

Author: Claude. Date: 17 November 2026.

**The deadline sign-test rule is withdrawn and will not be run.** I asked for a feedback-free trajectory, other than a bend placed at the deadline, that makes both X and Y negative, and said I would drop the test if one existed. The cubic does it. The point is structural, as the review says: Y is a third difference and annihilates only quadratics; with four window means a change at the deadline cannot be told from third-order curvature, and adding a window only moves the problem up one order. "Guards against smooth curvature" and "smooth curvature is handled" were false as written.

I considered a local-linear discontinuity estimate in place of differences and rejected it for the same reason: on a discrete submission index with a few points per side its bias is also driven by the third derivative and cannot be shrunk by narrowing the window.

- Addendum v1.0, v1.1, their hashes and the stage 7 script are in `superseded/`, marked never run. The `KeyError` on empty eligibility is noted there and not fixed, since the script is retired.
- No post-deadline score has been read. The paper's limitations section records that the contrast was designed and withdrawn, and why.
- I agree with the two wording points (exposure uncertainty has no known direction; "same test sets" is an assumption). They no longer appear anywhere, since the addendum is withdrawn.

## Work the reviews asked for, now done (all exploratory; definitions logged before results)

1. **Dependence between related competitions** (`scripts/stage6_dependence_and_strata.py`, `outputs/stage6/dependence_and_strata.csv`, `competition_clusters.csv`). 365 groups for 652 competitions: hosting organisation where recorded, otherwise the slug without digits, first two tokens. Group bootstrap: H1a -0.03 pp (-0.20 to 0.11); H1b -0.0007 (-0.0043 to 0.0019); H2 share 68.0% (62.9 to 71.8); H3 0.0013 (-0.0042 to 0.0099). One competition per group, 2,000 draws: median H2 share 68.0% (66.0 to 69.6), sign-test p below 1e-4 in every draw.
2. **Stratified O versus E.** Accuracy, Community: 0.02 pp against 0.06. AUC, not Community: 0.0004 against 0.0005. Accuracy, not Community: 13 against 8 competitions, 0.23 pp against 0.01, interval -0.31 to 0.65, uninformative.
3. **Tails for H1** (`outputs/stage6/h1_tail_summary.csv`). A finding that qualifies the headline: the median absolute mean gap for accuracy is 0.34 pp in E against 0.20 in O (upper quartiles 1.09 and 0.61). Signed medians are similar; absolute discrepancies are larger. For AUC the absolute gaps are smaller in E. The paper now says so.
4. **Clean end-to-end run**, Python 3.12, fresh directory, every script from raw files, executed stage by stage in the order of `run_all.sh` (the shell I have cannot keep one process alive long enough to run the wrapper itself). 34 result tables compared with the repository: all identical except (a) `outputs/stage1/original_team_flags.csv`, an intermediate that the stage 1 script builds with all teams of the 120 competitions on a fresh run but that the repository holds in a shorter form; nothing downstream differs; (b) `outputs/stage6/split_size_symmetry.csv`, where bootstrap intervals depended on row order. Fixed by sorting; now identical. Reported numbers unchanged at the precision shown.
5. **Own finding:** the archived label table had been built by an inline snippet. `scripts/stage3_build_labels.py` now builds it and reproduces the archived file byte for byte.

## Still open

Anonymised review package; arXiv endorsement; the author's own reading of the paper.
