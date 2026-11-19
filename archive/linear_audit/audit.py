from pathlib import Path
import numpy as np, pandas as pd, json
P=Path(__file__).resolve().parent; R=P.parent
sums=np.zeros(4); count=0; positive=0
for p in sorted((R/'geo_check/unpacked/outputs/Global_nightlight_20260928/global_segment_cache').glob('batch_*.npz')):
 with np.load(p) as z:
  L=z['length_km']; Q=z['aadt_median']; F=np.clip(z['positive_fraction'],0,1)
  W=L*F
  sums+= [L.sum(), W.sum(),np.dot(L,Q),np.dot(W,Q)]
  count+=len(Q);positive+=np.count_nonzero(W)
L,W,LQ,WQ=sums
rat=WQ/LQ
eta=144.8/239.4;ret=.8;h=.5
annual_L=(365*h*LQ)/3.6e15
annual_W=(365*h*WQ)/3.6e15
results=pd.read_csv(R/'duarte_unilateral/ISO_A-H_contact_results.csv').set_index('iso').loc[list('ABCDEFGH')]
rows=[]
for iso,row in results.iterrows():
 g=row.ratio_tau25
 rows.append(dict(ISO=iso,roughness_ratio=g,
  network_mechanical_trial_TWh=annual_L*20*239.4*g,candidate_mechanical_trial_TWh=annual_W*20*239.4*g,
  network_mechanical_loadstroke_TWh=annual_L*40*98.1*g,candidate_mechanical_loadstroke_TWh=annual_W*40*98.1*g,
  candidate_electric_trial_TWh=annual_W*20*144.8*ret*g,
  candidate_electric_loadstroke_TWh_common_eta=annual_W*40*98.1*eta*ret*g))
data=pd.DataFrame(rows)
data.to_csv(P/'supply_domain_audit.csv',index=False,float_format='%.12g')
ladder=json.loads((R/'esi_update/power_ladder/power_ladder.json').read_text())
assert np.isclose(W,ladder['road_km'])
bench=[]
for k,label in [(0,'Radar electronics'),(2,'Monitoring package'),(4,'Local lighting package'),(6,'20 lamps/km')]:
 item=ladder['scenarios'][k];demand=item['annual_kWh_per_km']*W/1e9
 bench.append(dict(label=label,power_W_per_km=item['power_W_per_km'],electric_demand_TWh=demand,mechanical_equivalent_TWh=demand/(eta*ret)))
pd.DataFrame(bench).to_csv(P/'demand_domain_audit.csv',index=False,float_format='%.12g')
audit=dict(records=count,positive_weight_records=int(positive),total_road_km=L,candidate_weighted_km=W,
 total_length_weighted_AADT=LQ/L,candidate_weighted_AADT=WQ/W,
 traffic_weighted_candidate_supply_share=rat,
 all_road_trial_pair_count=20*L,candidate_equivalent_trial_pair_count=20*W,
 candidate_equivalent_loading_row_count=40*W,
 all_road_trial_A_TWh=annual_L*20*239.4,
 candidate_trial_A_mechanical_TWh=annual_W*20*239.4,
 candidate_trial_A_load_electric_TWh=annual_W*20*144.8*ret,
 trial_A_supply_kWh_per_candidate_km_year=annual_W*20*144.8*ret*1e9/W,
 h=h,eta_me=eta,retention=ret)
(P/'audit.json').write_text(json.dumps(audit,indent=2))
print(json.dumps(audit,indent=2))
print(data.round(3).to_string(index=False))
