from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,json,time
import pandas as pd
import run as m
P=Path(__file__).resolve().parent
def task(args):
 name,seed,iso,h,tol,dt,warm,length,speed=args
 f=P/'runs'/f'{name}_{seed}_{iso}_{h:g}_{speed:g}.json';f.parent.mkdir(exist_ok=True)
 if f.exists():return f.name
 out=[m.sim(seed=seed,iso=iso,stroke=h,rtol=tol,maxdt=dt,warm=warm,length=length,speed=speed,sign=sign) for sign in [-1,1]]
 f.write_text(json.dumps({'name':name,'cases':out}));return f.name
def execute(tasks):
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,f in enumerate(as_completed([pool.submit(task,x) for x in tasks]),1):
   print(i,'/',len(tasks),f.result(),flush=True)
def table():
 rows=[]
 for f in (P/'runs').glob('*.json'):
  z=json.loads(f.read_text())
  for r in z['cases']:rows.append(dict(batch=z['name'],**r))
 d=pd.DataFrame(rows);d.to_csv(P/'all_adaptive_cases.csv',index=False)
 for col in ['plate_J','extra_wheel_J','suspension_change_J','terminal_change_J']:
  d[col+'_per_km']=d[col]/(d.length_m/1000)
 print(d.groupby(['batch','ISO','stroke_m','speed_kmh'])[['plate_J_per_km','extra_wheel_J_per_km','off_fraction']].mean().round(3).to_string())
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('batch');z=a.parse_args();tasks=[]
 if z.batch=='duration':
  for seed in range(3101,3109):
   for h in [.005,.01,.025]:
    for L in [1000.,4000.,8000.]:
     tasks.append((f'duration{int(L)}',seed,'H',h,2e-6,.0025,4000.,L,50.))
 elif z.batch=='precision':
  for seed in range(3101,3117):
   for iso in ['A','G','H']:
    for h in [.005,.01,.025]:
     for nm,tol,dt in [('coarse',1e-5,.005),('fine',4e-7,.00125)]:
      tasks.append((nm,seed,iso,h,tol,dt,1000.,1000.,50.))
 elif z.batch=='ensemble':
  for seed in range(3101,3165):
   for h in [.005,.01,.025]:tasks.append(('ensemble',seed,'H',h,2e-6,.0025,4000.,4000.,50.))
 elif z.batch=='speed':
  for seed in range(3101,3117):
   for v in [10.,20.,30.,50.]:
    for h in [.005,.01,.025]:tasks.append(('speed',seed,'H',h,2e-6,.0025,2000.,2000.,v))
 execute(tasks);table()
