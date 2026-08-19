# Reproducibility protocol

## 1. Environment

Recommended Python: **3.11**.

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

Start Jupyter from the repository root:

```bash
jupyter lab
```

Run `notebooks/00_data_audit.ipynb` through `notebooks/10_final_ml_benchmark.ipynb` in numerical order.

If Jupyter is started from another directory, set:

```bash
PERSIMMON_HSI_ROOT=/absolute/path/to/persimmon-hsi-longitudinal-tracking
```

## 4. Frozen biological partitions

Do not regenerate the manuscript splits. The exact outer and inner fruit-disjoint assignments are in `data/splits/`.

## 5. Randomness and resampling

The analysis uses the fixed seed `20260818`. Bootstrap comparisons are performed at the physical-fruit level. The number of bootstrap repetitions is defined inside each analysis notebook and is preserved from the manuscript workflow.

## 6. Main reproducibility guardrails

- Physical fruit is the biological grouping unit.
- No camera, side, or day from the same fruit may cross an outer train/test boundary.
- Official DeepHS record-level train/validation/test partitions are **not** used for temporal model evaluation because fruit IDs overlap across those partitions.
- `train_only_labeled_v2` is excluded as a duplicate logical subset.
- `storage_days_model` follows the verified day-code mapping in `docs/DATASET.md`.
- Firmness and ripeness labels are terminal destructive endpoints and are not propagated backward.
- Session-excluded tests use a null model subjected to the same target-day exclusion.

## 7. Scope of inference

All predictive performance is internal to the same acquisition campaign. Fruit-disjoint validation estimates generalization to unseen fruits within that campaign. It does not constitute independent harvest/batch/campaign validation.
