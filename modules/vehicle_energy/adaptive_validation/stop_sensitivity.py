from diagnostics import task
from concurrent.futures import ProcessPoolExecutor,as_completed
if __name__=='__main__':
 args=[(f's_{seed}_{travel}_{ratio}',dict(seed=seed,travel=travel,stopratio=ratio)) for seed in range(3101,3105) for travel in [.06,.08,.1] for ratio in [100,1000]]
 with ProcessPoolExecutor(max_workers=2) as pool:
  for i,z in enumerate(as_completed([pool.submit(task,a) for a in args]),1):print(i,z.result(),flush=True)
