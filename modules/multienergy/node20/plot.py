from pathlib import Path
import json,numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parent;O=P/'out';D=P/'data'
font_dir=P/'fonts' if (P/'fonts').exists() else P.parent/'confirmed_g/fonts'
for f in font_dir.glob('*.TTF'):font_manager.fontManager.addfont(str(f))
plt.rcParams.update({'font.family':'Times New Roman','font.size':10,'svg.fonttype':'none','text.color':'#203746','axes.labelcolor':'#203746','axes.spines.top':False,'axes.spines.right':False})
names=['Solar PV','Savonius wind','Road vibration'];colors=['#b78a41','#9B3F80','#236b8e'];m=pd.read_csv(O/'five_metrics.csv').set_index('source').loc[names];x=np.load(O/'minute_inputs.npz');n=len(x['load_Wh']);hour=(np.arange(n)%1440)//60
# Annual output per explicitly defined collector-reference area.
counts=[20, 20, 40] # 20 harvester pairs = 40 single prototypes.
unit_areas=[2.274*1.134,.65*.65,.33]
area_basis=['PV module front external area','VAWT D x H; H=D assumed for area normalization','Road module external plan area']
areas={name:count*A for name,count,A in zip(names,counts,unit_areas)}
area_yields={name:m.loc[name,'annual_generation_kWh_per_km']/areas[name] for name in names}
area_rows=[{'source':name,'installed_single_units':count,'unit_area_m2':A,'total_reference_area_m2':areas[name],'annual_generation_kWh':m.loc[name,'annual_generation_kWh_per_km'],'annual_electricity_kWh_per_m2':area_yields[name],'area_definition':basis} for name,count,A,basis in zip(names,counts,unit_areas,area_basis)]
pd.DataFrame(area_rows).to_csv(O/'collector_area_normalization.csv',index=False)
radar_data=m[['annual_energy_sufficiency_pct','night_direct_energy_coverage_pct','no_storage_minute_full_load_coverage_pct','annual_generation_kWh_per_km']].copy()
radar_data['annual_electricity_kWh_per_m2']=[area_yields[name] for name in names]
radar_data.to_csv(O/'radar_five_metrics.csv',index_label='source')
fig=plt.figure(figsize=(15.2,11.1));gs=fig.add_gridspec(2,2,left=.072,right=.97,bottom=.08,top=.88,wspace=.29,hspace=.55)
fig.text(.072,.973,'Same service-node density: 20 PV panels; 20 Savonius turbines; 20 road-harvester pairs per km',fontsize=10.5,weight='bold')
fig.text(.072,.946,'Krakow weather, 2023 | Urban wind: H = 15 m; frontal density = 0.20; hub = 3 m | Same traffic and load | Bench-output scenario',fontsize=10.2,color='#536d7d')
a=fig.add_subplot(gs[0,0]);mean={}
for name,k,c in zip(names,['PV_Wh','wind_Wh','vibration_Wh'],colors):
 v=np.array([x[k][hour==j].mean()*60 for j in range(24)]);mean[name]=v;a.plot(np.arange(24)+.5,v,color=c,lw=2,label=name)
v=np.array([x['load_Wh'][hour==j].mean()*60 for j in range(24)]);mean['Load']=v;a.plot(np.arange(24)+.5,v,color='#37454e',lw=1.6,ls=':',label='Load')
a.set(xlim=(0,24),xticks=np.arange(0,25,4),xlabel='Local solar hour',ylabel='Mean electrical power (W/km)',ylim=(0,4500),yticks=np.arange(0,4501,1000));a.grid(axis='y',color='#e1e8ec',lw=.6);a.set_axisbelow(True)
a.set_title('a   Annual mean daily supply and demand',loc='left',pad=20,fontsize=13,weight='bold');a.legend(frameon=False,ncol=2,fontsize=9.4,loc='upper left')
a.text(.98,.53,f"Wind: {m.loc['Savonius wind','annual_generation_kWh_per_km']:.4f} kWh/km/year",ha='right',transform=a.transAxes,fontsize=9,color=colors[1])
wi=a.inset_axes([.57,.65,.40,.22]);wi.plot(np.arange(24)+.5,mean['Savonius wind']*1000,color=colors[1],lw=1.6);wi.set(xlim=(0,24),xticks=[0,12,24]);wi.tick_params(labelsize=7);wi.set_title('Wind only (mW/km)',fontsize=8);wi.grid(axis='y',alpha=.2)
pd.DataFrame({'hour':np.arange(24)+.5,**mean}).to_csv(O/'panel_a_profiles.csv',index=False)

