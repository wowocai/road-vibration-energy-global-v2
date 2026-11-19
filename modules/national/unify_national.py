"""Scope-cleaned national reconstruction; validation and inventory share one implementation."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

COLS={'Passenger':'Passenger Car Traffic (Mio Vehicle-Km Annual)',
 'Bus':'Bus and Motor Coach Traffic (Mio Vehicle-Km Annual)',
 'Freight':'Total Van, Pickup, Lorry and Road Tractor Traffic (Mio Vehicle-Km Annual)'}
STOCK={'Passenger':'Passenger Cars In Use (n)','Bus':'Buses and Motor Coaches In Use (n)',
 'Freight':'Total Vans, Pickups, Lorries and Road Tractors In Use (n)'}
FEATURES=['Population',*STOCK.values(),'Motorway or Highway Network (km)',
 'Main or National Road Network - Total (km)','Secondary or Regional Road Network - Total (km)',
 'Other Roads - Combined (Urban and Rural) - Total (km)','GDP_per_capita','Urbanization_Rate']

def predict(d,label,train,test):
 y=pd.to_numeric(d[COLS[label]],errors='coerce').to_numpy(float)
 stock=pd.to_numeric(d[STOCK[label]],errors='coerce').to_numpy(float)
 tr=train[np.isfinite(y[train])&(y[train]>=0)]
 assert len(tr)>2
 x=np.log1p(d[FEATURES].apply(pd.to_numeric,errors='coerce').where(lambda x:x>=0))
 med=x.iloc[tr].median().fillna(0)
 x=x.fillna(med).to_numpy(float)
 sc=StandardScaler().fit(x[tr])
 reg=Ridge(alpha=10,solver='svd').fit(sc.transform(x[tr]),np.log1p(y[tr]))
 ridge=np.maximum(np.expm1(reg.predict(sc.transform(x[test]))),0)
 mile_ids=tr[np.isfinite(stock[tr])&(stock[tr]>0)]
 mileage=float(np.median(y[mile_ids]*1e6/stock[mile_ids]))
 good=np.isfinite(stock[test])&(stock[test]>0)
 primary=np.where(good,stock[test]*mileage/1e6,ridge)
 rf=RandomForestRegressor(n_estimators=800,min_samples_leaf=2,random_state=42,n_jobs=1)
 rf.fit(x[tr],np.log1p(y[tr]))
 rfp=np.maximum(np.expm1(rf.predict(x[test])),0)
 return {'stock_or_ridge':primary,'ridge':ridge,'RF':rfp},mileage,tr

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,default=Path(__file__).parent/'project');ap.add_argument('--out',type=Path,default=Path(__file__).parent/'out');args=ap.parse_args()
 p=args.project;out=args.out;out.mkdir(parents=True,exist_ok=True)
 raw=p/'inputs/national/vkt_candidate_inputs.json'
 d=pd.DataFrame(json.loads(raw.read_text()));clean=d.copy()
 sw=d.Country.eq('Switzerland');assert sw.sum()==1
 # Apply the pre-existing source-scope exclusion BEFORE every fit and evaluation.
 edits=[]
 for col in [COLS['Bus'],STOCK['Bus']]:
  edits.append({'country':'Switzerland','field':col,'old_value':float(d.loc[sw,col].iloc[0]),'new_value':None,'reason':'Pre-existing scope audit: Swiss bus target and broad stock are not category-compatible; treat as missing, not zero.'})
  clean.loc[sw,col]=np.nan
 clean.to_json(out/'national_inputs_scope_clean.json',orient='records',force_ascii=False,indent=2)
 pd.DataFrame(edits).to_csv(out/'scope_corrections.csv',index=False)
 ids=np.arange(len(clean));obs=np.flatnonzero(clean[list(COLS.values())].notna().any(axis=1).to_numpy())
 predictions=[];membership=[];metrics=[]
 for seed in [42,2026]:
  for fold,(a,b) in enumerate(KFold(5,shuffle=True,random_state=seed).split(obs),1):
   train,test=obs[a],obs[b];assert not np.intersect1d(train,test).size
   for k,c in COLS.items():
    pp,mileage,tr=predict(clean,k,train,test)
    for j in tr:membership.append(dict(seed=seed,fold=fold,category=k,role='training',row_id=int(j),country=clean.iloc[j].Country))
    y=pd.to_numeric(clean[c],errors='coerce').to_numpy(float)
    for pos,j in enumerate(test):
     membership.append(dict(seed=seed,fold=fold,category=k,role='held_out_country',row_id=int(j),country=clean.iloc[j].Country))
     if not np.isfinite(y[j]):continue
     for method,v in pp.items():predictions.append(dict(seed=seed,fold=fold,category=k,method=method,row_id=int(j),country=clean.iloc[j].Country,observed=float(y[j]),predicted=float(v[pos]),training_n=len(tr),training_mileage=mileage))
 ph=pd.DataFrame(predictions)
 for keys,g in ph.groupby(['seed','category','method']):
  metrics.append(dict(zip(['seed','category','method'],keys),n=len(g),RMSLE=float(np.sqrt(np.mean((np.log1p(g.predicted)-np.log1p(g.observed))**2)))))
 ph.to_csv(out/'country_held_out_predictions.csv',index=False)
 pd.DataFrame(membership).to_csv(out/'fold_membership.csv',index=False)
 pd.DataFrame(metrics).to_csv(out/'country_held_out_metrics.csv',index=False)
 rows=[]
 for k,c in COLS.items():
  pp,mileage,tr=predict(clean,k,ids,ids)
  for j,r in clean.iterrows():
   observed=pd.notna(r[c])
   for method,v in pp.items():
    value=float(r[c]) if observed else float(v[j])
    route='reported' if observed else ('stock_mileage' if method=='stock_or_ridge' and pd.notna(r[STOCK[k]]) and r[STOCK[k]]>0 else method)
    rows.append(dict(method=method,row_id=j,country=r.Country,country_code=r['Country Code'],category=k,annual_VKT_million_km=value,route=route,training_n=len(tr),training_mileage=mileage))
 final=pd.DataFrame(rows);final.to_csv(out/'national_inventory_all_methods.csv',index=False)
 main=final[final.method.eq('stock_or_ridge')].copy();assert len(main)==654
 main.to_csv(out/'national_inventory_PRIMARY.csv',index=False)
 units=pd.read_csv(p/'Lighting_replacement_20261023/Global_three_layer_20261024/Vehicle_model_alignment_20261025/current_ISO_response.csv')
 base=units[units.ISO.eq('A')].set_index('vehicle').unit_J_km.to_dict()
 old=pd.read_csv(p/'outputs/Vehicle_resource_reproduction_20261022/country_traffic_reconstructed.csv');old=old[old.feature_set.eq('retained_ten')]
 totals=[];country=[];regional=[]
 for iso,scale in zip('ABCDEFGH',4.**np.arange(8)):
  for mix in [0.,.5,1.]:
   weights=base.copy();weights['Freight']=(1-mix)*base['Passenger']+mix*base['Freight']
   oldsum=float(np.sum(old.annual_VKT_million_km*old.category.map(weights))*1e6*scale/3.6e15)
   for method,g in final.groupby('method'):
    gg=g.copy();gg['TWh_year']=gg.annual_VKT_million_km*gg.category.map(weights)*1e6*scale/3.6e15
    total=float(gg.TWh_year.sum());totals.append(dict(ISO=iso,freight_heavy_fraction=mix,method=method,TWh_year=total,old_TWh_year=oldsum,change_pct=100*(total/oldsum-1)))
    if method=='stock_or_ridge':
     for _,r in gg.iterrows():country.append(dict(ISO=iso,freight_heavy_fraction=mix,**r.to_dict()))
     if iso=='B':
      cn=gg.groupby('country').TWh_year.sum()
      lengths=pd.to_numeric(clean['Total Road Network - All Road Types - Total (km)'],errors='coerce')
      intensity=pd.Series(cn.reindex(clean.Country).to_numpy()/lengths.to_numpy(),index=clean.Country)
      for name in ['China, Hong Kong','Hong Kong SAR, China','Hong Kong','Korea, Rep.','South Korea','China']:
       if name in intensity.index:regional.append(dict(country=name,freight_heavy_fraction=mix,intensity_TWh_km=float(intensity[name]),ratio_to_China=float(intensity[name]/intensity['China'])))
 pd.DataFrame(totals).to_csv(out/'global_resources_A_H.csv',index=False)
 pd.DataFrame(country).to_csv(out/'country_resources_A_H.csv',index=False)
 pd.DataFrame(regional).to_csv(out/'regional_intensity_sensitivity.csv',index=False)
 qa={'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'clean_input_sha256':hashlib.sha256((out/'national_inputs_scope_clean.json').read_bytes()).hexdigest(),'countries':len(clean),'observed_country_union':len(obs),'observed_category_targets':int(clean[list(COLS.values())].notna().sum().sum()),'primary_method':'stock_or_ridge','model_selection_basis':'Existing benchmark was already preferable to Ridge; RF is a same-fold benchmark, not tuned against these test folds.','same_preprocessing_and_predict_function_for_inventory_and_CV':True,'primary_rows':len(main),'CV_prediction_rows':len(ph),'source_year_status':'Original input does not encode a year for each datum; do not describe this mixed-source inventory as a single-year observed census.','road_device_supply_changed':False,'scope_rule_origin':'Previously documented Swiss bus target and broad-stock exclusion, now applied before all fits and folds.'}
 (out/'QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 print(pd.DataFrame(totals).query("method=='stock_or_ridge' and freight_heavy_fraction==0.5").to_string(index=False))
 print(pd.DataFrame(metrics).to_string(index=False));print(json.dumps(qa,ensure_ascii=False))

if __name__=='__main__':main()
