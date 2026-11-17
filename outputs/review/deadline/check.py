import sys, json
from pathlib import Path
import pandas as pd
root=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting')
sys.path.insert(0,str(root/'scripts'))
from stage7_deadline_contrast import team_steps, competition_row
out=[]
for name,npost,plateau in [('linear_one_post',1,False),('linear_four_post',4,False),('linear_eight_post',8,False),('saturating_eight_post',8,True)]:
 rows=[]
 for team in range(40):
  for k in range(16+npost):
   private=.6+.002*k
   gap=.001*(min(k,16) if plateau else k)
   rows.append(dict(TeamId=team,Id=100*team+k,day=pd.Timestamp('2020-01-01')+pd.Timedelta(days=k),pub=private+gap,priv=private,k=k))
 d=pd.DataFrame(rows)
 r=competition_row(team_steps(d[d.k<16],d[d.k>=16],True))
 r['case']=name
 out.append(r)
print(json.dumps(out,indent=2))
Path(__file__).with_name('synthetic_results.json').write_text(json.dumps(out,indent=2))
