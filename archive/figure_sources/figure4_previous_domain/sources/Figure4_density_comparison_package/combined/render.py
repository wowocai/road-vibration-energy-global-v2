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
try:font_manager.findfont('Times New Roman',fallback_to_default=False);font='Times New Roman'
except ValueError:font='Liberation Serif'
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
fig=plt.figure(figsize=(12.1,13.3))
fig.text(.057,.995,'Annual road energy balance by load and deployment',fontsize=17,weight='bold',va='top')
examples=['1 radar electronic unit/km; 1 harvester pair/km','3 radars + 1 basic weather node/km; 1 harvester pair/km','1 radar + 1 heated weather node/km; 1 harvester pair/km','1 weather monitoring node/km; 1 harvester pair/km','1 lamp/km; 1 harvester pair/km','1 lamp/km; 20 harvester pairs/km']
for i in range(6):
 x=.057+(i%2)*.452;y=.775-(i//2)*.212
 n=20 if i==5 else 1;k=min(i+1,5)
 row=df.query("ISO == 'ISO A' and pairs_per_km == @n and load_level == @k").iloc[0]
 fig.text(x,y+.184,f'{chr(97+i)}   {row.power_W_per_km:.3f} W/km',fontsize=10.7,weight='bold',va='bottom')
 fig.text(x+.414,y+.184,f'{row.road_balance_pct:.2f}% reach annual energy balance',fontsize=9.4,ha='right',weight='bold',color=blue,va='bottom')
 fig.text(x,y+.165,examples[i],fontsize=8,color=muted,va='bottom')
 ax=fig.add_axes([x,y,.428,.153])
 for path in paths:ax.add_patch(PathPatch(path,facecolor='#f2f4f4',edgecolor='#c5cdd2',lw=.25,zorder=1))
 path=P/f'data/approved_panel_{i:02d}.mask' if i<4 else P/f'data/panel_{i-4:02d}.mask'
 mask=np.fromfile(path,dtype=np.uint8).reshape(1222,2800)
 ax.imshow(tab[mask],extent=(-18050000,18050000,-7100000,8650000),interpolation='hanning',origin='upper',zorder=2)
 ax.set(xlim=(-18050000,18050000),ylim=(-7100000,8650000),aspect='equal');ax.set_axis_off()
fig.text(.927,.983,'a–f | Uniform ISO A reference',fontsize=8.7,color=blue,ha='right',va='top')
cb=fig.add_axes([.265,.328,.47,.009])
for j,col in enumerate(colors):cb.add_patch(Rectangle((j,0),1,1,color=col,lw=0))
for j in range(1,8):cb.axvline(j,color='white',lw=.6)
cb.axvline(4,color=navy,lw=1.1);cb.set(xlim=(0,8),ylim=(0,1),yticks=[],xticks=range(1,8),xticklabels=['0.01×','0.1×','0.5×','1×','2×','5×','10×']);cb.tick_params(length=2,labelsize=8,pad=2)
for s in cb.spines.values():s.set_visible(False)
cb.text(2,1.4,'Below annual balance',fontsize=7.8,color='#9a483d',ha='center');cb.text(6,1.4,'Annual balance or surplus',fontsize=7.8,color=blue,ha='center')
fig.text(.5,.301,'Annual electricity supply ÷ annual service demand',ha='center',fontsize=8.5)
# Old panel f becomes g; remove only the output-threshold panel.
fig.text(.057,.277,'g   Road length reaching annual balance',weight='bold',fontsize=10.3)
top=fig.add_axes([.115,.174,.355,.078]);bot=fig.add_axes([.115,.066,.355,.052],sharex=top)
v=df.pivot(index=['pairs_per_km','load_level'],columns='ISO',values='road_balance_pct').sort_index();dc={1:blue,20:'#3d7779'}
for ax in [top,bot]:
 ax.set_xscale('log');ax.set_xlim(.092,550);ax.set_xticks(powers,['0.12','0.47','1.81','7.00','20.4','105','409']);ax.minorticks_off();ax.tick_params(labelsize=7.5,length=2,pad=2);ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dce3e7',lw=.55);ax.set_axisbelow(True)
for n,m,ls in [(1,'o','-'),(20,'s','--')]:
 top.plot(powers,v.loc[n]['ISO A'],color=dc[n],ls=ls,marker=m,lw=1.4,ms=3)
 for aa,bb,col in [('ISO A','ISO B','#a75b24'),('ISO B','ISO C','#6952a0')]:bot.plot(powers,v.loc[n][aa]-v.loc[n][bb],color=col,ls=ls,marker=m,lw=1.3,ms=3)
top.set(ylim=(-4,108),yticks=[0,50,100],ylabel='Weighted road length (%)');top.yaxis.label.set_fontsize(8);top.tick_params(axis='x',labelbottom=False)
bot.set(ylim=(-1.17,.075),yticks=[-1,-.5,0],ylabel='Difference (pp)',xlabel='Annual average load (W/km)');bot.yaxis.label.set_fontsize(8);bot.xaxis.label.set_fontsize(8);bot.axhline(0,color='#8c9ca8',lw=.65)
fig.text(.115,.262,'Baseline coverage (ISO A)',fontsize=8,weight='bold');fig.text(.115,.137,'Adjacent scenario differences',fontsize=8,weight='bold')
fig.legend(handles=[Line2D([0],[0],color=dc[n],ls=ls,marker=m,lw=1.2,ms=3,label=l) for n,m,ls,l in [(1,'o','-','1 pair/km'),(20,'s','--','20 pairs/km')]],loc='lower right',bbox_to_anchor=(.475,.255),frameon=False,ncol=2,fontsize=7.3,handlelength=1.5,columnspacing=.8)
fig.legend(handles=[Line2D([0],[0],color=c,lw=1.3,label=l) for c,l in [('#a75b24','A − B'),('#6952a0','B − C')]],loc='lower right',bbox_to_anchor=(.475,.13),frameon=False,ncol=2,fontsize=7.3,handlelength=1.5)
fig.text(.509,.277,'h   Annual lighting contribution by array scenario',fontsize=10.3,weight='bold')
h=fig.add_axes([.565,.093,.356,.157]);dh=pd.read_csv(P/'data/panel_h_named_scenarios.csv');vals=dh.annual_energy_matched_pct.to_numpy()
h.bar(np.arange(3),vals,width=.55,color=['#aab7c1','#6eafc3',blue],edgecolor='white',lw=.6,zorder=3)
for i,val in enumerate(vals):h.text(i,val+2,f'{val:.2f}%',ha='center',fontsize=9.6,weight='bold')
h.set(xlim=(-.6,2.6),ylim=(0,80),yticks=[0,20,40,60,80],xticks=[0,1,2],xticklabels=['Original array with\nreference storage\ntransfer','Original array with\nideal electrical\nextraction','Full active-length array\nwith ideal electrical\nextraction'],ylabel='Annual lighting demand met (%)');h.tick_params(axis='x',length=0,pad=7,labelsize=7.8);h.tick_params(axis='y',labelsize=8);h.yaxis.label.set_fontsize(8.5);h.spines[['top','right']].set_visible(False);h.grid(axis='y',color='#dce3e7',lw=.65);h.set_axisbelow(True)
h.text(.02,.95,'20 lamps/km',transform=h.transAxes,ha='left',va='top',fontsize=8,color=muted)
fig.savefig(O/'Figure4_with_g_h.png',dpi=370,bbox_inches='tight',pad_inches=.10)
svg=O/'Figure4_density_and_array_scenarios.svg';fig.savefig(svg,bbox_inches='tight',pad_inches=.10)
if font!='Times New Roman':svg.write_text(svg.read_text().replace("'Liberation Serif'","'Times New Roman', 'Liberation Serif', serif"))
im=Image.open(O/'Figure4_with_g_h.png');im.thumbnail((1500,1800));im.save(O/'Figure4_preview.png')
# e/f enlargement for checking the density comparison.
from matplotlib.transforms import Bbox
fig.savefig(O/'Figure4_e_f_comparison.png',dpi=240,bbox_inches=Bbox.from_extents(.52,4.56,11.43,7.20))
print('Rendered updated a–h figure.')
