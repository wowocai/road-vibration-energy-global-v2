from pathlib import Path
import numpy as np,pandas as pd,json
P=Path(__file__).resolve().parent;R=P.parent;D=P/'data';D.mkdir(exist_ok=True)
factors=pd.read_csv(D/'ISO_A_H_response_factors.csv')
qq=[];ww=[];records=0
for f in sorted((R/'geo_check/unpacked/outputs/Global_nightlight_20260928/global_segment_cache').glob('batch_*.npz')):
 with np.load(f) as z:
  records+=len(z['length_km']);w=z['length_km']*np.clip(z['positive_fraction'],0,1);ok=w>0;qq.append(z['aadt_median'][ok]);ww.append(w[ok])
q=np.concatenate(qq);w=np.concatenate(ww);ix=np.argsort(q);q=q[ix];w=w[ix];cw=np.r_[0,np.cumsum(w)];total=cw[-1]
lamp=179.01140330823847;power=np.geomspace(.12,20*lamp/8.76,7);power[4]=lamp/8.76
names=['1 radar electronic unit/km','3 radars + 1 basic weather node/km','1 radar + 1 heated weather node/km','1 weather monitoring node/km','1 lamp/km','Budget supporting 5 lamps/km','20 lamps/km']
grid=np.arange(0,420.00001,.25);rows=[];anchors=[]
for f in factors.itertuples():
 for n in [1,20]:
  coef=365*n*.5*.8*144.8*f.roughness_ratio/3.6e6
  def coverage(p):
   j=np.searchsorted(q,p*8.76/coef,side='left');return 100*(total-cw[j])/total
  values=coverage(grid)
  assert (np.diff(values)<=1e-8).all() and np.isclose(values[0],100)
  for p,c in zip(grid,values):rows.append(dict(ISO=f.ISO,pairs_per_km=n,power_W_per_km=p,annual_balance_weighted_road_pct=c))
  for k,(p,name) in enumerate(zip(power,names)):
   anchors.append(dict(ISO=f.ISO,pairs_per_km=n,load_level=k+1,power_W_per_km=p,device_configuration=name,annual_balance_weighted_road_pct=float(coverage(p))))
t=pd.DataFrame(rows);a=pd.DataFrame(anchors);t.to_csv(D/'coverage_uniform_power_grid.csv',index=False,float_format='%.12g');a.to_csv(D/'coverage_device_markers.csv',index=False,float_format='%.12g')
old=pd.read_csv(R/'ah_coverage_linear/data/ISO_A_H_load_coverage.csv')
assert np.allclose(a.annual_balance_weighted_road_pct,old.weighted_road_length_at_annual_balance_pct,atol=1e-8)
meta=dict(power_min=0,power_max=420,power_step=.25,grid_levels=len(grid),ISO_classes=8,densities=[1,20],grid_cases=len(t),device_marker_cases=len(a),source_records=records,candidate_weighted_km=total,method='Direct weighted AADT threshold on sorted road records; no spline smoothing')
(D/'calculation_summary.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
