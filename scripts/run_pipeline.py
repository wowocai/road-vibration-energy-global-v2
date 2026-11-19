"""Portable release entry point. Python 3.12, Linux/macOS; see docs/WORKFLOW.md."""
from pathlib import Path
import argparse,subprocess,sys,json,hashlib,importlib.util,time,os
R=Path(__file__).resolve().parents[1];M=R/'modules';O=R/'outputs';O.mkdir(exist_ok=True)
os.environ.setdefault('MPLBACKEND','Agg')
def run(path,*args):
 print('RUN',path,flush=True);subprocess.run([sys.executable,str(R/path),*map(str,args)],cwd=R,check=True)
def compile_model():
 p=M/'vehicle_energy/repaired_model';subprocess.run(['cc','-O3','-fPIC','-shared',str(p/'model.c'),'-o',str(p/'model.so'),'-lm'],check=True)
def passive():
 import numpy as np,pandas as pd
 p=M/'passive_vehicle/model.py';sp=importlib.util.spec_from_file_location('passive_model',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 rows=[];checks=[]
 for vehicle in m.PARAMS:
  mass,c,k,_,b=m.assemble(vehicle)
  assert np.allclose(c,c.T) and np.linalg.eigvalsh(c).min()>-1e-6
  for iso,j in zip('ABCDEFGH',range(8)):
   z=m.response(vehicle,g0=16e-6*4**j);z['ISO']=iso;rows.append(z)
  fine=m.response(vehicle,g0=16e-6);coarse=m.response(vehicle,g0=16e-6,points=6000)
  error=abs(coarse['unit_J_km']/fine['unit_J_km']-1);assert error<1e-4
  checks.append(dict(vehicle=vehicle,relative_refinement_error=error))
 pd.DataFrame(rows).to_csv(O/'passive_vehicle_A_H.csv',index=False)
 # National reconstruction consumes the freshly calculated A-C unit responses.
 target=M/'national/project/Lighting_replacement_20261023/Global_three_layer_20261024/Vehicle_model_alignment_20261025/current_ISO_response.csv'
 pd.DataFrame(rows).query("ISO in ['A','B','C']").to_csv(target,index=False)
 (O/'passive_vehicle_validation.json').write_text(json.dumps(checks,indent=2))
def energy_profiles():
 import numpy as np,pandas as pd
 p=M/'multienergy';v=pd.read_csv(p/'reported_power_points.csv')
 for case,count in [('node20',20),('equal_investment',10)]:
  q=p/'inputs'/case;out=p/case/'out';out.mkdir(parents=True,exist_ok=True)
  h=pd.read_csv(q/'out/hourly_weather_and_generation.csv');z=np.load(q/'out/minute_inputs.npz');x={k:z[k] for k in z.files}
  speeds=h.urban_hub_wind_mps.to_numpy();assert speeds.max()<=v.wind_mps.max()
  power=count*.8*np.interp(speeds,v.wind_mps,v.electrical_power_W,left=0,right=np.nan)
  x['wind_Wh']=np.repeat(power,60)/60;np.savez_compressed(out/'minute_inputs.npz',**x)
  h['wind_W']=power;h.to_csv(out/'hourly_weather_and_generation.csv',index=False)
  load=x['load_Wh'];night=x['night'];rows=[]
  for name,key in [('Solar PV','PV_Wh'),('Savonius wind','wind_Wh'),('Road vibration','vibration_Wh')]:
   g=x[key];direct=np.minimum(g,load);rows.append(dict(source=name,annual_generation_kWh_per_km=g.sum()/1000,annual_load_kWh=load.sum()/1000,annual_energy_sufficiency_pct=min(1,g.sum()/load.sum())*100,night_direct_energy_coverage_pct=direct[night].sum()/load[night].sum()*100,no_storage_minute_full_load_coverage_pct=np.mean(g>=load-1e-8)*100))
  pd.DataFrame(rows).to_csv(out/'five_metrics.csv',index=False)
def validate():
 import pandas as pd,numpy as np
 t=pd.read_csv(M/'supply/service_all_domains.csv');a=t.query("domain=='full_road_length' and ISO=='A'")
 def val(load,density,key):return a[(a.load==load)&(a.pairs_per_km==density)][key].iloc[0]
 assert np.isclose(val('Radar',1,'coverage_pct'),97.342471,atol=1e-5)
 assert np.isclose(val('1_lamp',20,'coverage_pct'),66.307543,atol=1e-5)
 assert np.isclose(val('20_lamps',20,'energy_match_pct'),16.108944,atol=1e-5)
 s=pd.read_csv(M/'vehicle_energy/figure/data/current_joint_scenarios.csv');assert len(s)==24 and (s.extra_wheel_J_per_km>0).all()
 energy=pd.read_csv(M/'multienergy/node20/out/five_metrics.csv').set_index('source')
 assert np.isclose(energy.loc['Savonius wind','annual_generation_kWh_per_km'],.011106825,atol=1e-8)
 (O/'validation.json').write_text(json.dumps({'status':'passed','checks':['full-length headline percentages','24 ISO/stroke vehicle scenarios','positive ensemble-mean additional wheel work','current Savonius wind annual energy','passive vehicle matrix and refinement (separate file)']},indent=2))
def figures():
 import pandas as pd,matplotlib
 matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib import font_manager
 fonts={x.name for x in font_manager.fontManager.ttflist};plt.rcParams['font.family']='Times New Roman' if 'Times New Roman' in fonts else 'Liberation Serif'
 d=pd.read_csv(M/'supply/Figure4g_full_length_curves.csv');d=d[d.domain=='full_road_length'];fig,axs=plt.subplots(2,1,figsize=(8,9),sharex=True)
 for ax,density in zip(axs,[1,20]):
  for j,iso in enumerate('ABCDEFGH'):
   z=d[(d.ISO==iso)&(d.pairs_per_km==density)];ax.plot(z.power_W_km,z.coverage_pct,color=plt.cm.viridis(.1+.8*j/7),label='ISO '+iso)
  ax.set(ylabel='Road length reaching annual balance (%)',ylim=(0,102),title=f'{density} pair(s)/km');ax.grid(alpha=.2)
 axs[0].legend(ncol=4,frameon=False);axs[1].set(xlabel='Annual mean load (W/km)',xlim=(0,420));fig.tight_layout();fig.savefig(O/'full_length_coverage_curves.png',dpi=200);plt.close(fig)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['quick','national','cost','all','device-dynamics','vehicle-dynamics'],default='quick');a=ap.parse_args();start=time.time()
 if a.stage in ['quick','all','national']:passive()
 if a.stage in ['quick','all']:
  run('modules/supply/recalculate.py');run('modules/vehicle_energy/aggregate.py');energy_profiles();validate();figures()
 if a.stage in ['national','all']:run('modules/national/unify_national.py','--out',O/'national')
 if a.stage in ['cost','all']:
  energy_profiles();run('modules/lifecycle/optimized_storage/optimize.py')
 if a.stage=='device-dynamics':run('modules/device_response/run.py');run('modules/device_response/summarize.py')
 if a.stage=='vehicle-dynamics':compile_model();run('modules/vehicle_energy/compute.py')
 (O/'last_run.json').write_text(json.dumps({'stage':a.stage,'elapsed_seconds':time.time()-start,'python':sys.version,'aggregation_primary':'full_road_length'},indent=2))
