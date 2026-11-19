from pathlib import Path
import argparse,json,hashlib
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=P.parent.parent/'data/road_batches');ap.add_argument('--figure-data',type=Path,default=P/'input_data');ap.add_argument('--out',type=Path,default=P/'out');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
keys=['row_id','country','road_type','length_km','positive_fraction','outside_fraction','aadt_median','aadt_q05','aadt_q95'];parts={k:[] for k in keys};hs=hashlib.sha256();nb=0
for f in sorted(a.cache.glob('batch_*.npz')):
 hs.update(f.name.encode());hs.update(hashlib.sha256(f.read_bytes()).digest());nb+=1
 with np.load(f) as z:
  for k in keys:parts[k].append(z[k])
d={k:np.concatenate(v) for k,v in parts.items()};L=d['length_km'];p=d['positive_fraction'];o=d['outside_fraction'];n=len(L)
assert n==3293705 and len(np.unique(d['row_id']))==n
assert all(np.isfinite(d[k]).all() for k in keys)
assert (L>0).all() and (p>=-1e-12).all() and (p<=1+1e-12).all() and (o>=-1e-12).all() and (p+o<=1+1e-10).all()
p=np.clip(p,0,1);o=np.clip(o,0,1)
for k in ['aadt_median','aadt_q05','aadt_q95']:assert (d[k]>=0).all()
assert (d['aadt_q05']<=d['aadt_median']+1e-8).all() and (d['aadt_median']<=d['aadt_q95']+1e-8).all()
# Complements in the pre-existing cache, not a validated streetlight inventory.
weights={'positive_radiance':L*p,'nonpositive_in_bounds':L*np.maximum(0,1-p-o),'outside_raster':L*o}
valid=L*(1-o)
# Whole-record definitions provide sensitivity to mixed lit/dark records.
weights.update({'whole_record_no_positive':np.where((p==0)&(o==0),L,0),'whole_record_positive_le10pct':np.where((p<=.1)&(o==0),L,0),'whole_record_all_positive':np.where((p>=1-1e-10)&(o==0),L,0),'whole_record_positive_ge90pct':np.where((p>=.9)&(o==0),L,0)})
assert np.allclose(weights['positive_radiance']+weights['nonpositive_in_bounds'],valid,atol=1e-10)
factors=pd.read_csv(a.figure_data/'ISO_A_H_response_factors.csv');anchors=pd.read_csv(a.figure_data/'coverage_device_markers.csv');loads=anchors[(anchors.ISO=='A')&(anchors.pairs_per_km==1)].sort_values('load_level')
# Export strict-dark records for independently checking selected cross counts.
sel=weights['whole_record_no_positive']>0
rec=pd.DataFrame({k:v[sel] for k,v in d.items()})
basecoef=365*.5*.8*144.8/3.6e6
for name,nrow,annual in [('radar_1pair',1,.12*8.76),('lamp_20pairs',20,179.01140330823847),('20lamps_20pairs',20,20*179.01140330823847)]:
 rec['ISO_A_balance_'+name]=rec.aadt_median*basecoef*nrow>=annual
