import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import to_rgb
COLORS=['#275f85','#79aebd','#cf956c'];STROKES=[.005,.01,.025]
def pale(c):return tuple(.48*np.array(to_rgb(c))+.52)
def metric_handles():
 return [Patch(fc='#b8c4cb',ec='white',label='Additional wheel work (95% CI)'),Patch(fc='#586e7d',ec='white',hatch='////',label='Delivered electricity')]
def bars(ax,data,small=False):
 x=np.arange(8);w=.23
 for j,(stroke,color) in enumerate(zip(STROKES,COLORS)):
  z=data[np.isclose(data.stroke_m,stroke)].set_index('ISO').loc[list('ABCDEFGH')]
  wheel=z.extra_wheel_J_per_km.to_numpy()/1000;elec=z.delivered_J_per_km.to_numpy()/1000
  ci=z.extra_wheel_J_per_km_CI95_half.to_numpy()/1000;xx=x+(j-1)*w
  ax.bar(xx,wheel,width=w,color=pale(color),edgecolor='white',lw=.4,zorder=3)
  ax.bar(xx,elec,width=w*.64,color=color,edgecolor='white',lw=.25,hatch='////',zorder=4)
  ax.errorbar(xx,wheel,yerr=ci,fmt='none',ecolor=color,elinewidth=.85 if small else 1.1,capsize=1.5 if small else 2.5,zorder=5)
 upper=max((data.extra_wheel_J_per_km+data.extra_wheel_J_per_km_CI95_half).max(),data.delivered_J_per_km.max())/1000
 top=np.ceil(upper/2)*2
 ax.set(xlim=(-.55,7.55),xticks=x,xticklabels=list('ABCDEFGH'),ylim=(0,top*1.08))
 ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',color='#dce3e7',lw=.6);ax.set_axisbelow(True)
 ax.tick_params(length=2,pad=3,labelsize=9.2)
 return metric_handles()
def zoom(ax,data,small=False):
 a=ax.inset_axes([.73,.55,.255,.40]);z=data[data.ISO=='H'].sort_values('stroke_m')
 for j,(_,v) in enumerate(z.iterrows()):
  a.bar(j,v.extra_wheel_J_per_km/1000,width=.7,color=pale(COLORS[j]),zorder=3)
  a.bar(j,v.delivered_J_per_km/1000,width=.44,color=COLORS[j],hatch='////',edgecolor='white',lw=.2,zorder=4)
  a.errorbar(j,v.extra_wheel_J_per_km/1000,yerr=v.extra_wheel_J_per_km_CI95_half/1000,fmt='none',color=COLORS[j],capsize=1.5,lw=.8,zorder=5)
 a.set(ylim=(0,.8),xticks=[0,1,2],xticklabels=['5','10','25'],yticks=[0,.4,.8])
 a.tick_params(labelsize=6.5 if small else 8,length=2,pad=1)
 a.set_title('ISO H',fontsize=8 if small else 10,pad=3)
 a.set_xlabel('Stroke (mm)',fontsize=7 if small else 8,labelpad=1)
 a.text(.02,.96,'kJ/km',ha='left',va='top',transform=a.transAxes,fontsize=6.5 if small else 8)
 a.spines[['top','right']].set_visible(False);a.grid(axis='y',color='#dce3e7',lw=.4,zorder=0);a.set_axisbelow(True)
def draw_panel_i(fig,data):
 handles=[Patch(fc=pale(c),label=f'{h*1000:.0f} mm') for h,c in zip(STROKES,COLORS)]
 fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.727,.337),ncol=3,fontsize=9.6,frameon=False,borderaxespad=0,columnspacing=1.1,handlelength=1.2)
 ax=fig.add_axes([.734,.083,.235,.24]);handles=bars(ax,data,True)
 ax.set_xlabel('ISO road class',fontsize=10,labelpad=5);ax.set_ylabel('Energy (kJ/vehicle-km)',fontsize=10.5,labelpad=6)
 ax.legend(handles=handles,loc='upper left',frameon=False,fontsize=7.4,borderaxespad=.4,handlelength=1.2)
 zoom(ax,data,True)
 return ax
def draw_standalone(data,out):
 f,ax=plt.subplots(figsize=(10.2,6.2));f.subplots_adjust(left=.10,right=.98,top=.74,bottom=.20)
 f.text(.10,.97,'Vehicle energy demand and electricity across ISO A–H',fontsize=17,weight='bold',va='top')
 f.text(.10,.91,'Stroke-limited model · 2 t · 20 harvester pairs/km',fontsize=11,color='#516473')
 handles=[Patch(fc=pale(c),label=f'{h*1000:.0f} mm stroke limit') for h,c in zip(STROKES,COLORS)]
 f.legend(handles=handles,loc='upper left',bbox_to_anchor=(.095,.86),frameon=False,ncol=3,fontsize=11)
 metric=bars(ax,data);ax.set_xlabel('ISO road class',fontsize=11);ax.set_ylabel('Energy (kJ/vehicle-km)',fontsize=11);ax.tick_params(labelsize=11)
 ax.legend(handles=metric,loc='upper left',frameon=False,fontsize=10)
 zoom(ax,data)
 f.savefig(out/'Panel_i_ISO_A_H_three_strokes.png',dpi=330);f.savefig(out/'Panel_i_ISO_A_H_three_strokes.pdf');plt.close(f)
