# Notebook cleanup and repository audit

The repository package contains **11** cleaned canonical notebooks.

## Changes applied

- Removed Google Colab Drive mounting cells.
- Removed chat-specific review ZIP downloads and instructions.
- Replaced the historical hard-coded `/content/drive/MyDrive/AgroAI/...` root with repository-relative path resolution.
- Standardized top-level generated paths to:
  - `data/`
  - `results/`
  - `figures/`
  - `tables/`
  - `exports/`
- Stripped notebook execution outputs and reset execution counts so the repository does not expose stale outputs as if they were freshly reproduced.
- Preserved the manuscript random seed, frozen fruit-disjoint splits, model grids, nested CV logic, session-excluded logic, negative controls, bootstrap procedures, and reported metrics.
- Added data provenance and reproducibility documentation.
- Added a static repository verifier and official-data downloader.
- Included the exact frozen split CSV files used by the manuscript.
- Updated the sequential notebook runner so canonical notebooks are never overwritten; executed copies are written to `exports/executed_notebooks/`.
- Added a GitHub Actions workflow that runs the static repository verifier automatically on pushes and pull requests to `main`.
- Aligned the documented Python environment with the final benchmark manifest (Python 3.12.13; NumPy 2.0.2; pandas 2.2.3). Exact versions not preserved in the historical manifest remain constrained to compatible ranges rather than being invented.

## Critical correction retained in Notebook 00

The repository `00_data_audit.ipynb` is aligned with the **approved corrected audit**, not the earlier exploratory parser. It reads only:

- `train_all_v2.json`
- `val_v2.json`
- `test_v2.json`

and explicitly excludes `train_only_labeled_v2.json`, which is a labeled subset of `train_all_v2.json`.

The notebook also reconstructs and verifies the temporal target for all 793 Kaki cubes using the approved day-code mapping before writing `data/interim/kaki_master_index_v2.csv`.

## Frozen split hashes

- Outer 5-fold split: `56013aaf85c546c8ac2df1d7db0552918a8687a5e510e42c73e099eb5fef8973`
- Inner 4-fold split: `785adc00e1a2f8a2fc6800a921390a0eaaf87b2cfc82cb04d892ab1ca3814e0b`

The verifier now recomputes both hashes and checks the biological nesting explicitly:

- 40 unique physical fruits total;
- 5 outer folds with 8 held-out fruits each;
- 4 inner folds with 8 development fruits each within every outer training set;
- no outer-test fruit occurs in its corresponding inner CV.

## Static validation

The automated audit checks that:

- all 11 canonical notebooks are present and valid JSON;
- notebook outputs are stripped and execution counts are null;
- all notebook code cells and repository utility scripts compile;
- no active notebook contains hard-coded Google Drive paths, `google.colab` imports, or chat-specific instructions;
- required frozen result JSON, reference tables, and PNG figures are present and structurally valid;
- no raw HSI archives, model checkpoints, secret files, private keys, or common credential patterns are tracked.

Detailed historical notebook-cleaning status is in `docs/notebook_cleanup_audit.csv`.

This audit is static; a full from-raw execution remains the final end-to-end reproducibility test because the raw HSI archive is intentionally not bundled in GitHub.
