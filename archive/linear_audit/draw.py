from pathlib import Path
import numpy as np,pandas as pd,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator
P=Path(__file__).resolve().parent
s=pd.read_csv(P/'supply_domain_audit.csv')
b=pd.read_csv(P/'demand_domain_audit.csv')
try:
 font_manager.findfont('Times New Roman',fallback_to_default=False)
 fonts=['Times New Roman','Liberation Serif']
except ValueError: fonts=['Liberation Serif']
plt.rcParams.update({'font.family':fonts,'font.size':12,'axes.labelcolor':'#22384a','axes.edgecolor':'#8399aa','text.color':'#21384b','xtick.color':'#243b4d','ytick.color':'#243b4d','svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(11.7,5.7))
fig.subplots_adjust(left=.097,right=.72,top=.74,bottom=.15)
fig.text(.097,.93,'Mechanical input and demand on the same candidate roads',weight='bold',fontsize=19)
fig.text(.097,.862,'3.387 million weighted km  |  2 t at 50 km/h  |  50% effective passages',fontsize=11.6,color='#4e6677')
xx=np.arange(8);w=.325
ax.axvspan(2.5,7.55,color='#eef2f5',zorder=0)
ax.text(4.9,66.5,'D–H: intermittent tire contact scenarios',ha='center',fontsize=10,color='#4f697b')
for j,(col,key,label) in enumerate([('#367b9a','candidate_mechanical_trial_TWh','Experiment-referenced harvesting: 20 pairs/km'),('#d98a43','candidate_mechanical_loadstroke_TWh','Load–stroke-referenced harvesting: 40 rows/km')]):
 y=s[key].to_numpy()
 ax.bar(xx+(j-.5)*w,y,width=w,color=col,edgecolor='white',linewidth=.65,zorder=3,label=label)
 for a,yy in zip(xx+(j-.5)*w,y):
  ax.annotate(f'{yy:.1f}',(a,yy),xytext=(0,4),textcoords='offset points',ha='center',va='bottom',fontsize=9.7)
ax.set(xlim=(-.55,7.55),ylim=(0,72),xticks=xx,xticklabels=[f'ISO {x}' for x in s.ISO],
 ylabel='Annual mechanical input (TWh/yr)',xlabel='ISO 8608 reference spectrum')
ax.xaxis.labelpad=10
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.grid(axis='y',color='#dfe7ec',linewidth=.7);ax.set_axisbelow(True)
ax.spines[['right','top']].set_visible(False)
ax.tick_params(length=0,pad=6)
c='#6c8293'
for row in b.itertuples():
 ax.axhline(row.mechanical_equivalent_TWh,color=c,ls=(0,(5,3)),lw=1,zorder=4)
# Side annotations separate demand labels from nearly coincident lines.
for i,ytext in [(3,float(b.iloc[3].mechanical_equivalent_TWh)),(2,13.6)]:
 row=b.iloc[i];yeq=row.mechanical_equivalent_TWh
 ax.annotate(f'{row.power_W_per_km:.3f} W/km\n{row.label}\n{yeq:.3g} TWh/yr',
    xy=(1,yeq),xycoords=ax.get_yaxis_transform(),
    xytext=(1.055,ytext),textcoords=ax.get_yaxis_transform(),ha='left',va='center',
    arrowprops={'arrowstyle':'-','color':c,'lw':.8,'connectionstyle':'angle,angleA=0,angleB=90,rad=0'},
    fontsize=10.8,color='#3d576a',linespacing=1.17)
a0,a1=b.iloc[0],b.iloc[1]
ax.annotate(f'0.120 W/km: {a0.mechanical_equivalent_TWh:.4f} TWh/yr\n1.805 W/km: {a1.mechanical_equivalent_TWh:.3f} TWh/yr',
 xy=(1,a1.mechanical_equivalent_TWh),xycoords=ax.get_yaxis_transform(),
 xytext=(1.055,3.5),textcoords=ax.get_yaxis_transform(),ha='left',va='center',
 arrowprops={'arrowstyle':'-','color':c,'lw':.8,'connectionstyle':'angle,angleA=0,angleB=90,rad=0'},
 fontsize=10.2,color='#3d576a',linespacing=1.17)
fig.text(.752,.72,'Demand-equivalent input',fontsize=12,weight='bold',va='bottom')
fig.text(.752,.665,'60.48% conversion\n80% downstream retention',fontsize=10.4,color='#536c7d',linespacing=1.22,va='top')
handles,labels=ax.get_legend_handles_labels()
fig.legend(handles,labels,ncol=2,loc='upper left',bbox_to_anchor=(.097,.827),frameon=False,fontsize=11.1,columnspacing=1.8,borderaxespad=0)
fig.savefig(P/'preview.png',dpi=145)
svg=P/'out/Figure3_linear_same_domain.svg'
fig.savefig(svg)
if fonts[0]!='Times New Roman':
 txt=svg.read_text().replace("'Liberation Serif'","'Times New Roman', 'Liberation Serif', serif")
 svg.write_text(txt)
assert 'Times New Roman' in svg.read_text()
