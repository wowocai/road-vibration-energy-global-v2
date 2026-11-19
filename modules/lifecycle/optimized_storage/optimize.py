from pathlib import Path
import numpy as np,pandas as pd,subprocess,json,itertools
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
root=P.parent;z=np.load(root.parent/'multienergy/node20/out/minute_inputs.npz');load=z['load_Wh'];D=float(load.sum()/1000)
profiles={s:z[s+'_Wh'] for s in ['PV','wind','vibration']}
exe=P/'dispatch'
subprocess.run(['g++','-O3',str(P/'dispatch.cpp'),'-o',str(exe)],check=True)
for s,g in profiles.items():np.r_[g,load].astype('float64').tofile(O/(s+'.bin'))
cache={}
def dispatch(s,C):
 key=(s,round(C,8))
 if key not in cache:
  a=list(map(float,subprocess.check_output([str(exe),str(O/(s+'.bin')),str(C)],text=True).split(',')))
  r=dict(zip(['grid_kWh','served_kWh','spill_kWh','loss_kWh','full_min_fraction','soc_start','soc_end','warm_years','battery_internal_discharge_kWh','battery_internal_charge_kWh','charging_minutes','discharging_minutes'],a));r['annual_EFC']=a[8]/C if C else 0
  assert abs(a[5]-a[6])<1e-5
  assert abs(float(profiles[s].sum())/1000-a[1]-a[2]-a[3])<1e-6
  assert abs(D-a[0]-a[1])<1e-6
  cache[key]=r
 return cache[key]
A=sum(1.05**(-t) for t in range(1,21));q=1.05**-10
sourcepars={'PV':(6556.25,2500),'wind':(14279.8,5000),'vibration':(17151.48,2000)}
def cost(s,C,price=.16,calendar=10,efcbudget=4000,specialhours=2,wage=40,bmult=1,relaxed=False):
 v=dispatch(s,C);e,install=sourcepars[s]
 n=C/5.12 if relaxed else int(round(C/5.12));initial=(n*1097.99+620)*bmult if C else 0
 life=min(calendar,efcbudget/v['annual_EFC']) if C and v['annual_EFC']>0 else calendar
 times=np.arange(life,20-1e-7,life) if C else []
 rep=sum((n*1097.99+200)*bmult/1.05**t for t in times)
 parts=dict(equipment=e,installation=install,common_inspection=80*A,specialist_maintenance=(specialhours*wage+20)*A,harvester_replacement=(e*.25+2000)*q,power_initial=1399.98,power_replacement=1599.98*q,storage_initial=initial,storage_checks=10*A if C else 0,storage_replacement=rep,grid_backup=v['grid_kWh']*price*A)
 return dict(source=s,capacity_kWh=C,**v,battery_life_years=life,battery_replacements=len(times),**parts,total=sum(parts.values()))
rows=[cost(s,5.12*n) for s in profiles for n in range(17)]
df=pd.DataFrame(rows);df.to_csv(O/'module_capacity_sweep.csv',index=False)
best=df.loc[df.groupby('source').total.idxmin()].copy();best.to_csv(O/'optimized_cost_breakdown.csv',index=False)
fixed=df[np.isclose(df.capacity_kWh,10.24)];fixed.to_csv(O/'fixed_capacity_new_maintenance.csv',index=False)
# Dense proportional-price sensitivity is not a quote for smaller battery products.
dense=pd.DataFrame([cost(s,float(C),relaxed=True) for s in profiles for C in np.r_[0,np.arange(.25,20.01,.25)]])
dense.to_csv(O/'relaxed_capacity_sweep.csv',index=False);densebest=dense.loc[dense.groupby('source').total.idxmin()];densebest.to_csv(O/'relaxed_optima.csv',index=False)
sens=[]
for s,price,cal,bm in itertools.product(profiles,[.08,.16,.32],[5,10,15],[.5,1,2]):
 cand=[cost(s,5.12*n,price=price,calendar=cal,bmult=bm) for n in range(17)];r=min(cand,key=lambda x:x['total']);sens.append(dict(price=price,calendar=cal,battery_price_multiplier=bm,**r))
pd.DataFrame(sens).to_csv(O/'storage_cost_sensitivity.csv',index=False)
# Separate uncertainty in annual specialist labor budget, same inspection/consumables.
maint=[]
for s,h in itertools.product(profiles,[1,2,4]):
 r=min([cost(s,5.12*n,specialhours=h) for n in range(17)],key=lambda x:x['total']);maint.append(dict(specialist_hours_per_year=h,**r))
pd.DataFrame(maint).to_csv(O/'maintenance_sensitivity.csv',index=False)
assumptions={'objective':'Minimum20yr discounted expenditure at fixed20nodes/km and maintained source output,with grid residualbackup;not offgrid optimization','input':'Original2023 minute weather/traffic/demand,2015roadinventory assumptions retained;stationary year repeated','service_kWh_year':D,'capacity_candidates':'0–16 modules,5.12kWh/module.0 battery allowed. Standardized aggregatedperkm screening,not validated20distributedpoint wiring design.5kWcharge/discharge,80%usable,85%roundtrip,no gridcharging,exports,standbyorheat demand','maintenance':{'inspection':'2visits/year*1personhour/km/visit*40USD/hr=80USD/km/year,common','specialist':'PVtwo cleanings*3min/panel*20=2h/year;windone6min/turbine*20=2h/year;roadone6min/pair*20=2h/year.Each80USD labor+20consumables=100USD/year. Tasktimes and frequencies are explicit matched engineering budgets,not empirical serviceintervals. Source DOE supportsactivity-based accounting,not these numbers.','batterychecks':'0.25personhour/year*40USD/hour=10USDyearonlywhenbatteryinstalled;included no duplicate1%maintenance','scope':'Road laneclosure and extraordinary correctivework unpriced,require project specific adders;harvester replacement already separately25%year10+100USDnode.'},'battery':{'module_USD':1097.99,'integration_initial_USD':620,'replacement_labor_USD':200,'calendar_years':10,'cycle_EFC_budget':4000,'rule':'life=min(calendar,4000/annualinternaldischargeEFC).Vendor4000cycles100%DOD/6000cycles80%DOD usedas screeninganchor,not rainflowdegradationmodel. Annual fixedcapacity dispatch;no fade/temperature/selfdischarge model. Calendar5/10/15 sensitivity. No cyclelife claimverifiedinthefield.'},'sources':{'battery':'https://www.litime.com/products/litime-48v-100ah-smart-comflex-lithium-battery checked16Nov2026 price1097.99;5.12kWh;4000cycles100%DOD;5yearwarranty;up to10yearclaim','maintenance_method':'https://www.energy.gov/cmei/femp/life-cycle-photovoltaic-systems-operate-and-maintain-existing-photovoltaic-system checked16Nov2026'},'cost_basis':'Low-costcandidategear/bearing scenario,k=.5;originalhardwareperformanceandnonstoragepricesunchanged. Price/performance matching not validated;gridconnection existingcommon,20years5%,electricity.16USD/kWh;no carboncredit/salvage/exportvalue.'}
(O/'assumptions.json').write_text(json.dumps(assumptions,indent=2))
print('OPTIMAL\n',best[['source','capacity_kWh','grid_kWh','served_kWh','annual_EFC','battery_life_years','total']].round(4).to_string(index=False));print('RELAXED\n',densebest[['source','capacity_kWh','grid_kWh','annual_EFC','total']].round(4).to_string(index=False));print('FIXED\n',fixed[['source','capacity_kWh','grid_kWh','annual_EFC','total']].round(4).to_string(index=False))
