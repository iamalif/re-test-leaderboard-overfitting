"""Original 120 competitions only. Never analyze scores from the extension sample.
Run: python3 scripts/stage1_reproduce.py --project /path/to/project
Requires pandas, numpy, matplotlib. Manifest transcribed from published appendix.
"""
import argparse,json,platform
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--from-cache',action='store_true');a=p.parse_args()
root=a.project; out=a.output or root/'outputs'/'stage1';out.mkdir(parents=True,exist_ok=True)
manifest=pd.read_csv(root/'data'/'reference'/'original_120_manifest.csv').set_index('CompetitionId')
assert len(manifest)==120 and manifest.index.is_unique
if a.from_cache:
 d=pd.read_csv(out/'original_predeadline_submissions.csv.gz')
 assert set(d.CompetitionId)<=set(manifest.index)
else:
 teams=[]
 for c in pd.read_csv(root/'data/raw/Teams.csv',usecols=['Id','CompetitionId'],chunksize=200000):
  teams.append(c[c.CompetitionId.isin(manifest.index)])
 teams=pd.concat(teams).set_index('Id').CompetitionId
 parts=[]
 cols=['Id','TeamId','SubmissionDate','IsAfterDeadline','PublicScoreFullPrecision','PrivateScoreFullPrecision']
 for i,c in enumerate(pd.read_csv(root/'data/raw/Submissions.csv',usecols=cols,chunksize=250000)):
  # Filter by published competition IDs before converting or comparing scores.
  c=c[c.TeamId.isin(teams.index)].copy()
  c['CompetitionId']=c.TeamId.map(teams)
  c=c[c.IsAfterDeadline.astype(str).str.lower()=='false']
  parts.append(c)
  if i%10==0: print('Read submission chunk',i,flush=True)
 d=pd.concat(parts,ignore_index=True)
 assert set(d.CompetitionId)<=set(manifest.index)
 d.to_csv(out/'original_predeadline_submissions.csv.gz',index=False)
summary=[]
fig,axes=plt.subplots(1,5,figsize=(16,3.5))
for cid,m in manifest.iterrows():
 g=d[d.CompetitionId==cid].copy(); npre=len(g)
 for col in ['PublicScoreFullPrecision','PrivateScoreFullPrecision']:g[col]=pd.to_numeric(g[col],errors='coerce')
 valid=np.isfinite(g.PublicScoreFullPrecision)&np.isfinite(g.PrivateScoreFullPrecision)
 g=g[valid].copy(); high=m.PaperMetric not in ['LogLoss','MulticlassLoss'];sign=1 if high else -1
 g['gap']=sign*(g.PublicScoreFullPrecision-g.PrivateScoreFullPrecision)
 top=g.sort_values(['PublicScoreFullPrecision','Id'],ascending=[not high,True]).head(int(np.ceil(.1*len(g))))
 summary.append(dict(CompetitionId=cid,Metric=m.PaperMetric,paper_n=m.PaperSubmissions,current_pre=npre,valid_n=len(g),excluded_nonfinite=npre-len(g),mean_gap=g.gap.mean(),top10_mean_gap=top.gap.mean(),top10_n=len(top)))
 if True:
  fig2,axs=plt.subplots(1,2,figsize=(9,4))
  for ax,s,label in zip(axs,[g,top],['All submissions','Top 10%']):
   ax.scatter(s.PublicScoreFullPrecision,s.PrivateScoreFullPrecision,s=2,alpha=.25)
   lo=min(s.PublicScoreFullPrecision.min(),s.PrivateScoreFullPrecision.min());hi=max(s.PublicScoreFullPrecision.max(),s.PrivateScoreFullPrecision.max())
   ax.plot([lo,hi],[lo,hi],color='black',lw=.7,label='Equal scores')
   if s.PublicScoreFullPrecision.nunique()>1:
    slope,intercept=np.polyfit(s.PublicScoreFullPrecision,s.PrivateScoreFullPrecision,1);ax.plot([lo,hi],intercept+slope*np.array([lo,hi]),color='red',lw=.8,label='Linear fit')
   ax.set(xlabel='Public score',ylabel='Private score',title=label);ax.legend(fontsize=7)
  fig2.suptitle(f'{cid}: {str(m.PaperName).replace(chr(8413), '')}',fontsize=10);fig2.tight_layout();fig2.savefig(out/f'{m.PaperMetric}_{cid}.png',dpi=120);plt.close(fig2)
