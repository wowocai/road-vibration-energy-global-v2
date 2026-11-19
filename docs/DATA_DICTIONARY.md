# Data dictionary and units

| File/field | Definition and units |
|---|---|
| data/road_batches/batch_*.npz: row_id | Zero-based source road record ID; join to source/display geometry, not a resampled segment identifier |
| length_km | Source attribute LEN/1000; one occurrence per retained record; no additional lane/direction factor |
| aadt_q05, aadt_median, aadt_q95 | Predicted annual-average daily traffic, vehicles/day |
| country, road_type | Source coded attributes; retain original codes |
| positive_fraction, outside_fraction | Fractions of precomputed along-road nightlight samples; not a direct observation of lamp count or electricity access |
| data/geometry/roads.bin | Varint/zigzag display geometry; encoding, original CRS and source hashes in manifest.json/source.prj; not the source of statistical road lengths |
| modules/supply/input_records.npz | Compact four-field fallback (ID,L,Q,positive_fraction); same retained records as full batches |
| national VKT input | Mixed-source national table; reported targets in million vehicle-km/year; not a single-year globally observed census |
| national outputs | Long form country/category/method, observed or reconstructed route; held-out fold membership and prediction per record |
| work_tau25; ratio_tau25 | Device-response mechanical statistic and its ISOA-normalized ratio; 25ms primary response |
| vehicle-energy JSON | Single simulation settings, convergence status, mechanical work in J/km and energy balances; averaging hierarchy in aggregate.py |
| current_joint_scenarios.csv | A–H x three stroke upper limits; additional wheelwork and delivered electricity in J/vehicle/km |
| minute_inputs.npz | 525600 minute bins; PV_Wh,wind_Wh,vibration_Wh,load_Wh in Wh/bin; night Boolean mask |
| lifecycle outputs | USD/km net present expenditure, battery nominal kWh/km, purchased kWh/year, EFC/year; quantity and replacement assumptions in assumptions.json |
| service_all_domains.csv | ISO, density pairs/km, facility scenario, spatial domain; coverage_pct is balanced length fraction, energy_match_pct is locally credited energy fraction |

Primary formulas: s_i=365 Q_i h d e r/3.6e6 [kWh/km/year]; D_i=8760 P_i/1000 for continuous equivalent power [kWh/km/year]. C=Σ L_i 1(s_i≥D_i)/Σ L_i; U=Σ L_i min(s_i,D_i)/Σ L_i D_i. h=.5 and r=.8 are deployment assumptions; eta=144.8/239.4 is the trial-derived conversion ratio. Nightlight-weighted historical comparisons use L_i p_i and are never the primary denominator.

ISOA is a reference-spectrum anchoring assumption, not a measured classification of Duarte's test pavement. Device A–H relative responses and national linear A–H suspension dissipation are distinct outputs. H vehicle-extra-work uses a separate low-speed joint scenario.
