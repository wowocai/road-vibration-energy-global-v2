import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import to_rgb
COLORS=['#275f85','#79aebd','#cf956c']
STROKES=[.005,.01,.025]
def pale(c):
    rgb=np.array(to_rgb(c));return tuple(.48*rgb+.52)
def bars(ax,data):
    x=np.arange(8);w=.23
    for j,(stroke,color) in enumerate(zip(STROKES,COLORS)):
        z=data[np.isclose(data.stroke_m,stroke)].set_index('ISO').loc[list('ABCDEFG')]
        wheel=z.extra_wheel_work_J_per_km.to_numpy()/1000
        elec=z.delivered_electricity_J_per_km.to_numpy()/1000
        assert np.all(elec<=wheel)
        xx=x[:7]+(j-1)*w
        ax.bar(xx,wheel,width=w,color=pale(color),edgecolor='white',linewidth=.4,zorder=3)
        # Same baseline, narrower overlaid bars. The two energies are NOT added.
        ax.bar(xx,elec,width=w*.64,color=color,edgecolor='#ffffff',linewidth=.25,
               hatch='////',zorder=4)
    ax.axvspan(6.52,7.48,facecolor='#f3f4f4',edgecolor='#bec7cb',hatch='///',lw=.45,zorder=0)
    ax.text(7,.49,'Not converged',transform=ax.get_xaxis_transform(),ha='center',va='center',
            rotation=90,fontsize=8.3,color='#687984',bbox=dict(fc='white',ec='none',pad=1.4))
    ax.set(xlim=(-.55,7.55),xticks=x,xticklabels=list('ABCDEFGH'),ylim=(0,12),yticks=np.arange(0,13,2))
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color='#dce3e7',lw=.6);ax.set_axisbelow(True)
    ax.tick_params(length=2,pad=3,labelsize=9.2)
    return [Patch(fc='#b8c4cb',ec='white',label='Additional wheel work'),
            Patch(fc='#586e7d',ec='white',hatch='////',label='Delivered electricity')]
def draw_panel_i(fig,data):
    handles=[Patch(fc=pale(c),label=f'{h*1000:.0f} mm') for h,c in zip(STROKES,COLORS)]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.727,.337),ncol=3,
               fontsize=9.6,frameon=False,borderaxespad=0,columnspacing=1.1,handlelength=1.2)
    ax=fig.add_axes([.734,.083,.235,.24]);handles=bars(ax,data)
    ax.set_xlabel('ISO 8608 road class',fontsize=10,labelpad=5)
    ax.set_ylabel('Energy (kJ/vehicle-km)',fontsize=10.5,labelpad=6)
    ax.legend(handles=handles,loc='upper left',frameon=False,fontsize=9.5,
              borderaxespad=.6,handlelength=1.7)
    return ax
def draw_standalone(data,out):
    f,ax=plt.subplots(figsize=(9.2,5.5))
    f.subplots_adjust(left=.10,right=.98,top=.76,bottom=.14)
    f.text(.10,.97,'Vehicle energy demand and electricity across ISO A–H',fontsize=17,weight='bold',va='top')
    f.text(.10,.90,'Stroke-limited model · 2 t · 50 km/h · 20 harvester pairs/km',fontsize=11,color='#516473')
    handles=[Patch(fc=pale(c),label=f'{h*1000:.0f} mm stroke limit') for h,c in zip(STROKES,COLORS)]
    f.legend(handles=handles,loc='upper left',bbox_to_anchor=(.095,.854),frameon=False,ncol=3,fontsize=11)
    metric=bars(ax,data)
    ax.set_xlabel('ISO 8608 road class',fontsize=11)
    ax.set_ylabel('Energy (kJ/vehicle-km)',fontsize=11)
    ax.tick_params(labelsize=11)
    ax.legend(handles=metric,loc='upper right',bbox_to_anchor=(.84,1.01),frameon=False,fontsize=10.5,ncol=1)
    f.savefig(out/'Panel_i_ISO_A_H_three_strokes.png',dpi=330)
    f.savefig(out/'Panel_i_ISO_A_H_three_strokes.pdf')
    plt.close(f)
