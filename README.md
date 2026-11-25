# Road vibration energy: reproducible code and processed data

Release snapshot: **2026-11-19**. Code repository: https://github.com/wowocai/road-vibration-energy-global-v2

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

The processed data are published on [Zenodo](https://zenodo.org/records/24359475), DOI [10.5281/zenodo.24359475](https://doi.org/10.5281/zenodo.24359475). Download `Road_Vibration_Energy_Global_data.zip` from that record. Merge its `road-vibration-energy-global/` contents with the code in the same working directory, or merge the matching code and data archives, which share that internal root. The data archive also contains reference outputs and geometry; the code archive alone does not contain the large numerical inputs.

See [installation](docs/INSTALLATION.md), [script workflow](docs/WORKFLOW.md), [data dictionary](docs/DATA_DICTIONARY.md), [sources](docs/SOURCES.md), [release boundaries](docs/RELEASE_SCOPE.md), and [upload instructions](docs/UPLOAD.md). `SHA256SUMS.txt` verifies file bytes. Results of the release checks are in `release_validation.json`.

## Data and code availability

Processed inputs, simulation records and numerical results are available on Zenodo at https://doi.org/10.5281/zenodo.24359475. The data deposit includes a file manifest and source notes. Analysis code is available in this repository, with environment configuration, pinned dependencies and script-level workflow documentation.

See [the Zenodo data guide](README_ZENODO_DATA.md) and [external data sources](EXTERNAL_PUBLIC_DATA_URLS.md). The Zenodo deposit specifies CC BY 4.0 for the deposited data; software licensing and third-party terms are described separately in THIRD_PARTY_NOTICES.md.


## License

Original analysis code is released under the [MIT License](LICENSE). Third-party data and other materials retain their respective terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
