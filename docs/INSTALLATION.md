# Environment configuration

Tested: Python 3.12, Linux x86_64. Install exact versions in requirements.txt in a fresh virtual environment. Conda users may use environment.yml; compiler names refer to conda-forge meta-packages. No internet connection is needed for numerical runs after installing dependencies and extracting both archives.

System tools: GNU-compatible C/C++ compilers (`cc`, `g++`), standard libm. Typical Ubuntu installation: `sudo apt install build-essential python3-venv`. On Windows use WSL2/Linux; Windows native shared-library loading is not a tested configuration. Do not reuse binaries from another operating system.

`quick` uses hundreds of MB of arrays for 3.29 million roads and minute profiles; allow several GB of free RAM. National RF cross-validation is slower than quick aggregation; fresh ODE ensembles are substantially more expensive. Exact runtimes are recorded in release_validation.json; do not use aggregation timing as ODE timing.

Times New Roman is used when installed locally. A serif fallback is selected by the portable coverage plot. Font binaries are not redistributed. Install a legitimately licensed font before final journal rendering.

Outputs are under outputs/ and module-local out/ folders as listed in WORKFLOW.md. Run commands from the project directory; entry points resolve input paths against their own file location, not the previous author's computer.
