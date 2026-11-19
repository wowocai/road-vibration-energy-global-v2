"""Summarize phase averages, traffic scaling, local lighting and draft Fig. 4."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import pandas as pd
from scipy.stats import t
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
P=Path(__file__).resolve().parent; ROOT=P.parent
x=pd.read_csv(P/'phase_results.csv')
l=pd.read_csv(ROOT/'duarte_iso/reference_results.csv')
l=l[(l.mass_kg==2000)&(l.speed_kmh==50)].set_index('road')
cols=['work_tau10','work_tau25','work_tau50','fixed_stroke_linear_work']
base=pd.read_csv(ROOT/'geo_check/figures/figures/source_data/Figure4_efficiency_scenarios.csv')
base=base[(base.input_case=='fixed_trial_input')&(base.eta==1)].iloc[0]
J_A=144.8
TWh_A=base.load_TWh*J_A/239.4
assert np.isclose(TWh_A,4.350793,atol=5e-7)
rows=[]
for (ref, mode),g in x.groupby(['refinement','vehicle_proxy']):
    y=g.groupby(['iso','seed']).mean(numeric_only=True)
    avg=y.groupby('iso').mean()
    for grade in [a for a in 'ABCDEFGH' if a in avg.index]:
        a=y.loc['A','work_tau25']; q=y.loc[grade,'work_tau25']
        rel=avg.loc[grade,'work_tau25']/avg.loc['A','work_tau25']
        err=(q-rel*a).std(ddof=1)/np.sqrt(len(q))/a.mean()*t.ppf(.975,len(q)-1)
        alt=avg.loc[grade,cols]/avg.loc['A',cols]
        sr=avg.loc[grade,'suspension_J_per_m']/avg.loc['A','suspension_J_per_m']
        rows.append(dict(iso=grade,refinement=ref,vehicle_proxy=mode,
            reference_spectrum_density_m3=16e-6*4**('ABCDEFGH'.index(grade)),
            road_height_rms_m=np.sqrt(np.sum(16e-6*(np.arange(11,3073)/1024/.1)**-2)/1024)*2**('ABCDEFGH'.index(grade)),
            ratio_tau25=rel,phase95_low=rel-err,phase95_high=rel+err,
            ratio_tau10=alt.iloc[0],ratio_tau50=alt.iloc[2],ratio_fixed_stroke=alt.iloc[3],
            linear_model_ratio=(1+l.loc[grade,'increment_pct']/100)/(1+l.loc['A','increment_pct']/100),
            device_J_per_pair_pass=J_A*rel,global_delivered_TWh_per_year=TWh_A*rel,
            vehicle_suspension_J_per_m=avg.loc[grade,'suspension_J_per_m'],vehicle_suspension_ratio_vs_A=sr,
            tire_time_out_of_contact_pct=100*avg.loc[grade,'tire_time_out_of_contact'],
            vehicle_time_any_tire_out_of_contact_pct=100*avg.loc[grade,'vehicle_time_any_tire_out_of_contact']))
s=pd.DataFrame(rows)
d=s[(s.refinement==2)&(s.vehicle_proxy==0)].set_index('iso').copy()
c=s[(s.refinement==1)&(s.vehicle_proxy==0)].set_index('iso')
v=s[(s.refinement==1)&(s.vehicle_proxy==1)].set_index('iso')
max_grid=(np.abs(d.ratio_tau25/c.ratio_tau25-1)).max()
max_match=(np.abs(d.ratio_tau25/d.linear_model_ratio-1)).max()
w=s[(s.refinement==3)&(s.vehicle_proxy==0)].set_index('iso')
fine=s[(s.refinement==4)&(s.vehicle_proxy==0)].set_index('iso')
max_fine=np.abs(fine.ratio_tau25/d.ratio_tau25-1).max()
max_warm=np.abs(w.ratio_tau25/d.ratio_tau25-1).max()
assert max_grid<.015 and max_fine<.008 and max_warm<.008, (max_grid,max_fine,max_warm)
assert max_match<.001, max_match
assert (d.tire_time_out_of_contact_pct.loc[list('DEFGH')]>0).all()
assert x.energy_residual_relative.abs().max()<.005
D=20*179.01140330823847
cache=ROOT/'geo_check/unpacked/outputs/Global_nightlight_20260928/global_segment_cache'
acc=np.zeros((8,3))
n=0; den=0
for f in sorted(cache.glob('batch_*.npz')):
    with np.load(f) as z:
        lengths=z['length_km']; weights=lengths*np.clip(z['positive_fraction'],0,1)
        q=z['aadt_median']
    n+=len(q)
    den+=D*weights.sum()
    for i,rel in enumerate(d.ratio_tau25):
        S=365*q*20*J_A*.5*.8/3.6e6*rel
        acc[i]+=[np.dot(lengths,S),np.dot(weights,np.minimum(S,D)),weights[S>=D].sum()]
assert n==3293705
assert np.allclose(acc[:,0]/1e9,d.global_delivered_TWh_per_year,rtol=1e-9)
assert abs(acc[0,1]/den-.24649928)<1e-7
d['local_Fingal_demand_met_pct']=100*acc[:,1]/den
d['candidate_weighted_length_balanced_pct']=100*acc[:,2]*D/den
d['fixed_stroke_global_TWh_per_year']=TWh_A*d.ratio_fixed_stroke
d['alternate_vehicle_global_TWh_per_year']=TWh_A*v.ratio_tau25
d['tau10_global_TWh_per_year']=TWh_A*d.ratio_tau10
d['tau50_global_TWh_per_year']=TWh_A*d.ratio_tau50
s.to_csv(P/'numerical_sensitivity.csv',index=False,float_format='%.9g')
d.to_csv(P/'ISO_A-H_contact_results.csv',float_format='%.9g')
print(d[['device_J_per_pair_pass','global_delivered_TWh_per_year','local_Fingal_demand_met_pct','tire_time_out_of_contact_pct','fixed_stroke_global_TWh_per_year','vehicle_suspension_ratio_vs_A','alternate_vehicle_global_TWh_per_year','tau10_global_TWh_per_year','tau50_global_TWh_per_year']].round(4).to_string())
print(f'Grid max: {max_grid:.4%}; fine grid max: {max_fine:.4%}; warm-up max: {max_warm:.4%}; linear A–C max: {max_match:.4%}; max energy closure relative residual: {x.energy_residual_relative.abs().max():.4%}; max mean-load mismatch: {x.max_mean_wheel_load_relative_error.max():.4%}; annual lighting demand: {den/1e9:.9f} TWh/yr')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.labelcolor':'#22384a','axes.edgecolor':'#889ba8','text.color':'#1b2e3e','xtick.color':'#283d50','ytick.color':'#283d50'})
fig,ax=plt.subplots(figsize=(10.3,4.6))
fig.subplots_adjust(left=.106,right=.977,bottom=.20,top=.72)
fig.text(.106,.928,'Annual electricity across ISO A–H reference roads',fontsize=17.5,weight='bold')
fig.text(.106,.853,'Duarte prototype  ·  Fixed-speed scenarios: 2 t at 50 km/h  ·  20 pairs/km',fontsize=11,color='#4f6473')
v=np.arange(8); y=d.global_delivered_TWh_per_year.to_numpy()
demand=den/1e9
ax.axhline(demand,c='#536572',ls=(0,(5,3)),lw=1.1,zorder=1)
ax.plot(v,d.fixed_stroke_global_TWh_per_year,'o--',color='#304a5b',ms=3.7,lw=1.2,zorder=4)
colors=['#146191']+['#65a6b4']*2+['#d78b54']*5
ax.bar(v,y,width=.59,color=colors,zorder=2)
# Intervals reflect random-phase sampling only. Show structural alternative separately.
lo=TWh_A*d.phase95_low.to_numpy(); hi=TWh_A*d.phase95_high.to_numpy()
ax.errorbar(v,y,yerr=np.maximum(0,np.array([y-lo,hi-y])),fmt='none',ecolor='#25394a',capsize=3,lw=1,zorder=3)
for i,h in enumerate(y):
    ax.annotate(f'{h:.2f}',(i,max(h,hi[i])),xytext=(0,6),textcoords='offset points',ha='center',va='bottom',fontsize=9.8)
ax.set(xticks=v,xticklabels=[f'ISO {a}' for a in d.index],xlim=(-.61,7.61),ylim=(0,max(demand*1.18,hi.max()*1.18)),
       ylabel='Annual electricity available (TWh/yr)')
ax.spines[['right','top']].set_visible(False)
ax.grid(axis='y',color='#e2e9ed',lw=.8);ax.set_axisbelow(True)
ax.tick_params(length=0,pad=7)
h=[Patch(fc=colors[0],label='Trial anchor'),Patch(fc=colors[1],label='B–C scenarios'),Patch(fc=colors[3],label='D–H: load-responsive model'),
   Line2D([0],[0],marker='o',ms=3.7,color='#304a5b',ls='--',label='Fixed-stroke model'),
   Line2D([0],[0],color='#536572',ls='--',label=f'Lighting demand ({demand:.2f} TWh/yr)')]
fig.legend(handles=h,loc='lower left',bbox_to_anchor=(.100,.022),ncol=3,frameon=False,fontsize=8.5,columnspacing=1.5)
out=P/'out'; out.mkdir(exist_ok=True)
fig.savefig(out/'Figure4_ISO_A-H_nonlinear.png',dpi=400)
