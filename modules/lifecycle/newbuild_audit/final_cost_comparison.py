from pathlib import Path
import pandas as pd,json,itertools,contextlib,io
with contextlib.redirect_stdout(io.StringIO()):import unified_maintenance as u
P=Path(__file__).resolve().parent;O=P/'out'
fx=1.1052
bom=pd.read_csv(P/'source/lifecycle_costs/out/road_pair_BOM.csv')
bom['original_total_USD']=bom.total_USD
bom.loc[bom.component.str.contains('rack-pinion'),'unit_USD']=20*fx
bom.loc[bom.component.str.contains('pillow-block'),'unit_USD']=11.51
bom.total_USD=bom.quantity*bom.unit_USD
bom.loc[bom.component.str.contains('rack-pinion'),'source']='CNCdrive price list; EUR16.50 M1.5 17x17x1000 straight rack + EUR3.50 M1.5Z20 pinion; bore/material/strength and original prototype match unverified'
bom.loc[bom.component.str.contains('pillow-block'),'source']='Baltic UCP205-16 1inch, quantity2-4 rateUSD11.51; geometry checked,load/fatigue unverified'
bom.to_csv(O/'candidate_road_pair_BOM.csv',index=False)
base=float(bom.total_USD.sum());k=.5
cases=[('PV','PV',6556.25,2500),('wind','wind',14279.8,5000),('road_candidate','vibration',20*base*k,2000),('road_original','vibration',20*1959.9*k,2000)]
rows=[]
for c in cases:
 r=u.calc(c);src=u.old.loc[c[1]]
 r['power_initial']=float(src.power_stage_initial);r['power_replacement']=float(src.power_stage_replacement_pv)
 r['storage_initial']=float(src.storage_initial);r['storage_maintenance']=float(src.storage_maintenance_pv);r['storage_replacement']=float(src.storage_replacement_pv)
 rows.append(r)
res=pd.DataFrame(rows);res.to_csv(O/'final_cost_comparison.csv',index=False)
sens=[]
for kk in [.4,.5,.7,1]:sens.append(dict(k=kk,pair_USD=base*kk,module_USD=base*kk/2,**u.calc(('road_candidate','vibration',20*base*kk,2000))))
pd.DataFrame(sens).to_csv(O/'candidate_scale_sensitivity.csv',index=False)
matched=[]
for om,share,year in itertools.product([.005,.01,.02],[0,.25,.5],[8,10,15]):
 for c in cases:matched.append(dict(OM_fraction=om,replacement_share=share,year=year,**u.calc(c,om=om,share=share,year=year,labor=0 if share==0 else 100)))
pd.DataFrame(matched).to_csv(O/'candidate_maintenance_sensitivity.csv',index=False)
meta={'current':'Low-cost candidate procurement scenario,not verified mechanically interchangeable replacement or built/tested low-cost device;original-price case remains sensitivity','base_USD_pair':base,'scale_coefficient':k,'fx_EUR_USD':fx,'fx_date':'13November2026','quotes_checked':'14November2026','EUR_price_inclusions':'Shipping,tax,shaft-bore machining unconfirmed;not declared landed prices','sources':{'rack':'https://shop.cncdrive.com/index.php?show_price=yes','bearing':'https://www.bearings.parts/ucp205-16-pillow-block-baltic-bearing','fx':'https://www.ecb.europa.eu/stats/shared/pdf/eurofxref.pdf ; retrieved13Nov2026rate1.1052'},'scale_assumption':'0.5 is engineering assumption;0.4–0.7 sensitivity motivated by quantity/channel differences,not empirically calibrated same-product factory saving. Applied to quoted parts+engineering allowances;not fieldinstallation/battery/inverter','service':'20lamps+radar3581.279266kWh/km/yr;20nodes/km;road20pairs40modules;10.24kWhstorage;gridresidual;20yr5%;electricity0.16USD/kWh;noexports,no carboncredit;existinggridconnectioncommon','equipment_accounting':'Module rectification allowanceUSD200/pair retained separately from common inverter/power-stage cost;not a verified electricalintegration design. No further generator substitution,smallerinput,or performance gain asserted.'}
(O/'final_cost_assumptions.json').write_text(json.dumps(meta,indent=2))
assert abs(base-1715.148)<1e-6
assert abs(res.loc[res.case=='road_candidate','total'].iloc[0]-37861.31446307)<.001
print(res.round(2).to_string(index=False));print(pd.DataFrame(sens)[['k','pair_USD','total']].round(2).to_string(index=False))
