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

## Repository structure

```text
persimmon-hsi-longitudinal-tracking/
├── notebooks/          # 00–10 cleaned analysis notebooks
├── data/
│   ├── raw/            # public raw archives; ignored by Git
│   ├── interim/        # generated spectral caches; ignored by Git
│   └── splits/         # frozen manuscript fruit-disjoint splits
├── results/reference/  # small frozen final benchmark outputs
├── tables/reference/   # selected manuscript benchmark tables
├── figures/reference/  # final benchmark figures
├── scripts/            # data download and repository verification
├── docs/               # dataset and reproducibility documentation
├── requirements.txt
├── environment.yml
└── .gitignore
```

## Quick start

### 1. Install

```bash
git clone YOUR_REPOSITORY_URL
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

```bash
jupyter lab
```

Execute the notebooks in numerical order from `00_data_audit.ipynb` to `10_final_ml_benchmark.ipynb`.

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

## Data availability

The raw dataset is not redistributed. It is available from the official DeepHS Fruit project:

- Project code: https://github.com/cogsys-tuebingen/deephs_fruit
- Dataset directory: https://cogsys.cs.uni-tuebingen.de/webprojects/DeepHS-Fruit-2023-Datasets/

See `docs/DATASET.md` for exact files and checksums.

## Reproducibility note

The public repository notebooks are cleaned versions of the analysis notebooks: Google Drive mounting, ChatGPT review-package downloads, and conversation-specific instructions were removed. The scientific analysis logic, frozen partitions, random seeds, nested selection procedures, controls, and metrics were preserved.

## Scope

The study evaluates unseen fruits within one acquisition campaign. The repository deliberately preserves session-aware stress tests and other controls, but no result here should be interpreted as independent harvest/batch/campaign validation.

## License and citation

Before public release, confirm the software license with all co-authors and the relevant institution. See `docs/LICENSE_GUIDANCE.md`.

A `CITATION.cff.template` is provided and should be finalized after the manuscript author list and repository URL are fixed.
