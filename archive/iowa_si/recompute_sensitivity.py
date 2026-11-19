from pathlib import Path
from itertools import product
import ast
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
P=(HERE/'inputs.csv')
if not P.exists(): P=HERE.parent/'iowa_audit/filtered_records.csv'
M=HERE/'source_vehicle_model.py'
if not M.exists(): M=HERE.parent/'geo_check/unpacked/reproduce_vehicle_resource_20261022.py'
g={'np':np}
for node in ast.parse(M.read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PARAMS' for t in node.targets) or isinstance(node,ast.FunctionDef) and node.name in ['assemble','response']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(M),'exec'),g)
d=pd.read_csv(P)
assert len(d)==3903
assert abs(d.PMIS_LENGTH.sum()*1.609344-16830.63220608)<1e-6
assert (d[['IRI','SPEED','PMIS_LENGTH','AADT']]>0).all().all()
assert ((d.TRUCKS>=0)&(d.TRUCKS<=d.AADT)).all()
iri=d.IRI.to_numpy()*0.0254/1.609344
n=np.geomspace(.01,3,12000)
v=80/3.6; w=2*np.pi*n*v
K=np.array([[63.3,-63.3],[-63.3,716.3]])
C=np.array([[6.,-6.],[-6.,6.]])
Z=K-w[:,None,None]**2*np.diag([1.,.15])+1j*w[:,None,None]*C
z=np.linalg.solve(Z,np.tile([0.,653.],(len(n),1))[:,:,None])[:,:,0]
H=np.abs(1j*w*(z[:,0]-z[:,1]))**2*np.sinc(n*.25)**2
slopes=[1.5,2.,2.5]
spectra=np.array([(n/.1)**(-s) for s in slopes])
integrate=lambda x: np.trapezoid(x,n,axis=-1)
coeff=np.sqrt(2/np.pi)*1000/v*np.sqrt(integrate(spectra*H))
assert np.isclose(coeff[1],543.1416455,rtol=1e-7)
from functools import lru_cache
@lru_cache(None)
def response(label,speed):
    M,C,K,R,B=g['assemble'](label)
    ms,mu,ip,ir,ks,cs,kt,t,a,b=g['PARAMS'][label]
    w=2*np.pi*n*speed
    Q=np.zeros((len(n),4,2),complex)
    Q[:,0,0]=Q[:,1,1]=1
    Q[:,2,0]=Q[:,3,1]=np.exp(-2j*np.pi*n*(a+b))
    Z=K-w[:,None,None]**2*M+1j*w[:,None,None]*C
    X=np.linalg.solve(Z,R@Q)
    V=1j*w[:,None,None]*(B@X)
    S=np.array([[1,.5],[.5,1]])
    variance=lambda q: np.einsum('nia,ab,nib->ni',q,S,q.conj()).real
    unit=1000/speed*cs*integrate(spectra*variance(V).sum(axis=1))
    F=kt*(Q-X[:,3:,:])
    rms=np.sqrt(integrate(spectra[:,None,:]*variance(F).T))
    static=np.array([ms*9.81*b/(2*(a+b))+mu*9.81]*2+[ms*9.81*a/(2*(a+b))+mu*9.81]*2)
    return unit,rms,static
def run(speeds,mixes):
    rows=[]
    for speed_factor,s,mix in product(speeds,range(3),mixes):
        speed=d.SPEED.to_numpy()*.44704*speed_factor if speed_factor!='fixed20' else np.full(len(d),20.)
        power={};contact={}
        for label in ['Passenger','Freight']:
            responses=[response(label,x) for x in speed]
            power[label]=np.array([r[0] for r in responses])
            rms=np.array([r[1][s] for r in responses]); load=np.array([r[2] for r in responses])
            contact[label]=(load-3*rms*iri[:,None]/coeff[s]).min(axis=1)
        factors=iri**2/coeff[s]**2
        vkt=d.PMIS_LENGTH.to_numpy()*1.609344*365
        truck=d.TRUCKS.to_numpy(); total=d.AADT.to_numpy()
        matrix=(power['Passenger']*(total-truck*mix)[:,None]+power['Freight']*(truck*mix)[:,None])*vkt[:,None]/3.6e12
        E=(matrix[:,s]*factors).sum()
        A=matrix[:,1].sum()*16e-6
        same_shape=matrix[:,s].sum()*16e-6
        flag=((contact['Passenger']<0)&(total-truck*mix>0))|((contact['Freight']<0)&(truck*mix>0))
        rows.append(dict(spectral_exponent=slopes[s],speed_fraction=speed_factor,heavy_proxy_fraction=mix,iri_gwh=E,iso_a_gwh=A,iso_b_gwh=4*A,iri_to_iso_a=E/A,matched_slope_reference_gwh=same_shape,iri_to_matched_slope_reference=E/same_shape,contact_screen_flagged_records=int(flag.sum()),flagged_iri_gwh=float((matrix[flag,s]*factors[flag]).sum()),golden_car_coefficient=coeff[s]))
    return pd.DataFrame(rows)
if __name__=='__main__':
    x=run([.8,1.,'fixed20'],[0.,.5,1.])
    assert len(x)==27 and not x.duplicated(['spectral_exponent','speed_fraction','heavy_proxy_fraction']).any()
    assert (x[['iri_gwh','iso_a_gwh','matched_slope_reference_gwh']]>0).all().all()
    baseline=x[(x.speed_fraction==.8)&(x.spectral_exponent==2)&(x.heavy_proxy_fraction==1)].iloc[0]
    assert np.allclose([baseline.iri_gwh,baseline.iso_a_gwh,baseline.iso_b_gwh],[9.928240999128802,21.83906105197383,87.35624420789532],rtol=1e-7)
    assert (x.iri_to_iso_a<1).all() and (x.iri_to_matched_slope_reference<1).all()
    x.to_csv(HERE/'Iowa_27_scenarios.csv',index=False)
    print(x.agg({c:['min','max'] for c in ['iri_gwh','iso_a_gwh','iri_to_iso_a','iri_to_matched_slope_reference','contact_screen_flagged_records']}))
    print(x.loc[x.iri_gwh.idxmin()].to_dict())
    print(x.loc[x.iri_gwh.idxmax()].to_dict())
