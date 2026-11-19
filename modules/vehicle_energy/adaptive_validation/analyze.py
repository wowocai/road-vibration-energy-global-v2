from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import t
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
ETA=144.8/239.4*.8
rows=[]
for folder in ['runs','diagnostic_runs']:
 for f in (P/folder).glob('*.json'):
  z=json.loads(f.read_text())
  for r in z['cases']:rows.append(dict(batch=z['name'],**r))
d=pd.DataFrame(rows)
for c in ['plate_J','extra_wheel_J','suspension_change_J','terminal_change_J','balance_paired_J']:
 d[c+'_per_km']=d[c]/(d.length_m/1000)
d['delivered_J_per_km']=ETA*d.plate_J_per_km
d.to_csv(O/'all_cases.csv',index=False)
measures=['plate_J_per_km','extra_wheel_J_per_km','suspension_change_J_per_km','terminal_change_J_per_km','delivered_J_per_km','off_fraction','reference_off_fraction','peak_tire_force_N','balance_paired_J_per_km','peak_suspension_travel_m']
keys=['batch','seed','ISO','stroke_m','rtol','maxdt','warm_m','length_m','speed_kmh']
z=d.groupby(keys,dropna=False)[measures].mean().reset_index()
z.to_csv(O/'independent_seed_means.csv',index=False)
def agg(df,by):
 out=[]
 for k,g in df.groupby(by,dropna=False):
  if not isinstance(k,tuple):k=(k,)
  r=dict(zip(by,k));n=len(g);r['independent_seeds']=n
  for col in measures:
   a=g[col].dropna();N=len(a);mean=a.mean();se=a.std(ddof=1)/np.sqrt(N) if N>1 else np.nan;ci=t.ppf(.975,N-1)*se if N>1 else np.nan
   r.update({col:mean,col+'_CI95_half':ci})
  out.append(r)
 return pd.DataFrame(out)
# Group by batch name but diagnostic batch names contain seed: strip seed.
z['experiment']=z.batch.str.replace(r'_[0-9]{4}_','_',regex=True)
s=agg(z,['experiment','ISO','stroke_m','rtol','warm_m','length_m','speed_kmh'])
s.to_csv(O/'validation_summary.csv',index=False)
main=pd.concat([z[z.batch=='reference'],z[(z.batch=='ensemble')&(z.seed<3165)]])
a=agg(main,['ISO','stroke_m']);a.to_csv(O/'A_H_energy_summary.csv',index=False)
cs=[]
for h,g in z[(z.batch=='ensemble')&(z.seed<3165)].groupby('stroke_m'):
 for n in [8,16,32,64,128]:
  g=g.sort_values('seed')
  if len(g)<n:continue
  c=agg(g.iloc[:n],['ISO','stroke_m']);c['first_n_seeds']=n;cs.append(c)
if cs:pd.concat(cs).to_csv(O/'H_sample_convergence.csv',index=False)
print(a[['ISO','stroke_m','independent_seeds','extra_wheel_J_per_km','extra_wheel_J_per_km_CI95_half','delivered_J_per_km']].round(3).to_string(index=False))
