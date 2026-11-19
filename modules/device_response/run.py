"""Reference Duarte A-H nonlinear contact audit. Run from any folder; needs cc, NumPy, SciPy."""
from pathlib import Path
import ctypes as ct
import subprocess, os, sys, json, csv
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy.signal import lfilter
from scipy.stats import t
from concurrent.futures import ProcessPoolExecutor
P=Path(__file__).resolve().parent
root=P.parent
V=50/3.6
N0=65536; LROAD=1024.; DX0=LROAD/N0; WB=2.8; GRADE='ABCDEFGH'; TAUS=[.01,.025,.05]
ROAD_N=np.fft.rfftfreq(N0,DX0)
FREQ=ROAD_N[(ROAD_N>=.01)&(ROAD_N<=3)]
PSD=16e-6*(FREQ/.1)**-2
SEEDS=list(range(3101,3117))
STATIC=np.array([(1600*9.81*1.6/5.6+60*9.81)]*2+[(1600*9.81*1.2/5.6+60*9.81)]*2)*(2000/1840)
lib=None

def vehicle(roads,n,dx,mode,nonlinear,warm_m=128):
    global lib
    if lib is None:
        lib=ct.CDLL(str(P/'vehicle.so')).run
        vector=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
        lib.argtypes=[vector,ct.c_int,ct.c_int,ct.c_double,ct.c_int,ct.c_int,vector,ct.POINTER(ct.c_double)]
        lib.restype=ct.c_double
    out=np.empty((n,4))
    balance=ct.c_double()
    loss=lib(roads,n,round(warm_m/dx),dx/V,mode,nonlinear,out,ct.byref(balance))
    assert np.isfinite(out).all()
    if nonlinear: assert out.min()>=0
    return out,loss/LROAD,balance.value/max(loss,1e-14)

def synthesise(seed,n):
    rng=np.random.default_rng(seed)
    ph=np.exp(2j*np.pi*rng.random((len(FREQ),2)))
    ph[:,1]=.5*ph[:,0]+np.sqrt(.75)*ph[:,1]
    idx=rng.permutation(N0)[:128]
    two=2*n
    co=np.zeros((n+1,4),complex)
    bins=np.rint(FREQ*LROAD).astype(int)
    z=two*np.sqrt(PSD[:,None]/(2*LROAD))*ph
    co[bins,:2]=z
    co[bins,2:]=z*np.exp(-2j*np.pi*FREQ[:,None]*WB)
    return np.fft.irfft(co,n=two,axis=0),idx

def calc_events(force,idx,dx):
    n=len(force)
    y=(np.arange(390)+.5)*.01
    grid=idx[:,None]*(n//N0)+y/dx
    low=np.floor(grid).astype('int64')
    u=grid-low
    load=force[low%n]*(1-u[...,None])+force[(low+1)%n]*u[...,None]
    def g(x):return np.where((x>0)&(x<1.1),np.sin(np.pi*x/1.1)**2,0.)
    load=load[:,:,:2]*g(y)[None,:,None]+load[:,:,2:]*g(y-WB)[None,:,None]
    def energy(tau):
        a=np.exp(-.01/(V*tau))
        zz=lfilter([1-a],[1,-a],load,axis=1)
        prev=np.concatenate([np.zeros_like(zz[:,:1,:]),zz[:,:-1,:]],axis=1)
        out=.5*(1-a*a)*np.sum((load-prev)**2,axis=(1,2))+.5*np.sum(zz[:,-1,:]**2,axis=-1)
        inp=np.sum(load*(zz-prev),axis=(1,2))
        assert np.allclose(out,inp,rtol=3e-12)
        return out.mean()
    # Alternative model: plate follows a fixed stroke trajectory; work is linear in wheel force.
    return [*(energy(tau) for tau in TAUS),load.sum(axis=(1,2)).mean()]

def job(args):
    seed,refine,mode=args
    n=N0*refine; dx=LROAD/n
    road,idx=synthesise(seed,n)
    rows=[]
    for i,grade in enumerate('0'+GRADE):
        if refine==4 and grade not in ('A','G','H'): continue
        for sign in ([1] if i==0 else [-1,1]):
            rd=road*(0 if i==0 else sign*2**(i-1))
            f,diss,res=vehicle(rd,n,dx,mode,True,warm_m=1024 if i>=7 else 256)
            mean_err=np.max(np.abs(f.mean(0)/STATIC-1))
            if not i: assert np.allclose(f,STATIC) and diss<1e-20
            rows.append([seed,refine,mode,grade,sign,*calc_events(f,idx,dx),diss,(f==0).mean(),(f==0).any(axis=1).mean(),res,mean_err])
            if i==1 and refine==1 and mode==0:
                ff,dd,_=vehicle(rd,n,dx,mode,False,warm_m=256)
                assert ff.min()>0
                assert np.max(np.abs(f-ff))/STATIC.min()<1e-5 and abs(diss/dd-1)<1e-5
            if i>=7 and refine==2 and mode==0:
                ff,dd,rr=vehicle(rd,n,dx,mode,True,warm_m=2048)
                rows.append([seed,3,mode,grade,sign,*calc_events(ff,idx,dx),dd,(ff==0).mean(),(ff==0).any(axis=1).mean(),rr,np.max(np.abs(ff.mean(0)/STATIC-1))])
            elif refine==2 and mode==0:
                rows.append([seed,3,mode,grade,sign,*calc_events(f,idx,dx),diss,(f==0).mean(),(f==0).any(axis=1).mean(),res,mean_err])
    return rows

def main():
    subprocess.run(['cc','-O3','-fPIC','-shared',str(P/'vehicle.c'),'-o',str(P/'vehicle.so')],check=True)
    extra='--fine-check' in sys.argv
    combos=[(seed,ref,mode) for ref,mode in ([(4,0)] if extra else [(1,0),(2,0),(1,1),(4,0)]) for seed in SEEDS]
    with ProcessPoolExecutor(max_workers=min(7,os.cpu_count() or 1)) as pool:
        results=[r for sub in pool.map(job,combos) for r in sub]
    cols=['seed','refinement','vehicle_proxy','iso','phase_sign','work_tau10','work_tau25','work_tau50','fixed_stroke_linear_work','suspension_J_per_m','tire_time_out_of_contact','vehicle_time_any_tire_out_of_contact','energy_residual_relative','max_mean_wheel_load_relative_error']
    with (P/'phase_results.csv').open('a' if extra else 'w') as f:
        wr=csv.writer(f)
        if not extra: wr.writerow(cols)
        wr.writerows(results)
    print('vehicle simulation complete',len(results),flush=True)

if __name__=='__main__':main()
