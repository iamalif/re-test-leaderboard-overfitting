# TMLR submission kit (frozen 18 November 2026)

## 1. Files to upload (do not rebuild; these are the versions the final QA reviewed)

| Upload as | File | SHA-256 |
|---|---|---|
| Submission PDF | `submission/tmlr_submission_v0.17.pdf` (14 pages; references start on p. 11) | baef9c1da507fec9ab97d76b3b7323eb690a3e81e80671658781e7ef242441ff |
| Supplementary material (ZIP, 2.8 MB; limit 100 MB) | `submission/supplementary_anonymous_package.zip` | 9735c944e62826fe1e64ab4e0a510e80d6ca606c1152161e7c67747fbc5458f9 |

Checks done on the PDF: TMLR style files byte-identical to the official repository; PDF title/author metadata blank; no author, university or account strings in the text; all fonts embedded; anonymous "Under review as submission to TMLR" header.

## 2. Form fields

**Title**
Leaderboard Overfitting on Kaggle, Revisited: A Pre-Specified Re-Test and the Limits of Aggregate Scores

**Authors**
~Al_Amin_Alif1 (sole author)

**Abstract** (plain text, paste as is)
Roelofs et al. (2019) compared public and private leaderboard scores in 120 Kaggle competitions and found little evidence of substantial adaptive overfitting. We reconstruct that study from public data and re-test its conclusion on 487 later competitions, under an analysis plan archived before any new score was examined. The reconstruction recovers all 120 competitions and the five accuracy outliers, but the published test-set sizes are incompatible with the recorded scores in 11 of 32 accuracy competitions. In the clearest case, Allstate, the published sizes count rows of the test file while the task scores customers; a normal-approximation sensitivity calculation changes the share of submissions with p ≤ 0.05 under the original null model from 74.6% with the published row counts to 1.3% with customer counts. Sizes inferred from the scores make the original test computable for 33 of 34 accuracy competitions instead of 19. In the re-test, the median public–private gap of the 95 accuracy and 73 AUC competitions differs from the original sample by less than margins set in advance, although absolute accuracy gaps are somewhat larger. Within teams, later submissions favour the public leaderboard more than earlier ones in 68% of later competitions and in 68% of the original ones; in later competitions the median size is 1.7% of the distance between a median and a top-decile team. This is the pattern adaptation to public feedback would produce, but we show that it also arises without any use of feedback when the two sets differ in composition, and that under random splits of unequal size its sign need not be balanced. The lesson extends to any audit of test reuse from aggregate scores: formal tests need verified scoring units and test-set sizes, and a divergence between reused and held-out scores does not by itself distinguish adaptation from differences between the evaluation sets.

**Keywords** (if asked)
adaptive overfitting; test set reuse; leaderboards; Kaggle; reproducibility; replication; pre-registration; evaluation

**Submission length**
Regular submission: main content is about 10 pages (references from page 11, then appendices).

**Recommended action editors** (pick from the form's list; check each still appears there)
1. A. Feder Cooper (Yale University): evaluations
2. Junpei Komiyama (MBZUAI): reproducibility, hypothesis testing
3. Olawale Elijah Salaudeen (Microsoft): benchmarking
4. Matt J. Kusner (Mila): hypothesis testing
Avoid recommending the authors of the 2019 study (Roelofs, Shankar, Recht, Fridovich-Keil, Hardt, Miller, Schmidt), whose work this paper corrects.

**Human subjects / IRB**: Not applicable. The study uses only public, aggregate Meta Kaggle data (Apache 2.0); no human participants, no personal data beyond anonymous team identifiers.
**Funding**: None.
**Competing interests**: None.
**Previous TMLR submission**: None.
**Supplementary material**: the anonymised code, plan, label table and result tables (ZIP above).

## 3. Confidential comment to the Action Editor and Editors-in-Chief

Post right after submission, as an OpenReview comment whose readers are only the Action Editor(s) and Editors-in-Chief (check the "Readers" setting before posting; never "Everyone" or "Reviewers").

> Dear Action Editor,
>
> Two pieces of evidence behind the submission cannot be anonymised, so I share them here, for the editors only.
>
> 1. **Exact input data.** The analysis uses three tables of Meta Kaggle (Apache 2.0), downloaded on 15 November 2026. The dataset is updated daily and offers no earlier versions, so a fresh download will not reproduce the paper's inputs. The exact files, unmodified, with their SHA-256 hashes and run instructions, are here: [GOOGLE DRIVE LINK]
> Placed in `data/raw/` of the supplementary package, they rebuild every table with `CLEAN=1 bash run_all.sh`, and `scripts/compare_outputs.py` checks the result against the shipped tables. If a reviewer requests the data, I can provide an anonymous copy through you.
>
> 2. **Timing of the pre-registration.** The analysis plan was committed to a public repository and archived by the Internet Archive before any later-competition score was examined:
> - Plan (2026-11-16 02:23:05 UTC): https://web.archive.org/web/20261116022305/https://github.com/iamalif/re-test-leaderboard-overfitting/blob/main/analysis_plan/stage2_analysis_plan_v1.0.md
> - Commit with plan, label table and hashes (2026-11-16 02:25:22 UTC): https://web.archive.org/web/20261116022522/https://github.com/iamalif/re-test-leaderboard-overfitting/commit/0969d41
> The plan file's SHA-256 (2198d3d71593d304a3ecda942c25387514b208aa1d7efe52f04c74709a7e2fb1) is stated in the paper and matches `analysis_plan/SHA256SUMS.txt` in the supplementary package. These links reveal my identity, so please do not forward them to reviewers.
>
> Thank you for handling the submission.

## 4. Pre-flight checklist (tick before clicking Submit)

- [ ] Logged in to OpenReview as ~Al_Amin_Alif1.
- [ ] PDF uploaded is `tmlr_submission_v0.17.pdf`; supplementary is `supplementary_anonymous_package.zip`.
- [ ] Abstract pasted from section 2; title exact.
- [ ] Action editors chosen from the list; none of the 2019 authors.
- [ ] Declarations: IRB not applicable, funding none, competing interests none.
- [ ] The Drive link and the archive links appear ONLY in the confidential comment, never in the PDF, abstract, ZIP or a public comment.
- [ ] Google Drive folder shared "Anyone with the link: Viewer"; test the link in a private browser window first.

## 5. After submitting

1. Post the confidential comment (section 3) and check its Readers list.
2. Tell Claude the forum URL; it is logged in the decision log.
3. In the first week: watch for a desk-rejection notice or AE assignment.
4. Don't post the paper anywhere under your name with a link to the anonymous submission. A separate arXiv preprint is allowed, but must not link the OpenReview page.
5. Reviews arrive over the following weeks; bring each one here unanswered and we draft the responses together. Wait for all three before uploading a revised PDF.
