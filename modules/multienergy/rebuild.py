from pathlib import Path
import shutil,json,subprocess,numpy as np,pandas as pd
R=Path(__file__).resolve().parent; BASE=R/'inputs'; OLD=R.parent/'aln_trial/base/Figure5'
if not BASE.exists():
 BASE.mkdir()
 for case in ['node20','equal_investment']:
  Q=BASE/case;Q.mkdir()
  for d in ['data','fonts']:shutil.copytree(OLD/case/d,Q/d)
  (Q/'out').mkdir()
  for f in ['minute_inputs.npz','five_metrics.csv','hourly_weather_and_generation.csv','audit.json']:shutil.copy(OLD/case/'out'/f,Q/'out'/f)
  shutil.copy(OLD/case/'plot.py',Q/'plot.py')
# Reported Table 3 data, only the monotonic low-speed block needed for all current exposures.
vx=np.array([.7,1.1,1.3,1.7,1.9,2.1,2.5,3.4,4.2,4.7,4.9,5.3,5.9,6.7,7,7.3,7.9,8.1,8.4])
px=np.array([.003,.040,.075,.104,.141,.199,.289,.379,.468,.5346,.666,.804,.976,1.277,1.4396,1.6384,1.742,1.978,2.275])
pd.DataFrame(dict(wind_mps=vx,electrical_power_W=px)).to_csv(R/'reported_power_points.csv',index=False)
def power(v):
 assert np.max(v)<=vx[-1], 'Outside retained measured range'
 return np.interp(v,vx,px,left=0,right=np.nan)
def fac(lam=.2):
 H=15;d=(.15+5.5*(lam-.05) if lam<.15 else .7+.35*(lam-.15))*H;z0=min(lam,.15)*H
 return np.log((H-d)/z0)/np.log((50-d)/z0)*np.exp(9.6*lam*(3/H-1))
