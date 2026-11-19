from pathlib import Path
import pandas as pd,numpy as np,json,itertools
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
S=P/'source/lifecycle_costs/out'
old=pd.read_csv(S/'lifecycle_comparison.csv');common=old[old.case=='common_10p24kWh_storage'].set_index('source')
T=20;r=.05;A=sum((1+r)**(-t) for t in range(1,T+1));d=(1+r)**-10
# Put wind and road on the same prescribed modular maintenance boundary. PV module replacement remains zero within 20 years; power electronics are replaced separately for all sources.
wind_old=common.loc['wind'].service_lcc
wind_revised=common.loc['wind'].equipment+5000+common.loc['wind'].equipment*.01*A+(common.loc['wind'].equipment*.25+2000)*d+common.loc['wind'].power_stage_initial+common.loc['wind'].power_stage_replacement_pv+common.loc['wind'].storage_initial+common.loc['wind'].storage_maintenance_pv+common.loc['wind'].storage_replacement_pv+common.loc['wind'].backup_electricity_pv
common.loc['wind','service_lcc']=wind_revised
def costs(unit=1000,install=100,om=.01,replace=.25,labor=100,rate=.05):
 a=sum((1+rate)**(-t) for t in range(1,21));q=(1+rate)**-10
 # Fixed generation chronology and common 10.24 kWh dispatch. No hardware/performance substitution claimed.
 row=common.loc['vibration'];battery=row.storage_initial+.01*row.storage_initial*a+(2*1097.99+200)*q
 power=1399.98+1599.98*q;backup=row.grid_kWh*.16*a
 vals=dict(equipment=20*unit,incremental_newbuild_install=20*install,routine_maintenance=20*unit*om*a,replace_parts=20*unit*replace*q,replace_labor=20*labor*q,common_power=power,storage=battery,grid_backup=backup)
 vals['total']=sum(vals.values());return vals
def threshold(ref,**kwargs):
 c0=costs(unit=0,**kwargs)['total'];k=costs(unit=1,**kwargs)['total']-c0
 return (ref-c0)/k
rows=[]
for C in [500,750,1000,1250,1500,1959.9]:rows.append(dict(unit_USD_per_pair=C,unit_USD_per_single_module=C/2,**costs(C)))
pd.DataFrame(rows).to_csv(O/'newbuild_cost_targets.csv',index=False)
limits=[]
for f,yr,ma in itertools.product([.25,.5,1],[100,250,500],[.005,.01,.02]):
 kw=dict(install=yr,om=ma,replace=f)
 limits.append(dict(replaced_fraction_at_year10=f,incremental_install_per_pair=yr,annual_OM_fraction=ma,break_even_vs_PV_USD_pair=threshold(common.loc['PV'].service_lcc,**kw),break_even_vs_wind_USD_pair=threshold(common.loc['wind'].service_lcc,**kw)))
pd.DataFrame(limits).to_csv(O/'break_even_cost_grid.csv',index=False)
exact=costs(1959.9);original=common.loc['vibration'].service_lcc
audit={'status':'conditional cost target analysis; not a new vendor quote or a validated batch-production BOM','nodes':'20 pairs/km = 40 road modules, compared with 20 complete wind turbines','fixed_performance':'original 144.8 J/pair effective passage and all archived traffic/weather/load unchanged','architecture':'Duarte patent US10954926B2 supports components and alternative shared generator arrangements; no evidence identifies exact trial BOM or permits assigning unchanged yield to shared machinery','main_assumptions':{'unit_cost_USD_pair':'parameter, not a newly estimated price','incremental_install_USD_pair':100,'routine_OM_fraction_of_equipment':.01,'replacement_fraction_at_year10':.25,'replacement_labor_USD_pair':100,'assessment_years':20,'discount':.05,'battery_kWh':10.24,'wind_consistency':'same 1% routine OM and 25% equipment replacement at year10, with USD100 per turbine labor; install USD5000 retained as incremental field construction scenario; no full turbine replacement','PV_consistency':'module price/field installation retained; inverter and storage replacements retained; no PV-module replacement in20 years'},'baseline_previous_total':original,'same_old_equipment_price_newbuild_modular_total':exact['total'],'PV_reference_total':common.loc['PV'].service_lcc,'wind_previous_total':wind_old,'wind_modular_reference_total':wind_revised,'threshold_vs_PV_USD_pair':threshold(common.loc['PV'].service_lcc),'threshold_vs_wind_USD_pair':threshold(wind_revised),'no_grid_or_storage_autonomy_claim':True,'old_quote_share':739.9/1959.9,'old_allowance_share':1220/1959.9,'primary_cost_diagnosis':'retail single-part prototype reconstruction vs complete commercial turbine; two modules vs one turbine per point; unverified complete replacement at year10; not established actual market cost ratio'}
(O/'audit.json').write_text(json.dumps(audit,indent=2))
print(pd.DataFrame(rows).round(2).to_string(index=False));print(json.dumps(audit,indent=2))
assert abs(costs(1000)['total']-sum(v for k,v in costs(1000).items() if k!='total'))<1e-8
