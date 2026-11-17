# Chronology (identities and links removed)

All times UTC. The dated decision log and the archive links are available to the editor.

| When | Event |
|---|---|
| 15 Nov 2026, about 22:40 | Meta Kaggle downloaded (hashes in `ANON_README.md`). |
| 15 Nov, 22:42 | Stage 0: counts of submissions and score presence per competition. No score values compared. |
| 15-16 Nov | Stage 1: reconstruction of the original 120 competitions only. |
| 16 Nov, about 01:30-02:10 | Measures developed and piloted on the original 120. Split labels assigned from description text for all cohorts. |
| 16 Nov, 02:21 | Analysis plan v1.0, label table and measure code committed to a public repository. |
| 16 Nov, 02:23 and 02:25 | Third-party web archive snapshots of the plan and of the commit. |
| 16 Nov, 02:27 | Later-competition scores read for the first time; stage 3 run under the plan. |
| 16 Nov | Exploratory follow-ups (stage 4); first draft. |
| 16-17 Nov | Four rounds of independent review. The claim that drift identifies adaptation was withdrawn; sizes relabelled as minimum compatible sizes; the selection adjustment relabelled as a reference. Planned results unchanged throughout. |
| 17 Nov | A further contrast at the competition deadline was designed, reviewed twice before any post-deadline score was analysed, found unable to separate a deadline change from smooth curvature, and withdrawn unused. Post-deadline scores have not been analysed. (Pipeline steps load all submissions before filtering to pre-deadline ones, and one parser diagnostic on 17 Nov passed 14,733 post-deadline public-score strings of two original competitions through a number-format comparison without computing anything from them.) |
| 17 Nov | Dependence, stratified and tail analyses, with definitions logged before results. Clean rebuild from raw files compared table by table. |
| 17 Nov | Package review found the comparison tool ignored text columns and the zip dropped the run script's executable setting; both fixed. The stricter comparison found that one stage 3 table had been built across two runs (column order, one bookkeeping column); regenerated in a single run with a fixed column order. No result changed. |
| 17 Nov, afternoon | A further review found the comparison tool still too lenient (tolerance on identifiers and signs; a blanket exception for one intermediate file) and stage 3 re-parsing its own stored numbers. Fixed: comparison v3 (exact identifiers, labels and signs), exact CSV reading in every script, stage 3 row store, team-flag script aligned with its stored output, per-stage ledger. Final clean runs under Python 3.14 and 3.12 pass; no paper number changed. |
| 17 Nov | Main environment moved to Python 3.14; rebuild under it found inexact CSV number parsing in two original-sample scripts; fixed; both environments now give identical tables. No number in the paper changed. |

Deviations from plan v1.0: (1) the formal accuracy test also requires scores within the unit interval; (2) the 1,000-submission rule was applied to finite scores, removing 2 competitions; (3) bootstrap intervals are computed with competitions sorted by identifier, for reproducibility; (4) the audit of 50 unflagged labels was first done by the original reader on excerpts, and completed later by a second reader on full text who knew the labels and results; (5) two original-sample scripts now read scores exactly (see `outputs/rebuild/`), changing four original-sample table rows not used in the paper.
