# External public data and parameter sources

Associated snapshot: `Road_Vibration_Energy_Global_data.zip` and `GitHub_code_20261119.zip`, 2026-11-19.

This list separates external original-data portals, literature parameters and included processed inputs. Portal links are discovery locations; they are not substitutes for the source-version identifiers and file hashes included in the release. Product-price records retain their original observation dates and are not current quotations.

## Weather

- NASA POWER: <https://power.larc.nasa.gov/>.
- Exact saved hourly request for Krakow (50.0647 N, 19.945 E), 2023, local solar time: <https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=ALLSKY_SFC_SW_DWN%2CALLSKY_SFC_SW_DNI%2CALLSKY_SFC_SW_DIFF%2CT2M%2CWS10M%2CWS50M%2CWD50M&community=RE&longitude=19.945&latitude=50.0647&start=20230101&end=20231231&format=JSON&time-standard=LST>.
- Included request and responses: `modules/multienergy/inputs/node20/data/weather_request.json`, `NASA_POWER_Krakow_2023.json`, `NASA_POWER_2023_radiation_components.json`. Hourly and minute intermediates accompany them.

## Road network, traffic and national inputs

- Road source release identifier: `GRIP4_ExSet_2015_AADTpred_20240312` (ETH/GRIP traffic/road source used in the study). Reuse the exact identifier when obtaining the original source files. This release includes processed road attributes, compact display geometry, source projection and source hashes under `data/`; it does not include the complete original SHP distribution.
- National reconstruction input is included as `modules/national/project/inputs/national/vkt_candidate_inputs.json`. This is a mixed-source compiled input rather than a single-year downloadable census. Scope corrections and training/held-out records are exported by the national reconstruction script.

## Satellite nightlight

- Earth Observation Group VIIRS annual nighttime lights portal: <https://eogdata.mines.edu/products/vnl/>.
- The study cache records 2021 nightlight-derived along-road fractions. Included fractions and group provenance appear in `data/road_batches/` and `modules/nightlight/audit.json`. The full source raster is external; the default release workflow begins with these processed attributes.

## Road spectra and device experiments

- ISO 8608:2016 standard page: <https://www.iso.org/standard/71202.html>. Only the implemented spectrum settings are included, not the copyrighted standard text.
- Duarte, Ferreira and Fael (2020), road-pavement electromechanical harvester experiment: <https://www.researchgate.net/publication/342179415_Road_pavement_energy_harvesting_experimental_validation_of_an_electromechanical_system>. Trial energy is used as the ISO A reference anchor; the test pavement was not reported as measured ISO A.
- Ahmad and Abu Hanieh, Savonius measured power points (Table 3): <https://doi.org/10.1007/s13369-025-10373-w>. Retained points are included in `modules/multienergy/reported_power_points.csv`; the lowest retained nonzero measured speed is 0.7 m/s.
- Contact/limit modelling reference: <https://doi.org/10.1007/978-3-642-01356-0_12>. This supports model formulation, not calibration of the device to all road classes.

## Procurement and storage parameters

- Detailed quoted items, URLs, currencies, dates and interpretation: `modules/lifecycle/newbuild_audit/source/lifecycle_costs/out/price_sources.csv`.
- Rack/pinion catalogue: <https://shop.cncdrive.com/index.php?show_price=yes>.
- Bearing candidate: <https://www.bearings.parts/ucp205-16-pillow-block-baltic-bearing>.
- Battery source: <https://www.litime.com/products/litime-48v-100ah-smart-comflex-lithium-battery>.
- Maintenance-accounting reference: <https://www.energy.gov/cmei/femp/life-cycle-photovoltaic-systems-operate-and-maintain-existing-photovoltaic-system>.
- Complete price, storage-life, maintenance-task and bulk-factor assumptions are retained in `modules/lifecycle/optimized_storage/out/assumptions.json` and `modules/lifecycle/newbuild_audit/out/final_cost_assumptions.json`. Engineering allowances and bulk discounts remain explicit assumptions.

## Corresponding code and deposit identifier

- Code repository: <https://github.com/wowocai/road-vibration-energy-global-v2>.
- Published Zenodo data record: https://zenodo.org/records/24359475; version DOI: https://doi.org/10.5281/zenodo.24359475.
