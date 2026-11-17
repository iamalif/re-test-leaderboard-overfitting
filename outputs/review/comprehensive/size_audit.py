from pathlib import Path
import pandas as pd,numpy as np,pyarrow.dataset as ds,json,sys
from scipy.stats import hypergeom
p=Path('/Users/alif/Base/Projects/re-test-leaderboard-overfitting');out=Path(__file__).parent
m=pd.read_csv(p/'outputs/stage3/competition_measures.csv',float_precision='round_trip');a=m[(m.Group=='Accuracy') & m.p05_all.notna()];data=ds.dataset(p/'outputs/stage3/analysis_submissions.parquet',format='parquet');rows=[]
for r in a.itertuples():
 g=data.to_table(filter=ds.field('CompetitionId')==r.CompetitionId,columns=['pub','priv','TeamId','Id','day']).to_pandas();npub,npriv=int(r.n_pub),int(r.n_priv);kp=np.rint(g.pub.to_numpy()*npub).astype('int64');kq=np.rint(g.priv.to_numpy()*npriv).astype('int64');N=npub+npriv;m=kp+kq
 # independent public-count version, instead of production private-count formula
 delta=np.abs(kp*N-m*npub);low=(m*npub-delta)//N;high=(m*npub+delta+N-1)//N
 prob=np.minimum(1.,hypergeom.cdf(low,N,m,npub)+hypergeom.sf(high-1,N,m,npub));g['pcheck']=prob
 first=g.sort_values(['day','Id']).drop_duplicates('TeamId');v=float((first.pcheck<=.05).mean())
 rows.append({'CompetitionId':r.CompetitionId,'p05_first_check':v,'p05_first_saved':r.p05_first,'difference':v-r.p05_first,'max_count_residual':float(max(np.abs(g.pub*npub-kp).max(),np.abs(g.priv*npriv-kq).max()))})
x=pd.DataFrame(rows);x.to_csv(out/'formal_accuracy_check.csv',index=False);print('accuracy competitions',len(x),'max fraction difference',x.difference.abs().max(),'max lattice residual',x.max_count_residual.max())