b=fig.add_subplot(gs[0,1]);b.set_aspect('equal');b.axis('off');b.set(xlim=(-1.48,1.48),ylim=(-1.42,1.42));ang=np.pi/2-np.arange(5)*2*np.pi/5;u=np.column_stack([np.cos(ang),np.sin(ang)])
for r in [.2,.4,.6,.8,1]:
 q=np.vstack([u*r,u[0]*r]);b.plot(q[:,0],q[:,1],color='#d6e1e7',lw=.6)
for v in u:b.plot([0,v[0]],[0,v[1]],color='#d6e1e7',lw=.6)
labels=['Annual energy sufficiency\n(%; 20 lamps/km)','Night-time direct\nenergy coverage (%)','No-storage coverage\n(%; 1-min energy balance)','Annual electricity per collector area\n(kWh/m²/year; log scale)','Annual electricity\n(kWh/km/year; log scale)']
radar_max=np.array([100.,20.,60.,np.nan,np.nan])
# Physical log ranges: 1e-4..1e3 kWh/m²/year and 1e-3..1e4 kWh/km/year.
log_bounds={3:(-4.,3.),4:(-3.,4.)}
for j,(v,label) in enumerate(zip(u,labels)):
 label_pos=v*1.25
 if j in [1,4]:label_pos[1]+=.14
 b.text(*label_pos,label,ha='center',va='center',fontsize=8.4)
 if j<3:
  ticks=[(rr,f'{radar_max[j]*rr:.0f}') for rr in [.2,.4,.6,.8,1]]
 else:
  lo,hi=log_bounds[j]
  ticks=[((ex-lo)/(hi-lo),f'$10^{{{ex}}}$' if ex not in [0,1] else ('1' if ex==0 else '10')) for ex in range(int(lo)+1,int(hi)+1)]
 for rr,val in ticks:
  pp=v*rr+np.array([-v[1],v[0]])*.038
  b.text(*pp,val,ha='center',va='center',fontsize=6.7,color='#8195a0',bbox=dict(facecolor='white',alpha=.8,edgecolor='none',pad=.1))
for k,(name,c) in enumerate(zip(names,colors)):
 z=m.loc[name]
 raw_r=np.array([z.annual_energy_sufficiency_pct,z.night_direct_energy_coverage_pct,z.no_storage_minute_full_load_coverage_pct,area_yields[name],z.annual_generation_kWh_per_km])
 r=np.empty(5);r[:3]=raw_r[:3]/radar_max[:3]
 for j in [3,4]:
  lo,hi=log_bounds[j]
  assert raw_r[j]>0, 'A zero value cannot be plotted on a logarithmic axis'
  r[j]=(np.log10(raw_r[j])-lo)/(hi-lo)
 assert ((r>=0)&(r<=1)).all(), 'Radar data outside declared axis range'
 q=u*r[:,None]
 for j in range(5):
  jj=(j+1)%5
  b.plot(q[[j,jj],0],q[[j,jj],1],color=c,lw=1.8,ls=['-','--','-'][k])
 b.plot(q[:,0],q[:,1],ls='',marker=['o','s','D'][k],ms=4,color=c,label=name)
b.text(-.04,-1.34,'Area basis: PV module / VAWT D x H (H=D assumed) / road-module plan area',ha='center',va='top',fontsize=7.6,color='#536d7d')
b.set_title('b   Quantified service under the stated deployment',loc='center',pad=23,fontsize=13,weight='bold')
# Common three-source legend for b–d; a includes its load curve separately.
fig.legend([Line2D([0],[0],color=c,lw=2) for c in colors],names,loc='lower center',bbox_to_anchor=(.52,.015),ncol=3,frameon=False,fontsize=10.5)

