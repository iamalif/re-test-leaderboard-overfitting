"""EXPLORATORY review: numerical checks, provenance, and denominator discrepancy inventory."""
import argparse, json, sys, hashlib, subprocess, math
from pathlib import Path
import numpy as np, pandas as pd, pyarrow.parquet as pq
from scipy.stats import binomtest, mannwhitneyu
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.path.insert(0,str(a.project/'scripts'))
from stage2_measures import exact_pvalues

test=[]
for npub,npriv in [(3,4),(7,5),(12,9)]:
    for kp in range(npub+1):
        for kq in range(npriv+1):
            N=npub+npriv; m=kp+kq; delta=abs(kp*npriv-kq*npub)
            num=sum(math.comb(m,j)*math.comb(N-m,npub-j) for j in range(max(0,npub-(N-m)),min(npub,m)+1) if abs(j*N-m*npub)>=delta)
            brute=num/math.comb(N,npub)
            test.append(abs(brute-exact_pvalues([kp/npub],[kq/npriv],npub,npriv)[0]))
stats={'exact_tail_cases':len(test),'exact_tail_max_error':max(test)}
m=pd.read_csv(a.project/'outputs/stage3/competition_measures.csv');d=m[m.excluded.isna()]; e=d[d.Cohort=='E'];o=d[d.Cohort=='O']
tests=[]
for group,col in [('Accuracy','mean_gap'),('AUC','mean_gap'),('FIVE','rel_drift')]:
    sel=lambda x:x[x.Group.isin(['Accuracy','AUC','MAP@K','LogLoss','MulticlassLoss'])] if group=='FIVE' else x[x.Group==group]
    x,y=sel(e)[col].dropna(),sel(o)[col].dropna()
    tests.append({'group':group,'p':mannwhitneyu(x,y).pvalue,'n_E':len(x),'n_O':len(y),'diff_medians':x.median()-y.median()})
v=e.drift_mean.dropna();tests.append({'group':'H2','p':binomtest(int((v>0).sum()),int((v!=0).sum())).pvalue,'n_E':len(v)})
order=np.argsort([t['p'] for t in tests]); run=0
for rank,idx in enumerate(order):run=max(run,min(1,(4-rank)*tests[idx]['p']));tests[idx]['holm']=run
stats['independent_tests']=tests
stats['drift_by_metric']=e.groupby('Group').drift_mean.agg(n='count',positive=lambda v:int((v>0).sum())).to_dict('index')
stats['noncommunity_auc_counts']={'E':int(((e.Group=='AUC')&(e.Segment!='Community')).sum()),'total_E':int((e.Group=='AUC').sum())}
sizes=pd.read_csv(a.project/'outputs/stage2/pilot_original_inferred_sizes.csv')
dis=sizes[sizes.paper_pub.notna()&((sizes.paper_pub!=sizes.inferred_pub)|(sizes.paper_priv!=sizes.inferred_priv))].copy()
for idx,r in dis.iterrows():
    g=pq.read_table(a.project/'outputs/stage3/analysis_submissions.parquet',filters=[('CompetitionId','=',r.CompetitionId)]).to_pandas()
    for side,col in [('pub','pub'),('priv','priv')]:
        dis.loc[idx,'published_'+side+'_fit']=float((abs(g[col]*r['paper_'+side]-np.rint(g[col]*r['paper_'+side]))<1e-4).mean())
dis.to_csv(a.out/'original_11_size_disagreements.csv',index=False)
allstate=pd.read_csv(a.project/'data/reference/test_v2.csv',usecols=['customer_ID'])
stats['allstate']={'rows':len(allstate),'customers':allstate.customer_ID.nunique(),'missing':int(allstate.customer_ID.isna().sum())}
stats['size_multiplier_note']='Exploratory non-identifiability illustration only; multiplying source-verified counts is not a plausible alternative for those contests.'
# Execute only the confirmatory section of the supplied script, redirecting its sole write.
# This checks exact bootstrap reproduction, separately from the tests above.
src=(a.project/'scripts/stage3_tests.py').read_text().split('# descriptive companions')[0]
src=src.replace('"outputs/stage3/competition_measures.csv"',repr(str((a.project/'outputs/stage3/competition_measures.csv').resolve())))
src=src.replace('"outputs/stage3/results_confirmatory.csv"',repr(str((a.out/'confirmatory_recomputed.csv').resolve())))
exec(compile(src,'stage3_confirmatory_redirected','exec'),{})
orig=pd.read_csv(a.project/'outputs/stage3/results_confirmatory.csv');re=pd.read_csv(a.out/'confirmatory_recomputed.csv')
cols=orig.select_dtypes(include='number').columns
stats['bootstrap_table_max_absolute_difference']=float((orig[cols]-re[cols]).abs().max().max())
stats['hashes']={}
for line in (a.project/'analysis_plan/SHA256SUMS.txt').read_text().splitlines():
    expected,path=line.split(maxsplit=1);actual=hashlib.sha256((a.project/path).read_bytes()).hexdigest();stats['hashes'][path]=(expected==actual)
stats['plan_diff_from_initial_commit']=subprocess.check_output(['git','-C',str(a.project),'diff','0969d41','HEAD','--','analysis_plan','scripts/stage2_measures.py','outputs/stage3/split_labels.csv'],text=True)
(a.out/'additional_checks.json').write_text(json.dumps(stats,indent=2,default=int))
print(json.dumps(stats,indent=2,default=int))
