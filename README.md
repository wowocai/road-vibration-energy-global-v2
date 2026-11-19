# Road vibration energy: reproducible code and processed data

Release snapshot: **2026-11-19**. Intended repository: https://github.com/wowocai/road-vibration-energy-global-v2

This package provides the national traffic reconstruction, passive seven-degree-of-freedom resource model, road-level device supply/demand calculations, coupled vehicle–device model, multi-energy profiles and lifecycle-cost calculations used in the revised study.

**Primary aggregation is full source road length.** Nightlight fractions define supplementary groups and historical comparisons; they do not multiply primary road length or facility demand. The 218-country resource calculation and the 6.906689-million-km deployment calculation are different scales and are not interchangeable energy totals.

## Install and run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_pipeline.py --stage quick
python scripts/run_pipeline.py --stage national
python scripts/run_pipeline.py --stage cost
```

Linux/macOS is recommended. Cost optimization and fresh dynamics require `cc` and `g++`. Python 3.12 and exact tested package versions are recorded in requirements.txt. `--stage all` runs all three numerical stages above. Expensive fresh dynamics are separate: `--stage device-dynamics`, `--stage vehicle-dynamics`, and `scripts/run_H_scenario.py`.

The GitHub code archive and Zenodo data archive expand into the **same top-level directory**. Extract both together, or use the all-in-one archive. The data archive also contains reference outputs and geometry; the code archive alone does not contain the large numerical inputs.

See [installation](docs/INSTALLATION.md), [script workflow](docs/WORKFLOW.md), [data dictionary](docs/DATA_DICTIONARY.md), [sources](docs/SOURCES.md), [release boundaries](docs/RELEASE_SCOPE.md), and [upload instructions](docs/UPLOAD.md). `SHA256SUMS.txt` verifies file bytes. Results of the release checks are in `release_validation.json`.

## Data/code availability wording

The code and processed data are provided in the associated repository and data deposit, with environment configuration, dependency versions, and script-level workflow documentation. Add the actual Zenodo record DOI and repository release URL after publication; this snapshot does not assert that a DOI or public release already exists.

No software or third-party data license is assigned by this packaging step. Consult THIRD_PARTY_NOTICES.md before public redistribution.
