from pathlib import Path
import ctypes as ct,subprocess,time
import numpy as np
P=Path(__file__).resolve().parent
subprocess.run(['cc','-O3','-shared','-fPIC',str(P/'variant.c'),'-o',str(P/'variant.so'),'-lm'],check=True)
f=ct.CDLL(str(P/'variant.so')).simulate
vec=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
f.argtypes=[vec,vec,ct.c_int,*([ct.c_double]*14),vec];f.restype=ct.c_int
COLS=['plate_J','extra_wheel_J','suspension_change_J','terminal_change_J','balance_with_J','balance_without_J','balance_paired_J','off_fraction','reference_off_fraction','peak_q_m','peak_tire_force_N','accepted_steps','rejected_steps','events','suspension_with_J','suspension_without_J','peak_suspension_travel_m']
def road(seed,L,n,patch=0):
 freq=np.fft.rfftfreq(n,L/n);ix=np.flatnonzero((freq>=.01)&(freq<=3))
 rng=np.random.default_rng(seed);ph=np.exp(2j*np.pi*rng.random((len(ix),2)))
 ph[:,1]=.5*ph[:,0]+np.sqrt(.75)*ph[:,1]
 co=np.zeros((n//2+1,4),complex)
 z=n*np.sqrt(16e-6*(freq[ix,None]/.1)**-2/(2*L))*ph
 if patch:z*=np.sinc(freq[ix,None]*patch)
 co[ix,:2]=z;co[ix,2:]=z*np.exp(-2j*np.pi*freq[ix,None]*2.8)
 return np.ascontiguousarray(np.fft.irfft(co,n=n,axis=0)),np.ascontiguousarray(np.fft.irfft(co*(2j*np.pi*freq[:,None]),n=n,axis=0))
def sim(seed=3101,iso='H',stroke=.005,rtol=2e-6,maxdt=.0025,warm=1000.,length=1000.,speed=50.,sign=1,patch=0,travel=0,stopratio=10,road_length=1000.):
 n=2**int(np.ceil(np.log2(road_length/.02)))
 r,dr=road(seed,road_length,n,patch);o=np.empty(17);t=time.monotonic()
 ret=f(r,dr,n,road_length,speed/3.6,77170.4861042,.025,stroke,20.,10.+(seed-3101)*.73,sign*2**('ABCDEFGH'.index(iso)),warm,length,rtol,maxdt,travel,stopratio,o)
 if ret:raise RuntimeError((ret,seed,iso,stroke))
 return dict(seed=seed,ISO=iso,stroke_m=stroke,rtol=rtol,maxdt=maxdt,warm_m=warm,length_m=length,speed_kmh=speed,sign=sign,patch_m=patch,travel_m=travel,stopratio=stopratio,road_length_m=road_length,seconds=time.monotonic()-t,**dict(zip(COLS,o)))
if __name__=='__main__':
 import json
 for kw in [dict(),dict(patch=.3048),dict(travel=.08),dict(patch=.3048,travel=.08),dict(speed=20),dict(speed=10)]:
  z=sim(**kw);print(json.dumps(z),flush=True)
