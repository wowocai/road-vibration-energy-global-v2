from pathlib import Path
import pandas as pd,numpy as np,json
from scipy.stats import t
P=Path(__file__).resolve().parent
rows=[]
for f in (P/'reference_runs').glob('*.json'):
 for z in json.loads(f.read_text())['cases']:
  assert z['status']=='completed',(f,z['status'])
  rows.append(z)
r=pd.DataFrame(rows)
assert len(r)==672,len(r)
raw=r.copy();raw.to_csv(P/'figure/data/repaired_A_G_raw.csv',index=False)
cols={'net_wheel_J':'extra_wheel_J_per_km','plate_J':'plate_J_per_km'}
result=[]
for (iso,h),g in r.groupby(['ISO','stroke_m']):
 paired=g.groupby('seed')[list(cols)].mean();assert len(paired)==16 and len(g)==32
 out={'ISO':iso,'stroke_m':h,'speed_kmh':g.speed_kmh.iloc[0],'n_seeds':len(paired)}
 for c,k in cols.items():
  out[k]=paired[c].mean();out[k+'_CI95_half']=paired[c].std(ddof=1)/np.sqrt(len(paired))*t.ppf(.975,len(paired)-1)
 factor=144.8/239.4*.8
 out['delivered_J_per_km']=out['plate_J_per_km']*factor;out['delivered_J_per_km_CI95_half']=out['plate_J_per_km_CI95_half']*factor
 out['max_abs_balance_J_km']=g.balance_paired_J.abs().max()
 result.append(out)
h=pd.read_csv(P/'H_validation/out/summary.csv');h=h[h.batch=='ensemble_2'];assert len(h)==3
for _,z in h.iterrows():
 out={'ISO':'H','stroke_m':z.stroke_m,'speed_kmh':2,'n_seeds':int(z.total_seeds)}
 for c,k in [('net_wheel','extra_wheel'),('plate','plate'),('electric','delivered')]:
  out[k+'_J_per_km']=z[c+'_J_km'];out[k+'_J_per_km_CI95_half']=z[c+'_J_km_half95']
 result.append(out)
s=pd.DataFrame(result).sort_values(['ISO','stroke_m']);s.to_csv(P/'figure/data/current_joint_scenarios.csv',index=False)
print(s[['ISO','stroke_m','speed_kmh','extra_wheel_J_per_km','delivered_J_per_km']].to_string(index=False))
