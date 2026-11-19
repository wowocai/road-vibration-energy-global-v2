# -*- coding: utf-8 -*-
"""Independent reconstruction from accepted SI text; no original manuscript edits."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
from pathlib import Path
import json, hashlib, csv, math, shutil
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from sklearn.model_selection import KFold
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_log_error

ROOT = Path(__file__).resolve().parent
OUT = Path(r'D:\GlobalRoadVibrationEnergy\Revision_Archive\C_workspace_storage_20261012\outputs\Vehicle_resource_reproduction_20261022')
OUT.mkdir(parents=True, exist_ok=True)
PARAMS = {
    'Passenger': [1600,60,2400,1800,22000,1600,200000,.8,1.2,1.6],
    'Freight': [8000,200,25000,15000,400000,60000,800000,.9,1.5,2.5],
    'Bus': [16000,450,150000,100000,250000,35000,800000,1.1,3.5,5.5],
}
COLS = {
    'Passenger': 'Passenger Car Traffic (Mio Vehicle-Km Annual)',
    'Bus': 'Bus and Motor Coach Traffic (Mio Vehicle-Km Annual)',
    'Freight': 'Total Van, Pickup, Lorry and Road Tractor Traffic (Mio Vehicle-Km Annual)',
}
STOCK = {
    'Passenger': 'Passenger Cars In Use (n)',
    'Bus': 'Buses and Motor Coaches In Use (n)',
    'Freight': 'Total Vans, Pickups, Lorries and Road Tractors In Use (n)',
}
BASE = ['Population', *list(STOCK.values()), 'Motorway or Highway Network (km)',
        'Main or National Road Network - Total (km)',
        'Secondary or Regional Road Network - Total (km)',
        'Other Roads - Combined (Urban and Rural) - Total (km)',
        'GDP_per_capita', 'Urbanization_Rate']
FEATURES = {'retained_ten': BASE,
            'all_thirteen': BASE + ['Inland transport CO2 emissions by ROAD (Million Tonnes of CO2 / year)',
                                    'Total Four-wheeled Vehicles in Use (n)',
                                    'Total Road Network - All Road Types - Total (km)']}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_csv(name, rows):
    pd.DataFrame(rows).to_csv(OUT/name, index=False, encoding='utf-8-sig')

CHECKS = []
def check(name, value, limit, passed=None):
    CHECKS.append(dict(check=name, value=float(value), limit=float(limit),
                       passed=bool(value <= limit if passed is None else passed)))

def assemble(label):
    ms,mu,ip,ir,ks,cs,kt,t,a,b = PARAMS[label]
    B=np.zeros((4,7)); B[:,0]=1; B[:,1]=[a,a,-b,-b]; B[:,2]=[-t,t,-t,t]
    B[np.arange(4),np.arange(3,7)]=-1
    M=np.diag([ms,ip,ir,mu,mu,mu,mu])
    C=cs*B.T@B; K=ks*B.T@B; K[3:,3:]+=kt*np.eye(4)
    R=np.zeros((7,4)); R[3:]=kt*np.eye(4)
    return M,C,K,R,B

def response(label, speed=20., rho=.5, points=12000, g0=.001024, delay=True):
    M,C,K,R,B=assemble(label)
    ms,mu,ip,ir,ks,cs,kt,t,a,b=PARAMS[label]
    n=np.geomspace(.01,3.,points); w=2*np.pi*n*speed
    Q=np.zeros((points,4,2),complex)
    Q[:,0,0]=1; Q[:,1,1]=1
    phase=np.exp(-2j*np.pi*n*(a+b)) if delay else np.ones(points)
    Q[:,2,0]=phase; Q[:,3,1]=phase
    Z=K[None]-w[:,None,None]**2*M[None]+1j*w[:,None,None]*C[None]
    H=np.linalg.solve(Z,np.einsum('ij,njk->nik',R,Q))
    V=1j*w[:,None,None]*np.einsum('ij,njk->nik',B,H)
    S=np.array([[1,rho],[rho,1]])
    g=g0*(n/.1)**-2
    power=float(np.trapz(cs*np.einsum('nia,ab,nib->n',V,S,V.conj()).real*g,n))
    tire=kt*(Q-H[:,3:,:])
    forcevar=np.trapz(np.einsum('nia,ab,nib->ni',tire,S,tire.conj()).real*g[:,None],n,axis=0)
    rms=np.sqrt(np.maximum(forcevar,0))
    static=np.array([ms*9.81*b/(2*(a+b))+mu*9.81]*2+[ms*9.81*a/(2*(a+b))+mu*9.81]*2)
    return dict(vehicle=label,speed_m_s=speed,rho=rho,points=points,g0_m3=g0,delay=delay,
                mean_power_W=power,unit_J_km=1000*power/speed,
                min_static_minus_3rms_N=float(np.min(static-3*rms)),
                front_dynamic_rms_N=float(rms[0]),rear_dynamic_rms_N=float(rms[2]))

def harmonic_check(label, freq):
    M,C,K,R,B=assemble(label); cs=PARAMS[label][5]; ks=PARAMS[label][4]; kt=PARAMS[label][6]
    wb=PARAMS[label][-2]+PARAMS[label][-1]
    w=2*np.pi*freq; period=1/freq
    qamp=.003*np.array([1,np.exp(.7j),np.exp(-1j*w*wb/20),np.exp(.7j-1j*w*wb/20)])
    X=np.linalg.solve(K-w*w*M+1j*w*C,R@qamp)
    y0=np.r_[X.real,(1j*w*X).real,0.,0.]
    def rhs(t,y):
        q=(qamp*np.exp(1j*w*t)).real; qdot=(1j*w*qamp*np.exp(1j*w*t)).real
        x=y[:7]; v=y[7:14]
        acc=np.linalg.solve(M,R@q-C@v-K@x)
        damp=cs*np.dot(B@v,B@v); work=np.dot(kt*(q-x[3:]),qdot)
        return np.r_[v,acc,damp,work]
    sol=solve_ivp(rhs,[0,period],y0,rtol=2e-10,atol=1e-12,max_step=period/250)
    def energy(y,t):
        x=y[:7]; v=y[7:14]; q=(qamp*np.exp(1j*w*t)).real
        return .5*v@M@v+.5*ks*np.dot(B@x,B@x)+.5*kt*np.dot(x[3:]-q,x[3:]-q)
    expected=.5*cs*np.sum(abs(1j*w*B@X)**2)*period
    actual=sol.y[14,-1]; work=sol.y[15,-1]; de=energy(sol.y[:,-1],period)-energy(y0,0)
    rel=abs(actual-expected)/max(expected,1e-30); balance=abs(work-actual-de)/max(expected,1e-30)
    check(label+' harmonic %.1fHz dissipation'%freq,rel,1e-6)
    check(label+' harmonic %.1fHz input work'%freq,balance,1e-6)
    return dict(vehicle=label,frequency_Hz=freq,frequency_cycle_dissipation_J=expected,
                ODE_cycle_dissipation_J=actual,road_input_work_J=work,stored_energy_change_J=de,
                relative_dissipation_error=rel,relative_balance_error=balance,solver_success=sol.success)

def fit_predict(d,features,label,train,test):
    y=pd.to_numeric(d[COLS[label]],errors='coerce').to_numpy(float)
    stock=pd.to_numeric(d[STOCK[label]],errors='coerce').to_numpy(float)
    valid=np.isfinite(y)&(y>=0); tr=np.intersect1d(train,np.flatnonzero(valid))
    X=d[features].apply(pd.to_numeric,errors='coerce'); X=np.log1p(X.where(X>=0))
    med=X.iloc[tr].median().fillna(0); X=X.fillna(med).to_numpy(float)
    scaler=StandardScaler().fit(X[tr]); ridge=Ridge(alpha=10,solver='svd')
    ridge.fit(scaler.transform(X[tr]),np.log1p(y[tr]))
    rp=np.maximum(np.expm1(ridge.predict(scaler.transform(X[test]))),0)
    mileage_tr=tr[np.isfinite(stock[tr])&(stock[tr]>0)]
    mileage=np.median(1e6*y[mileage_tr]/stock[mileage_tr])
    ok=np.isfinite(stock[test])&(stock[test]>0)
    sp=np.where(ok,stock[test]*mileage/1e6,rp)
    return rp,sp,float(mileage),len(tr),len(mileage_tr)

def main():
    print('Calculating passive vehicle response',flush=True)
    units=[]; contacts=[]; harmonics=[]
    mainunits={}
    for label in PARAMS:
        M,C,K,R,B=assemble(label)
        for name,A in [('M',M),('C',C),('K',K)]:
            check(label+' '+name+' symmetry',np.max(abs(A-A.T)),1e-9)
        check(label+' damping PSD',max(0.,-np.linalg.eigvalsh(C).min()),1e-8)
        check(label+' stiffness positive',np.linalg.eigvalsh(K).min(),0,passed=np.linalg.eigvalsh(K).min()>0)
        for pts in [12000,24000]: units.append(response(label,points=pts))
        base=units[-2]; refined=units[-1]; mainunits[label]=base['unit_J_km']
        check(label+' integration refinement',abs(base['unit_J_km']/refined['unit_J_km']-1),1e-4)
        for v in [10,15,25,30]: units.append(response(label,speed=v))
        for rho in [0,1]: units.append(response(label,rho=rho))
        units.append(response(label,delay=False))
        for i,c in enumerate('ABCDEFGH'):
            z=response(label,points=3000,g0=16e-6*4**i); z['road_class']=c; contacts.append(z)
        low=response(label,points=12000,g0=.000256)
        check(label+' PSD fourfold scaling',abs(base['unit_J_km']/low['unit_J_km']-4),1e-10)
        for f in [1,5,15]: harmonics.append(harmonic_check(label,f))
    write_csv('vehicle_unit_energy.csv',units); write_csv('contact_screen.csv',contacts)
    write_csv('harmonic_ODE_audit.csv',harmonics)
    print('Reconstructing observation-preserving national traffic',flush=True)
    inp=ROOT/'Public_release_preparation_v516/internal_test/vkt_candidate_inputs.json'
    d=pd.DataFrame(json.loads(inp.read_text(encoding='utf-8')))
    ids=np.arange(len(d)); observed=np.zeros(len(d),bool)
    for c in COLS.values(): observed|=pd.to_numeric(d[c],errors='coerce').notna().to_numpy()
    observed_ids=ids[observed]
    CV=[]; totals=[]; countries=[]; heldout=[]
    source_metrics={'Passenger':{'ridge':[1.183,.775],'stock':[1.014,.581]},
                    'Bus':{'ridge':[1.043,1.072],'stock':[.949,.950]},
                    'Freight':{'ridge':[.803,.853],'stock':[.753,.767]}}
    for feature_set,features in FEATURES.items():
        for si,seed in enumerate([42,2026]):
            pred={label:{'ridge':np.full(len(d),np.nan),'stock':np.full(len(d),np.nan)} for label in COLS}
            for train0,test0 in KFold(5,shuffle=True,random_state=seed).split(observed_ids):
                train=observed_ids[train0]; test=observed_ids[test0]
                check(feature_set+' fold country exclusion',len(np.intersect1d(train,test)),0)
                for label in COLS:
                    rp,sp,*_=fit_predict(d,features,label,train,test)
                    pred[label]['ridge'][test]=rp; pred[label]['stock'][test]=sp
            for label,col in COLS.items():
                yy=pd.to_numeric(d[col],errors='coerce').to_numpy(float); valid=np.isfinite(yy)&(yy>=0)
                for model in ['ridge','stock']:
                    metric=float(np.sqrt(mean_squared_log_error(yy[valid],pred[label][model][valid])))
                    CV.append(dict(feature_set=feature_set,seed=seed,category=label,model=model,
                                   n=int(valid.sum()),RMSLE=metric,source_SI_RMSLE=source_metrics[label][model][si],
                                   difference=metric-source_metrics[label][model][si]))
                    for j in np.flatnonzero(valid):
                        heldout.append(dict(feature_set=feature_set,seed=seed,category=label,model=model,
                            country=d.iloc[j]['Country'],country_code=d.iloc[j]['Country Code'],
                            observed_VKT_million_km=yy[j],predicted_VKT_million_km=pred[label][model][j],
                            residual_log1p=float(np.log1p(yy[j])-np.log1p(pred[label][model][j]))))
        estimates={}
        for label,col in COLS.items():
            yy=pd.to_numeric(d[col],errors='coerce').to_numpy(float); valid=np.isfinite(yy)&(yy>=0)
            rp,sp,mileage,ntrain,nstock=fit_predict(d,features,label,ids,ids)
            final=np.where(valid,yy,sp); estimates[label]=final
            check(feature_set+' '+label+' observations retained',np.max(abs(final[valid]-yy[valid])),0)
            for j,row in d.iterrows():
                countries.append(dict(feature_set=feature_set,country=row['Country'],country_code=row['Country Code'],
                       category=label,observed=bool(valid[j]),annual_VKT_million_km=final[j],
                       source_VKT_million_km=yy[j],ridge_estimate_million_km=rp[j],stock_or_ridge_estimate_million_km=sp[j],
                       training_median_km_per_vehicle=mileage,training_n=ntrain,training_valid_stock_n=nstock))
        for mix in [0,.5,1]:
            es={'Passenger':mainunits['Passenger'],'Bus':mainunits['Bus'],
                'Freight':(1-mix)*mainunits['Passenger']+mix*mainunits['Freight']}
            subtot={k:float(estimates[k].sum()*1e6*es[k]/3.6e15) for k in COLS}
            total=sum(subtot.values())
            totals.append(dict(feature_set=feature_set,freight_heavy_proxy_fraction=mix,D_mechanical_TWh_year=total,
                         source_D_TWh_year=625.263,difference_percent=100*(total/625.263-1),
                         **{k+'_TWh_year':v for k,v in subtot.items()},
                         **{k+'_share_percent':100*v/total for k,v in subtot.items()},
                         **{k+'_VKT_million_km':float(estimates[k].sum()) for k in COLS}))
    write_csv('country_traffic_reconstructed.csv',countries); write_csv('country_held_out_metrics.csv',CV)
    write_csv('country_held_out_predictions.csv',heldout)
    write_csv('global_mechanical_totals.csv',totals)
    speedrows=[]
    primary=next(t for t in totals if t['feature_set']=='retained_ten' and t['freight_heavy_proxy_fraction']==.5)
    for v in [10,15,20,25,30]:
        ee={k:next(u['unit_J_km'] for u in units if u['vehicle']==k and u['speed_m_s']==v and u['rho']==.5 and u['delay'] and u['points']==12000) for k in PARAMS}
        ee['Freight']=.5*(ee['Freight']+ee['Passenger'])
        total=sum(primary[k+'_VKT_million_km']*1e6*ee[k]/3.6e15 for k in COLS)
        speedrows.append(dict(speed_m_s=v,mechanical_TWh_year=total))
    write_csv('global_speed_sensitivity.csv',speedrows)
    # Scenario propagation only: empirical CV errors are not a calibrated confidence interval.
    h=pd.DataFrame(heldout)
    h=h[(h.feature_set=='retained_ten')&(h.model=='stock')]
    vectors=h.groupby(['country_code','category']).residual_log1p.mean().unstack().dropna()
    names=list(COLS); vec=vectors[names].to_numpy(float)
    original=pd.DataFrame(countries)
    original=original[original.feature_set=='retained_ten']
    yy=np.column_stack([original[original.category==k].annual_VKT_million_km.to_numpy() for k in names])
    fixed=np.column_stack([original[original.category==k].observed.to_numpy(bool) for k in names])
    es=np.array([mainunits['Passenger'],mainunits['Bus'],.5*(mainunits['Passenger']+mainunits['Freight'])])
    rng=np.random.default_rng(20261022); propagated=[]
    for draw in range(500):
        rr=vec[rng.integers(0,len(vec),size=len(d))]
        sampled=np.where(fixed,yy,np.maximum(np.expm1(np.log1p(yy)+rr),0))
        propagated.append(dict(draw=draw,D_mechanical_TWh_year=float(np.sum(sampled*es[None,:])*1e6/3.6e15)))
    write_csv('traffic_residual_propagation.csv',propagated)
    interval=np.quantile([z['D_mechanical_TWh_year'] for z in propagated],[.025,.5,.975])
    write_csv('numerical_checks.csv',CHECKS)
    sources=json.loads((ROOT/'NEW_DIRECTION_ACCEPTED_TEXT_20261022.json').read_text(encoding='utf-8'))
    summary=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        status='Independent SI-equation reconstruction; exact historical final traffic code not located',
        numerical_checks=len(CHECKS),numerical_checks_passed=sum(c['passed'] for c in CHECKS),
        main_units_J_km=mainunits,freight_to_passenger_ratio=mainunits['Freight']/mainunits['Passenger'],
        national_input=dict(path=str(inp.resolve()),sha256=sha(inp),countries=len(d),observed_country_union=len(observed_ids)),
        primary=primary,alternative_feature_set=next(t for t in totals if t['feature_set']=='all_thirteen' and t['freight_heavy_proxy_fraction']==.5),
        empirical_residual_scenario=dict(complete_country_vectors=len(vec),draws=500,seed=20261022,
            D_2_5_percentile_TWh=float(interval[0]),D_median_TWh=float(interval[1]),D_97_5_percentile_TWh=float(interval[2]),
            interpretation='Empirical missing-VKT scenario spread; not a calibrated confidence interval and not total model uncertainty'),
        feature_definitions=FEATURES,vehicle_parameters=PARAMS,
        source_DOCX=[dict(path=s['source'],sha256=sha(s['source'])) for s in sources],
        boundaries=['Suspension damper dissipation; not pavement-accessible work or electricity',
                    'At D the passenger and freight configurations fail the three-RMS screen; bus still passes. The combined D-H total remains formal extrapolation.',
                    'National VKT and 50:50 freight mapping contain scenario uncertainty',
                    'Numerical consistency does not establish field validation'])
    (OUT/'RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    shutil.copy2(__file__,OUT/Path(__file__).name)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__': main()
