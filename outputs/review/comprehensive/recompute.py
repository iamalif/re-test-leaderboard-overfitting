from pathlib import Path
import pandas as pd,numpy as np,pyarrow.parquet as pq,json,hashlib
from scipy.stats import mannwhitneyu,binomtest,hypergeom
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');out=Path(__file__).parent
m=pd.read_csv(p/'outputs/stage3/competition_measures.csv',float_precision='round_trip').set_index('CompetitionId');rows=[]
def calc(cid,g):
 r=m.loc[cid];rawident=float((g.pub==g.priv).mean());n=len(g)
 if n<1000:rows.append(dict(CompetitionId=cid,n=n,raw_identical=rawident));return
 if r.Group not in ['Accuracy','AUC','MAP@K']:
  lo,hi=g.pub.quantile([.01,.99]);g=g.assign(pub=g.pub.clip(lo,hi),priv=g.priv.clip(lo,hi))
 gap=(g.pub-g.priv)*(1 if r.higher_better else -1);g=g.assign(gap=gap).sort_values(['TeamId','day','Id'])
 ix=g.groupby('TeamId').cumcount();cnt=g.groupby('TeamId').Id.transform('size');half=cnt//2
 early=g[(cnt>=4)&(ix<half)].groupby('TeamId').gap.mean();late=g[(cnt>=4)&(ix>=cnt-half)].groupby('TeamId').gap.mean();drift=(late-early).mean()
 rows.append(dict(CompetitionId=cid,n=n,raw_identical=rawident,clipped_identical=float((g.pub==g.priv).mean()),mean_gap=gap.mean(),drift_mean=drift))
cur=None;parts=[]
for b in pq.ParquetFile(p/'outputs/stage3/analysis_submissions.parquet').iter_batches(batch_size=250000):
 d=b.to_pandas()
 for cid,g in d.groupby('CompetitionId',sort=False):
  if cur is not None and cid!=cur:calc(cur,pd.concat(parts,ignore_index=True));parts=[]
  cur=cid;parts.append(g)
if parts:calc(cur,pd.concat(parts,ignore_index=True))
z=pd.DataFrame(rows).set_index('CompetitionId');z.to_csv(out/'recomputed_measures.csv');res={'competitions':len(z),'submissions':int(z.n.sum()),'mismatches':{}}
for col in ['mean_gap','drift_mean']:
 a,b=z[col],m.loc[z.index,col];mask=~np.isclose(a,b,rtol=1e-10,atol=1e-12,equal_nan=True);res['mismatches'][col]=z.index[mask].tolist()
res['exclusion_raw_vs_clip']=z[(z.raw_identical>=.99)!=(z.clipped_identical>=.99)].index.tolist()
d=m[m.excluded.fillna('')==''];e=d[d.Cohort=='E'];o=d[d.Cohort=='O']
ps=[]
for group in ['Accuracy','AUC']:ps.append(float(mannwhitneyu(e[e.Group==group].mean_gap,o[o.Group==group].mean_gap).pvalue))
v=e.drift_mean.dropna();ps.append(float(binomtest(int((v>0).sum()),int((v!=0).sum())).pvalue));five=['Accuracy','AUC','MAP@K','LogLoss','MulticlassLoss'];ps.append(float(mannwhitneyu(e[e.Group.isin(five)].rel_drift.dropna(),o[o.Group.isin(five)].rel_drift.dropna()).pvalue))
res['confirmatory_raw_p']=ps
res['cohorts']=d.Cohort.value_counts().to_dict();res['later_accuracy_post2022']=int(((e.Group=='Accuracy')&(e.DeadlineYear>2022)).sum());res['zero_drifts']=int((v==0).sum())
res['archived_hashes']={}
for l in (p/'analysis_plan/SHA256SUMS.txt').read_text().splitlines():
 h,f=l.split(None,1);res['archived_hashes'][f]=hashlib.sha256((p/f).read_bytes()).hexdigest()==h
(out/'recompute_summary.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
