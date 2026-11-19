from pathlib import Path
import numpy as np,pandas as pd,subprocess,json,itertools
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
z=np.load(P/'source/Figure5/node20/out/minute_inputs.npz');load=z['load_Wh'];D=load.sum()/1000
profiles={k:z[k+'_Wh'] for k in ['PV','wind','vibration']}
for k,g in profiles.items():np.r_[g,load].astype('float64').tofile(O/(k+'.bin'))
cache={}
def dispatch(k,C):
 key=(k,round(C,8))
 if key not in cache:
  a=list(map(float,subprocess.check_output([str(P/'dispatch'),str(O/(k+'.bin')),str(C)],text=True).strip().split(',')))
  cache[key]=dict(grid_kWh=a[0],local_served_kWh=a[1],spill_kWh=a[2],storage_loss_kWh=a[3],minute_coverage_pct=a[4]*100,soc_start_Wh=a[5],soc_end_Wh=a[6],warm_years=a[7])
  assert abs(a[5]-a[6])<1e-5
  assert abs(profiles[k].sum()/1000-a[1]-a[2]-a[3])<1e-6
 return cache[key]
T=20;r=.05;ann=sum((1+r)**(-t) for t in range(1,T+1))
# Retail references checked 2026-11-13. Analogous equipment costs do NOT validate source-prototype performance or constitute installation quotes.
road_pair=2*174.47+2*142+4*13.99+4*12.75+400+300+200+8*40
pars={'PV':dict(equipment=10*803+20*100+1000,installation=2500,om=300,replace_equipment=0,replace_labor=0,life=10),
 'wind':dict(equipment=20*563.99+20*100+1000,installation=5000,om=.02*(20*563.99+20*100+1000+5000),replace_equipment=20*563.99+20*100+1000,replace_labor=2500,life=10),
 'vibration':dict(equipment=20*road_pair,installation=10000,om=.02*(20*road_pair+10000),replace_equipment=20*road_pair,replace_labor=5000,life=10)}
def cost(k,C,disc=.05,price=.16,b_mult=1,tech_mult=1):
 p=pars[k];A=sum((1+disc)**(-t) for t in range(1,T+1));s=dispatch(k,C)
 n_b=int(np.ceil((C-1e-10)/5.12)) if C else 0
 # Common power-stage cost retained even with no storage. 2 x 5kW quoted units are cost analogues; dispatch cap is conservatively 5kW.
 initial_power=2*699.99
 initial_b=(n_b*1097.99+300+320)*b_mult if C else 0
 battery_om=.01*initial_b*A
 # Explicit pack/electronics replacement at year 10; routine OM excludes that replacement.
 battery_rep=((n_b*1097.99+200)*b_mult/(1+disc)**10) if C else 0
 out=dict(equipment=p['equipment']*tech_mult,installation=p['installation']*tech_mult,maintenance_pv=p['om']*A*tech_mult,replacement_pv=(p['replace_equipment']+p['replace_labor'])/(1+disc)**p['life']*tech_mult,power_stage_initial=initial_power,power_stage_replacement_pv=(initial_power+200)/(1+disc)**10,storage_initial=initial_b,storage_maintenance_pv=battery_om,storage_replacement_pv=battery_rep,backup_electricity_pv=s['grid_kWh']*price*A)
 out['asset_lcc']=sum(v for j,v in out.items() if j!='backup_electricity_pv');out['service_lcc']=sum(v for j,v in out.items() if j not in ['asset_lcc'])
 out['delivered_cost_USD_kWh']=out['service_lcc']/(D*A)
 return out
caps=[0,.1,.25,.5,1,2,5,5.12,10,10.24,15.36,20.48,51.2,102.4,204.8]
rows=[]
for k in profiles:
 for C in caps:rows.append(dict(source=k,capacity_kWh=C,**dispatch(k,C),**cost(k,C)))
