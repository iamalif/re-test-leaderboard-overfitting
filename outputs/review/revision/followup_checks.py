"""EXPLORATORY second review, 2026-11-16. Exact counterexamples and metadata audit.
Writes only to --out. No simulations fitted to observed scores.
"""
import argparse,sys,json,hashlib,subprocess
from pathlib import Path
from fractions import Fraction
import numpy as np,pandas as pd
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.project/'scripts'))
from stage2_measures import team_drift
rows=[]
# All models are chosen before the random assignment. First six predict all five incorrectly;
# last six predict examples 1..4 correctly. Same predetermined trajectory for 100 teams.
for public_example in range(5):
    gain=np.array([0,1,1,1,1]);pub=gain[public_example];priv=np.delete(gain,public_example).mean()
    rec=[]
    for team in range(100):
        for step in range(12):
            late=step>=6; rec.append((team,len(rec),float(pub*late),float(priv*late)))
    g=pd.DataFrame(rec,columns=['TeamId','Id','pub','priv']);g['day']=pd.Timestamp('2000-01-01');g['gap']=g.pub-g.priv
    rows.append(dict(public_example=public_example,probability=.2,drift=float(team_drift(g).mean())))
pd.DataFrame(rows).to_csv(a.out/'random_split_exact_counterexample.csv',index=False)
summary={'five_examples':{'mean_drift':sum(r['probability']*r['drift'] for r in rows),'positive_probability':sum(r['probability'] for r in rows if r['drift']>0)},
 'large_example':{'N':10000,'public_size':2000,'private_size':8000,'positive_drift':str(Fraction(1,8000)),'positive_probability':.8,'negative_drift':str(-Fraction(1,2000)),'negative_probability':.2,'mean_drift':0},
 'baseline':subprocess.check_output(['git','-C',str(a.project),'rev-parse','HEAD'],text=True).strip()}
m=pd.read_csv(a.project/'outputs/stage3/competition_measures.csv')
t=pd.read_csv(a.project/'outputs/stage6/size_evidence_tiers.csv').merge(m[['CompetitionId','fit_pub','fit_priv','scores_in_0_1']],on='CompetitionId')
# Earlier resumable rows predate scores_in_0_1, so missing there is not failure.
# p05_all is populated only for the 125 usable cases in the recorded results.
t['all_scores_compatible']=t.fit_pub.eq(1)&t.fit_priv.eq(1)&t.p05_all.notna()
t[~t.all_scores_compatible].to_csv(a.out/'ineligible_size_tiers.csv',index=False)
summary['invalid_sizes_in_tiers']=t.loc[~t.all_scores_compatible,'CompetitionId'].tolist()
summary['tier_counts_all']=t.groupby(t.size_tier.str[0]).size().to_dict()
summary['tier_counts_compatible']=t[t.all_scores_compatible].groupby(t[t.all_scores_compatible].size_tier.str[0]).size().to_dict()
summary['paper_sha256']=hashlib.sha256((a.project/'paper/main.pdf').read_bytes()).hexdigest()
summary['plan_unchanged']=not bool(subprocess.check_output(['git','-C',str(a.project),'diff','0969d41','HEAD','--','analysis_plan','scripts/stage2_measures.py','outputs/stage3/split_labels.csv'],text=True))
summary['stage3_confirmatory_unchanged']=not bool(subprocess.check_output(['git','-C',str(a.project),'diff','787131f','HEAD','--','outputs/stage3/results_confirmatory.csv'],text=True))
(a.out/'followup_checks.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
