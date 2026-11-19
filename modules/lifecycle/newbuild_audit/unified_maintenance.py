from pathlib import Path
import pandas as pd,itertools,json
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
old=pd.read_csv(P/'source/lifecycle_costs/out/lifecycle_comparison.csv');old=old[old.case=='common_10p24kWh_storage'].set_index('source')
A=sum(1.05**(-t) for t in range(1,21))
# Same accounting coefficients for all technologies; original price evidence/discount assumptions retained.
cases=[('PV_bulk','PV',20*5690/32+3000,2500),('wind_retail','wind',14279.8,5000),('wind_discount20','wind',14279.8-20*563.99*.2,5000)]+[(f'road_discount{d}','vibration',20*1959.9*(1-d/100),2000) for d in [20,30,40,50,60]]
def calc(c,om=.01,share=.25,year=10,labor=100):
 name,src,equip,install=c;q=1.05**(-year);r=old.loc[src]
 vals=dict(equipment=equip,installation=install,maintenance=equip*om*A,harvester_replacement=equip*share*q+20*labor*q,power_electronics=r.power_stage_initial+r.power_stage_replacement_pv,storage=r.storage_initial+r.storage_maintenance_pv+r.storage_replacement_pv,grid_backup=r.backup_electricity_pv)
 return dict(case=name,**vals,total=sum(vals.values()))
base=pd.DataFrame([calc(c) for c in cases]);base.to_csv(O/'unified_cost_baseline.csv',index=False)
rows=[]
for om,share,year in itertools.product([.005,.01,.02],[0,.25,.5],[8,10,15]):
 for c in cases:rows.append(dict(annual_maintenance_fraction=om,replacement_fraction=share,replacement_year=year,**calc(c,labor=0 if share==0 else 100,om=om,share=share,year=year)))
grid=pd.DataFrame(rows);grid.to_csv(O/'unified_cost_sensitivity.csv',index=False)
pivot=grid.pivot(index=['annual_maintenance_fraction','replacement_fraction','replacement_year'],columns='case',values='total')
audit={'baseline':'All technologies 1% annual equipment-cost maintenance; year10 replacement of25% of initial equipment value plus100USD/node labor. Common20nodes/km. PV20panels,wind20turbines,road20pairs40modules. Applies to equipment-and-structure aggregate as screening assumption,not observed component lifetimes. Power electronics and batteries separately counted.','sensitivity':'27 matched settings per technology:annual OM0.5/1/2%;replace0/25/50%;year8/10/15;zero replacement means zero replacement labor. Zero-share timing rows duplicate scenarios but are retained for rectangular grid.','minimum_PV_vs_other_gap':float((pivot.drop(columns='PV_bulk').sub(pivot.PV_bulk,axis=0)).min().min()),'road50_minus_wind_retail_minmax':[float((pivot.road_discount50-pivot.wind_retail).min()),float((pivot.road_discount50-pivot.wind_retail).max())],'road60_minus_wind_discount20_minmax':[float((pivot.road_discount60-pivot.wind_discount20).min()),float((pivot.road_discount60-pivot.wind_discount20).max())],'boundary':'20yr5% discounted grid-supported same-service expenditure,not standalone autonomy. Price reductions remain assumptions. No performance or dispatch changes.'}
(O/'unified_audit.json').write_text(json.dumps(audit,indent=2))
assert (base.total-base[['equipment','installation','maintenance','harvester_replacement','power_electronics','storage','grid_backup']].sum(axis=1)).abs().max()<1e-8
print(base.round(2).to_string(index=False));print(json.dumps(audit,indent=2))
