from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pandas as pd,numpy as np
D=Path(__file__).resolve().parent
d=pd.read_csv(D/'Iowa_27_scenarios.csv',dtype={'speed_fraction':str})
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'svg.fonttype':'none'})
fig=plt.figure(figsize=(11.5,3.65))
grid=fig.add_gridspec(1,5,width_ratios=[2,1.18,1.18,1.18,.08],left=.065,right=.95,bottom=.26,top=.77,wspace=.32)
a=fig.add_subplot(grid[0]);v=[21.83906105,87.35624421,9.928241]
a.bar(range(3),v,width=.61,color=['#aab6c1','#aab6c1','#1d7186'])
for i,y in enumerate(v): a.text(i,y+2,f'{y:.2f}',ha='center',fontsize=10)
a.set_xticks(range(3),['ISO A','ISO B','IRI-constrained'])
a.set_ylabel('Annual suspension dissipation (GWh)')
a.set_ylim(0,100);a.spines[['right','top']].set_visible(False)
a.tick_params(axis='x',length=0)
fig.text(.065,.94,'a  Road-input comparison',weight='bold',fontsize=11)
fig.text(.391,.94,'b  Sensitivity to spectrum, speed and freight representation',weight='bold',fontsize=11)
norm=Normalize(.25,.65)
for i,(speed,title) in enumerate([('0.8','80% of posted limit'),('1.0','Posted limit'),('fixed20','Fixed 20 m/s')]):
    ax=fig.add_subplot(grid[i+1]); sub=d[d.speed_fraction==speed]
    e=sub.pivot(index='spectral_exponent',columns='heavy_proxy_fraction',values='iri_gwh').values
    r=sub.pivot(index='spectral_exponent',columns='heavy_proxy_fraction',values='iri_to_iso_a').values
    im=ax.imshow(r,norm=norm,cmap='Blues',aspect='auto')
    for y,x in np.ndindex(r.shape):
        ax.text(x,y,f'{e[y,x]:.2f}\n{r[y,x]:.0%}',ha='center',va='center',fontsize=8,color='white' if r[y,x]>.51 else '#18232c')
    if i==0: ax.add_patch(plt.Rectangle((1.52,.52),.96,.96,fill=False,edgecolor='#e38233',lw=2))
    ax.set_title(title,pad=7)
    ax.set_xticks(range(3),['0','50','100'])
    ax.set_yticks(range(3),['1.5','2.0','2.5'] if i==0 else [])
    if i==0: ax.set_ylabel('Spectral exponent')
    ax.tick_params(length=0)
    for sp in ax.spines.values():sp.set_visible(False)
c=fig.colorbar(im,cax=fig.add_subplot(grid[4]),ticks=[.3,.4,.5,.6],format=lambda x,_: f'{x:.0%}')
c.outline.set_visible(False);c.ax.tick_params(length=0,labelsize=8)
fig.text(.662,.142,'Share of reported truck traffic assigned to the heavy proxy (%)',ha='center')
fig.text(.662,.062,'Cell: GWh/year (top), % of matched ISO A reference (bottom). Orange outline: baseline.',ha='center',fontsize=8.4)
for ext in ('png','pdf','svg'):fig.savefig(D/f'Iowa_Supplementary_Figure.{ext}',dpi=450,facecolor='white')