s=pd.DataFrame(summary);s.to_csv(out/'replication_summary.csv',index=False)
for ax,(metric,g) in zip(axes,s.groupby('Metric',sort=True)):
 vals=np.sort(g.mean_gap);ax.step(vals,np.arange(1,len(vals)+1)/len(vals),where='post');ax.axvline(0,color='gray',lw=.7);ax.set(title=f'{metric} (n={len(g)})',xlabel='Mean degradation',ylabel='Fraction of competitions')
fig.tight_layout();fig.savefig(out/'mean_gap_distributions.png',dpi=160);plt.close(fig)
json.dump({'python':platform.python_version(),'pandas':pd.__version__,'numpy':np.__version__,'matplotlib':matplotlib.__version__,'scope':'Published 120 IDs only','first_submission_rule':'Earliest recorded date, ties by submission ID; date-only records do not independently verify within-day order','top10_rule':'ceil(0.1*n); public score sorted, ties by submission ID; paper tie rule unspecified','pvalues':'Not computed pending denominator and inequality audit'},open(out/'run_metadata.json','w'),indent=2)
print(s[s.Metric=='Accuracy'].sort_values('mean_gap',ascending=False).head(8).to_string(index=False))

# Exact finite-population tail calculation, separately preserving > and >=.
from scipy.stats import hypergeom
from fractions import Fraction
from collections import Counter
import scipy

