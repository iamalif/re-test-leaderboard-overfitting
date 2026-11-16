# Stage 1 replication: first audit

Updated 16 November 2026. See `stage1_audit_update.md` for subsequent benchmark, tie, and scoring-unit findings. **Status: descriptive replication is encouraging; the full stage 1 gate has not passed.** No extension-sample public/private score comparisons have been performed.

## What was recovered

The official supplement contains a 40-page paper with appendices, including all 120 original competition IDs. All are present in the downloaded Meta Kaggle snapshot. The sample contains 34 accuracy, 40 AUC, 17 MAP@K, 15 LogLoss and 14 MulticlassLoss competitions. Eighteen ended in 2019; the latest deadline currently recorded is 4 April 2019. This is not necessarily the authors' data-extraction cutoff.

The paper groups five MAP@K aliases and two multiclass-loss aliases. Counting only one alias or applying a 2018 cutoff cannot reproduce its sample.

We recovered 1,510,406 pre-deadline, finite paired scores across the original IDs, compared with 1,513,918 submissions listed in the paper: 3,512 fewer, or 0.232%. Forty-six competition counts match exactly; the largest relative count discrepancy is 2.56%. The reason for the differences remains unverified. The three raw-file SHA-256 hashes match the prior decision log.

## What replicated

The five largest positive mean accuracy gaps are exactly the five named by the original paper. Positive values mean higher public accuracy than private accuracy; these are observed gaps, not causal estimates of adaptive overfitting.

| Competition | ID | Mean public-minus-private gap, percentage points |
|---|---:|---:|
| TAU Robot Surface Detection | 12598 | 7.007 |
| 2019 1st ML month with KaKR | 12349 | 3.929 |
| Prediction Reviews Sentiment Analysis (Light) | 5903 | 2.828 |
| DecMeg2014 | 3641 | 2.103 |
| PadhAI: Text - Non Text Classification Level 2 | 12681 | 1.813 |

The aggregate distributions visually resemble Figures 4 and 6, including the large MAP@K and multiclass-loss tails. This is a qualitative comparison, not an exact match to digitized figure coordinates. Individual all-submission and top-10% scatter plots with fitted lines were generated for all 120 competitions. Confidence intervals have not yet been added to the accuracy scatter plots.

The current data also reproduce a striking diagnostic case: 1,364 of 1,431 submissions to competition 3043 have private score exactly 99. The original Figure 6 already contains a similarly extreme multiclass-loss tail. We retain these values in the faithful descriptive pass; their interpretation needs verification. Presence and numerical finiteness alone do not establish a meaningful held-out score.

## Why formal replication is unfinished

1. **Published size inconsistencies.** For competition 5275, main Table 1 gives 249,344 public / 249,343 private examples, whereas appendix Table 2 gives 696 / 696. The recorded scores are consistent with the appendix pair. We preserve the conflict rather than treating either table as independently verified truth.
2. **Integer-count checks.** Ordinary unweighted accuracy multiplied by the number of scored examples must be an integer, up to numerical precision. Nineteen of 34 accuracy competitions satisfy this check for every submission using appendix sizes (tolerance 0.0001 of one correct prediction). Thirteen have at least one inconsistency; two have missing sizes. These issues could reflect size errors, different scoring units, historical changes, exceptional records or other score semantics. They are not evidence of misconduct or proof that the paper's computations are wrong.
3. **Counting scored units matters.** The local competition descriptions say Allstate predicts one outcome per customer despite multiple rows per customer; speech recognition explicitly says not all supplied test files count toward scoring. File row counts times a nominal split percentage therefore need not equal the actual scoring denominators. Cdiscount's description says its data were removed after the competition.
4. **Different p-value definitions.** Main equation 1 uses an inclusive tail (`>=`), while appendix equations use a strict tail (`>`). We compute both using the hypergeometric distribution. Both implementations passed 400 small-population checks against direct enumeration. The paper instead describes an approximation using Stirling's formula, so numerical identity is not claimed.
5. **Limited conditional p-value results.** We generated p-values and all/top/first-submission CDFs for the 19 fully consistent competitions only, conditional on the published sizes. Arithmetic consistency does not independently establish those sizes or independence of the public/private sets. We did not round incompatible scores into invented correct-prediction counts. Diagnostic candidate denominators are explicitly marked UNVERIFIED and are not used for tests.
6. **Submission ordering and ties.** Every retained submission date has day precision only. First-per-team uses earliest recorded day, then smallest submission ID; within-day chronology is an assumption. Top 10% uses `ceil(0.1*n)` and breaks score ties by submission ID. The paper does not specify its tie rule. These choices need sensitivity checks or original-code confirmation.

The 15 accuracy competitions requiring size/source resolution are: 3362, 3428, 3641, 3649, 3788, 6109, 7042, 7115, 7634, 9051, 12187, 12349, 12598, 13078 and 13383.

## Corrected extension feasibility — metadata only

| Provisional cohort | At least 1,000 paired pre-deadline submissions | Reported public percentage between 0 and 100, exclusive | Accuracy within that subset |
|---|---:|---:|---:|
| 2019 onward, excluding the 120 original IDs | 600 | 525 | 94 |
| 2020 onward | 505 | 443 | 74 |

Neither row is a finalized inclusion rule. Excluding original IDs alone does not establish that all remaining 2019 competitions occurred after the original sampling window. The original submission-count threshold did not explicitly require paired scores. Final feasibility also needs metric grouping, valid-score semantics, and actual split verification. Neither candidate cohort resolves the scarcity of recent accuracy competitions.

## Next work and decision

Continue stage 1; do not pass its gate yet. First obtain authoritative scored-example counts or released solution files with public/private usage labels for the main mismatched examples, especially Allstate and speech recognition. Check whether original analysis code or a historical snapshot can be located. Then resolve size and ordering discrepancies, complete the formal plots, and document remaining deviations before the researcher's next gate decision.

The researcher checked the speech challenge Data tab and reported only `link_to_gcp_credits_form.txt`, `sample_submission.7z`, `test.7z` and `train.7z`. No answer-key file was visible in that listing. No download is needed from that page for the current size audit. A targeted web search found contestant model solutions, but did not locate a verified released answer key; absence is not established.

arXiv's current help page says first-time/category submitters require endorsement. Account-specific eligibility has not been checked and no one has been contacted.

## Reproduction and provenance

The project script is `scripts/stage1_reproduce.py`, with the published-ID allowlist in `data/reference/original_120_manifest.csv`. It filters submissions to original IDs before computing any score differences. Outputs are in `outputs/stage1/`. Run metadata records the actual environment; it differs from the older project's untested requirements file. A separate `requirements-stage1.txt` records the versions used without rewriting that prior file.

Full run from the project folder:

```sh
python3 scripts/stage1_reproduce.py --project .
```

After a full run, use `--from-cache` to reuse the extracted original-only submission file. No fresh download is needed to reproduce the current calculations. Source-size verification is still required before interpreting the formal results as a completed reproduction.

Sources: [official paper and supplement listing](https://papers.nips.cc/paper_files/paper/2019/hash/ee39e503b6bedf0c98c388b7e8589aca-Abstract.html), tables 1–6 and appendix B.5 in the supplement; the researcher's downloaded Meta Kaggle snapshot; [arXiv endorsement guidance](https://info.arxiv.org/help/endorsement.html). A limited search for the paper title with GitHub/code terms did not locate original code; that is not proof that none is public.
