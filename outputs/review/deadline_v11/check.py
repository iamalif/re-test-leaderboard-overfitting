import sys,json
from pathlib import Path
import pandas as pd
sys.path.insert(0,'/Users/alif/Base/Projects/re-test-leaderboard-overfitting/scripts')
from stage7_deadline_contrast import team_windows,competition_row,sign_summary
rows=[]
for t in range(40):
 for k in range(19):
  priv=.5+k/1024
  gap=(2048*k-k**3)/1048576
  rows.append(dict(TeamId=t,Id=t*100+k,day=pd.Timestamp('2020-01-01')+pd.Timedelta(days=k),pub=priv+gap,priv=priv,k=k))
d=pd.DataFrame(rows)
r=competition_row(team_windows(d[d.k<16],d[d.k>=16],True))
res={'trajectory':'private=0.5+k/1024; gap=(2048*k-k^3)/1048576; deadline between k=15 and16', 'result':r,'X_test':sign_summary('X',[r['X']]*20),'Y_test':sign_summary('Y',[r['Y']]*20)}
try:
 team_windows(d[d.k<16],d[d.k>=16],True,w=6)
 res['empty_eligible_check']='passed'
except Exception as e:res['empty_eligible_check']=repr(e)
print(json.dumps(res,indent=2))
Path(__file__).with_name('results.json').write_text(json.dumps(res,indent=2))
