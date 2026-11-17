"""EXPLORATORY post-unsealing full-text second-reader audit, 2026-11-16.
Decisions below were made after reading all sampled Overview and DatasetDescription text.
This exports decisions, not automatic labels. Original archived labels are never changed.
"""
import argparse,json,hashlib
from pathlib import Path
import pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
notes={
3933:'Inflated unscored rows disclosed; no difference in public/private sampling stated.',
4588:'Time/location prediction task; no public/private construction statement.',
5186:'Explicitly random public/private split; time split refers to train/test.',
5558:'Explicitly random public/private split; time split refers to train/test.',
9051:'50/50 leaderboard shares specified, no randomization mechanism.',
9120:'Train/test application and credit tables described; public/private split unstated.',
9992:'Some image pairs unscored; families described, no public/private grouping rule.',
13720:'Homework files and edit-distance metric only; split unstated.',
14038:'Russian text: churn prediction, KDD2009 origin; no split construction statement.',
14101:'Hungarian text: public score on 30% of test; no construction mechanism.',
14313:'Molecule-disjoint TRAIN/TEST split, not public/private.',
14774:'Hidden rerun private files versus downloadable public files; no explicit different sampling mechanism for the two leaderboard subsets. Ambiguous terminology; retain UNSTATED.',
14859:'Congestion aggregates and quantile targets; no public/private construction statement.',
15128:'Spanish text: 2018 browsing predicts Q1 2019 conversion; train/test forecasting, not distinct leaderboard periods.',
15733:'50/50 leaderboard shares; randomization unstated.',
16295:'Tweet spans and notebook requirements; no public/private construction statement.',
17575:'Rebar count files; no split statement.',
18005:'50/50 leaderboard boilerplate; randomization unstated.',
18278:'Explicitly says code is NOT re-run and no completely hidden test set. Validation stratification is training/validation, not leaderboard split.',
18459:'Only slides link in description and empty dataset heading; no substantive local split text.',
18809:'Empty description/evaluation/dataset headings.',
19018:'Train English/test other languages; no public/private language split. Explicitly code is NOT re-run.',
20850:'Generic evaluation template and user-item fields; split unstated.',
22422:'Synthetic chemical images; no distinct public/private construction stated.',
23478:'Fashion images and labels; split unstated.',
25829:'Training/test arrays and submission format only.',
25914:'Modern-text imbalance concerns train/test. Public licensing fields versus hidden blanks differs in available metadata; not an explicit different sampling/scoring rule. Retain UNSTATED; ambiguity noted.',
26479:'CTGAN synthetic train/test data; public/private construction unstated.',
27751:'50/50 leaderboard shares; housing dataset, randomization unstated.',
29653:'Named training/validation(public)/testing(private) cohorts and hidden rerun set. Does not state different sampling mechanism; retain UNSTATED with ambiguity noted.',
29761:'New test/index diversity compared with previous editions; downloadable files representative of hidden rerun data, not a stated difference between current leaderboard subsets.',
30198:'Downloadable mock videos explicitly not scored; 15 unseen plays form holdout. No public/private assignment rule.',
31254:'Seven-day prediction window follows training; no separate public/private periods.',
33110:'Chronological training events and scrambled test rows; no public/private assignment rule.',
35321:'Worker productivity dataset and dates; no split construction statement.',
35340:'Patient regression dataset; no split construction statement.',
39222:'Different human opponents in TRAIN/TEST; 30/70 leaderboard split, no stated grouping between leaderboard subsets.',
47790:'Synthetic dataset; public/private construction unstated.',
52254:'Multiple medical sites and hidden rerun set; no public/private site or time separation stated.',
53377:'Synthetic dataset and averaged target AUC; no public/private construction statement.',
59093:'EEG examples replaced with complete test set; training overlaps consolidated, no overlapping test samples. No public/private assignment statement.',
59291:'Efficiency side prize uses private scores, but main leaderboard is RMSE on both subsets. Placeholder logs replaced; no public/private construction rule.',
65862:'51/49 leaderboard shares; no randomization mechanism stated.',
66631:'Chatbot preference test placeholders replaced; no public/private model/source split stated.',
71485:'Essay scores and efficiency side prize; no different rule for main public/private scoring. Hidden rerun size disclosed.',
76728:'Synthetic car-price dataset; split unstated.',
91496:'240 unseen tasks replace placeholders; no distinct public/private task construction statement in snapshot.',
91844:'Training/unlabelled and test recording sites differ; no distinct public/private sites stated.',
104383:'Question and misconception data, rerun size; no public/private grouping stated.',
117682:'Additional labels released for TRAINING; mock downloadable test volume replaced by hidden volumes, no second-stage private-only data stated.'}
l=pd.read_csv(a.project/'outputs/stage3/split_labels.csv');s=l[(~l.flagged)&l.cohort.isin(['O','E'])].sample(50,random_state=20261116).sort_values('CompetitionId')
assert set(s.CompetitionId)==set(notes)
c=pd.read_csv(a.project/'data/raw/Competitions.csv',usecols=['Id','Overview','DatasetDescription']).fillna('')
d=s.merge(c,left_on='CompetitionId',right_on='Id')
records=[];source=[]
for r in d.itertuples():
    content=r.Overview+'\n'+r.DatasetDescription
    records.append(dict(CompetitionId=r.CompetitionId,cohort=r.cohort,slug=r.slug,original_label=r.split_label,review_label=r.split_label,original_flagged=bool(r.flagged),review_flagged=False,full_text_read=True,review_reason=notes[r.CompetitionId],text_sha256=hashlib.sha256(content.encode()).hexdigest()))
    source.append(dict(CompetitionId=r.CompetitionId,Overview=r.Overview,DatasetDescription=r.DatasetDescription))
pd.DataFrame(records).to_csv(a.out/'full_text_second_reader_audit.csv',index=False)
(a.out/'audit_full_source_text.json').write_text(json.dumps(source,ensure_ascii=False,indent=2))
(a.out/'audit_summary.json').write_text(json.dumps(dict(n=50,changed_labels=0,changed_flags=0,reviewer='Codex, second assistant; post-unsealing and not blinded to prior labels/results',label_counts=s.split_label.value_counts().to_dict(),ambiguous_hidden_file_terminology=[14774,25914,29653],scope='Full local Overview and DatasetDescription; no linked documents, image contents, or external host verification',original_label_sha256=hashlib.sha256((a.project/'outputs/stage3/split_labels.csv').read_bytes()).hexdigest()),indent=2))