df=pd.DataFrame(rows);df.to_csv(O/'storage_cost_sweep.csv',index=False)
best=df.loc[df.groupby('source').service_lcc.idxmin()].copy();best['case']='lowest_cost_in_grid_backup_sweep'
standard=df[df.capacity_kWh==10.24].copy();standard['case']='common_10p24kWh_storage'
pd.concat([best,standard]).to_csv(O/'lifecycle_comparison.csv',index=False)
# Off-grid sizing at fixed node count: require both annual energy and full-minute service >=99%.
off=[]
for k,g in profiles.items():
 E=g.sum()/1000
 if E<.99*D:off.append(dict(source=k,annual_generation_kWh=E,capacity_kWh=None,status='annual_energy_infeasible_at_fixed_20_nodes',annual_energy_upper_bound_pct=min(E/D,1)*100));continue
 lo=0;hi=1
 def good(C):
  s=dispatch(k,C);return s['grid_kWh']<=.01*D and s['minute_coverage_pct']>=99
 while not good(hi) and hi<1024:hi*=2
 if not good(hi):off.append(dict(source=k,status='not_feasible_within_1024kWh'));continue
 for _ in range(24):
  mid=(lo+hi)/2
  if good(mid):hi=mid
  else:lo=mid
 C=np.ceil(hi/5.12)*5.12;s=dispatch(k,C);c=cost(k,C);off.append(dict(source=k,status='theoretical_99pct_target_requires_multiple_isolated_banks_above_16_modules',capacity_kWh=C,annual_generation_kWh=E,annual_energy_upper_bound_pct=100,**s,**c))
pd.DataFrame(off).to_csv(O/'offgrid_feasibility.csv',index=False)
# Explicit costs sensitivities. All multipliers are scenarios, not statistical intervals.
sens=[]
for k in profiles:
 for disc,price,tm,bm in itertools.product([.03,.05,.08],[.08,.16,.32],[.5,1,2],[.5,1,2]):
  cands=[(cost(k,C,disc,price,bm,tm)['service_lcc'],C) for C in caps];v,C=min(cands)
  sens.append(dict(source=k,discount=disc,price=price,technology_cost_multiplier=tm,battery_cost_multiplier=bm,best_capacity_kWh=C,service_lcc=v))
pd.DataFrame(sens).to_csv(O/'cost_sensitivity.csv',index=False)
grid_only=.16*D*ann
audit=dict(T_years=T,real_discount=r,annual_load_kWh=D,year_repeat='2023 minute chronology repeated; constant maintained output',cost_currency='2026-11-13 nominal USD held constant in real-cost scenario; no conversion of old GBP prices',annual_factor=ann,grid_only_energy_cost=grid_only,road_pair_BOM_USD=road_pair,technology_parameters=pars,PV_plant_cost_source='retailer 2x500W pack USD803; 10 packs; racking, electrical balance and installation prescribed separately',uncertain_costs='wind and PMG are cost analogues, not same tested devices; mechanical BOM and labor allowances, field installation, O&M/replacement years prescribed; quoted hardware swept 0.5x-2x',storage_efficiency=.85,usable_fraction=.8,power_kW=5,battery_module_kWh=5.12,battery_module_USD=1097.99,power_unit_USD=699.99,service_boundary='existing reliable grid supplies residual load, no export revenue, no new grid extension, no grid charging',minimum_storage='minimum over listed candidate set only; not global optimization',offgrid_target='>=99% annual energy and >=99% full-demand minutes in cyclic year; theoretical aggregate energy sizing only; >16 modules requires independently engineered banks',fixed_grid_connection_cost='common sunk existing connection cancels; remote extension needs separate costing',end_of_life='zero salvage credit and zero net decommission cost prescribed; no climate net-benefit claim',generation_excludes='vehicle fuel, standby auxiliaries and inter-node wiring losses not separately resolved; inherited 80% retention maintained; no lifecycle carbon monetization',original_equal_investment='previous GBP assumptions not relabelled as USD quotes',checks='cyclic SOC and annual energy conservation assertions passed')
(O/'audit.json').write_text(json.dumps(audit,indent=2))
print(best[['source','capacity_kWh','grid_kWh','local_served_kWh','service_lcc','asset_lcc']].to_string(index=False))
print(pd.DataFrame(off).to_string(index=False))
print('common10',standard[['source','local_served_kWh','service_lcc']].to_string(index=False));print('gridonly',grid_only)
