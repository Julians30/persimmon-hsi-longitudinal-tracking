# Fruit-Disjoint and Matched-Null Validation of Baseline-Referenced Hyperspectral Models for Tracking Persimmon Storage Time

[![Repository audit](https://github.com/Julians30/persimmon-hsi-longitudinal-tracking/actions/workflows/repository-audit.yml/badge.svg)](https://github.com/Julians30/persimmon-hsi-longitudinal-tracking/actions/workflows/repository-audit.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![Release](https://img.shields.io/badge/release-v1.0.0-black.svg)](https://github.com/Julians30/persimmon-hsi-longitudinal-tracking/releases/tag/v1.0)
![Python 3.12](https://img.shields.io/badge/Python-3.12-black.svg)

Code and reproducibility materials for the article submitted to *Chemometrics and Intelligent Laboratory Systems*:

> Coronel-Reyes, J.; Carvajal Romero, H. R.; Haro-Sarango, A. Fruit-Disjoint and Matched-Null Validation of
> Baseline-Referenced Hyperspectral Models for Tracking Persimmon Storage Time. (under review)

The study reanalyses the public **DeepHS Fruit v2** persimmon (kaki) series with a validation framework for
longitudinal spectral regression: fruit-disjoint nested cross-validation, target-day/session-exclusion stress tests
against matched null models, negative and baseline-mismatch controls, and multiplicity-adjusted paired
fruit-bootstrap inference. The results reported in the article correspond to release **v1.0**.

## Data

| Item | Value |
|---|---|
| Physical fruits | 40 |
| Fruit-day observations | 199 |
| HSI cubes | 793 |
| Cameras | VIS (Specim FX10, 224 bands) and VIS_COR (Corning microHSI 410, 249 bands) |
| Storage days | 0, 1, 2, 3, 4, 6, 7, 8 |

All observations of one physical fruit always stay in the same fold. The outer design has 5 folds of 8 test fruits;
each outer-development set is split into 4 inner folds of 8 fruits for preprocessing and hyperparameter selection.
The raw data are not redistributed here; they are downloaded from the official source and checked by SHA-256.

## Repository structure

```text
persimmon-hsi-longitudinal-tracking/
├── notebooks/              # 00–10 analysis notebooks (run in order)
├── data/
│   ├── raw/                # public raw archives (downloaded, not tracked)
│   ├── interim/            # fruit-day spectra written by notebook 01 (not tracked)
│   └── splits/             # frozen fruit-disjoint outer and inner splits
├── results/
│   ├── reference/          # final benchmark summary and run manifest
│   └── manuscript_oof/     # frozen out-of-fold predictions of notebooks 05, 06, 08–10
├── tables/reference/       # benchmark tables of notebook 10
├── figures/reference/      # benchmark figures of notebook 10
├── manuscript/
│   ├── scripts/            # primary contrasts, Table 5 comparison, Figures 1–9, Ridge re-fit check
│   ├── tables/             # outputs of the manuscript scripts
│   └── figures/            # Figures 1–9 of the article (PNG 600 dpi and PDF)
├── scripts/                # data download, notebook runner, repository verifier
├── docs/                   # dataset, notebook map and reproducibility protocol
├── LICENSE                 # MIT
├── CITATION.cff
├── CHANGELOG.md
├── requirements.txt
└── environment.yml
```

## Quick verification (no raw data needed)

```bash
git clone https://github.com/Julians30/persimmon-hsi-longitudinal-tracking.git
cd persimmon-hsi-longitudinal-tracking
pip install -r requirements.txt
python scripts/verify_repository.py
cd manuscript/scripts
python primary_contrasts.py          # C1–C4 with Holm and Bonferroni adjustment
python simplification_vs_final.py    # sparse and virtual panels versus the full spectrum (Table 5)
python make_workflow_figure.py       # Figure 1
python make_figures.py               # Figures 2, 4, 5, 6, 8, 9 (3 and 7 need the fruit-day spectra)
```

See `manuscript/README.md` for the correspondence between scripts, tables and figures of the article.

## Full reproduction from the raw data

```bash
python scripts/download_data.py      # Kaki.zip and annotations, verified by SHA-256
python scripts/run_notebooks.py      # executes notebooks 00–10 in order into exports/executed_notebooks/
cd manuscript/scripts
python make_figures.py --results-root ../../results
python check_ridge_reproduction.py   # independent re-fit of the notebook 10 Ridge model
```

The notebooks can also be run interactively with `jupyter lab`, from `00_data_audit.ipynb` to
`10_final_ml_benchmark.ipynb`. All analyses use the random seed 20260818. The final benchmark run recorded
Python 3.12.13, NumPy 2.0.2 and pandas 2.2.3; see `docs/REPRODUCIBILITY.md` and `docs/NOTEBOOK_MAP.md`.

## Models and metrics

Ridge regression, partial least squares regression (PLSR), RBF support vector regression, Random Forest and Extra
Trees, applied to absolute spectra (single-scan screening) and to SNV spectra referenced to the same fruit at day 0
(Δ-SNV, longitudinal tracking). The primary metric is the fruit-balanced mean absolute error (FB-MAE); MAE, RMSE, R²,
Spearman ρ, ±1-day accuracy, day-balanced MAE and bias are also reported.

## Automated checks

GitHub Actions runs on every push: it confirms that the notebooks, splits and reference outputs are unchanged since
the benchmark run, verifies split hashes and fruit-disjoint integrity, checks that notebooks carry no stored outputs,
credentials or environment-specific code, and recomputes the primary contrasts from the frozen predictions.

## Scope

All results come from one acquisition campaign in which storage day coincides with acquisition session. They
describe generalization to unseen fruits of that campaign, not to independent harvest lots or campaigns.

## Data source

DeepHS Fruit project, Cognitive Systems Group, University of Tübingen:
code at https://github.com/cogsys-tuebingen/deephs_fruit and data at
https://cogsys.cs.uni-tuebingen.de/webprojects/DeepHS-Fruit-2023-Datasets/. See `docs/DATASET.md`.

## License and citation

The code is released under the [MIT License](LICENSE). The DeepHS Fruit data remain subject to the terms of their
original providers. Please cite the article and this repository (`CITATION.cff`).
