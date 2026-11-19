from pathlib import Path
import json,subprocess
import numpy as np,pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.lines import Line2D
from matplotlib import font_manager
P=Path(__file__).resolve().parent;R=P.parent;O=P/'out';O.mkdir(exist_ok=True)
for fp in (P.parent/'fonts').glob('*'):
 if fp.suffix.lower()=='.ttf':font_manager.fontManager.addfont(str(fp))
font='Times New Roman'
assert font_manager.findfont(font,fallback_to_default=False)
navy='#162638';muted='#516473';blue='#176498'
plt.rcParams.update({'font.family':font,'font.size':9,'text.color':navy,'axes.labelcolor':navy,'axes.edgecolor':'#a1afb8','xtick.color':navy,'ytick.color':navy,'svg.fonttype':'none','savefig.facecolor':'white'})
features=json.loads((P/'data/world_mollweide.geojson').read_text())['features']
paths=[]
for ft in features:
 g=ft['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']];v=[];c=[]
 for poly in polys:
  for ring in poly:v.extend(ring);c.extend([MPath.MOVETO]+[MPath.LINETO]*(len(ring)-2)+[MPath.CLOSEPOLY])
 paths.append(MPath(np.asarray(v),c))
colors=['#8a3544','#b54c43','#d27450','#e9a67e','#69afcd','#278ab9','#1b639b','#173f68'];tab=np.zeros((9,4),np.uint8)
for j,col in enumerate(colors,1):tab[j]=[int(col[k:k+2],16) for k in (1,3,5)]+[255]
df=pd.read_csv(P/'data/coverage_all_scenarios.csv');powers=df.query("ISO == 'ISO A' and pairs_per_km == 1").power_W_per_km.to_numpy()
fig=plt.figure(figsize=(12.1,16.5))
extra=3.2;HH=16.5
def YY(y):return (13.3*y+extra)/HH
def HHH(y):return 13.3*y/HH
fig.text(.057,YY(.995),'Annual road energy balance by load and deployment',fontsize=17,weight='bold',va='top')
examples=['1 radar electronic unit/km; 1 harvester pair/km','3 radars + 1 basic weather node/km; 1 harvester pair/km','1 radar + 1 heated weather node/km; 1 harvester pair/km','1 weather monitoring node/km; 1 harvester pair/km','1 lamp/km; 1 harvester pair/km','1 lamp/km; 20 harvester pairs/km']
for i in range(6):
 x=.057+(i%2)*.452;y=.775-(i//2)*.212
 n=20 if i==5 else 1;k=min(i+1,5)
 row=df.query("ISO == 'ISO A' and pairs_per_km == @n and load_level == @k").iloc[0]
 fig.text(x,YY(y+.184),f'{chr(97+i)}   {row.power_W_per_km:.3f} W/km',fontsize=10.7,weight='bold',va='bottom')
 fig.text(x+.414,YY(y+.184),f'{row.road_balance_pct:.2f}% reach annual energy balance',fontsize=9.4,ha='right',weight='bold',color=blue,va='bottom')
 fig.text(x,YY(y+.165),examples[i],fontsize=8,color=muted,va='bottom')
 ax=fig.add_axes([x,YY(y),.428,HHH(.153)])
 for path in paths:ax.add_patch(PathPatch(path,facecolor='#f2f4f4',edgecolor='#c5cdd2',lw=.25,zorder=1))
 path=P/f'data/approved_panel_{i:02d}.mask' if i<4 else P/f'data/panel_{i-4:02d}.mask'
 mask=np.fromfile(path,dtype=np.uint8).reshape(1222,2800)
 ax.imshow(tab[mask],extent=(-18050000,18050000,-7100000,8650000),interpolation='hanning',origin='upper',zorder=2)
 ax.set(xlim=(-18050000,18050000),ylim=(-7100000,8650000),aspect='equal');ax.set_axis_off()
fig.text(.927,YY(.983),'a–f | Uniform ISO A reference',fontsize=8.7,color=blue,ha='right',va='top')
cb=fig.add_axes([.265,YY(.328),.47,HHH(.009)])
for j,col in enumerate(colors):cb.add_patch(Rectangle((j,0),1,1,color=col,lw=0))
for j in range(1,8):cb.axvline(j,color='white',lw=.6)
cb.axvline(4,color=navy,lw=1.1);cb.set(xlim=(0,8),ylim=(0,1),yticks=[],xticks=range(1,8),xticklabels=['0.01×','0.1×','0.5×','1×','2×','5×','10×']);cb.tick_params(length=2,labelsize=8,pad=2)
for s in cb.spines.values():s.set_visible(False)
cb.text(2,1.4,'Below annual balance',fontsize=7.8,color='#9a483d',ha='center');cb.text(6,1.4,'Annual balance or surplus',fontsize=7.8,color=blue,ha='center')
fig.text(.5,YY(.301),'Annual electricity supply ÷ annual service demand',ha='center',fontsize=8.5)

# g: dense-load ISO A–H coverage, grouped as one main panel.
t=pd.read_csv(P.parent/'work/data/coverage_uniform_power_grid.csv');aa=pd.read_csv(P.parent/'work/data/coverage_device_markers.csv')
ref=aa[(aa.ISO=='A')&(aa.pairs_per_km==1)].sort_values('load_level');loads=ref.power_W_per_km.to_numpy()
cc=['#235f85']*4+['#789092']*4;ls=['-','--','-.',':']*2
fig.text(.057,6.77/HH,'g   Annual energy balance across ISO A–H',weight='bold',fontsize=10.5)
handles=[Line2D([0],[0],color=cc[j],ls=ls[j],lw=1.5,label=f'ISO {iso}') for j,iso in enumerate('ABCDEFGH')]
fig.legend(handles,[h.get_label() for h in handles],loc='upper left',bbox_to_anchor=(.057,6.60/HH),ncol=4,fontsize=8.0,frameon=False,borderaxespad=0,columnspacing=1.2,handlelength=1.9,labelspacing=.7)
gaxes=[fig.add_axes([.092,3.24/HH,.555,1.66/HH]),fig.add_axes([.092,.74/HH,.555,1.66/HH])]
for ax,n,title in zip(gaxes,[1,20],['1 harvester pair/km','20 harvester pairs/km']):
 for pp in loads:ax.axvline(pp,color='#9baab3',ls=(0,(3,3)),lw=.6,zorder=1)
 for j in reversed(range(8)):
  iso='ABCDEFGH'[j];z=t[(t.ISO==iso)&(t.pairs_per_km==n)];v=aa[(aa.ISO==iso)&(aa.pairs_per_km==n)]
  curve=pd.concat([z[['power_W_per_km','annual_balance_weighted_road_pct']],v[['power_W_per_km','annual_balance_weighted_road_pct']]]).sort_values('power_W_per_km').drop_duplicates('power_W_per_km')
  ax.plot(curve.power_W_per_km,curve.annual_balance_weighted_road_pct,color=cc[j],ls=ls[j],lw=1.35,zorder=3+(7-j)*.1)
 ax.set(xlim=(0,420),ylim=(-4,106),yticks=[0,25,50,75,100],xticks=np.arange(0,401,50));ax.minorticks_off();ax.grid(axis='y',color='#dce5eb',lw=.5);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False);ax.tick_params(length=2,pad=3,labelsize=8)
 ax.text(.985,.92,title,transform=ax.transAxes,ha='right',va='top',fontsize=9.0,weight='bold')
 ax.set_xlabel('Annual average load (W/km)',fontsize=8.5,labelpad=5)
 row=aa[(aa.ISO=='A')&(aa.pairs_per_km==n)&(aa.load_level==5)].iloc[0]
 xytext=(90,27) if n==1 else (150,101)
 ax.annotate(f'ISO A: {row.annual_balance_weighted_road_pct:.2f}%',(loads[4],row.annual_balance_weighted_road_pct),xytext=xytext,fontsize=8,color=cc[0],arrowprops=dict(arrowstyle='-',color=cc[0],lw=.7))
