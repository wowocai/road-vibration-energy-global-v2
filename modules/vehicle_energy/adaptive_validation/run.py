from pathlib import Path
import ctypes as ct,subprocess,time,json
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
subprocess.run(['cc','-O3','-shared','-fPIC',str(P/'adaptive.c'),'-o',str(P/'adaptive.so'),'-lm'],check=True)
_f=ct.CDLL(str(P/'adaptive.so')).simulate
vec=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
_f.argtypes=[vec,vec,ct.c_int,*([ct.c_double]*12),vec];_f.restype=ct.c_int
COLS=['plate_J','extra_wheel_J','suspension_change_J','terminal_change_J','balance_with_J',
 'balance_without_J','balance_paired_J','off_fraction','reference_off_fraction','peak_q_m',
 'peak_tire_force_N','accepted_steps','rejected_steps','events','suspension_with_J','suspension_without_J']
def road(seed,n=65536,L=1000.):
 f=np.fft.rfftfreq(n,L/n);ix=np.flatnonzero((f>=.01)&(f<=3))
 rng=np.random.default_rng(seed);ph=np.exp(2j*np.pi*rng.random((len(ix),2)))
 ph[:,1]=.5*ph[:,0]+np.sqrt(.75)*ph[:,1]
 co=np.zeros((n//2+1,4),complex)
 z=n*np.sqrt(16e-6*(f[ix,None]/.1)**-2/(2*L))*ph
 co[ix,:2]=z;co[ix,2:]=z*np.exp(-2j*np.pi*f[ix,None]*2.8)
 return np.ascontiguousarray(np.fft.irfft(co,n=n,axis=0)),np.ascontiguousarray(np.fft.irfft(co*(2j*np.pi*f[:,None]),n=n,axis=0))
def sim(seed=3101,iso='H',stroke=.005,rtol=2e-6,maxdt=.005,warm=1000.,length=1000.,speed=50.,n=65536,sign=1):
 r,dr=road(seed,n);o=np.empty(16)
 t=time.monotonic()
 ret=_f(r,dr,n,1000.,speed/3.6,77170.4861042,.025,stroke,20.,10.+(seed-3101)*.73,
        sign*2**('ABCDEFGH'.index(iso)),warm,length,rtol,maxdt,o)
 if ret:raise RuntimeError((ret,seed,iso,stroke,rtol,maxdt))
 return dict(seed=seed,ISO=iso,stroke_m=stroke,rtol=rtol,maxdt=maxdt,warm_m=warm,
  length_m=length,speed_kmh=speed,road_n=n,sign=sign,seconds=time.monotonic()-t,**dict(zip(COLS,o)))
if __name__=='__main__':
 rows=[]
 for iso in ['A','G','H']:
  for tol,dt in [(1e-5,.005),(2e-6,.0025),(4e-7,.00125)]:
   d=sim(iso=iso,rtol=tol,maxdt=dt);rows.append(d);print(json.dumps(d),flush=True)
 pd.DataFrame(rows).to_csv(P/'pilot.csv',index=False)
