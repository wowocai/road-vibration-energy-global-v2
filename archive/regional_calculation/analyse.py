from pathlib import Path
import pandas as pd,numpy as np,json
from scipy.stats import spearmanr
root=Path('geo_check/unpacked'); out=Path('regional_calculation')
d=pd.DataFrame(json.load(open(root/'inputs/national/vkt_candidate_inputs.json')))
t=pd.read_csv(root/'outputs/Vehicle_resource_reproduction_20261022/country_traffic_reconstructed.csv');t=t[t.feature_set=='retained_ten']
u=json.load(open(root/'outputs/Vehicle_resource_reproduction_20261022/RESULTS.json'))['main_units_J_km'];u['Freight']=(u['Freight']+u['Passenger'])/2
p=t.pivot(index='country',columns='category',values='annual_VKT_million_km');q=d.set_index('Country').join(p)
for c in ['Passenger','Bus','Freight']:q[c+'_B_TWh']=q[c]*1e6*u[c]/16/3.6e15
q['B_TWh']=q[[c+'_B_TWh' for c in ['Passenger','Bus','Freight']]].sum(axis=1)
q['VKT']=q[['Passenger','Bus','Freight']].sum(axis=1)
q['J_per_vehicle_km']=q.B_TWh*3.6e15/(q.VKT*1e6)
q['Freight_energy_percent']=q.Freight_B_TWh/q.B_TWh*100
q['Passenger_energy_percent']=q.Passenger_B_TWh/q.B_TWh*100
q['road_km']=q['Total Road Network - All Road Types - Total (km)']
q['B_kWh_per_road_km']=q.B_TWh*1e9/q.road_km
q['vehicle_km_per_road_km']=q.VKT*1e6/q.road_km
q['global_energy_percent']=q.B_TWh/q.B_TWh.sum()*100
ref=pd.read_csv('geo_check/figures/figures/source_data/Figure2_country_ISO.csv');ref=ref[ref.ISO=='B'].set_index('country_code')
j=q.set_index('Country Code')[['B_TWh']].join(ref.suspension_TWh_year).dropna();err=(j.B_TWh-j.suspension_TWh_year).abs().max()
q.sort_values('B_TWh',ascending=False).to_csv(out/'country_decomposition.csv',encoding='utf-8-sig')
valid=q[(q.road_km>0)&(q.B_TWh>0)&(q.VKT>0)].copy();valid.sort_values('B_kWh_per_road_km',ascending=False).to_csv(out/'road_intensity_available.csv',encoding='utf-8-sig')
print('max difference Fig2',err,'valid road',len(valid),'coverage',valid.B_TWh.sum()/q.B_TWh.sum())
cols=['B_TWh','B_kWh_per_road_km','vehicle_km_per_road_km','J_per_vehicle_km','Freight_energy_percent','Passenger_energy_percent']
names=['United States','China','Brazil','Japan','Korea, Rep.','Germany','France','Italy','United Kingdom','China, Hong Kong','Switzerland']
print(q.loc[names,cols].round(3).to_string())
print('intensity leaders\n',valid.sort_values('B_kWh_per_road_km',ascending=False)[cols].head(12).round(3).to_string())
summary={'max_abs_difference_Figure2_TWh':err,'road_available_n':len(valid),'road_available_energy_share':valid.B_TWh.sum()/q.B_TWh.sum(),'correlations':{}}
for x,y,label in [('VKT','B_TWh','total_vs_VKT'),('road_km','B_TWh','total_vs_road'),('vehicle_km_per_road_km','B_kWh_per_road_km','intensity_vs_activity_density'),('J_per_vehicle_km','B_kWh_per_road_km','intensity_vs_mix')]:
 z=q[[x,y]].replace([np.inf,-np.inf],np.nan).dropna();z=z[(z[x]>0)&(z[y]>0)];s=spearmanr(z[x],z[y]);summary['correlations'][label]={'n':len(z),'rho':s.statistic};print(label,len(z),s.statistic)
json.dump(summary,open(out/'checks.json','w'),indent=2)
