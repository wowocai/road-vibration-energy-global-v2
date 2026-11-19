"""Fresh ISO H simulation, no substitution of nonconvergence by zero."""
from pathlib import Path
import subprocess,sys,json,argparse,importlib.util
R=Path(__file__).resolve().parents[1];P=R/'modules/vehicle_energy/repaired_model'
a=argparse.ArgumentParser();a.add_argument('--seed',type=int,default=3101);a.add_argument('--stroke',type=float,default=.005);args=a.parse_args()
subprocess.run(['cc','-O3','-fPIC','-shared',str(P/'model.c'),'-o',str(P/'model.so'),'-lm'],check=True)
s=importlib.util.spec_from_file_location('coupled_model',P/'run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
z=[m.sim(iso='H',seed=args.seed,stroke=args.stroke,speed=2,warm=200,length=1000,maxdt=.005,sign=sign) for sign in [-1,1]]
o=R/'outputs/H_fresh';o.mkdir(parents=True,exist_ok=True);(o/f'{args.seed}_{args.stroke}.json').write_text(json.dumps(z,indent=2));print(o)
