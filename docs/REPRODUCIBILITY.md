# Reproducibility protocol

## 1. Environment

Recommended Python for reproducing the final benchmark: **3.12**.

The frozen final benchmark manifest records:

- Python **3.12.13**
- NumPy **2.0.2**
- pandas **2.2.3**

Exact historical versions of SciPy, scikit-learn, matplotlib, tqdm, JupyterLab, nbconvert, and ipykernel were not preserved in the final run manifest. They are therefore constrained to compatible ranges in `requirements.txt` / `environment.yml` rather than assigned invented exact versions.

Create an environment with either:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

or:

```bash
conda env create -f environment.yml
conda activate persimmon-hsi
```

## 2. Obtain the raw data

```bash
python scripts/download_data.py
```

The downloader retrieves only the public Kaki archive and updated annotations and verifies the SHA-256 values used in the analysis.

## 3. Run notebooks

For interactive reproduction, start Jupyter from the repository root:

```bash
jupyter lab
```

Run `notebooks/00_data_audit.ipynb` through `notebooks/10_final_ml_benchmark.ipynb` in numerical order.

For sequential automated execution, use:

```bash
python scripts/run_notebooks.py
```

The runner deliberately **does not overwrite the canonical cleaned notebooks**. Executed copies are written to `exports/executed_notebooks/` by default. A custom destination can be supplied with `--output-dir`.

If Jupyter is started from another directory, set:

```bash
PERSIMMON_HSI_ROOT=/absolute/path/to/persimmon-hsi-longitudinal-tracking
```

## 4. Frozen biological partitions

Do not regenerate the manuscript splits. The exact outer and inner fruit-disjoint assignments are in `data/splits/`.

The repository verifier checks both split files against the manuscript SHA-256 fingerprints and validates the nested structure:

- outer CV: 5 folds × 8 held-out physical fruits;
- inner CV: 4 folds × 8 development fruits within each outer training set;
- no outer-test fruit may occur in the corresponding inner CV.

## 5. Randomness and resampling

The analysis uses the fixed seed `20260818`. Bootstrap comparisons are performed at the physical-fruit level. The final classical benchmark manifest records 5,000 bootstrap repetitions.

## 6. Main reproducibility guardrails

- Physical fruit is the biological grouping unit.
- No camera, side, or day from the same fruit may cross an outer train/test boundary.
- Official DeepHS record-level train/validation/test partitions are **not** used for temporal model evaluation because fruit IDs overlap across those partitions.
- `train_only_labeled_v2` is excluded as a duplicate logical subset.
- `storage_days_model` follows the verified day-code mapping in `docs/DATASET.md`.
- Firmness and ripeness labels are terminal destructive endpoints and are not propagated backward.
- Session-excluded tests use a null model subjected to the same target-day exclusion.
- Canonical notebooks are kept output-free; executed copies are stored outside `notebooks/`.

## 7. Automated repository audit

`python scripts/verify_repository.py` performs static pre-publication checks for:

- the exact 11-notebook inventory and notebook JSON validity;
- stripped outputs and cleared execution counts;
- Python syntax of notebook code cells and repository utility scripts;
- absence of hard-coded Google Drive / Colab / chat-specific notebook code;
- exact SHA-256 hashes and biological integrity of the frozen outer/inner splits;
- required frozen reference JSON outputs, CSV tables, and PNG figures;
- absence of tracked raw HSI archives, model checkpoints, secrets, and common credential patterns.

The same verifier is executed automatically on pushes and pull requests through GitHub Actions (`.github/workflows/repository-audit.yml`).

## 8. Scope of inference

All predictive performance is internal to the same acquisition campaign. Fruit-disjoint validation estimates generalization to unseen fruits within that campaign. It does not constitute independent harvest/batch/campaign validation.

This repository audit is static. Full end-to-end reproduction still requires downloading the approximately 2.2 GB public HSI archive and executing the workflow from raw data.
