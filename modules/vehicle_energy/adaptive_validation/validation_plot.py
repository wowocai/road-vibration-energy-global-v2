from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
P=Path(__file__).resolve().parent;O=P/'out'
font_dirs=[P/'fonts',P.parent/'figure/sources/Figure4_density_comparison_package/fonts',P.parent/'overlay_bars/figure/sources/Figure4_density_comparison_package/fonts']
for p in [f for fd in font_dirs for f in fd.glob('*')]:
 if p.suffix.lower()=='.ttf':font_manager.fontManager.addfont(str(p))
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
s=pd.read_csv(O/'validation_summary.csv');c=pd.read_csv(O/'H_sample_convergence.csv')
cols=['#275f85','#79aebd','#cf956c'];hs=[.005,.01,.025]
f,aa=plt.subplots(2,3,figsize=(14,8.4));f.subplots_adjust(left=.07,right=.98,bottom=.1,top=.9,wspace=.34,hspace=.6)
f.suptitle('ISO H: numerical convergence and model-applicability checks',fontsize=18,y=.985)
f.text(.5,.942,'2 t; 50 km/h unless indicated; 20 harvester pairs/km',ha='center',fontsize=12)
for h,col in zip(hs,cols):
 z=s[(s.experiment.str.startswith('duration'))&np.isclose(s.stroke_m,h)].sort_values('length_m')
 aa[0,0].errorbar(z.length_m/1000,z.extra_wheel_J_per_km/1000,yerr=z.extra_wheel_J_per_km_CI95_half/1000,color=col,capsize=3,marker='o',label=f'{h*1000:.0f} mm')
 z=c[np.isclose(c.stroke_m,h)].sort_values('first_n_seeds')
 aa[0,1].errorbar(z.first_n_seeds,z.extra_wheel_J_per_km/1000,yerr=z.extra_wheel_J_per_km_CI95_half/1000,color=col,capsize=3,marker='o')
 z=s[(s.experiment.str.startswith('p_'))&np.isclose(s.stroke_m,h)].sort_values('rtol',ascending=False)
 aa[0,2].plot(range(3),z.extra_wheel_J_per_km/1000,color=col,marker='o')
 z=s[s.experiment.str.startswith('n_')&np.isclose(s.stroke_m,h)]
 aa[1,0].errorbar([h*1000],z.extra_wheel_J_per_km/1000,yerr=z.extra_wheel_J_per_km_CI95_half/1000,fmt='o',color=col,capsize=5)
for ax in aa.ravel():ax.grid(axis='y',color='#e0e5e8',lw=.6);ax.axhline(0,color='#697b86',lw=.7);ax.set_axisbelow(True)
aa[0,0].set(title='a  Measurement length (8 independent seeds)',xlabel='Measured distance (km)',ylabel='Wheel-work change (kJ/vehicle-km)',xticks=[1,4,8]);aa[0,0].legend(frameon=False,ncol=3,fontsize=10,loc='lower left')
aa[0,1].set(title='b  Number of independent road seeds',xlabel='Independent seeds (sign pairs averaged)',ylabel='Wheel-work change (kJ/vehicle-km)')
aa[0,2].set(title='c  Adaptive-integration precision (8 seeds)',xticks=[0,1,2],xticklabels=['2e−6 / 2.5 ms','4e−7 / 1.25 ms','8e−8 / 0.625 ms'],ylabel='Wheel-work change (kJ/vehicle-km)',xlabel='Relative tolerance / maximum step');aa[0,2].tick_params(axis='x',labelsize=9)
aa[1,0].set(title='d  4 km run on an 8 km road (16 seeds)',xlabel='Plate stroke limit (mm)',ylabel='Wheel-work change (kJ/vehicle-km)',xticks=[5,10,25])
z=s[s.experiment.isin(['d_point','d_patch','d_stops','d_both'])].set_index('experiment').loc[['d_point','d_patch','d_stops','d_both']]
aa[1,1].bar(range(4),z.peak_suspension_travel_m,color=['#b5c3cb','#79aebd','#cf956c','#c6b1a2']);aa[1,1].axhline(.08,color='#9d534c',ls='--',lw=1)
aa[1,1].set(title='e  Contact / suspension model diagnostics',xticks=range(4),xticklabels=['Point tyre','0.305 m\nenvelope','80 mm\nstop onset','Envelope\n+ stop'],ylabel='Mean of sample peak suspension travel (m)');aa[1,1].tick_params(axis='x',labelsize=10)
z=s[s.experiment.isin(['d_v10','d_v20','d_point'])].sort_values('speed_kmh')
aa[1,2].plot(z.speed_kmh,z.off_fraction*100,'o-',color=cols[0]);aa[1,2].set(title='f  Speed applicability (8 seeds; 5 mm plate)',xlabel='Speed (km/h)',ylabel='Tyre no-contact time (%)',xticks=[10,20,50],ylim=(0,100))
f.text(.5,.02,'Error bars: 95% Student-t intervals across independent seed means; they exclude numerical and model uncertainty.',ha='center',fontsize=10)
f.savefig(O/'H_validation_checks.png',dpi=250);f.savefig(O/'H_validation_checks.pdf');plt.close(f)
