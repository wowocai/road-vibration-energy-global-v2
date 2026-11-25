"""Literature-input-matched coupled reference, with uniform calibrated device parameters."""
from pathlib import Path
import argparse,sys,json,subprocess
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
from scipy.stats import t
P=Path(__file__).resolve().parent
if not (P/'inertial/model.so').exists():
    subprocess.run(['cc','-O3','-shared','-fPIC',str(P/'inertial/model.c'),'-lm','-o',str(P/'inertial/model.so')],check=True)
sys.path.insert(0,str(P/'inertial'))
from run import sim

def task(config):
    iso,seed,sign=config
    # One calibrated device is used throughout; G/H extend the analysis to slow passage.
    speed=50 if iso in 'ABCDEF' else (5 if iso=='G' else 2)
    tau=.06116776015056465
    z=sim(seed=seed,iso=iso,sign=sign,speed=speed,tau=tau,maxdt=.0015,rtol=2e-6)
    if z['status']!='completed':raise RuntimeError(z['status'])
    passages=z['length_m']/50
    z['pair_mechanical_J']=z['plate_J']/passages
    z['pair_added_wheel_J']=z['net_wheel_J']/passages
    z['pair_delivered_J']=z['pair_mechanical_J']*(144.8/239.4)*.8
    return z

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--quick',action='store_true');ap.add_argument('--iso',choices=list('ABCDEFGH'),default='A');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--output',type=Path,default=P/'out');args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    cases=[(args.iso,3101,1)] if args.quick else [(iso,seed,sign) for iso in 'ABCDEFGH' for seed in range(3101,3117) for sign in [-1,1]]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:rows=list(pool.map(task,cases))
    raw=pd.DataFrame(rows);raw.to_csv(args.output/'individual_trajectories.csv',index=False)
    if args.quick:print(json.dumps(rows[0],indent=2))
    else:
        seeds=raw.groupby(['ISO','seed']).mean(numeric_only=True).reset_index();seeds.to_csv(args.output/'individual_seed_means.csv',index=False)
        summaries=[]
        for iso,g in seeds.groupby('ISO'):
            r={'ISO':iso,'n_seeds':len(g),'speed_kmh':g.speed_kmh.iloc[0],'loading_c_Ns_m':g.plate_c_Ns_m.iloc[0]}
            for k in ['pair_mechanical_J','pair_added_wheel_J','pair_delivered_J']:
                r[k]=float(g[k].mean());r[k+'_half95']=float(t.ppf(.975,len(g)-1)*g[k].std(ddof=1)/np.sqrt(len(g)))
            r['extra_wheel_J_per_traffic_vehicle_km']=r['pair_added_wheel_J']*20*.5
            r['delivered_J_per_traffic_vehicle_km']=r['pair_delivered_J']*20*.5
            r['delivered_to_added_pct']=100*r['pair_delivered_J']/r['pair_added_wheel_J']
            summaries.append(r)
        pd.DataFrame(summaries).to_csv(args.output/'matched_reference_A_H.csv',index=False)
