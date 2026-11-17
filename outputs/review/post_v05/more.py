from pathlib import Path
import pandas as pd,numpy as np,subprocess,io,json,zipfile,re,ast
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');out=Path(__file__).parent;r={}
for file in ['outputs/stage3/results_confirmatory.csv','outputs/stage2/pilot_original_drift_tests.csv','outputs/stage1/replication_summary.csv','outputs/stage2/pilot_original_measures.csv','outputs/stage2/pilot_original_inferred_sizes.csv']:
 old=subprocess.check_output(['git','show','f96fd05:'+file],cwd=p)
 a=pd.read_csv(io.BytesIO(old),float_precision='round_trip');b=pd.read_csv(p/file,float_precision='round_trip')
 diff={}
 for col in a.columns:
  if pd.api.types.is_numeric_dtype(a[col]) and pd.api.types.is_numeric_dtype(b[col]):
   mask=~np.isclose(a[col],b[col],rtol=1e-9,atol=1e-12,equal_nan=True)
   if mask.any():diff[col]={'rows':int(mask.sum()),'ids':b.loc[mask,'CompetitionId'].tolist() if 'CompetitionId' in b else b.index[mask].tolist(),'old':a.loc[mask,col].tolist(),'new':b.loc[mask,col].tolist()}
 r[file]=diff
f=p/'outputs/stage3/competition_measures.csv';a=pd.read_csv(f);b=pd.read_csv(f,float_precision='round_trip');r['current_default_vs_roundtrip_signchanges']={col:int(((np.sign(a[col])!=np.sign(b[col]))&a[col].notna()&b[col].notna()).sum()) for col in ['drift_mean','rel_drift','mean_gap']}
a=pd.read_csv(p/'superseded/outputs_before_single_run/competition_measures.csv',float_precision='round_trip').set_index('CompetitionId').sort_index();b=b.set_index('CompetitionId').sort_index();r['stage3_beyond_tolerance']={}
for col in a:
 if pd.api.types.is_numeric_dtype(a[col]) and pd.api.types.is_numeric_dtype(b[col]):
  mask=~np.isclose(a[col],b[col],rtol=1e-9,atol=1e-12,equal_nan=True)
  if mask.any():r['stage3_beyond_tolerance'][col]=int(mask.sum())
# parse conversion without running script
src=ast.parse((p/'scripts/stage1_reproduce.py').read_text());fn=next(n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='exact_scores');ns={'SCORE_TEXT':{'PublicScoreFullPrecision':str}};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<function>','exec'),ns)
v=['',' ','1e-3','nan',' NaN ',' 0.25 ','inf','-inf',np.nan]
r['converter_formats']=[str(x) for x in ns['exact_scores'](pd.DataFrame({'PublicScoreFullPrecision':v})).PublicScoreFullPrecision]
# metadata and identity scan
z=zipfile.ZipFile(p/'anonymous_review_package.zip');hits={};metadata={}
from pypdf import PdfReader
from PIL import Image
for n in z.namelist():
 data=z.read(n)
 if n.endswith('.pdf'):
  rd=PdfReader(io.BytesIO(data));metadata[n]=dict(rd.metadata or {})
 elif n.endswith('.png'):metadata[n]=Image.open(io.BytesIO(data)).info
 try:s=data.decode()
 except UnicodeDecodeError:continue
 hit=re.findall(r'iamalif|re-test-leaderboard-overfitting|/Users/|/sessions/|Al Amin|@gmail',s,re.I)
 if hit:hits[n]=sorted(set(hit))
r['identity_hits']=hits;r['image_pdf_metadata']=metadata
(out/'more_results.json').write_text(json.dumps(r,indent=2,default=str));print(json.dumps({k:v for k,v in r.items() if k!='image_pdf_metadata'},indent=2,default=str))
