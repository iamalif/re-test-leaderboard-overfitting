import sys,importlib.util,io,json,hashlib
from pathlib import Path
import pandas as pd
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');sys.path.insert(0,str(p/'scripts'))
import compare_outputs as c
from csvio import read_csv_exact
r={'cells':{},'reader':{},'ledgers':{}}
for a,b in [('0.0499999999999','0.0500000000001'),('10.0','10.000000001'),('1e-400','2e-400'),('NA','NULL'),('1e-14','-1e-14')]:r['cells'][a+' => '+b]=c.cell_match(a,b)
for name,s in {'uint64':'x\n9223372036854775808\n','missing_large':'x,y\n9007199254740993,a\n,b\n','underscore':'x\n1_000\n','leadingzero':'x\n001\n','date':'x\n2026-11-17\n','inf':'x\ninf\n'}.items():
 rr={}
 for label,fn in [('exact',read_csv_exact),('pandas',pd.read_csv)]:
  try:
   d=fn(io.StringIO(s));rr[label]={'dtype':str(d.x.dtype),'values':[str(v) for v in d.x]}
  except Exception as e:rr[label]=repr(e)
 r['reader'][name]=rr
for f in (p/'outputs/rebuild').glob('ledger_final*.jsonl'):
 rows=[json.loads(x) for x in f.read_text().splitlines()];bad=[]
 for x in rows:
  if hashlib.sha256((p/'scripts'/x['stage']).read_bytes()).hexdigest()!=x['script_sha256']:bad.append(x['stage'])
 r['ledgers'][f.name]={'stages':len(rows),'exits':[x['exit'] for x in rows],'current_script_hash_mismatch':bad,'first':rows[0]['start_utc'],'last':rows[-1]['end_utc']}
r['tolerance_tables']=pd.read_csv(p/'outputs/rebuild/final_py312_vs_final_py314_2026-11-17.csv').sort_values('cells_within_tolerance',ascending=False)[['table','cells_within_tolerance']].head(8).to_dict('records')
Path(__file__).with_name('results.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
