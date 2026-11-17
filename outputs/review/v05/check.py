from pathlib import Path
import numpy as np,pandas as pd,json,re
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting')
m=pd.read_csv(p/'outputs/stage3/competition_measures.csv');m=m[m.excluded.fillna('')==''].sort_values('CompetitionId')
meta=pd.read_csv(p/'data/raw/Competitions.csv',usecols=['Id','Slug','OrganizationId'],dtype=str).rename(columns={'Id':'CompetitionId'});meta.CompetitionId=meta.CompetitionId.astype(int)
m=m.merge(meta,on='CompetitionId')
m['cluster']=m.apply(lambda r: 'org:'+r.OrganizationId if pd.notna(r.OrganizationId) else 'slug:'+'-'.join([t for t in re.sub(r'\d','',r.Slug.lower()).split('-') if t][:2]),axis=1)
a=pd.read_csv(p/'outputs/stage6/competition_clusters.csv')
res={'cluster_count':m.cluster.nunique(),'cluster_mapping_matches':bool((m.set_index('CompetitionId').cluster.sort_index()==a.set_index('CompetitionId').cluster.sort_index()).all())}
rng=np.random.default_rng(20261117);out=[]
for col,gr,scale in [('mean_gap',['Accuracy'],100),('mean_gap',['AUC'],1),('rel_drift',['Accuracy','AUC','MAP@K','LogLoss','MulticlassLoss'],1)]:
 d=m[m.Group.isin(gr)&m.Cohort.isin(['O','E'])&m[col].notna()]
 groups=[(g[col].to_numpy(),g.Cohort.to_numpy()) for _,g in d.groupby('cluster')]; vals=[]
 for _ in range(4000):
  ix=rng.integers(0,len(groups),len(groups));v=np.concatenate([groups[i][0] for i in ix]);c=np.concatenate([groups[i][1] for i in ix]);vals.append((np.median(v[c=='E'])-np.median(v[c=='O']))*scale)
 out.append(np.percentile(vals,[2.5,97.5]).tolist())
d=m[(m.Cohort=='E')&m.drift_mean.notna()]; groups=[g.drift_mean.to_numpy() for _,g in d.groupby('cluster')]; vals=[]
for _ in range(4000):
 ix=rng.integers(0,len(groups),len(groups));vals.append((np.concatenate([groups[i] for i in ix])>0).mean())
out.append(np.percentile(vals,[2.5,97.5]).tolist());res['bootstrap_intervals']=out
old=pd.read_csv(p/'outputs/stage6/dependence_and_strata.csv').iloc[:4][['ci_lo','ci_hi']].to_numpy();res['bootstrap_max_abs_difference']=float(np.abs(old-np.array(out)).max())
tails=pd.read_csv(p/'outputs/stage6/h1_tail_summary.csv');errs=[]
for r in tails.itertuples():
 v=m[(m.Group==r.metric)&(m.Cohort==r.cohort)].mean_gap*(100 if r.metric=='Accuracy' else 1)
 if r.gap=='absolute':v=v.abs()
 errs.extend(abs(v.quantile(q/100)-getattr(r,'p'+str(q))) for q in [10,25,50,75,90])
res['tail_max_abs_difference']=float(max(errs))
print(json.dumps(res,indent=2));Path(__file__).with_name('results.json').write_text(json.dumps(res,indent=2))
