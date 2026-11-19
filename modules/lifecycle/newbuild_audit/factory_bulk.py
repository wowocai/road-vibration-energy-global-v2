from pathlib import Path
import contextlib,io
import pandas as pd,json
with contextlib.redirect_stdout(io.StringIO()):import unified_maintenance as u
P=Path(__file__).resolve().parent
rows=[]
for k in [1,.7,.5,.4]:
 c=('road_factory_k'+str(k),'vibration',40*460*k,2000)
 rows.append(dict(coefficient=k,USD_module=460*k,USD_pair=920*k,**u.calc(c)))
r=pd.DataFrame(rows);r.to_csv(P/'out/factory_bulk_costs.csv',index=False)
(P/'out/factory_bulk_assumptions.json').write_text(json.dumps({'factory_quote':{'USD_module':460,'source':'Author-supplied direct manufacturer quote; communicated14Nov2026; no public document; supplier,dateofquotation,MOQ,freight,tax and prototype equivalence unverified'},'coefficient':{'illustrative':.5,'sensitivity':[.4,.7],'undiscounted_anchor':1,'basis':'Same modelPV smallpack vs pallet displayed price ratio 177.8125/467.5=0.38035; quantity/channel benchmark only,not measured manufacturing factor; cannot transfer causally across technologies. Prior road reconstructed/quoted price gap is not an independent discount and is not used to calibrate k. Whether460 already reflectsvolumepricing isunknown. Therefore k=.5 is a conditional projection,not validatedcurrentcost.'},'main_equal_service':'20yr5%; common equipmentOM1%;year10replace25%plus100USDpernode;20nodes;common10.24kWh;gridbackup;performanceunchangedbycostscenario'},indent=2))
print(r[['coefficient','USD_module','USD_pair','total']].round(2).to_string(index=False))
