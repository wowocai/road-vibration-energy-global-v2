"""Hard-stop complementarity reconstruction. No hard-stop force is converted to electricity."""
from pathlib import Path
import ctypes as ct,subprocess,os,json
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor,as_completed
P=Path(__file__).resolve().parent
L=1000.;ETA=144.8/239.4;RETENTION=.8
CONFIG=[('trial_energy_scale_1pair',77170.4861042,1),('trial_energy_scale_20pairs',77170.4861042,20),
        ('design_energy_scale_40rows',328946.9653136,40)]
def road(seed,n):
 f=np.fft.rfftfreq(n,L/n);ix=np.flatnonzero((f>=.01)&(f<=3))
 rng=np.random.default_rng(seed);ph=np.exp(2j*np.pi*rng.random((len(ix),2)))
 ph[:,1]=.5*ph[:,0]+np.sqrt(.75)*ph[:,1]
 co=np.zeros((n+1,4),complex)
 z=2*n*np.sqrt(16e-6*(f[ix,None]/.1)**-2/(2*L))*ph
 co[ix,:2]=z;co[ix,2:]=z*np.exp(-2j*np.pi*f[ix,None]*2.8)
 return np.ascontiguousarray(np.fft.irfft(co,n=2*n,axis=0))
_lib=None
def sim(rd,k,n,rows=20,tau=.025,stroke=.005,offset=10.,warm=1000.):
 global _lib
 if _lib is None:
  _lib=ct.CDLL(str(P/'constrained.so')).simulate
  vec=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
  _lib.argtypes=[vec,ct.c_int,ct.c_int,*([ct.c_double]*6),vec]
 o=np.empty(11);_lib(rd,n,round(warm/(L/n)),L/n,L/rows,offset,k,tau,stroke,o)
 return o
def run_seed(seed,n=131072):
 rows=[];r=road(seed,n);offset=10+(seed-3101)*.73
 for i,iso in enumerate('ABCDEFGH'):
  for sign in [-1,1]:
   rd=np.ascontiguousarray(r*2**i*sign)
   ref=sim(rd,0,n)
   for name,k,density in CONFIG:
    for stroke in [.005,.01,.025]:
     z=sim(rd,k,n,rows=density,stroke=stroke,offset=offset)
     dw=z[2]+z[3]-ref[2]-ref[3]
     budget=z[1]+z[0]-ref[0]+z[4]-ref[4]
     assert np.isfinite(z).all()
     assert z[6]<=stroke+2e-12,(seed,iso,z[6],stroke)
     rows.append([seed,iso,sign,name,density,stroke,z[1],z[0]-ref[0],z[4]-ref[4],dw,
      z[1]*ETA*RETENTION,z[6],z[7],z[8],z[9],z[10],z[5],ref[5],dw-budget])
 cols=['seed','ISO','phase_sign','configuration','pairs_or_rows_per_km','stroke_m','plate_work_J_per_km',
 'suspension_change_J_per_km','terminal_energy_change_J_per_km','extra_wheel_work_J_per_km',
 'delivered_electricity_J_per_km','peak_displacement_m','no_contact_fraction','peak_tire_force_N',
 'peak_stop_reaction_N','stop_time_fraction','energy_residual_J','reference_energy_residual_J',
 'paired_energy_residual_J']
 d=pd.DataFrame(rows,columns=cols);d.to_csv(P/f'seed_{seed}.csv',index=False)
 return seed
def summary():
 from scipy.stats import t
 d=pd.concat([pd.read_csv(x) for x in sorted(P.glob('seed_*.csv'))],ignore_index=True)
 d.to_csv(P/'constrained_realizations.csv',index=False)
 g=['configuration','pairs_or_rows_per_km','stroke_m','ISO']
 s=d.groupby(g).mean(numeric_only=True)
 s['electricity_to_extra_work_ratio']=s.delivered_electricity_J_per_km/s.extra_wheel_work_J_per_km
 s['extra_Wh_per_vehicle_km_50pct_interaction']=s.extra_wheel_work_J_per_km*.5/3600
 s['electricity_Wh_per_vehicle_km_50pct_interaction']=s.delivered_electricity_J_per_km*.5/3600
 byseed=d.groupby(g+['seed']).extra_wheel_work_J_per_km.mean().groupby(g).agg(['std','count'])
 s['extra_work_seed95_halfwidth_J']=t.ppf(.975,byseed['count']-1)*byseed['std']/np.sqrt(byseed['count'])
 s.to_csv(P/'constrained_summary.csv')
 print(s.loc['trial_energy_scale_20pairs'][['plate_work_J_per_km','extra_wheel_work_J_per_km',
  'delivered_electricity_J_per_km','extra_work_seed95_halfwidth_J']].round(3).to_string())
def main():
 subprocess.run(['cc','-O3','-shared','-fPIC',str(P/'constrained.c'),'-o',str(P/'constrained.so'),'-lm'],check=True)
 with ProcessPoolExecutor(max_workers=4) as pool:
  tasks=[pool.submit(run_seed,seed) for seed in range(3101,3117) if not (P/f'seed_{seed}.csv').exists()]
  for f in as_completed(tasks): print('completed',f.result(),flush=True)
 summary()
if __name__=='__main__':main()
