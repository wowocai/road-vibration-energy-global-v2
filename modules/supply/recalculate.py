from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
CACHE=ROOT.parent.parent/'data/road_batches'
parts={k:[] for k in ['row_id','length_km','aadt_median','positive_fraction']}
manifest=[]
for path in sorted(CACHE.glob('batch_*.npz')):
    with np.load(path) as z:
        for k in parts: parts[k].append(z[k])
    manifest.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
if manifest:
    a={k:np.concatenate(v) for k,v in parts.items()}
    np.savez_compressed(ROOT/'input_records.npz',**a)
else:
    with np.load(ROOT/'input_records.npz') as z:
        a={k:z[k] for k in parts}
    manifest=json.loads((ROOT/'input_batch_manifest.json').read_text())
(ROOT/'input_batch_manifest.json').write_text(json.dumps(manifest,indent=2))
L=a['length_km']; Q=a['aadt_median']; p=np.clip(a['positive_fraction'],0,1)
assert len(Q)==3293705 and len(np.unique(a['row_id']))==len(Q)
assert np.all(np.isfinite(L)) and np.all(L>0) and np.all(np.isfinite(Q)) and np.all(Q>=0)
assert np.isclose(L.sum(),6906689.106,atol=.001)
assert np.isclose((L*p).sum(),3387073.284124114,atol=.001)
order=np.argsort(Q); qs=Q[order]
domains={}
for label,w in [('old_positive_nightlight',L*p),('full_road_length',L),('zero_positive_nightlight',L*(p==0))]:
    ws=w[order]
    domains[label]={'w':w,'cw':np.r_[0,np.cumsum(ws)],'cwq':np.r_[0,np.cumsum(ws*qs)],'total':w.sum(),'wq':w@Q}

def metrics(domain,coef,demand):
    d=domains[domain]; ix=np.searchsorted(qs,demand/coef,side='left')
    above=d['total']-d['cw'][ix]
    credit=coef*d['cwq'][ix]+demand*above
    return {'coverage_pct':100*above/d['total'],'energy_match_pct':100*credit/(demand*d['total']),
            'balanced_km':above,'supply_TWh':coef*d['wq']/1e9,'credit_TWh':credit/1e9,
            'demand_TWh':demand*d['total']/1e9,'domain_km':d['total']}

lamp=179.01140330823847
basecoef=365*.5*144.8*.8/3.6e6
assert np.isclose(basecoef*20*domains['full_road_length']['wq']/1e9,4.35079316,rtol=1e-8)
ladderpath=ROOT/'power_ladder.json'
if not ladderpath.exists(): ladderpath.write_bytes((ROOT.parent/'esi_update/power_ladder/power_ladder.json').read_bytes())
ladder=json.loads(ladderpath.read_text())
loads=[('Radar',.120*8.76),('Monitoring_1',ladder['scenarios'][1]['annual_kWh_per_km']),
       ('Monitoring_2',ladder['scenarios'][2]['annual_kWh_per_km']),
       ('Monitoring_3',ladder['scenarios'][3]['annual_kWh_per_km']),
       ('1_lamp',lamp),('5_lamps',5*lamp),('20_lamps',20*lamp)]
responsepath=ROOT/'ISO_A-H_contact_results.csv'
if not responsepath.exists():responsepath.write_bytes((ROOT.parent/'duarte_unilateral/ISO_A-H_contact_results.csv').read_bytes())
response=pd.read_csv(responsepath).set_index('iso')
rows=[]
for iso in 'ABCDEFGH':
    ratio=float(response.loc[iso,'ratio_tau25'])
    for density in [1,20]:
        for load,demand in loads:
            for domain in domains:
                rows.append({'ISO':iso,'pairs_per_km':density,'load':load,'demand_kWh_km_year':demand,
                             'domain':domain,'response_ratio':ratio,**metrics(domain,basecoef*density*ratio,demand)})
df=pd.DataFrame(rows);df.to_csv(ROOT/'service_all_domains.csv',index=False)
sel=df[(df.ISO=='A') & (((df.load=='Radar')&(df.pairs_per_km==1))|((df.load.isin(['1_lamp','20_lamps']))&(df.pairs_per_km==20)))]
sel.to_csv(ROOT/'headline_device_comparison.csv',index=False)

arraycoef=365*.5*1000*(17.36/1.32)*.8/3.6e6
arrayrows=[]
for label,f,b in [('H1_original_storage',1.32/2.49,.307),('H2_original_ideal',1.32/2.49,1),('H3_full_active_ideal',1,1)]:
    for domain in domains:
        arrayrows.append({'scenario':label,'domain':domain,'active_fraction':f,'extraction':b,
                          **metrics(domain,arraycoef*f*b,20*lamp)})
ar=pd.DataFrame(arrayrows);ar.to_csv(ROOT/'dense_array_comparison.csv',index=False)
assert np.isclose(ar[(ar.scenario=='H3_full_active_ideal')&(ar.domain=='old_positive_nightlight')].energy_match_pct.iloc[0],67.4177036413129,atol=1e-8)
for load,density,expected in [('Radar',1,99.83217796288102),('1_lamp',20,85.792264),('20_lamps',20,3.81966987)]:
    v=df[(df.ISO=='A')&(df.load==load)&(df.pairs_per_km==density)&(df.domain=='old_positive_nightlight')].coverage_pct.iloc[0]
    assert abs(v-expected)<.003,(load,v,expected)

def inverse(target,density,domain):
    lo,hi=1e-10,1e7
    unit=365*.5*density*.8/3.6e6
    for _ in range(100):
        mid=(lo+hi)/2
        if metrics(domain,unit*mid,20*lamp)['energy_match_pct']<target:lo=mid
        else:hi=mid
    return (lo+hi)/2
inv=[{'domain':domain,'target_pct':t,'pairs_per_km':20,'electric_J_pair_pass':inverse(t,20,domain)} for domain in domains for t in [50,90]]
pd.DataFrame(inv).to_csv(ROOT/'inverse_targets.csv',index=False)
curves=[]
for iso in 'ABCDEFGH':
    ratio=float(response.loc[iso,'ratio_tau25'])
    for density in [1,20]:
        for power in np.linspace(0,420,421):
            for domain in ['old_positive_nightlight','full_road_length']:
                C=100. if power==0 else metrics(domain,basecoef*density*ratio,power*8.76)['coverage_pct']
                curves.append({'ISO':iso,'pairs_per_km':density,'power_W_km':power,'domain':domain,'coverage_pct':C})
pd.DataFrame(curves).to_csv(ROOT/'Figure4g_full_length_curves.csv',index=False)
audit={'records':len(Q),'batch_count':len(manifest),'domains':{k:{'length_km':float(v['total']),'length_weighted_AADT':float(v['wq']/v['total'])} for k,v in domains.items()},
       'h':.5,'r':.8,'peak_J_pair_pass':144.8,'lamp_kWh_year':lamp,'array_J_per_pass':17.36,'array_active_length_m':1.32,
       'change':'Only spatial aggregation weights change from L*p to L; per-road supply, normative demand and physical response are unchanged.',
       'source_files':manifest,'checks':['unique source IDs','finite positive length','finite nonnegative traffic','source domain totals reproduced','4.35079316 TWh reproduced','old headline percentages reproduced','old dense-array 67.41770364% reproduced']}
(ROOT/'audit.json').write_text(json.dumps(audit,indent=2))
print(sel.to_string(index=False))
print(ar.to_string(index=False))
print(pd.DataFrame(inv).to_string(index=False))
