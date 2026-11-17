from pathlib import Path
import sys,json,zipfile,hashlib,io,re
import numpy as np,pandas as pd
from scipy.stats import hypergeom
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');sys.path.insert(0,str(p/'scripts'))
from stage2_measures import exact_pvalues,infer_denominator
out=Path(__file__).parent;r={};err=0;cases=0
for npub in range(1,8):
 for npriv in range(1,8):
  for kp in range(npub+1):
   for kq in range(npriv+1):
    obs=abs(kp*npriv-kq*npub);m=kp+kq;N=npub+npriv
    truth=sum(hypergeom.pmf(k,N,m,npub) for k in range(max(0,m-npriv),min(npub,m)+1) if abs(k*N-m*npub)>=obs)
    got=exact_pvalues([kp/npub],[kq/npriv],npub,npriv)[0];err=max(err,abs(got-truth));cases+=1
r['hypergeom_cases']=cases;r['max_error']=err
N=10**12+1;s=np.arange(20)*(N//100)/N;r['rounded_lattice_example']={'true_N':N,'inferred':infer_denominator(s),'multiple':N%100==0}
z=zipfile.ZipFile(p/'anonymous_review_package.zip');r['zip_files']=len(z.namelist());r['zip_sha256']=hashlib.sha256((p/'anonymous_review_package.zip').read_bytes()).hexdigest();bad=[];hits=[]
for l in z.read('MANIFEST_SHA256.txt').decode().splitlines():
 h,n=l.split('  ',1)
 if hashlib.sha256(z.read(n)).hexdigest()!=h:bad.append(n)
for n in z.namelist():
 try:t=z.read(n).decode()
 except UnicodeDecodeError:continue
 if re.search(r'iamalif|re-test-leaderboard-overfitting|/Users/alif|/sessions/',t,re.I):hits.append(n)
r['zip_hash_failures']=bad;r['targeted_identity_hits']=hits
s=pd.read_csv(p/'outputs/stage3/results_secondary.csv');r['S1_denominators']=s[(s.analysis=='S1') & s.measure.isin(['drift_mean','rel_drift','rel_mean_gap'])][['group','measure','n','share_positive']].to_dict('records')
r['secondary_rows']=len(s);r['spearman_missing_CIs']=int((s.group.str.contains('Spearman')&s.ci_lo.isna()).sum())
(out/'extra_summary.json').write_text(json.dumps(r,indent=2,default=str));print(json.dumps({k:v for k,v in r.items() if k!='S1_denominators'},indent=2,default=str))