rec.to_csv(a.out/'strict_dark_records.csv.gz',index=False,compression='gzip')
# Text labels do not alter any approved numerical load budget.
rows=[];national=[];repro=[]
for traffic in ['median','q05','q95']:
 q=d['aadt_'+traffic];idx=np.argsort(q);qs=q[idx]
 group_arrays={name:np.r_[0,np.cumsum(w[idx])] for name,w in weights.items()}
 for fac in factors.itertuples():
  for density in [1,20]:
   coef=365*density*.5*.8*144.8*fac.roughness_ratio/3.6e6
   for load in loads.itertuples():
    demand=load.power_W_per_km*8.76;threshold=demand/coef;cut=np.searchsorted(qs,threshold,side='left')
    for group,cw in group_arrays.items():
     total=float(cw[-1]);balanced=float(cw[-1]-cw[cut]);pct=100*balanced/total if total else np.nan
     rows.append(dict(traffic=traffic,ISO=fac.ISO,pairs_per_km=density,load_level=load.load_level,power_W_per_km=load.power_W_per_km,device_configuration=load.device_configuration,nightlight_group=group,total_weighted_length_km=total,balanced_weighted_length_km=balanced,annual_balance_length_pct=pct,threshold_aadt=threshold,output_J_pair_interacting_vehicle=144.8*fac.roughness_ratio,interaction_fraction=.5,downstream_retention=.8,demand_kWh_per_km_year=demand))
     if traffic=='median' and group=='positive_radiance':
      old=anchors[(anchors.ISO==fac.ISO)&(anchors.pairs_per_km==density)&(anchors.load_level==load.load_level)].iloc[0]
      assert np.isclose(pct,old.annual_balance_weighted_road_pct,atol=1e-8),(fac.ISO,density,load.load_level,pct,old.annual_balance_weighted_road_pct)
      repro.append(abs(pct-old.annual_balance_weighted_road_pct))
    if traffic=='median' and fac.ISO=='A' and load.load_level in [1,5,7]:
     hit=q>=threshold
     frame=pd.DataFrame({'country_numeric':d['country']})
     for name in ['positive_radiance','nonpositive_in_bounds','whole_record_no_positive','whole_record_all_positive']:
      frame[name+'_km']=weights[name];frame[name+'_balanced_km']=np.where(hit,weights[name],0)
     frame=frame.groupby('country_numeric',as_index=False).sum();frame['pairs_per_km']=density;frame['load_level']=load.load_level;frame['power_W_per_km']=load.power_W_per_km
     national.append(frame)
t=pd.DataFrame(rows);t.to_csv(a.out/'cross_statistics_all_scenarios.csv',index=False)
pd.concat(national,ignore_index=True).to_csv(a.out/'national_ISO_A_overlap.csv',index=False)
main=t[(t.traffic=='median')&(t.ISO=='A')&(t.nightlight_group=='nonpositive_in_bounds')];main.to_csv(a.out/'ISO_A_dark_domain_summary.csv',index=False)
meta=dict(source_archive='道路振动能论文_数据与代码.zip',figure_source='Road_energy_9panels_source_package.zip version 5',batches=nb,cache_sha256=hs.hexdigest(),records=n,road_length_km=float(L.sum()),in_bounds_length_km=float(valid.sum()),positive_radiance_km=float(weights['positive_radiance'].sum()),nonpositive_in_bounds_km=float(weights['nonpositive_in_bounds'].sum()),outside_raster_km=float(weights['outside_raster'].sum()),nightlight_year=2021,traffic_year=2015,group_totals_km={k:float(v.sum()) for k,v in weights.items()},group_nonzero_record_counts={k:int((v>0).sum()) for k,v in weights.items()},comparisons=len(rows),reproduced_figure_cases=len(repro),max_reproduction_error_pct=max(repro),interpretation='Existing masked-radiance cache split, NOT independently verified streetlighting, grid access, normative lighting need or unpaved-road status. Fractions become equivalent weighted lengths, not exact geolocated subsegment boundaries. Uniform ISO scenarios are assumptions, not measured per-road roughness.',outside_policy='Exclude outside-raster samples from nonpositive/light-absent denominator.',sensitivity='q05 and q95 are source traffic prediction scenarios; whole-record groups check mixed-radiance classification. Neither is a joint confidence interval.')
(a.out/'audit.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
print(json.dumps(meta,indent=2,ensure_ascii=False))
print(main[['pairs_per_km','load_level','power_W_per_km','balanced_weighted_length_km','annual_balance_length_pct','threshold_aadt']].to_string(index=False))
print('Positive and dark one-lamp:')
print(t[(t.traffic=='median')&(t.load_level==5)&(t.nightlight_group.isin(['positive_radiance','nonpositive_in_bounds']))][['ISO','pairs_per_km','nightlight_group','balanced_weighted_length_km','annual_balance_length_pct']].to_string(index=False))
