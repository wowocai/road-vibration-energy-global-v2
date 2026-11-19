from pathlib import Path
import json
import numpy as np,pandas as pd
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.lines import Line2D
from matplotlib import font_manager
P=Path(__file__).resolve().parent
R=P/'sources/Figure4_density_comparison_package';O=P/'out';O.mkdir(exist_ok=True)
for f in (R/'fonts').glob('*'):
 if f.suffix.lower()=='.ttf':font_manager.fontManager.addfont(str(f))
assert font_manager.findfont('Times New Roman',fallback_to_default=False)
navy='#162638';muted='#516473';blue='#176498'
plt.rcParams.update({'font.family':'Times New Roman','font.size':11,'text.color':navy,
 'axes.labelcolor':navy,'axes.edgecolor':'#a1afb8','xtick.color':navy,'ytick.color':navy,
 'svg.fonttype':'none','pdf.fonttype':42,'savefig.facecolor':'white'})
features=json.loads((R/'combined/data/world_mollweide.geojson').read_text())['features'];paths=[]
for ft in features:
 g=ft['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']];v=[];c=[]
 for poly in polys:
  for ring in poly:v.extend(ring);c.extend([MPath.MOVETO]+[MPath.LINETO]*(len(ring)-2)+[MPath.CLOSEPOLY])
 paths.append(MPath(np.asarray(v),c))
colors=['#8a3544','#b54c43','#d27450','#e9a67e','#69afcd','#278ab9','#1b639b','#173f68']
tab=np.zeros((9,4),np.uint8)
for j,col in enumerate(colors,1):tab[j]=[int(col[k:k+2],16) for k in (1,3,5)]+[255]
df=pd.read_csv(R/'combined/data/coverage_all_scenarios.csv')
fig=plt.figure(figsize=(18,15),facecolor='white')
fig.text(.04,.987,'Annual road energy balance and vehicle energy demand',fontsize=22,weight='bold',va='top')
examples=['1 radar electronic unit/km','3 radars + 1 basic weather node/km',
 '1 radar + 1 heated weather node/km','1 weather monitoring node/km','1 lamp/km','1 lamp/km']
for i in range(6):
 x=[.04,.365,.69][i%3];y=.705-(i//3)*.25
 n=20 if i==5 else 1;k=min(i+1,5)
 row=df.query("ISO == 'ISO A' and pairs_per_km == @n and load_level == @k").iloc[0]
 fig.text(x,y+.225,f'{chr(97+i)}   {row.power_W_per_km:.3f} W/km',fontsize=14,weight='bold',va='bottom')
 fig.text(x,y+.203,f'{row.road_balance_pct:.2f}% reach annual energy balance',fontsize=11.3,color=blue,va='bottom')
 fig.text(x,y+.166,examples[i]+f'\n{n} harvester '+('pair/km' if n==1 else 'pairs/km')+'; ISO A',fontsize=10.2,color=muted,va='bottom',linespacing=1.2)
 ax=fig.add_axes([x,y,.285,.153])
 for path in paths:ax.add_patch(PathPatch(path,facecolor='#f2f4f4',edgecolor='#c5cdd2',lw=.25,zorder=1))
 maskfile=R/f'combined/data/approved_panel_{i:02d}.mask' if i<4 else R/f'combined/data/panel_{i-4:02d}.mask'
 mask=np.fromfile(maskfile,dtype=np.uint8).reshape(1222,2800)
 ax.imshow(tab[mask],extent=(-18050000,18050000,-7100000,8650000),interpolation='hanning',origin='upper',zorder=2)
 ax.set(xlim=(-18050000,18050000),ylim=(-7100000,8650000),aspect='equal');ax.set_axis_off()
cb=fig.add_axes([.23,.42,.54,.010])
for j,col in enumerate(colors):cb.add_patch(Rectangle((j,0),1,1,color=col,lw=0))
for j in range(1,8):cb.axvline(j,color='white',lw=.6)
cb.axvline(4,color=navy,lw=1.1)
cb.set(xlim=(0,8),ylim=(0,1),yticks=[],xticks=range(1,8),xticklabels=['0.01×','0.1×','0.5×','1×','2×','5×','10×'])
cb.tick_params(length=2,labelsize=10,pad=2)
for spine in cb.spines.values():spine.set_visible(False)
cb.text(2,1.5,'Below annual balance',fontsize=10,color='#9a483d',ha='center')
cb.text(6,1.5,'Annual balance or surplus',fontsize=10,color=blue,ha='center')
fig.text(.5,.395,'Annual electricity supply ÷ annual service demand',ha='center',fontsize=10.5)

# g retains both densities, A-H curves, uniform load axis and all facility markers.
t=pd.read_csv(R/'work/data/coverage_uniform_power_grid.csv');aa=pd.read_csv(R/'work/data/coverage_device_markers.csv')
ref=aa[(aa.ISO=='A')&(aa.pairs_per_km==1)].sort_values('load_level');loads=ref.power_W_per_km.to_numpy()
cc=['#235f85']*4+['#789092']*4;ls=['-','--','-.',':']*2
fig.text(.04,.365,'g   Annual energy balance across ISO A–H',fontsize=13,weight='bold')
handles=[Line2D([0],[0],color=cc[j],ls=ls[j],lw=1.5,label=f'ISO {iso}') for j,iso in enumerate('ABCDEFGH')]
fig.legend(handles,[h.get_label() for h in handles],loc='upper left',bbox_to_anchor=(.06,.352),ncol=4,
 fontsize=8.7,frameon=False,borderaxespad=0,columnspacing=1.0,handlelength=1.8,labelspacing=.4)
gaxes=[fig.add_axes([.077,.213,.245,.084]),fig.add_axes([.077,.067,.245,.084])]
for ax,n,title in zip(gaxes,[1,20],['1 harvester pair/km','20 harvester pairs/km']):
 for pp in loads:ax.axvline(pp,color='#9baab3',ls=(0,(3,3)),lw=.6,zorder=1)
 for j in reversed(range(8)):
  iso='ABCDEFGH'[j];z=t[(t.ISO==iso)&(t.pairs_per_km==n)];v=aa[(aa.ISO==iso)&(aa.pairs_per_km==n)]
  curve=pd.concat([z[['power_W_per_km','annual_balance_weighted_road_pct']],v[['power_W_per_km','annual_balance_weighted_road_pct']]]).sort_values('power_W_per_km').drop_duplicates('power_W_per_km')
  ax.plot(curve.power_W_per_km,curve.annual_balance_weighted_road_pct,color=cc[j],ls=ls[j],lw=1.3,zorder=3+(7-j)*.1)
 ax.set(xlim=(0,420),ylim=(-4,106),yticks=[0,25,50,75,100],xticks=np.arange(0,401,100))
 ax.grid(axis='y',color='#dce5eb',lw=.5);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)
 ax.tick_params(length=2,pad=3,labelsize=9)
 ax.text(.985,.92,title,transform=ax.transAxes,ha='right',va='top',fontsize=9.2,weight='bold')
 ax.set_xlabel('Annual average load (W/km)',fontsize=10,labelpad=3)
 row=aa[(aa.ISO=='A')&(aa.pairs_per_km==n)&(aa.load_level==5)].iloc[0]
 ax.annotate(f'ISO A: {row.annual_balance_weighted_road_pct:.2f}%',(loads[4],row.annual_balance_weighted_road_pct),
  xytext=(100,30) if n==1 else (170,99),fontsize=9,color=cc[0],arrowprops=dict(arrowstyle='-',color=cc[0],lw=.7))
