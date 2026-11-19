from pathlib import Path
import contextlib,io,json
import pandas as pd
with contextlib.redirect_stdout(io.StringIO()):import unified_maintenance as u
P=Path(__file__).resolve().parent
bom=pd.read_csv(P/'source/lifecycle_costs/out/road_pair_BOM.csv')
base=float(bom.total_USD.sum());assert abs(base-1959.9)<1e-8
rows=[]
for k in [1,.7,.5,.4]:
 c=(f'road_parts_k{k}','vibration',20*base*k,2000)
 rows.append(dict(coefficient=k,USD_module=base*k/2,USD_pair=base*k,**u.calc(c)))
r=pd.DataFrame(rows);r.to_csv(P/'out/parts_bulk_costs.csv',index=False)
(P/'out/parts_bulk_assumptions.json').write_text(json.dumps({'current_basis':'Supersedes460USD author quote and factory_bulk.py results. User withdrew nonpublic quote; do not use as evidence.','base_USD_pair':base,'public_parts_subtotal':739.9,'engineering_allowances_subtotal':1220,'coefficient_reference':.5,'sensitivity':[.4,.7],'coefficient_interpretation':'Engineering projection applied to complete component-and-assembly reconstruction,including unquoted allowances. PV quantity-price ratio0.38035 supports exploring scale scenarios,not a transferable measured manufacturing factor. No valid complete same-model Savonius parts/whole procurement coefficient found. No exact Duarte pricedBOM validation.','boundary':'Same20yr5%,common1%OM,25%year10replacement,100USD/node replacementlabor; originalgeneration/dispatch/storage/gridservice retained. Coefficient does not reduce installation,battery or inverter independently. Separate module-level rectification allowance and common power-stage equipment retained as prescribed integration accounting,not a verified electrical BOM.'},indent=2))
print(r[['coefficient','USD_module','USD_pair','total']].round(3).to_string(index=False))
