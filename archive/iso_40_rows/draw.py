from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator
P=Path(__file__).resolve().parent
d=pd.read_csv(P.parent/'duarte_unilateral/ISO_A-H_contact_results.csv').set_index('iso').loc[list('ABCDEFGH')]
mech=pd.read_csv(P.parent/'iso_mechanical/ISO_A-H_two_mechanical_inputs.csv').set_index('iso').loc[d.index]
response=d.ratio_tau25.to_numpy()
base_A=mech.loc['A','trial_TWh_mechanical_per_year']
annual_scale=base_A/(20*239.4)
base=annual_scale*(20*239.4)*response
low=annual_scale*(40*98.1)*response
assert len(base)==8 and np.allclose(base,mech.trial_TWh_mechanical_per_year)
assert np.allclose(low/base,(40*98.1)/(20*239.4))
assert np.isclose(low[0],mech.loc['A','prescribed_quasistatic_ceiling_TWh_per_year']/10)
out=P/'out'
out.mkdir(exist_ok=True)
try:
    font_manager.findfont('Times New Roman',fallback_to_default=False)
    preview_fonts=['Times New Roman','Liberation Serif']
except ValueError:
    preview_fonts=['Liberation Serif']
plt.rcParams.update({'font.family':preview_fonts,'font.size':12,'axes.labelcolor':'#203346',
    'axes.edgecolor':'#8799a9','text.color':'#1b2e40','xtick.color':'#203346',
    'ytick.color':'#203346','svg.fonttype':'none'})
fig,ax=plt.subplots(figsize=(10.3,4.85))
fig.subplots_adjust(left=.104,right=.978,top=.746,bottom=.155)
fig.text(.104,.928,'Annual mechanical energy across ISO A–H reference roads',
         fontsize=19.5,weight='bold')
fig.text(.104,.864,'Shared roughness response  |  2 t at 50 km/h  |  50% effective passages',
         fontsize=12,color='#4c6577')
x=np.arange(8)
width=.325
ax.axvspan(2.5,7.55,color='#eef2f5',zorder=0)
ax.text(4.65,84,'D–H: model scenarios with intermittent tire contact',
        ha='center',va='center',color='#4a6173',fontsize=10.6)
for j,(v,color,label) in enumerate([(base,'#367b9a','Prototype: 20 pairs/km'),
                        (low,'#d98a43','Design scenario: 40 rows/km')]):
    xx=x+(j-.5)*width
    ax.bar(xx,v,width=width,color=color,edgecolor='white',linewidth=.65,zorder=3,label=label)
    for a,b in zip(xx,v):
        ax.annotate(f'{b:.1f}',(a,b),xytext=(0,4),textcoords='offset points',
            ha='center',va='bottom',fontsize=10.5)
ax.set(xlim=(-.53,7.55),ylim=(0,92),xticks=x,
       xticklabels=[f'ISO {i}' for i in d.index],
       ylabel='Annual mechanical energy (TWh/yr)')
ax.yaxis.set_major_locator(MultipleLocator(20))
ax.grid(axis='y',color='#dce5eb',linewidth=.7)
ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
ax.tick_params(length=0,pad=6)
ax.set_xlabel('ISO 8608 reference spectrum',labelpad=9)
handles,labels=ax.get_legend_handles_labels()
fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.104,.83),borderaxespad=0,
    frameon=False,ncol=2,columnspacing=2,fontsize=11.6)
fig.savefig(P/'preview.png',dpi=145,facecolor='white')
svg=out/'Figure4_ISO_A-H_40_rows.svg'
fig.savefig(svg,facecolor='white')
if preview_fonts[0]!='Times New Roman':
    t=svg.read_text()
    assert "'Liberation Serif'" in t
    t=t.replace("'Liberation Serif'","'Times New Roman', 'Liberation Serif', serif")
    svg.write_text(t)
assert 'Times New Roman' in svg.read_text()
print(pd.DataFrame({'ISO':d.index,'prototype_TWh_per_year':base,'40_rows_TWh_per_year':low}).round(2).to_string(index=False))
print('Preview font:',preview_fonts[0])
