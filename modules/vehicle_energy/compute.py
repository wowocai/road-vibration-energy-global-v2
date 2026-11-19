from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import sys,json,hashlib
P=Path(__file__).resolve().parent
MP=P/'repaired_model'
sys.path.insert(0,str(MP));import run as m
H=hashlib.sha256((MP/'model.c').read_bytes()+(MP/'run.py').read_bytes()).hexdigest()
def task(a):
 iso,seed,h=a;v=5. if iso=='G' else 50.
 f=P/'reference_runs'/f'{iso}_{seed}_{h:g}.json';f.parent.mkdir(exist_ok=True)
 if f.exists():return f.name
 out=[]
 for sign in [-1,1]:
  z=m.sim(iso=iso,seed=seed,stroke=h,speed=v,warm=200,length=1000,maxdt=.005,sign=sign);out.append(z)
 f.write_text(json.dumps(dict(model_sha256=H,cases=out)));return f.name
if __name__=='__main__':
 ts=[(iso,seed,h) for iso in 'ABCDEFG' for seed in range(3101,3117) for h in [.005,.01,.025]]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for i,x in enumerate(as_completed([pool.submit(task,t) for t in ts]),1):print(i,'/',len(ts),x.result(),flush=True)
