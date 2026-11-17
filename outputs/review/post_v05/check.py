import sys,importlib.util,json,subprocess,io,zipfile,hashlib
from pathlib import Path
import pandas as pd,numpy as np
root=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');out=Path(__file__).parent
sp=importlib.util.spec_from_file_location('cmp',root/'scripts/compare_outputs.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
r={'environment':{'python':sys.version,'pandas':pd.__version__},'fixtures':{}}
fixtures={
'id_changed':('CompetitionId,value\n1000000000,0.5\n','CompetitionId,value\n1000000001,0.5\n'),
'sign_flip':('CompetitionId,drift_mean\n1,1e-14\n','CompetitionId,drift_mean\n1,-1e-14\n'),
'NA_text':('CompetitionId,label\n1,NA\n','CompetitionId,label\n1,NULL\n'),
'leading_zero_text':('CompetitionId,label\n1,001\n2,word\n','CompetitionId,label\n1,1\n2,word\n'),
'bool_flip':('CompetitionId,flagged\n1,True\n','CompetitionId,flagged\n1,False\n')}
for name,(a,b) in fixtures.items():
 (out/'a.csv').write_text(a);(out/'b.csv').write_text(b);r['fixtures'][name]=c.compare_tables(out/'a.csv',out/'b.csv')
for d in ['ref/stage1','new/stage1']:(out/d).mkdir(parents=True,exist_ok=True)
(out/'ref/stage1/original_team_flags.csv').write_text('TeamId,IsBenchmark\n1,True\n')
(out/'new/stage1/original_team_flags.csv').write_text('TeamId,IsBenchmark\n1,False\n')
r['corrupt_known_exception_exit']=c.run(str(out/'ref'),str(out/'new'))
a=pd.read_csv(root/'superseded/outputs_before_single_run/competition_measures.csv',float_precision='round_trip');b=pd.read_csv(root/'outputs/stage3/competition_measures.csv',float_precision='round_trip')
a=a.set_index('CompetitionId').sort_index();b=b.set_index('CompetitionId').sort_index();diff={}
for col in a:
 x,y=a[col],b[col];same=(x==y)|(x.isna()&y.isna())
 if not same.all():
  z={'rows':int((~same).sum())}
  if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):z['maxdiff']=float((x-y).abs().max());z['sign_changes']=int(((np.sign(x)!=np.sign(y))&x.notna()&y.notna()).sum())
  diff[col]=z
r['stage3_exact_differences']=diff
z=zipfile.ZipFile(root/'anonymous_review_package.zip');r['zip_mode']=oct(z.getinfo('run_all.sh').external_attr>>16);r['zip_files']=len(z.namelist());r['manifest_bad']=[]
for line in z.read('MANIFEST_SHA256.txt').decode().splitlines():
 h,n=line.split('  ',1)
 if hashlib.sha256(z.read(n)).hexdigest()!=h:r['manifest_bad'].append(n)
(out/'results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
