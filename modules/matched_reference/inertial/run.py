from pathlib import Path
import ctypes as ct,time
import numpy as np
from scipy.optimize import minimize
from scipy.interpolate import CubicHermiteSpline
P=Path(__file__).resolve().parent
vec=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS')
f=ct.CDLL(str(P/'model.so')).simulate
f.argtypes=[vec,vec,ct.c_int,*([ct.c_double]*19),vec,vec];f.restype=ct.c_int
COLS=['plate_J','net_wheel_J','suspension_change_J','terminal_change_J','balance_with_J','balance_without_J','balance_paired_J','off_fraction','reference_off_fraction','peak_q_m','peak_tire_force_N','accepted_steps','rejected_steps','events','suspension_with_J','suspension_without_J','tire_loss_with_J','tire_loss_without_J','stop_loss_with_J','stop_loss_without_J','peak_travel_m','peak_pitch_rad','peak_roll_rad','end_time_s','measured_distance_m','total_distance_m','positive_increment_J','negative_increment_J','plate_impact_loss_J','plate_viscous_loss_J']
def road(seed,L,n,patch=.13625,rho=1.):
 freq=np.fft.rfftfreq(n,L/n);ix=np.flatnonzero((freq>=.01)&(freq<=3))
 rng=np.random.default_rng(seed);ph=np.exp(2j*np.pi*rng.random((len(ix),2)));gam=np.exp(-rho*1.6*freq[ix]);ph[:,1]=gam*ph[:,0]+np.sqrt(1-gam**2)*ph[:,1]
 co=np.zeros((n//2+1,4),complex);z=n*np.sqrt(16e-6*(freq[ix,None]/.1)**-2/(2*L))*ph
 if patch:z*=np.sinc(freq[ix,None]*patch)
 co[ix,:2]=z;co[ix,2:]=z*np.exp(-2j*np.pi*freq[ix,None]*2.8)
 return np.ascontiguousarray(np.fft.irfft(co,n=n,axis=0)),np.ascontiguousarray(np.fft.irfft(co*(2j*np.pi*freq[:,None]),n=n,axis=0))
def equilibrium(r0,g,stroke,travel,stop_k,kp=77170.4861042):
 sc=2000/1840;ks=22000*sc;kt=200000*sc
 a=np.array([1.2,1.2,-1.6,-1.6]);b=np.array([-.8,.8,-.8,.8]);side=np.array([0,1,0,1]);stat=(1600*9.81*np.where(a>0,1.6,1.2)/5.6+60*9.81)*sc
 fit=np.linalg.lstsq(np.column_stack([np.ones(4),a,b]),r0,rcond=None)[0];th=np.arcsin(np.clip(fit[1],-.8,.8));ph=np.arcsin(np.clip(fit[2]/np.cos(th),-.8,.8));x0=np.r_[fit[0],th,ph,r0,0.,0.]
 def fun(x):
  jp=a*np.cos(x[1])-b*np.sin(x[1])*np.sin(x[2]);jr=b*np.cos(x[1])*np.cos(x[2]);z=x[0]+a*np.sin(x[1])+b*np.cos(x[1])*np.sin(x[2])-x[3:7]
  ex=np.maximum(0,np.abs(z)-travel) if travel>0 else np.zeros(4);fs=ks*z+stop_k*ex*np.sign(z)
  de=np.maximum(0,stat/kt+r0-g*x[7:9][side]-x[3:7]);F=kt*de
  en=.5*np.sum(ks*z*z+stop_k*ex*ex+kt*de*de)+np.dot(stat,x[3:7])+.5*kp*np.sum(x[7:9]**2)
  grad=np.r_[fs.sum(),np.dot(fs,jp),np.dot(fs,jr),stat-fs-F,kp*x[7]-np.sum(g[side==0]*F[side==0]),kp*x[8]-np.sum(g[side==1]*F[side==1])]
  return en,grad
 opt=minimize(fun,x0,jac=True,method='L-BFGS-B',bounds=[(None,None),(-1.2,1.2),(-1.2,1.2)]+[(None,None)]*4+[(0,stroke)]*2,options=dict(ftol=1e-15,gtol=1e-6,maxiter=3000,maxls=50))
 res=float(np.max(np.abs(fun(opt.x)[1][:7])))
 if res>.2:raise RuntimeError(('static equilibrium failed',res))
 out=np.zeros(20);out[:7]=opt.x[:7];out[14:16]=opt.x[7:9];return out,res

def sim(seed=3101,iso='A',stroke=.02,speed=50.,warm=200.,length=1000.,road_length=1000.,rtol=2e-6,maxdt=.01,sign=1,patch=.13625,rho=1.,travel=.08,ctire=400.,stop_k=2e6,offset=None,plate_k=40000.,tau=.06116776015056465,amplitude=None,height=.02,contact_patch=.13625,return_tau=.02,plate_mass=20.):
 n=2**int(np.ceil(np.log2(road_length/.02)));r,dr=road(seed,road_length,n,patch,rho);amp=sign*2**('ABCDEFGH'.index(iso)) if amplitude is None else amplitude;offset=10.+(seed-3101)*.73 if offset is None else offset
 spline=CubicHermiteSpline(np.arange(n+1)*road_length/n,np.vstack([r,r[0]]),np.vstack([dr,dr[0]]));r0=amp*spline((-warm)%road_length)
 gatex=(-warm-np.array([0,0,2.8,2.8])-offset)%50;g=np.where(gatex<1.1,np.sin(np.pi*gatex/1.1)**2,0.)
 init=np.zeros(53);init[:20],res=equilibrium(r0,g,stroke,travel,stop_k,plate_k);init[20:40],res0=equilibrium(r0,np.zeros(4),stroke,travel,stop_k,plate_k)
 out=np.empty(30);tt=time.monotonic()
 ret=f(r,dr,n,road_length,speed/3.6,plate_k,tau,stroke,20.,offset,amp,warm,length,rtol,maxdt,travel,ctire,stop_k,height,contact_patch,return_tau,plate_mass,init,out)
 if ret<0:raise RuntimeError(('integrator error',ret))
 return dict(plate_mass_kg=plate_mass,return_tau_s=return_tau,return_c_Ns_m=plate_k*return_tau,height_m=height,contact_patch_m=contact_patch,profile="reconstructed cubic S",plate_k_N_m=plate_k,tau_s=tau,plate_c_Ns_m=plate_k*tau,amplitude=amp,status='completed' if ret==0 else 'orientation_limit',seed=seed,ISO=iso,stroke_m=stroke,speed_kmh=speed,warm_m=warm,length_m=length,road_length_m=road_length,rtol=rtol,maxdt=maxdt,sign=sign,patch_m=patch,rho=rho,travel_m=travel,ctire=ctire,stop_k=stop_k,offset_m=offset,equilibrium_residual_N=max(res,res0),seconds=time.monotonic()-tt,**dict(zip(COLS,out)))
if __name__=='__main__':
 import json
 print(json.dumps(sim(),indent=2))
