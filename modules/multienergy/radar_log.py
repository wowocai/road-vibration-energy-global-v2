def apply_log_radar(template):
    start=template.index("labels=['Annual energy sufficiency")
    end=template.index("b.text(-.04,-1.34",start)
    block=r'''labels=['Annual energy sufficiency\n(%; 20 lamps/km)','Night-time direct\nenergy coverage (%)','No-storage coverage\n(%; 1-min energy balance)','Annual electricity per collector area\n(kWh/m²/year; log scale)','Annual electricity\n(kWh/km/year; log scale)']
radar_max=np.array([100.,20.,60.,np.nan,np.nan])
# Physical log ranges: 1e-4..1e3 kWh/m²/year and 1e-3..1e4 kWh/km/year.
log_bounds={3:(-4.,3.),4:(-3.,4.)}
for j,(v,label) in enumerate(zip(u,labels)):
 label_pos=v*1.25
 if j in [1,4]:label_pos[1]+=.14
 b.text(*label_pos,label,ha='center',va='center',fontsize=8.4)
 if j<3:
  ticks=[(rr,f'{radar_max[j]*rr:.0f}') for rr in [.2,.4,.6,.8,1]]
 else:
  lo,hi=log_bounds[j]
  ticks=[((ex-lo)/(hi-lo),f'$10^{{{ex}}}$' if ex not in [0,1] else ('1' if ex==0 else '10')) for ex in range(int(lo)+1,int(hi)+1)]
 for rr,val in ticks:
  pp=v*rr+np.array([-v[1],v[0]])*.038
  b.text(*pp,val,ha='center',va='center',fontsize=6.7,color='#8195a0',bbox=dict(facecolor='white',alpha=.8,edgecolor='none',pad=.1))
for k,(name,c) in enumerate(zip(names,colors)):
 z=m.loc[name]
 raw_r=np.array([z.annual_energy_sufficiency_pct,z.night_direct_energy_coverage_pct,z.no_storage_minute_full_load_coverage_pct,area_yields[name],z.annual_generation_kWh_per_km])
 r=np.empty(5);r[:3]=raw_r[:3]/radar_max[:3]
 for j in [3,4]:
  lo,hi=log_bounds[j]
  assert raw_r[j]>0, 'A zero value cannot be plotted on a logarithmic axis'
  r[j]=(np.log10(raw_r[j])-lo)/(hi-lo)
 assert ((r>=0)&(r<=1)).all(), 'Radar data outside declared axis range'
 q=u*r[:,None]
 for j in range(5):
  jj=(j+1)%5
  b.plot(q[[j,jj],0],q[[j,jj],1],color=c,lw=1.8,ls=['-','--','-'][k])
 b.plot(q[:,0],q[:,1],ls='',marker=['o','s','D'][k],ms=4,color=c,label=name)
'''
    return template[:start]+block+template[end:]
