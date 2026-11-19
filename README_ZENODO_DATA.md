# Zenodo data deposit: global road vibration energy

Release snapshot: 2026-11-19.

## Files and corresponding code

- `Road_Vibration_Energy_Global_data.zip`: processed inputs, numerical simulation records, reference outputs and data manifests.
- `README_ZENODO_DATA.md`: this deposit-level guide.
- `EXTERNAL_PUBLIC_DATA_URLS.md`: external data and parameter sources.
- The matching code archive is `GitHub_code_20261119.zip`, prepared for the repository <https://github.com/wowocai/road-vibration-energy-global-v2>.
- `Road_vibration_complete_20261119.zip` combines the matching code and data archives; it is an alternative download, not an additional dependency.

Extract the data and code archives into the same parent directory. Both use the root folder `road-vibration-energy-global/`. The data archive alone is not the executable code release. Published data record: https://zenodo.org/records/24359475. Version DOI: https://doi.org/10.5281/zenodo.24359475.

## Contents

| Location after extraction | Contents |
|---|---|
| `data/road_batches/` | 331 processed road-attribute batches: IDs, source lengths, country/type codes, AADT Q05/median/Q95 and nightlight fractions |
| `data/geometry/` | Compact display geometry, source projection and geometry provenance |
| `modules/national/project/inputs/national/` | National traffic targets and reconstruction features |
| `modules/supply/` | Compact road-input fallback, device-response factors, facility budgets and regenerated supply/demand tables |
| `modules/vehicle_energy/` | Completed coupled-model records, H-class validation records and aggregated vehicle-energy results |
| `modules/device_response/` | Phase-level relative device-response data and numerical sensitivity results |
| `modules/multienergy/` | Weather JSON, hourly profiles, minute energy/load arrays and multi-energy metrics |
| `modules/lifecycle/` | Procurement/BOM source tables, storage/cost scenarios and optimization results |
| `modules/nightlight/` | Supplementary nightlight-group intersections |
| `reference/`, `outputs/` | Reference and release-run numerical outputs |
| `archive/` | Earlier plotting inputs and supplementary experiment provenance; labels identify historical domains |

## Run

Python 3.12 is the tested environment. Install the pinned dependencies supplied in the code archive:

```bash
cd road-vibration-energy-global
python -m pip install -r requirements.txt
python scripts/run_pipeline.py --stage quick
python scripts/run_pipeline.py --stage national
python scripts/run_pipeline.py --stage cost
```

Cost optimization and fresh dynamics require C/C++ compilers (`cc`, `g++`). Detailed installation instructions, script inputs/outputs, units and source notes are in `docs/INSTALLATION.md`, `docs/WORKFLOW.md`, `docs/DATA_DICTIONARY.md` and `docs/SOURCES.md` in the code archive.

`quick` recomputes road-level supply/demand, thresholds and coverage curves, reaggregates completed vehicle simulations and recalculates current wind/time-matching metrics. `national` refits traffic reconstruction and country-held-out validation. `cost` recompiles dispatch and optimizes battery capacities. Fresh nonlinear simulation ensembles have separate commands in the workflow guide.

## Spatial and energy accounting

Primary supply/demand aggregation uses the complete retained source road length: 3,293,705 records and 6,906,689.106 km. Nightlight defines supplementary groups and explicitly labelled historical comparisons; it does not reduce the primary facility-demand denominator. The 218-country suspension-resource inventory and the road-level device supply calculation describe different energy quantities.

The source road length determines statistics; simplified display geometry does not. ISO A–H are specified scenarios, and the trial output anchors ISO A by assumption. Completed simulation records and minute energy arrays are supplied as reproducible intermediate data.

## Sources, integrity and reuse

Full-resolution original global SHP and VIIRS raster are not included. The processed attributes, display geometry and source manifests are included. External source links and reconstruction boundaries are listed in `EXTERNAL_PUBLIC_DATA_URLS.md`.

`FILE_MANIFEST.csv` in the data archive describes release-tree files and SHA-256 hashes; `SHA256SUMS.txt` in the matching code archive verifies those files. `release_validation.json` records calculations actually executed for this release. Manuscripts and private reviewer documents are excluded.

Licensing for author-owned material should be selected by the authors when publishing. Third-party terms continue to apply; consult `THIRD_PARTY_NOTICES.md` in the code archive. The published data record is https://doi.org/10.5281/zenodo.24359475.
