from pathlib import Path
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parent;O=P/'out';O.mkdir(exist_ok=True)
t=pd.read_csv(P/'data/coverage_uniform_power_grid.csv');a=pd.read_csv(P/'data/coverage_device_markers.csv');ref=a[(a.ISO=='A')&(a.pairs_per_km==1)].sort_values('load_level');powers=ref.power_W_per_km.to_numpy()
for fp in (P.parent/'fonts').glob('*'):
 if fp.suffix.lower()=='.ttf':font_manager.fontManager.addfont(str(fp))
font='Times New Roman'
assert font_manager.findfont(font,fallback_to_default=False)
navy='#1b2e40';grey='#9baab3';colors=['#235f85']*4+['#789092']*4;styles=['-','--','-.',':']*2
plt.rcParams.update({'font.family':font,'font.size':11,'svg.fonttype':'none','pdf.fonttype':42,'text.color':navy,'axes.labelcolor':navy,'axes.edgecolor':'#8b9eac','xtick.color':navy,'ytick.color':navy})
fig=plt.figure(figsize=(12.1,8.8));fig.text(.085,.98,'Annual energy balance across ISO A–H',fontsize=17,weight='bold',va='top')
handles=[Line2D([0],[0],color=colors[j],ls=styles[j],lw=1.8,label=f'ISO {iso}') for j,iso in enumerate('ABCDEFGH')]
fig.legend(handles,[h.get_label() for h in handles],loc='upper left',bbox_to_anchor=(.085,.935),ncol=8,fontsize=10,frameon=False,borderaxespad=0,columnspacing=1.5,handlelength=2.4)
axs=[fig.add_axes([.085,.435,.88,.265]),fig.add_axes([.085,.10,.88,.265])]
for ax,n,title in zip(axs,[1,20],['a   1 harvester pair/km','b   20 harvester pairs/km']):
 for p in powers:ax.axvline(p,color=grey,ls=(0,(3,3)),lw=.75,zorder=1)
 for j in reversed(range(8)):
  iso='ABCDEFGH'[j];s=t[(t.ISO==iso)&(t.pairs_per_km==n)];ss=a[(a.ISO==iso)&(a.pairs_per_km==n)]
  curve=pd.concat([s[['power_W_per_km','annual_balance_weighted_road_pct']],ss[['power_W_per_km','annual_balance_weighted_road_pct']]]).sort_values('power_W_per_km').drop_duplicates('power_W_per_km')
  ax.plot(curve.power_W_per_km,curve.annual_balance_weighted_road_pct,color=colors[j],ls=styles[j],lw=1.8,zorder=3+(7-j)*.1)
 ax.set(xlim=(0,420),ylim=(-4,106),yticks=[0,25,50,75,100],xticks=np.arange(0,401,50));ax.minorticks_off();ax.grid(axis='y',color='#dce5eb',lw=.6);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False);ax.tick_params(length=3,pad=5,labelsize=10)
 ax.text(.985,.94,title,transform=ax.transAxes,ha='right',va='top',fontsize=12.5,weight='bold')
 ax.set_xlabel('Annual average load (W/km)',fontsize=11.5,labelpad=8)
 # Retain the familiar ISO A one-lamp reference without plotting a marker.
 row=a[(a.ISO=='A')&(a.pairs_per_km==n)&(a.load_level==5)].iloc[0]
 target=(75,24) if n==1 else (140,101)
 ax.annotate(f'ISO A: {row.annual_balance_weighted_road_pct:.2f}%',(powers[4],row.annual_balance_weighted_road_pct),xytext=target,fontsize=10,color=colors[0],ha='left',va='center',arrowprops=dict(arrowstyle='-',color=colors[0],lw=.9))
fig.text(.026,.40,'Weighted road length reaching annual energy balance (%)',rotation=90,va='center',ha='center',fontsize=12)
labels=['1 radar electronic\nunit/km','3 radar units +\n1 basic weather\nnode/km','1 radar unit +\n1 heated weather\nnode/km','1 weather\nmonitoring node/km','1 lamp/km','5 lamps/km','20 lamps/km']
labelx=np.linspace(.112,.92,7)
for k,(p,label,fx) in enumerate(zip(powers,labels,labelx)):
 fig.text(fx,.79,label+'\n'+f'{p:.3f} W/km',ha='center',va='bottom',fontsize=9.5,color='#465e6e',linespacing=1.2)
 axs[0].annotate('',xy=(p,106),xycoords='data',xytext=(fx,.785),textcoords=fig.transFigure,arrowprops=dict(arrowstyle='-',color=grey,lw=.7),annotation_clip=False)
fig.savefig(O/'Figure4g_ISO_A_H_coverage_preview.png',dpi=170,facecolor='white');fig.savefig(O/'Figure4g_ISO_A_H_coverage.png',dpi=400,facecolor='white')
svg=O/'Figure4g_ISO_A_H_coverage.svg';fig.savefig(svg,facecolor='white')
if font!='Times New Roman':svg.write_text(svg.read_text().replace("'Liberation Serif'","'Times New Roman', 'Liberation Serif', serif"))
plt.rcParams['svg.fonttype']='path'
fig.savefig(O/'Figure4g_ISO_A_H_coverage_outlined.svg',facecolor='white')
print('Rendered Times New Roman device guides and outlined SVG.')
