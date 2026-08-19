# Notebook cleanup audit

The repository package contains **11** cleaned notebooks.

## Changes applied

- Removed Google Colab Drive mounting cells.
- Removed chat-specific review ZIP downloads and instructions.
- Replaced the hard-coded `/content/drive/MyDrive/AgroAI/...` root with repository-relative path resolution.
- Standardized top-level generated paths to `data/`, `results/`, `figures/`, `tables/`, and `exports/`.
- Stripped notebook execution outputs and reset execution counts so the public repository does not expose stale outputs as if they were freshly reproduced.
- Preserved the manuscript random seed, frozen fruit-disjoint splits, model grids, nested CV logic, session-excluded logic, negative controls, bootstrap procedures, and reported metrics.
- Added data provenance and reproducibility documentation.
- Added a static repository verifier and official-data downloader.
- Included the exact frozen split CSV files used by the manuscript.

## Critical correction retained in Notebook 00

The public `00_data_audit.ipynb` is aligned with the **approved corrected audit**, not the earlier exploratory parser. It reads only `train_all_v2.json`, `val_v2.json`, and `test_v2.json`, and explicitly excludes `train_only_labeled_v2.json`, which is a labeled subset of `train_all_v2.json`.

The notebook also reconstructs and verifies the temporal target for all 793 Kaki cubes using the approved day-code mapping before writing `data/interim/kaki_master_index_v2.csv`.

## Frozen split hashes

- Outer 5-fold split: `56013aaf85c546c8ac2df1d7db0552918a8687a5e510e42c73e099eb5fef8973`
- Inner 4-fold split: `785adc00e1a2f8a2fc6800a921390a0eaaf87b2cfc82cb04d892ab1ca3814e0b`

## Static validation

All code cells compile successfully under Python syntax checking. No public notebook contains hard-coded Google Drive paths, `google.colab` imports, chat-specific upload/download instructions, or stored execution outputs.

Detailed status is in `docs/notebook_cleanup_audit.csv`.

This audit is static; a full from-raw execution remains the final end-to-end reproducibility test because the raw HSI archive is intentionally not bundled in GitHub.