fig.text(.045,.183,'Weighted road length reaching annual energy balance (%)',rotation=90,ha='center',va='center',fontsize=10)
labels=['1 radar','3 radars +\nbasic weather','Radar +\nheated weather','Weather\nmonitoring','1 lamp','5 lamps','20 lamps']
for p,label,fx in zip(loads,labels,np.linspace(.08,.315,7)):
 fig.text(fx,.310,label+'\n'+f'{p:.3f}',ha='center',va='bottom',fontsize=6.7,color='#465e6e',linespacing=1.1)
 gaxes[0].annotate('',xy=(p,106),xycoords='data',xytext=(fx,.308),textcoords=fig.transFigure,
  arrowprops=dict(arrowstyle='-',color='#9baab3',lw=.5),annotation_clip=False)

# h: retain the existing named array scenarios and values unchanged.
fig.text(.365,.365,'h   Annual lighting contribution by array scenario',fontsize=13,weight='bold')
h=fig.add_axes([.407,.083,.235,.24])
dh=pd.read_csv(R/'combined/data/panel_h_named_scenarios.csv');vals=dh.annual_energy_matched_pct.to_numpy()
h.bar(np.arange(3),vals,width=.55,color=['#aab7c1','#6eafc3',blue],edgecolor='white',lw=.6,zorder=3)
for j,val in enumerate(vals):h.text(j,val+1.7,f'{val:.2f}%',ha='center',fontsize=12,weight='bold')
h.set(xlim=(-.6,2.6),ylim=(0,80),yticks=[0,20,40,60,80],xticks=[0,1,2],
 xticklabels=['Original array\nwith reference\nstorage transfer','Original array\nwith ideal electrical\nextraction',
 'Full active-length\narray with ideal\nelectrical extraction'],ylabel='Annual lighting demand met (%)')
h.tick_params(axis='x',length=0,pad=8,labelsize=9.6);h.tick_params(axis='y',labelsize=10)
h.yaxis.label.set_fontsize(11);h.spines[['top','right']].set_visible(False)
h.grid(axis='y',color='#dce3e7',lw=.65);h.set_axisbelow(True)
h.text(.02,.96,'20 lamps/km',transform=h.transAxes,ha='left',va='top',fontsize=10,color=muted)

# i: three plate-stroke limits within each ISO A-H category.
from panel_i import draw_panel_i, draw_standalone
fig.text(.69,.365,'i   Vehicle energy demand and electricity',fontsize=13,weight='bold')
fig.text(.69,.346,'Stroke-limited model; 2 t; 20 pairs/km',fontsize=10,color=muted)
data=pd.read_csv(P/'data/current_joint_scenarios.csv').sort_values(['ISO','stroke_m'])
data.to_csv(O/'panel_i_source_data.csv',index=False)
draw_panel_i(fig,data)
draw_standalone(data,O)
fig.savefig(O/'Road_energy_9panels_3x3.png',dpi=330)
fig.savefig(O/'Road_energy_9panels_3x3.pdf')
fig.savefig(O/'Road_energy_9panels_3x3.svg')
plt.rcParams['svg.fonttype']='path';fig.savefig(O/'Road_energy_9panels_3x3_outlined.svg')
im=Image.open(O/'Road_energy_9panels_3x3.png');im.thumbnail((1800,1600));im.save(O/'preview.png')
print('saved',O)
