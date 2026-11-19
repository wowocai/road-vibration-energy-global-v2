from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,sys
import variant_run as m
P=Path(__file__).resolve().parent

def task(a):
 name,kw=a;f=P/'diagnostic_runs'/f'{name}.json';f.parent.mkdir(exist_ok=True)
 if f.exists():return name
 rows=[m.sim(**kw,sign=s) for s in [-1,1]]
 f.write_text(json.dumps(dict(name=name,cases=rows)));return name

if __name__=='__main__':
 mode=sys.argv[1];args=[]
 if mode=='precision':
  for seed in range(3101,3109):
   for h in [.005,.01,.025]:
    for tag,tol,dt in [('medium',2e-6,.0025),('fine',4e-7,.00125),('finest',8e-8,.000625)]:
     args.append((f'p_{seed}_{h}_{tag}',dict(seed=seed,stroke=h,rtol=tol,maxdt=dt)))
 elif mode=='details':
  for seed in range(3101,3109):
   for tag,kw in [('point',{}),('patch',dict(patch=.3048)),('stops',dict(travel=.08,stopratio=1000)),('both',dict(patch=.3048,travel=.08,stopratio=1000)),('v20',dict(speed=20)),('v10',dict(speed=10))]:
    args.append((f'd_{seed}_{tag}',dict(seed=seed,**kw)))
 elif mode=='nonperiodic':
  for seed in range(3101,3117):
   for h in [.005,.01,.025]:
    args.append((f'n_{seed}_{h}',dict(seed=seed,stroke=h,road_length=8000,warm=1000,length=4000)))
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,a) for a in args]),1):print(i,'/',len(args),f.result(),flush=True)