fig.text(.042,2.81/HH,'Weighted road length reaching annual energy balance (%)',rotation=90,ha='center',va='center',fontsize=8.5)
labels=['1 radar electronic\nunit/km','3 radar units +\n1 basic weather\nnode/km','1 radar unit +\n1 heated weather\nnode/km','1 weather\nmonitoring node/km','1 lamp/km','5 lamps/km','20 lamps/km']
for p,label,fx in zip(loads,labels,np.linspace(.092,.637,7)):
 fig.text(fx,5.52/HH,label+'\n'+f'{p:.3f} W/km',ha='center',va='bottom',fontsize=6.8,color='#465e6e',linespacing=1.2)
 gaxes[0].annotate('',xy=(p,106),xycoords='data',xytext=(fx,5.46/HH),textcoords=fig.transFigure,arrowprops=dict(arrowstyle='-',color='#9baab3',lw=.55),annotation_clip=False)
# h retains the complete named dense-array scenarios.
fig.text(.705,6.77/HH,'h   Annual lighting contribution',fontsize=10.1,weight='bold')
fig.text(.705,6.55/HH,'by array scenario',fontsize=10.1,weight='bold')
h=fig.add_axes([.752,1.43/HH,.218,4.41/HH]);dh=pd.read_csv(P/'data/panel_h_named_scenarios.csv');vals=dh.annual_energy_matched_pct.to_numpy()
h.bar(np.arange(3),vals,width=.55,color=['#aab7c1','#6eafc3',blue],edgecolor='white',lw=.6,zorder=3)
for i,val in enumerate(vals):h.text(i,val+2,f'{val:.2f}%',ha='center',fontsize=9.6,weight='bold')
h.set(xlim=(-.6,2.6),ylim=(0,80),yticks=[0,20,40,60,80],xticks=[0,1,2],xticklabels=['Original array\nwith reference\nstorage transfer','Original array\nwith ideal\nelectrical\nextraction','Full active-length\narray with ideal\nelectrical\nextraction'],ylabel='Annual lighting demand met (%)')
h.tick_params(axis='x',length=0,pad=7,labelsize=7.0);h.tick_params(axis='y',labelsize=8);h.yaxis.label.set_fontsize(8.5);h.spines[['top','right']].set_visible(False);h.grid(axis='y',color='#dce3e7',lw=.65);h.set_axisbelow(True);h.text(.02,.96,'20 lamps/km',transform=h.transAxes,ha='left',va='top',fontsize=8,color=muted)
fig.savefig(O/'Figure4_with_g_h.png',dpi=370,bbox_inches='tight',pad_inches=.10)
fig.savefig(O/'Figure4_updated_ISO_A_H.svg',bbox_inches='tight',pad_inches=.10)
# Outlined vector copy retains the actual Times New Roman letterforms on any system.
plt.rcParams['svg.fonttype']='path';fig.savefig(O/'Figure4_updated_ISO_A_H_outlined.svg',bbox_inches='tight',pad_inches=.10)
im=Image.open(O/'Figure4_with_g_h.png');im.thumbnail((1550,2150));im.save(O/'Figure4_preview.png')
print('Combined Figure4 saved with real Times New Roman and adopted dense A–H curves.')