def tails(npub,npriv,kpub,kpriv):
 kp=np.asarray(kpub,dtype=np.int64);kq=np.asarray(kpriv,dtype=np.int64)
 N=npub+npriv;m=kp+kq;center=m*npriv;delta=np.abs(kq*N-center)
 lower=(center-delta)//N;upper=-(-(center+delta)//N)
 inclusive=np.minimum(1.,hypergeom.cdf(lower,N,m,npriv)+hypergeom.sf(upper-1,N,m,npriv))
 lower_strict=-(-(center-delta)//N)-1;upper_strict=(center+delta)//N+1
 strict=np.minimum(1.,hypergeom.cdf(lower_strict,N,m,npriv)+hypergeom.sf(upper_strict-1,N,m,npriv))
 return inclusive,strict

# Independently enumerate small finite populations to validate both tail boundaries.
checks=0
for npub in range(1,6):
 for npriv in range(1,6):
  N=npub+npriv
  for kp in range(npub+1):
   for kq in range(npriv+1):
    m=kp+kq;ks=np.arange(max(0,m-npub),min(npriv,m)+1)
    distances=np.abs(ks*N-m*npriv);observed=abs(kq*N-m*npriv)
    mass=hypergeom.pmf(ks,N,m,npriv);pg,ps=tails(npub,npriv,kp,kq)
    assert np.isclose(pg,mass[distances>=observed].sum(),atol=1e-12)
    assert np.isclose(ps,mass[distances>observed].sum(),atol=1e-12)
    checks+=1

audit=[];pstats=[];candidates=[];pframes=[]
for cid,m in manifest[manifest.PaperMetric=='Accuracy'].iterrows():
 g=d[d.CompetitionId==cid].copy();row={'CompetitionId':cid,'n':len(g)};consistent=True;sizes=[]
 for side in ['Public','Private']:
  size=m['Paper'+side+'Size'];vals=g[side+'ScoreFullPrecision'].to_numpy()
  if pd.isna(size):consistent=False;row[side+'_status']='missing';sizes.append(None);continue
  size=int(size);sizes.append(size);err=np.abs(vals*size-np.rint(vals*size));good=np.isfinite(vals)&(vals>=0)&(vals<=1)&(err<1e-4)
  row[side+'_size']=size;row[side+'_consistent_fraction']=good.mean();row[side+'_inconsistent_n']=int((~good).sum())
  if not good.all():
   consistent=False;unique=np.unique(vals[np.isfinite(vals)])
   counts=Counter(Fraction(float(v)).limit_denominator(10000000).denominator for v in unique[:1000])
   for candidate in sorted(set([size-1,size+1]+[v for v,n in counts.most_common(4)])):
    if candidate>0:candidates.append({'CompetitionId':cid,'side':side,'candidate_denominator':candidate,'fraction_consistent':float((np.abs(unique*candidate-np.rint(unique*candidate))<1e-4).mean()),'status':'Arithmetic diagnostic only; not verified test size'})
 row['status']='consistent_with_published_sizes' if consistent else 'needs_source_verification';audit.append(row)
 if not consistent:continue
 npub,npriv=sizes;kp=np.rint(g.PublicScoreFullPrecision*npub).astype('int64');kq=np.rint(g.PrivateScoreFullPrecision*npriv).astype('int64')
 g['p_inclusive'],g['p_strict']=tails(npub,npriv,kp,kq)
 g['parsed_date']=pd.to_datetime(g.SubmissionDate,format='mixed',dayfirst=False,errors='raise')
 top=g.sort_values(['PublicScoreFullPrecision','Id'],ascending=[False,True]).head(int(np.ceil(.1*len(g))))
 first=g.sort_values(['parsed_date','Id']).drop_duplicates('TeamId',keep='first')
 fig,ax=plt.subplots(figsize=(5,4))
 for label,group in [('All',g),('Top 10%',top),('First per team',first)]:
  values=np.sort(group.p_inclusive);ax.step(values,np.arange(1,len(values)+1)/len(values),where='post',label=label)
  pstats.append({'CompetitionId':cid,'subset':label,'n':len(group),'fraction_p_le_005':float((group.p_inclusive<=.05).mean()),'max_inclusive_strict_difference':float((group.p_inclusive-group.p_strict).max())})
 ax.plot([0,1],[0,1],'k--',lw=.8);ax.set(xlim=(0,1),ylim=(0,1),xlabel='Inclusive exact p-value',ylabel='Empirical CDF',title=f'{cid}: published sizes {npub}/{npriv}');ax.legend();fig.tight_layout();fig.savefig(out/f'pvalues_{cid}.png',dpi=140);plt.close(fig)
 pframes.append(g[['CompetitionId','Id','p_inclusive','p_strict']])
pd.DataFrame(audit).to_csv(out/'denominator_audit.csv',index=False)
pd.DataFrame(candidates).to_csv(out/'denominator_candidates_UNVERIFIED.csv',index=False)
pd.DataFrame(pstats).to_csv(out/'pvalue_summary.csv',index=False)
pd.concat(pframes).to_csv(out/'original_pvalues_consistent_sizes.csv.gz',index=False)
metadata=json.load(open(out/'run_metadata.json'));metadata.update(scipy=scipy.__version__,pvalues='Exact inclusive and strict hypergeometric tails only for competitions with all scores consistent with appendix sizes; consistency is not independent proof of size',tail_enumeration_checks=checks,pvalue_competitions=len(pframes))
json.dump(metadata,open(out/'run_metadata.json','w'),indent=2)
print('Exact-tail validation cases:',checks,'; p-value competitions:',len(pframes),flush=True)
# Metadata-only cohort reconciliation; no extension scores are read here.
current=pd.read_csv(root/'outputs/stage0_per_competition.csv')
joined=manifest.reset_index().merge(current,on='CompetitionId',how='left',validate='one_to_one')
joined['PairedCountDifference']=joined.n_pre_both-joined.PaperSubmissions
joined.to_csv(out/'original_sample_audit.csv',index=False)
current['Deadline']=pd.to_datetime(current.Deadline)
cohorts=[]
for label,mask in [('2019 onward excluding published IDs',current.Deadline.ge('2019-01-01')&~current.CompetitionId.isin(manifest.index)),('2020 onward',current.Deadline.ge('2020-01-01'))]:
 eligible=current[mask&current.n_pre_both.ge(1000)];interior=eligible[eligible.LeaderboardPercentage.between(1,99)]
 cohorts.append({'candidate_definition':label,'paired_eligible':len(eligible),'interior_reported_split':len(interior),'accuracy_interior':int(interior.Metric.eq('CategorizationAccuracy').sum()),'status':'Provisional metadata-only sensitivity; not fixed extension inclusion rule'})
pd.DataFrame(cohorts).to_csv(out/'candidate_cohort_counts.csv',index=False)
# Preserve source and input fingerprints plus the executing script fingerprint.
import hashlib
fingerprints={}
for file in [root/'data/raw'/name for name in ['Competitions.csv','Teams.csv','Submissions.csv']]+[root/'data/reference/original_120_manifest.csv',Path(__file__)]:
 with file.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
 fingerprints[file.name]={'sha256':digest,'bytes':file.stat().st_size}
json.dump(fingerprints,open(out/'input_hashes.json','w'),indent=2)

# Original-sample metadata and tie sensitivity. These are audit outputs, not extensions.
if (out/'original_team_flags.csv').exists():
 teamflags=pd.read_csv(out/'original_team_flags.csv')
else:
 flagparts=[]
 for chunk in pd.read_csv(root/'data/raw/Teams.csv',usecols=['Id','CompetitionId','IsBenchmark'],chunksize=200000):
  flagparts.append(chunk[chunk.CompetitionId.isin(manifest.index)])
 teamflags=pd.concat(flagparts).rename(columns={'Id':'TeamId'})
 teamflags.to_csv(out/'original_team_flags.csv',index=False)
benchmark_ids=set(teamflags.loc[teamflags.IsBenchmark,'TeamId'])
sensitivity=[]
for cid,m in manifest.iterrows():
 g=d[d.CompetitionId==cid].copy();high=m.PaperMetric not in ['LogLoss','MulticlassLoss'];sign=1 if high else -1
 g['gap']=sign*(g.PublicScoreFullPrecision-g.PrivateScoreFullPrecision)
 n=int(np.ceil(.1*len(g)));ordered=g.sort_values(['PublicScoreFullPrecision','Id'],ascending=[not high,True]);threshold=ordered.iloc[n-1].PublicScoreFullPrecision
 better=g[g.PublicScoreFullPrecision>threshold] if high else g[g.PublicScoreFullPrecision<threshold]
 tied=g[g.PublicScoreFullPrecision==threshold];remaining=n-len(better)
 low=(better.gap.sum()+tied.gap.nsmallest(remaining).sum())/n;upper=(better.gap.sum()+tied.gap.nlargest(remaining).sum())/n
 ordinary=g[~g.TeamId.isin(benchmark_ids)]
 sensitivity.append({'CompetitionId':cid,'Metric':m.PaperMetric,'all_mean_gap':g.gap.mean(),'nonbenchmark_mean_gap':ordinary.gap.mean(),'benchmark_submission_n':len(g)-len(ordinary),'top10_gap_tie_min':low,'top10_gap_tie_max':upper,'top10_tie_bound_width':upper-low})
pd.DataFrame(sensitivity).to_csv(out/'benchmark_and_tie_sensitivity.csv',index=False)

pv=pd.read_csv(out/'original_pvalues_consistent_sizes.csv.gz')
joined=d.merge(pv,on=['CompetitionId','Id'],validate='one_to_one')
order=[]
for cid,g in joined.groupby('CompetitionId'):
 g=g.copy();g['day']=pd.to_datetime(g.SubmissionDate,format='%m/%d/%Y')
 earliest=g[g.day==g.groupby('TeamId').day.transform('min')]
 by_team=earliest.groupby('TeamId').agg(n=('Id','size'),p_min=('p_inclusive','min'),p_max=('p_inclusive','max'))
 order.append({'CompetitionId':cid,'teams':len(by_team),'teams_multiple_firstday':int((by_team.n>1).sum()),'fraction_first_p_le005_min':float((by_team.p_max<=.05).mean()),'fraction_first_p_le005_max':float((by_team.p_min<=.05).mean()),'all_fraction_inclusive_le005':float((g.p_inclusive<=.05).mean()),'all_fraction_strict_le005':float((g.p_strict<=.05).mean())})
pd.DataFrame(order).to_csv(out/'first_day_and_pvalue_sensitivity.csv',index=False)

# Synthetic no-adaptation check, entirely separate from Kaggle outcomes.
rng=np.random.default_rng(2019);nmodels=100000;npub=npriv=100
kp=rng.binomial(npub,.7,nmodels);kq=rng.binomial(npriv,.7,nmodels)
pge,pgt=tails(npub,npriv,kp,kq);selected=np.argsort(-kp,kind='stable')[:nmodels//10]
nullrows=[]
for label,index in [('all_fixed_models',np.arange(nmodels)),('top10_by_public',selected)]:
 nullrows.append({'subset':label,'n':len(index),'fraction_inclusive_p_le005':float(np.mean(pge[index]<=.05)),'fraction_strict_p_le005':float(np.mean(pgt[index]<=.05)),'mean_public_minus_private':float(np.mean(kp[index]/npub-kq[index]/npriv))})
json.dump({'seed':2019,'population_accuracy':.7,'public_n':100,'private_n':100,'adaptation':False,'results':nullrows,'interpretation':'Synthetic method diagnostic only; no inference about observed Kaggle adaptation'},open(out/'synthetic_selection_check.json','w'),indent=2)
# Source-supported denominator reconstruction for an original competition only.
# This is a conditional sensitivity analysis, kept separate from verified-size outputs.
g=d[d.CompetitionId==3788].copy();npub,npriv=16714,39002
assert npub+npriv==55716
for column,size in [('PublicScoreFullPrecision',npub),('PrivateScoreFullPrecision',npriv)]:
 assert np.max(np.abs(g[column]*size-np.rint(g[column]*size)))<1e-4
g['p'],g['p_strict']=tails(npub,npriv,np.rint(g.PublicScoreFullPrecision*npub),np.rint(g.PrivateScoreFullPrecision*npriv))
g['day']=pd.to_datetime(g.SubmissionDate,format='%m/%d/%Y');sizerows=[]
for label,subset in [('all',g),('top10',g.sort_values(['PublicScoreFullPrecision','Id'],ascending=[False,True]).head(int(np.ceil(.1*len(g))))),('first',g.sort_values(['day','Id']).drop_duplicates('TeamId'))]:
 sizerows.append({'subset':label,'n':len(subset),'fraction_inclusive_p_le005':float((subset.p<=.05).mean())})
json.dump({'status':'Conditional sensitivity using reconstructed denominators; original test file verification pending','public_n':npub,'private_n':npriv,'total_n_source':'https://speakerdeck.com/justmarkham/allstate-purchase-prediction-challenge-on-kaggle slide 7','derivation':'Reduced observed score fractions include 8991/16714 and 20777/39002. Assuming 55716 distinct equally weighted scored customers and disjoint exhaustive splits, the denominators must be these values. All current original-sample scores fit.','results':sizerows},open(out/'allstate_reconstructed_size_sensitivity.json','w'),indent=2)

# Optional independent source-file verification for the Allstate scoring unit.
from scipy.stats import norm
if (root/'data/reference/test_v2.csv').exists():
 p=root/'data/reference/test_v2.csv';test=pd.read_csv(p,usecols=['customer_ID']);N=test.customer_ID.nunique();assert len(test)==198856 and N==55716 and test.customer_ID.notna().all()
 d=pd.read_csv(out/'original_predeadline_submissions.csv.gz');g=d[d.CompetitionId==3788].copy();g['day']=pd.to_datetime(g.SubmissionDate,format='%m/%d/%Y')
 npub,npriv=16714,39002;assert npub+npriv==N
 kp=np.rint(g.PublicScoreFullPrecision*npub);kq=np.rint(g.PrivateScoreFullPrecision*npriv)
 assert (np.abs(kp-g.PublicScoreFullPrecision*npub)<1e-4).all() and (np.abs(kq-g.PrivateScoreFullPrecision*npriv)<1e-4).all()
 g['exact_customer_p'],_=tails(npub,npriv,kp,kq)
 for label,pub,priv in [('normal_customer',npub,npriv),('normal_table',59657,139199)]:
  pooled=(g.PublicScoreFullPrecision*pub+g.PrivateScoreFullPrecision*priv)/(pub+priv);se=np.sqrt(pooled*(1-pooled)*(1/pub+1/priv))
  z=np.divide(abs(g.PublicScoreFullPrecision-g.PrivateScoreFullPrecision),se,out=np.zeros(len(g)),where=se.to_numpy()>0)
  g[label+'_p']=2*norm.sf(z)
 fig,axes=plt.subplots(1,3,figsize=(13,4));rows=[]
 subsets=[('All submissions',g),('Top 10%',g.sort_values(['PublicScoreFullPrecision','Id'],ascending=[False,True]).head(int(np.ceil(len(g)*.1)))),('First per team',g.sort_values(['day','Id']).drop_duplicates('TeamId'))]
 for ax,(name,s) in zip(axes,subsets):
  row={'subset':name,'n':len(s)}
  for col,title,color in [('exact_customer_p','Customer counts: exact','#176c86'),('normal_customer_p','Customer counts: normal','#58a789'),('normal_table_p','Table row counts: normal diagnostic','#be6842')]:
   vals=np.sort(s[col]);ax.step(vals,np.arange(1,len(vals)+1)/len(vals),where='post',label=title,color=color,lw=1.2);row[col+'_fraction_le005']=float((s[col]<=.05).mean())
  ax.plot([0,1],[0,1],'k:',lw=.6);ax.set(xlim=(0,1),ylim=(0,1),title=name,xlabel='Tail probability',ylabel='Fraction of submissions');rows.append(row)
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=8)
 fig.suptitle('Allstate: counting customers versus quote-history rows',fontsize=14);fig.tight_layout(rect=[0,.08,1,.94]);fig.savefig(out/'allstate_scoring_unit_sensitivity.png',dpi=160);plt.close(fig)
 with p.open('rb') as h:digest=hashlib.file_digest(h,'sha256').hexdigest()
 result={'test_file_sha256':digest,'test_rows':len(test),'unique_customers':N,'paper_total':59657+139199,'reconstructed_public':npub,'reconstructed_private':npriv,'assumptions':['ordinary equally weighted customer accuracy','disjoint public/private scored customer subsets','score values accurately represented to tolerance'],'status':'Total customers verified from downloaded test file; split counts algebraically reconstructed, not directly read from a released split manifest','normal_diagnostic':'Normal pooled-variance approximation is a sensitivity diagnostic, not a reconstruction of the original Stirling implementation','rows':rows}
 (out/'allstate_file_verification.json').write_text(json.dumps(result,indent=2))
