# Script-level computational workflow

| Order | Entry or script | Inputs | Calculation | Outputs |
|---|---|---|---|---|
| 1 | scripts/run_pipeline.py: passive() | modules/passive_vehicle/model.py parameter table | Passive 7DOF spatial-frequency integration; corner assembly and mesh refinement | outputs/passive_vehicle_A_H.csv; fresh national unit-response input; validation JSON |
| 2 | modules/national/unify_national.py | project/inputs/national/vkt_candidate_inputs.json; fresh unit responses | Swiss bus scope correction before fitting; stock–mileage/ridge primary, RF and ridge benchmarks; shared country folds, seeds42/2026; national A–H resource totals | outputs/national/* CSV, cleaned JSON and QA.json |
| 3 | modules/supply/recalculate.py | data/road_batches/*.npz; power_ladder.json; ISO_A-H_contact_results.csv | Source-length/AADT validation; per-road supply and prescribed facility demand; weighted-CDF exact aggregation; dense arrays and inverse targets | modules/supply/service_all_domains.csv, dense_array_comparison.csv, inverse_targets.csv, Figure4g_full_length_curves.csv, audit.json |
| 4 | modules/vehicle_energy/aggregate.py | reference_runs/*.json; H_validation/out/summary.csv | Opposite-phase pairs, independent-seed mean and t confidence intervals; delivered energy using measured efficiency and retention | figure/data/current_joint_scenarios.csv, repaired_A_G_raw.csv |
| 5 | scripts/run_pipeline.py: energy_profiles() | archived minute PV/traffic/load inputs; hourly urban wind; reported_power_points.csv | Interpolate Savonius measured power points; zero below lowest retained measurement; compute annual/night/minute metrics | modules/multienergy/node20/out and equal_investment/out |
| 6 | modules/lifecycle/optimized_storage/optimize.py + dispatch.cpp | **Current** node20 minute profiles; procurement/BOM assumptions | Cyclic SOC storage dispatch; separate equipment, installation, task-based maintenance, replacement, storage and purchased electricity; 20yr5% present value | optimized_storage/out/optimized_cost_breakdown.csv; capacity, maintenance and storage-price sensitivities |
| 7 | scripts/run_pipeline.py: figures(),validate() | Current full-length supply outputs and recomputed metrics | Coverage-curve preview and numerical release checks | outputs/full_length_coverage_curves.png; validation.json |

## Fresh dynamics rather than record aggregation

`python scripts/run_pipeline.py --stage device-dynamics` compiles vehicle.c, regenerates contact/phase records and verifies relative ISO responses. This is the separate device-response model used to scale A-anchored output; it is not the fully coupled vehicle-extra-work model. Its summarizer does not use historical nightlight weights.

`python scripts/run_pipeline.py --stage vehicle-dynamics` compiles repaired_model/model.c, then compute.py runs A–G ensembles. Existing matching filenames are reused; move reference_runs aside to force a fresh A–G ensemble. Seeds3101–3116, opposite phases, strokes5/10/25mm, A–F50km/h and G5km/h are explicit in compute.py. The paired coupled solver includes unilateral contact/recontact and adaptive integration. Do not clip negative individual differences or replace failed integration with zero.

`python scripts/run_H_scenario.py --seed 3101 --stroke .005` reruns an H phase pair at2km/h. Repeat seeds and strokes for an ensemble; included H_validation records contain the completed stability experiments and settings. H reaggregation in the quick pipeline uses the validated ensemble_2 summary, not this single-pair diagnostic.

## Supplemental and archived scripts

`modules/nightlight/calculate_cross_statistics.py` and its existing outputs record supplementary nightlight group intersections; historical weighting labels must remain visible. The default pipeline uses full L for its primary outputs. Archive/iowa_si retains the 27-case spectral/speed/freight sensitivity, archive/regional_calculation the regional comparisons, and archive/figure_sources the prior manuscript plotting sources. These originals may expect their historical companion folders; they are preserved for provenance and are not portable default entry points.

`modules/multienergy/rebuild.py` preserves the detailed Fig5 rendering transformations, including logarithmic annual-energy/area axes. The portable numerical runner recomputes the wind substitution and metrics from the included reference minute inputs; it does not re-fetch NASA weather or claim to reconstruct the complete weather-to-minute preprocessing. File-to-file histories, intermediate records and original scripts are included so that this boundary is explicit.

`modules/lifecycle/newbuild_audit/` retains the parts/retail/bulk and common-maintenance comparisons. Current primary cost computation is optimized_storage/optimize.py; do not substitute an earlier fixed10.24kWh table.
