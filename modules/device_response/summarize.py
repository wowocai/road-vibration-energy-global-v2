from pathlib import Path
import pandas as pd,numpy as np
P=Path(__file__).resolve().parent
x=pd.read_csv(P/'phase_results.csv');out=[]
for (ref,mode),g in x.groupby(['refinement','vehicle_proxy']):
 means=g.groupby('iso').mean(numeric_only=True)
 for iso,z in means.iterrows():
  out.append(dict(iso=iso,refinement=ref,vehicle_proxy=mode,ratio_tau25=z.work_tau25/means.loc['A','work_tau25'],tire_time_out_of_contact_pct=100*z.tire_time_out_of_contact))
s=pd.DataFrame(out);s.to_csv(P/'recomputed_relative_response.csv',index=False)
ref=pd.read_csv(P/'ISO_A-H_contact_results.csv').set_index('iso');main=s[(s.refinement==2)&(s.vehicle_proxy==0)].set_index('iso')
assert np.allclose(main.ratio_tau25,ref.ratio_tau25,rtol=1e-7)
print(main)
