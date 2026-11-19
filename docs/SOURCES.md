# Input and parameter provenance

Sources below accompany the supplied study files; this packaging task did not re-audit live product prices. Per-item prices and URLs are in modules/lifecycle/newbuild_audit/source/lifecycle_costs/out/price_sources.csv, candidate_road_pair_BOM.csv and optimized_storage/out/assumptions.json. Procurement discounts and maintenance task times are explicit engineering assumptions, not manufacturer quotations.

| Input/parameter | Source or reconstruction |
|---|---|
| National target/features | Included vkt_candidate_inputs.json and scope_corrections.csv; stock–mileage/ridge reconstructed through the same function used for validation |
| Road traffic/length | ETH/GRIP release identified as GRIP4_ExSet_2015_AADTpred_20240312; original attribute/geometry hashes in data/geometry/manifest.json and input batch manifest |
| ISO class spectrum | ISO8608:2016, https://www.iso.org/standard/71202.html; reference0.1cycle/m, exponent−2, fourfold class PSD increments |
| Duarte trial energy | Duarte,Ferreira&Fael(2020), Road pavement energy harvesting: experimental validation of a new electromechanical system, TRA; supplied source https://www.researchgate.net/publication/342179415_Road_pavement_energy_harvesting_experimental_validation_of_an_electromechanical_system; peak pair input239.4J, electrical144.8J |
| Dense-array configuration | Supplied model snapshot in recalculate.py:17.36J, active length1.32m, repeat2.49m; conditional extraction.307 vs ideal1; ideal cases are numerical benchmarks |
| Nightlight | Precomputed2021VIIRS road-sampling attributes in source cache; original parameter/provenance notes in modules/nightlight/audit.json; do not infer physical lamp absence from non-detection alone |
| Weather/PV | Included NASA POWER2023 JSON and request JSON, Krakow50.0647,19.945; PV20x500Wp, south45deg, model settings in multienergy inputs/out/audit.json |
| Urban wind | Included hourly profile and urban_wind_height_transfer.csv; H15m, frontal density.20, hub3m; formula retained in multienergy/rebuild.py |
| Savonius output | Ahmad&AbuHanieh, Table3; https://doi.org/10.1007/s13369-025-10373-w; tabulated electrical points in reported_power_points.csv; .7m/s is lowest retained nonzero test point, not a validated charger cut-in |
| Device/road geometry | Loading length and response assumptions in device_response source/README; stroke, tire patch, stop stiffness and integration settings in repaired_model/run.py and archived run JSON |
| Facilities | Five power configurations in modules/supply/power_ladder.json and archived coverage_device_markers.csv; lamp annual179.0114kWh; equipment combinations and duty-cycle assumptions retained explicitly |
| Costs/storage | Bill of materials and price-source CSV; bulk coefficient.5 with sensitivity; LiTime5.12kWh module source and maintenance accounting references recorded in lifecycle assumptions JSON |

A publicly resolvable Zenodo record URL and DOI must be inserted only after the deposit is published. There is no invented Zenodo link in this package.