# c: electrical-output envelopes from declared exposure factors, not ordinal scores.
h=pd.read_csv(O/'hourly_weather_and_generation.csv');temp=h.T2M.to_numpy();ghi=h.ALLSKY_SFC_SW_DWN.to_numpy();ws=h.WS10M.to_numpy()
raw=json.loads((D/'NASA_POWER_2023_radiation_components.json').read_text())['properties']['parameter'];rdf=pd.DataFrame(raw);rdf.index=pd.to_datetime(rdf.index,format='%Y%m%d%H');rdf=rdf.sort_index()
ix=pd.date_range('2023-01-01',periods=8760,freq='h');dec=np.deg2rad(23.44*np.sin(2*np.pi*(284+ix.dayofyear.to_numpy())/365));lat=np.deg2rad(50.0647);beta=np.deg2rad(45);co=np.sin(dec)*np.sin(lat-beta)+np.cos(dec)*np.cos(lat-beta)*np.cos(np.deg2rad(15*(ix.hour.to_numpy()+.5-12)))
poa=rdf.ALLSKY_SFC_SW_DNI.to_numpy()*np.maximum(co,0)+rdf.ALLSKY_SFC_SW_DIFF.to_numpy()*(1+np.cos(beta))/2+.2*ghi*(1-np.cos(beta))/2
sunlit=(~x['night']).reshape(8760,60).mean(axis=1)
def pv_yield(f):
 g=poa*f;p=10000*g/1000*np.maximum(0,1-.004*(temp+25/800*g-25))*.8;return np.sum(p*sunlit)/1000


def new_wind_power(v):
 return np.interp(v,[0.7, 1.1, 1.3, 1.7, 1.9, 2.1, 2.5, 3.4, 4.2, 4.7, 4.9, 5.3, 5.9, 6.7, 7.0, 7.3, 7.9, 8.1, 8.4],[0.003, 0.04, 0.075, 0.104, 0.141, 0.199, 0.289, 0.379, 0.468, 0.5346, 0.666, 0.804, 0.976, 1.277, 1.4396, 1.6384, 1.742, 1.978, 2.275],left=0,right=np.nan)

# Road labels retain the previous layout; wind proxy morphology is explicitly prescribed.
def wf(lam):
 H=15.;d=(.15+5.5*(lam-.05) if lam<.15 else .7+.35*(lam-.15))*H;z0=min(lam,.15)*H
 k=np.log((H-d)/z0)/np.log((50-d)/z0)*np.exp(9.6*lam*(3/H-1))
 return np.sum(20*new_wind_power(h.WS50M.to_numpy()*k)*.8)/1000
scenes=['Open\nroad','Tree-lined\nroad','Covered\nroad','Tunnel\nportal','Tunnel\ninterior'];pf=[(1,1),(.1,.5),(0,0),(0,1),(0,0)]
# Open: lambda=.10 proxy; tree-lined/covered: same .20 built setting, no invented vegetation factor.
# Portal: no resolved portal-flow model, so display 0..open-road ambient scenario; interior ambient excluded.
wind_cases=[(wf(.1),wf(.1)),(wf(.2),wf(.2)),(wf(.2),wf(.2)),(0.,wf(.1)),(0.,0.)]
rows=[];c=fig.add_subplot(gs[1,0]);xx=np.arange(5);w=.23
for jj,(name,col) in enumerate(zip(names,colors)):
 for i,scene in enumerate(scenes):
  if jj==0:
   lo,hi=[pv_yield(v) for v in pf[i]];ref=pv_yield(sum(pf[i])/2)
  elif jj==1:lo,hi=wind_cases[i];ref=(lo+hi)/2
  else:lo=hi=ref=m.loc[name,'annual_generation_kWh_per_km']
  xp=xx[i]+(jj-1)*w;c.bar(xp,ref,width=w*.85,color=col,alpha=.86,edgecolor='white',lw=.5,zorder=3)
  if hi-lo>1e-5:c.errorbar(xp,ref,yerr=np.array([[ref-lo],[hi-ref]]),fmt='none',ecolor=col,elinewidth=1,capsize=3,zorder=4)
  if jj==1 or ref==0:c.annotate(f'{ref:.3f}' if jj==1 and 0<ref<1 else (f'{ref:.1f}' if ref else '0'),(xp,ref),xytext=(0,4),textcoords='offset points',ha='center',fontsize=7.5,color=col)
  rows.append(dict(scene=scene.replace('\n',' '),source=name,reference_electricity_kWh_per_km=ref,annual_electricity_low_kWh_per_km=lo,annual_electricity_high_kWh_per_km=hi,interval_type='prescribed_scenario_not_confidence_interval'))
