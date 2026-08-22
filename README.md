# Robust Longitudinal Hyperspectral Tracking of Postharvest Storage Time in Persimmon

Reproducible analysis code for a longitudinal reanalysis of the public **DeepHS Fruit v2** persimmon (Kaki) hyperspectral dataset.

The project evaluates postharvest storage-time estimation under biologically grouped validation and includes fruit-specific baseline referencing, session-excluded stress tests, negative controls, spectral simplification, cross-sensor transfer, and a final classical machine-learning benchmark.

## Scientific design

The reconstructed longitudinal panel contains:

- **40 physical fruits**
- **199 fruit × day observations**
- **793 HSI cubes**
- two Vis–NIR imaging sensors: **VIS (Specim FX10)** and **VIS_COR (Corning microHSI 410)**
- storage-day targets: **0, 1, 2, 3, 4, 6, 7, 8**

The core evaluation principle is that all observations from the same physical fruit remain together. The official DeepHS record-level splits are not used for temporal model assessment because fruit identities overlap across those splits.

The frozen manuscript partitions are committed under `data/splits/`. The outer design contains **5 folds × 8 held-out physical fruits**, and each outer-development set is subdivided into **4 inner folds × 8 fruits**. The repository verifier checks that no outer-test fruit appears in its corresponding inner cross-validation set and verifies the exact SHA-256 fingerprints of both split files.

## Repository structure

```text
persimmon-hsi-longitudinal-tracking/
├── .github/workflows/  # automated static repository audit
├── notebooks/          # 00–10 cleaned canonical analysis notebooks
├── data/
│   ├── raw/            # public raw archives; ignored by Git
│   ├── interim/        # generated spectral caches; ignored by Git
│   └── splits/         # frozen manuscript fruit-disjoint splits
├── results/reference/  # small frozen final benchmark outputs
├── tables/reference/   # selected manuscript benchmark tables
├── figures/reference/  # final benchmark figures
├── scripts/            # downloader, sequential runner, repository verifier
├── docs/               # dataset and reproducibility documentation
├── requirements.txt
├── environment.yml
└── .gitignore
```

## Quick start

### 1. Install

The final benchmark manifest records **Python 3.12.13**, **NumPy 2.0.2**, and **pandas 2.2.3**. `environment.yml` is aligned with Python 3.12 and the captured NumPy/pandas versions; compatible ranges are retained for packages whose exact historical versions were not recorded.

```bash
git clone https://github.com/Julians30/persimmon-hsi-longitudinal-tracking.git
cd persimmon-hsi-longitudinal-tracking
python -m venv .venv
```

Activate the environment and install:

```bash
pip install -r requirements.txt
```

### 2. Download the public data

```bash
python scripts/download_data.py
```

The script downloads `Kaki.zip` and `annotations-upd-2024-01-09.zip` from the official University of Tübingen server and verifies the SHA-256 checksums used in the manuscript analysis.

### 3. Run the workflow

Interactive execution:

```bash
jupyter lab
```

Execute the notebooks in numerical order from `00_data_audit.ipynb` to `10_final_ml_benchmark.ipynb`.

Sequential execution is also available:

```bash
python scripts/run_notebooks.py
```

The runner does **not** overwrite the cleaned canonical notebooks. Executed copies are written by default to `exports/executed_notebooks/`, which is ignored by Git.

See:
- `docs/NOTEBOOK_MAP.md`
- `docs/REPRODUCIBILITY.md`
- `docs/DATASET.md`

## Final classical benchmark

The final benchmark evaluates five regression algorithms:

- Ridge Regression
- PLS Regression
- RBF-SVR
- Random Forest
- Extra Trees

Reported metrics include MAE, RMSE, R², Spearman correlation, ±1-day accuracy, fruit-balanced MAE, day-balanced MAE, and bias.

The repository contains a small frozen set of final benchmark outputs under `results/reference/`, `tables/reference/`, and `figures/reference/` so reviewers can verify the reported manuscript values without storing the raw 2.2 GB HSI archive in Git.

## Automated reproducibility audit

`python scripts/verify_repository.py` performs a static pre-publication audit. GitHub Actions runs the same verifier automatically on pushes and pull requests to `main`.

The audit checks:

- the exact 11-notebook inventory;
- notebook JSON validity, stripped outputs, cleared execution counts, and code-cell syntax;
- syntax and headers of the repository utility scripts;
- absence of active Google Drive / Colab / chat-specific notebook code;
- exact frozen split hashes and nested fruit-disjoint integrity;
- required frozen reference JSON outputs, tables, and PNG figures;
- absence of tracked raw HSI archives, model checkpoints, secret files, and common credential patterns.

This is a **static** audit. Full end-to-end reproduction still requires downloading the public raw HSI archive and executing the analysis from raw data.

## Data availability

The raw dataset is not redistributed. It is available from the official DeepHS Fruit project:

- Project code: https://github.com/cogsys-tuebingen/deephs_fruit
- Dataset directory: https://cogsys.cs.uni-tuebingen.de/webprojects/DeepHS-Fruit-2023-Datasets/

See `docs/DATASET.md` for exact files and checksums.

## Reproducibility note

The repository notebooks are cleaned versions of the analysis notebooks: Google Drive mounting, ChatGPT review-package downloads, and conversation-specific instructions were removed. The scientific analysis logic, frozen partitions, random seed, nested selection procedures, controls, bootstrap design, and reported metrics were preserved.

## Scope

The study evaluates unseen fruits within one acquisition campaign. The repository deliberately preserves session-aware stress tests and other controls, but no result here should be interpreted as independent harvest/batch/campaign validation.

## License and citation

Before public release, confirm the software license with all co-authors and the relevant institution. See `docs/LICENSE_GUIDANCE.md`.

A `CITATION.cff.template` is provided and should be finalized after the manuscript author list and repository release metadata are fixed.
