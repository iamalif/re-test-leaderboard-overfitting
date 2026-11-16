"""EXPLORATORY independent review, 2026-11-16. Never overwrites recorded results.
Run: python review_checks.py --project PROJECT --out NEW_OUTPUT_DIRECTORY
Uses project measures directly; synthetic examples are falsification examples, not estimates of Kaggle mechanisms.
"""
import argparse, sys, json, hashlib, subprocess, platform
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy.stats import binomtest, mannwhitneyu

ap=argparse.ArgumentParser(); ap.add_argument('--project',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
a.out.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.project/'scripts'))
from stage2_measures import competition_measures, prepare_scores, oriented_gap, infer_denominator, exact_pvalues, null_top_decile_gap

def robustness(g):
    g=g.sort_values(['TeamId','day','Id']).copy(); g['gap']=g.pub-g.priv
    k=g.groupby('TeamId').cumcount(); n=g.groupby('TeamId').Id.transform('size')
    q=4*k//n
    t=g[n>=8].assign(q=q[n>=8]).groupby(['TeamId','q']).gap.mean().unstack()
    late=(t[3]-t[2]).mean()
    h=g[(n>=6)&(k>=2)]; kk=h.groupby('TeamId').cumcount(); nn=h.groupby('TeamId').Id.transform('size'); half=nn//2
    skip=(h[kk>=nn-half].groupby('TeamId').gap.mean()-h[kk<half].groupby('TeamId').gap.mean()).mean()
    h=g[n>=4].copy(); h['pos']=k[n>=4]/(n[n>=4]-1); h['lvl']=(h.pub+h.priv)/2
    X=h[['pos','lvl']]-h.groupby('TeamId')[['pos','lvl']].transform('mean'); y=h.gap-h.groupby('TeamId').gap.transform('mean'); sd=X.std()
    beta=np.linalg.lstsq((X/sd).values,y.values,rcond=None)[0]
    return dict(drift_late=late,drift_skip2=skip,slope_adj=beta[0]/sd.pos)

rng=np.random.default_rng(20261116)
rows=[]
for team in range(100):
    base=rng.uniform(.5,.7)
    for step,t in enumerate(np.linspace(0,1,20)):
        # Fixed learning trajectories, no access to either leaderboard. Both domains improve.
        level=base+.1*t+.1*t*t
        gap=-.001+.002*t
        # Fixed grids of 1 million example thresholds realize these accuracies (nested predictions).
        rows.append((team,team*20+step,np.floor((level+gap/2)*1e6)/1e6,np.floor((level-gap/2)*1e6)/1e6))
g=pd.DataFrame(rows,columns=['TeamId','Id','pub','priv']);g['day']=pd.Timestamp('2000-01-01')
syn={**competition_measures(g,True),**robustness(g)}
pd.DataFrame([syn]).to_csv(a.out/'nonadaptive_counterexample.csv',index=False)

# Integer scores identify a lattice, not its multiplier. Same scores fit actual n=100 or n=10000.
s=np.arange(40,81)/100
den=dict(inferred=infer_denominator(s)[0],fits_n100=bool(np.allclose(s*100,np.rint(s*100))),fits_n10000=bool(np.allclose(s*10000,np.rint(s*10000))))
den['p_for_075_vs_065_n100']=float(exact_pvalues([.75],[.65],100,100)[0])
den['p_for_075_vs_065_n10000']=float(exact_pvalues([.75],[.65],10000,10000)[0])

# Shared-split counterexample: all submissions make identical predictions. Top-decile ties include all.
# With a shared random split its expected gap is zero. Independent re-splits fabricate 1000 candidates.
mu,sd=null_top_decile_gap(np.full(1000,.7),np.full(1000,.7),1000,1000,reps=200,seed=20261116)
den.update(identical_predictions_true_expected_selected_gap=0,independent_null_gap=mu,independent_null_sd=sd)
(a.out/'identification_examples.json').write_text(json.dumps(den,indent=2))

m=pd.read_csv(a.project/'outputs/stage3/competition_measures.csv'); m['excluded']=m.excluded.fillna('')
stats=[]
for r in m.itertuples():
    if r.excluded=='rule3_fewer_than_1000': continue
    g=pq.read_table(a.project/'outputs/stage3/analysis_submissions.parquet',filters=[('CompetitionId','=',r.CompetitionId)]).to_pandas()
    # Scale raw scores to avoid overflow for sentinel magnitudes. Only sign is interpreted here.
    scale=max(float(g.pub.abs().max()),float(g.priv.abs().max()),1)
    raw=competition_measures(g.assign(pub=g.pub/scale,priv=g.priv/scale),r.higher_better)
    row=dict(CompetitionId=r.CompetitionId,Cohort=r.Cohort,Group=r.Group,excluded=r.excluded,recorded_drift=r.drift_mean,
             raw_drift_scaled=raw['drift_mean'],raw_share_identical=float((g.pub==g.priv).mean()),recorded_share_identical=r.share_identical)
    if r.Group=='Accuracy' and not r.excluded and np.isfinite(r.n_pub) and r.fit_pub==1 and r.fit_priv==1 and g.pub.between(0,1).all() and g.priv.between(0,1).all():
        for mult in (1,2,10):
            p=exact_pvalues(g.pub,g.priv,int(r.n_pub)*mult,int(r.n_priv)*mult)
            first=g.sort_values(['day','Id']).drop_duplicates('TeamId').index
            row[f'p05_first_size_x{mult}']=float((p[first]<=.05).mean())
    stats.append(row)
pd.DataFrame(stats).to_csv(a.out/'raw_drift_and_size_sensitivity.csv',index=False)
z=pd.DataFrame(stats); summary={}
for coh in ('O','E'):
    h=z[(z.Cohort==coh)&(z.excluded=='')]
    summary[coh]=dict(raw_positive=int((h.raw_drift_scaled>0).sum()),raw_finite=int(h.raw_drift_scaled.notna().sum()),
        clipped_positive=int((h.recorded_drift>0).sum()),sign_flips=int(((h.raw_drift_scaled>0)!=(h.recorded_drift>0)).sum()),
        accuracy_first_rejection_medians={str(i):float(h[f'p05_first_size_x{i}'].median()) for i in (1,2,10)})
summary['excluded_after_clipping_only']=z[(z.excluded=='rule4_identical_scores')&(z.raw_share_identical<.99)].CompetitionId.tolist()
summary['nonadaptive']=syn
summary['environment']=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__)
summary['git_head']=subprocess.check_output(['git','-C',str(a.project),'rev-parse','HEAD'],text=True).strip()
summary['files']={str(p.relative_to(a.project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [a.project/'paper/main.pdf',a.project/'scripts/stage2_measures.py',a.project/'analysis_plan/stage2_analysis_plan_v1.0.md']}
(a.out/'review_checks_summary.json').write_text(json.dumps(summary,indent=2,default=float))
print(json.dumps(summary,indent=2,default=float))
