from pathlib import Path
import contextlib,io,json
import pandas as pd
with contextlib.redirect_stdout(io.StringIO()):
 import recalculate as m
P=Path(__file__).resolve().parent
rows=[]
for discount in [0,.2,.3,.4,.5,.6]:
 c=1959.9*(1-discount)
 rows.append({'road_discount_assumed':discount,'USD_per_pair':c,'USD_per_single':c/2,'road_20yr_USD_km':m.costs(c)['total']})
pd.DataFrame(rows).to_csv(P/'out/bulk_road_sensitivity.csv',index=False)
pv_retail=float(m.common.loc['PV','service_lcc'])
pv_bulk=pv_retail-8030+20*5690/32
windbase=float(m.common.loc['wind','service_lcc'])
refs=[]
for disc in [0,.1,.2]:
 # Reduce turbine acquisition and proportional equipment OM / replacement;
 # retain mounts, conditioning, installation, battery, backup, labor.
 reduction=20*563.99*disc*(1+.01*m.A+.25*m.d)
 total=windbase-reduction
 target=m.threshold(total)
 refs.append(dict(wind_discount_assumed=disc,wind_20yr_USD_km=total,road_break_even_USD_pair=target,road_discount_needed=1-target/1959.9))
pd.DataFrame(refs).to_csv(P/'out/bulk_wind_crosscheck.csv',index=False)
audit=dict(road_discounts='assumed sensitivity on full 1959.90 USD/pair reconstruction including allowances; not measured production discounts',PV_bulk_panel=5690/32,PV_bulk_service_LCC=pv_bulk,PV_bulk_road_threshold=m.threshold(pv_bulk),PV_bulk_road_discount_needed=1-m.threshold(pv_bulk)/1959.9,PV_proration='20/32 pallet cost allocated across multi-km procurement, excludes procurement-specific freight/tax; single-km leftover inventory not treated as free',wind='retail complete commercial units, not documented wholesale; 10 and20% extra reductions are assumed sensitivity',performance='all archived generation dispatch and equal-service accounting retained')
(P/'out/bulk_audit.json').write_text(json.dumps(audit,indent=2))
print(pd.DataFrame(rows).round(2).to_string(index=False));print(pd.DataFrame(refs).round(3).to_string(index=False));print(json.dumps(audit,indent=2))