summary=[]
for case,count in [('node20',20),('equal_investment',10)]:
 Q=R/case;O=Q/'out';O.mkdir(parents=True,exist_ok=True)
 for d in ['data','fonts']:
  if (BASE/case/d).exists():shutil.copytree(BASE/case/d,Q/d,dirs_exist_ok=True)
 w=pd.read_csv(BASE/case/'out/hourly_weather_and_generation.csv');v=w.urban_hub_wind_mps.to_numpy();pw=count*.8*power(v)
 old=np.load(BASE/case/'out/minute_inputs.npz');x={k:old[k] for k in old.files};x['wind_Wh']=np.repeat(pw,60)/60
 np.savez_compressed(O/'minute_inputs.npz',**x)
 load=x['load_Wh'];night=x['night'];rows=[]
 for name,k in [('Solar PV','PV_Wh'),('Savonius wind','wind_Wh'),('Road vibration','vibration_Wh')]:
  g=x[k];direct=np.minimum(g,load)
  rows.append(dict(source=name,annual_generation_kWh_per_km=g.sum()/1000,annual_load_kWh=load.sum()/1000,annual_energy_sufficiency_pct=min(g.sum()/load.sum(),1)*100,night_direct_energy_coverage_pct=direct[night].sum()/load[night].sum()*100,no_storage_minute_full_load_coverage_pct=np.mean(g>=load-1e-8)*100,direct_annual_energy_coverage_pct=direct.sum()/load.sum()*100))
 pd.DataFrame(rows).to_csv(O/'five_metrics.csv',index=False)
 w['wind_W']=pw;w.to_csv(O/'hourly_weather_and_generation.csv',index=False)
 audit=json.loads((BASE/case/'out/audit.json').read_text());audit.update(wind_device='Ahmad & Abu Hanieh Savonius bench-output scenario; Table 3',DOI='10.1007/s13369-025-10373-w',wind_curve='linear interpolation of reported low-speed points; zero below 0.7 m/s assumed; no extrapolation above 8.4 m/s',cut_in_status='0.7 m/s is lowest nonzero test point, NOT validated charging cut-in; specification says 1.5 m/s',wind_reference_area_status='D=0.65 m reported; H=0.65 m assumed for area metric only; A=D*H',wind_cost_status='GBP 2000 per installed turbine remains a planning assumption, not a quote for this prototype',wind_hours_at_or_above_lowest_point=int((v>=.7).sum()),wind_cut_in_mps=None,lowest_used_nonzero_test_speed_mps=.7,manufacturer_claimed_start_mps=1.5,wind_retention=.8,wind_retention_status='common assumed downstream retention; does not validate low-voltage power electronics',metrics=rows)
 audit['counts']['Savonius wind']=audit['counts'].pop('Urban natural wind')
 (O/'audit.json').write_text(json.dumps(audit,indent=2))
 for lam in [.1,.2]:
  z=w.WS50M.to_numpy()*fac(lam)
  summary.append(dict(case=case,frontal_density=lam,turbines_per_km=count,hours_ge_0p7=int((z>=.7).sum()),yearly_kWh=float((count*.8*power(z)).sum()/1000)))
 # Threshold alternatives make source inconsistency explicit.
 sens=[]
 for onset in [.7,1.1,1.5]:
  for retention in [.5,.8,1.]:
   g=np.where(v>=onset,count*retention*power(v),0)
   sens.append(dict(minimum_used_wind_mps=onset,retention=retention,annual_kWh=g.sum()/1000))
 pd.DataFrame(sens).to_csv(O/'onset_retention_sensitivity.csv',index=False)
 template=(BASE/case/'plot.py').read_text().replace('Urban natural wind','Savonius wind')
 template=template.replace('np.pi*.91**2/4','.65*.65').replace("'Wind rotor swept area'","'VAWT D x H; H=D assumed for area normalization'")
 template=template.replace('20 wind turbines','20 Savonius turbines').replace('10 wind turbines','10 Savonius turbines')
 template=template.replace('Same standardized traffic and load','Same traffic and load | Bench-output scenario')
 template=template.replace('Same standardized traffic','Same traffic')
 template=template.replace(' / rotor swept area / ',' / VAWT D x H (H=D assumed) / ')
 template=template.replace("return np.sum(20*np.interp(h.WS50M.to_numpy()*k,[0,3,5,11,15],[0,0,24,143,262],left=0,right=262)*.8)/1000",f"return np.sum({count}*new_wind_power(h.WS50M.to_numpy()*k)*.8)/1000")
 template=template.replace("return np.sum(10*np.interp(h.WS50M.to_numpy()*k,[0,3,5,11,15],[0,0,24,143,262],left=0,right=262)*.8)/1000",f"return np.sum({count}*new_wind_power(h.WS50M.to_numpy()*k)*.8)/1000")
 curve=f"\ndef new_wind_power(v):\n return np.interp(v,{vx.tolist()!r},{px.tolist()!r},left=0,right=np.nan)\n"
 template=template.replace('# Road labels retain',curve+'\n# Road labels retain')
 template=template.replace("f'{ref:.1f}' if ref else '0'","f'{ref:.3f}' if jj==1 and 0<ref<1 else (f'{ref:.1f}' if ref else '0')")
 template=template.replace('Urban profile: 50 m reference -> roof -> hub; Rutland 914i cut-in 3 m/s. Traffic-induced airflow is reported separately.','Wind: reported bench-output curve; zero below 0.7 m/s assumed; 80% retained. VAWT area uses assumed H = D = 0.65 m.')
 # Keep the accepted four-panel layout, with numerical wind results visible at the small scale.
 template=template.replace("pd.DataFrame({'hour':", "a.text(.98,.60,f\"Wind: {m.loc['Savonius wind','annual_generation_kWh_per_km']:.4f} kWh/km/year\",ha='right',transform=a.transAxes,fontsize=9,color=colors[1])\npd.DataFrame({'hour':")
 template=template.replace("a.text(.98,.60", "a.text(.98,.53")
 template=template.replace("pd.DataFrame({'hour':", "wi=a.inset_axes([.57,.65,.40,.22]);wi.plot(np.arange(24)+.5,mean['Savonius wind']*1000,color=colors[1],lw=1.6);wi.set(xlim=(0,24),xticks=[0,12,24]);wi.tick_params(labelsize=7);wi.set_title('Wind only (mW/km)',fontsize=8);wi.grid(axis='y',alpha=.2)\npd.DataFrame({'hour':")
 template=template.replace('fig.canvas.draw()',"\n"+"fig.canvas.draw()")
 if case=='node20':
  template=template.replace('#82949e','#9B3F80')
  template=template.replace('ylim=(0,12000)', 'ylim=(0,4500),yticks=np.arange(0,4501,1000)')
  template=template.replace('ylim=(-500,33000)', 'ylim=(0,11000)').replace('yticks=[0,10000,20000,30000]', 'yticks=np.arange(0,11001,2000)')
  template=template.replace('ylim=(0,8000)', 'ylim=(0,2500),yticks=np.arange(0,2501,500)')
  template=template.replace("for j,(v,label) in enumerate(zip(u,labels)):", "radar_max=np.array([100.,20.,60.,200.,10000.])\nfor j,(v,label) in enumerate(zip(u,labels)):")
  template=template.replace("val=f'{100*r:.0f}' if j<3 else (f'{r*1000:.0f}' if j==3 else f'{r*40000:.0f}')", "val=f'{radar_max[j]*r:.0f}'")
  template=template.replace("r=np.array([z.annual_energy_sufficiency_pct/100,z.night_direct_energy_coverage_pct/100,z.no_storage_minute_full_load_coverage_pct/100,area_yields[name]/1000,z.annual_generation_kWh_per_km/40000])", "r=np.array([z.annual_energy_sufficiency_pct,z.night_direct_energy_coverage_pct,z.no_storage_minute_full_load_coverage_pct,area_yields[name],z.annual_generation_kWh_per_km])/radar_max")
 if case=='node20':
  from radar_log import apply_log_radar
  template=apply_log_radar(template)
 (Q/'plot.py').write_text(template)
 subprocess.run([__import__('sys').executable,str(Q/'plot.py')],check=True)
 assert np.array_equal(x['PV_Wh'],old['PV_Wh']) and np.array_equal(x['vibration_Wh'],old['vibration_Wh']) and np.array_equal(x['load_Wh'],old['load_Wh'])
pd.DataFrame(summary).to_csv(R/'wind_summary.csv',index=False)
print(pd.DataFrame(summary).to_string(index=False))
