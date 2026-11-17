"""EXPLORATORY v0.3 review, 2026-11-17. New outputs only; no research script execution."""
import argparse,sys,os,json,subprocess,hashlib
from pathlib import Path
import pandas as pd
from scipy.stats import binomtest
ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out=a.out.resolve();a.out.mkdir(parents=True,exist_ok=True)
m=pd.read_csv(a.project/'outputs/stage3/competition_measures.csv');m=m[m.excluded.fillna('')=='']
m=m.merge(pd.read_csv(a.project/'outputs/stage1/cohort_per_competition.csv')[['CompetitionId','LeaderboardPercentage']],on='CompetitionId')
m=m.merge(pd.read_csv(a.project/'outputs/stage6/verify_review_numbers.csv')[['CompetitionId','drift_raw']],on='CompetitionId')
m['band']=pd.cut(m.LeaderboardPercentage,[0,39,49,50,99],labels=['under40','40to49','50','over50'])
rows=[]
for cohort in ['O','E','W','O+E','O+E+W']:
 x=m if cohort=='O+E+W' else m[m.Cohort.isin(list(cohort.replace('+','')))]
 for kind,y,col in [('all',x,'drift_mean'),('raw3',x[x.Group.isin(['Accuracy','AUC','MAP@K'])],'drift_raw')]:
  for band,z in y.groupby('band',observed=True):
   v=z[col].dropna();v=v[v!=0];pos=int((v>0).sum());rows.append(dict(cohort=cohort,metrics=kind,band=band,n=len(v),positive=pos,share=pos/len(v),reference_sign_p=binomtest(pos,len(v)).pvalue))
pd.DataFrame(rows).to_csv(a.out/'corrected_split_share_table.csv',index=False)
acc=m[m.Cohort.isin(['O','E'])&m.Group.eq('Accuracy')&m.LeaderboardPercentage.eq(50)].copy()
acc['minimum_sizes_equal']=acc.n_pub.eq(acc.n_priv)
acc[['CompetitionId','Cohort','LeaderboardPercentage','n_pub','n_priv','fit_pub','fit_priv','minimum_sizes_equal','drift_raw']].to_csv(a.out/'nominal_50_accuracy_sizes.csv',index=False)
summary={'head':subprocess.check_output(['git','-C',str(a.project),'rev-parse','HEAD'],text=True).strip(),'nominal50_accuracy_n':len(acc),'unequal_minimum_sizes':int((~acc.minimum_sizes_equal).sum()),'simulation_134_of_300_p':binomtest(134,300).pvalue}
# Harmless dummy interpreter tests the actual runner's control flow; no analysis scripts run.
stub=a.out/'mock_interpreter.sh';marker=a.out/'mock_marker'
stub.write_text('''#!/bin/bash
if [[ "$1" == "scripts/stage3_extension.py" ]]; then
 case "$REVIEW_MODE" in
 fail) echo 'mock fatal error' >&2; exit 7 ;;
 missing) echo 'unexpected successful exit'; exit 0 ;;
 pause) if [[ ! -f "$REVIEW_MARKER" ]]; then touch "$REVIEW_MARKER"; echo 'PAUSED: mock'; exit 0; fi ;;
 esac
 echo 'DONE mock'
fi
exit 0
''');stub.chmod(0o755)
probes=[]
for mode,expected in [('fail',7),('missing',1),('pause',0),('done',0)]:
 marker.unlink(missing_ok=True);env=os.environ.copy();env.update(PY=str(stub),REVIEW_MODE=mode,REVIEW_MARKER=str(marker))
 r=subprocess.run(['bash','run_all.sh'],cwd=a.project,env=env,capture_output=True,text=True,timeout=10)
 probes.append(dict(mode=mode,expected=expected,actual=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==expected
summary['runner_probes']=probes
summary['preserved_plan_and_measures']=not bool(subprocess.check_output(['git','-C',str(a.project),'diff','0969d41','HEAD','--','analysis_plan','scripts/stage2_measures.py','outputs/stage3/split_labels.csv'],text=True))
summary['confirmatory_results_preserved']=not bool(subprocess.check_output(['git','-C',str(a.project),'diff','787131f','HEAD','--','outputs/stage3/results_confirmatory.csv'],text=True))
summary['hashes']={p:hashlib.sha256((a.project/p).read_bytes()).hexdigest() for p in ['paper/main.pdf','scripts/stage6_split_size_symmetry.py','run_all.sh']}
(a.out/'v03_checks.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