c.set(xlim=(-.55,4.55),ylim=(0,11000),xticks=xx,xticklabels=scenes,ylabel='Annual electricity (kWh/km/year)',yticks=np.arange(0,11001,2000));c.grid(axis='y',color='#e1e8ec',lw=.6);c.set_axisbelow(True)
c.set_title('c   Road settings with prescribed exposure and urban form',loc='left',pad=20,fontsize=12,weight='bold')
c.text(.98,.96,'Wind: explicit urban-form scenarios\nWhiskers: prescribed scenario ranges',ha='right',va='top',transform=c.transAxes,fontsize=8.5,color='#536d7d')
pd.DataFrame(rows).to_csv(O/'panel_c_exposure_scenarios.csv',index=False)

d=fig.add_subplot(gs[1,1]);cp=np.arange(0,181);rows=[]
for name,col in zip(names,colors):
 E=m.loc[name,'annual_generation_kWh_per_km'];value=E*(.16+.45*cp/1000);d.plot(cp,value,lw=2.2,color=col,label=name)
 for C,V in zip(cp,value):rows.append({'source':name,'carbon_price_USD_per_t':C,'annual_generation_kWh_per_km':E,'gross_generation_value_USD_per_km_year':V,'electricity_value_USD_per_kWh':.16,'prescribed_displacement_kg_per_kWh':.45})
 d.annotate(name,xy=(180,value[-1]),xytext=(4,12 if name=='Road vibration' else 0),textcoords='offset points',fontsize=9,color=col,va='center',annotation_clip=False)
d.set(xlim=(0,180),ylim=(0,2500),yticks=np.arange(0,2501,500),xticks=np.arange(0,181,30),xlabel='Assumed carbon price (USD/t CO$_2$)',ylabel='Conditional gross value (USD/km/year)');d.grid(axis='y',color='#e1e8ec',lw=.6);d.set_axisbelow(True);d.set_title('d   Carbon-price sensitivity by energy source',loc='left',pad=20,fontsize=13,weight='bold');d.text(.03,.96,'Same electricity value and carbon factor\nDifferent annual electricity under the stated deployment',transform=d.transAxes,va='top',fontsize=8.8,color='#536d7d')
pd.DataFrame(rows).to_csv(O/'panel_d_carbon_price.csv',index=False)
fig.text(.072,.002,'Wind: reported bench-output curve; zero below 0.7 m/s assumed; 80% retained. VAWT area uses assumed H = D = 0.65 m.',fontsize=8,color='#536d7d')

fig.canvas.draw()
radar_box=b.get_tightbbox(fig.canvas.get_renderer()).transformed(fig.dpi_scale_trans.inverted()).expanded(1.05,1.08)
fig.savefig(O/'Figure5b_area_radar.png',dpi=330,bbox_inches=radar_box)
fig.savefig(O/'Figure5_scope_corrected.png',dpi=330,bbox_inches='tight',pad_inches=.15);fig.savefig(O/'Figure5_scope_corrected.svg',bbox_inches='tight',pad_inches=.15);plt.rcParams['svg.fonttype']='path';fig.savefig(O/'Figure5_scope_corrected_outlined.svg',bbox_inches='tight',pad_inches=.15)
from PIL import Image
im=Image.open(O/'Figure5_scope_corrected.png');im.thumbnail((1800,1600));im.save(O/'Figure5_preview.png')

