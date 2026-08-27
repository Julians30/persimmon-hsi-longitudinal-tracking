# Pre-publication repository audit

Audit date: 2026-08-27

## Status

This repository is intentionally **private and pre-publication**. The scientific analysis corresponding to the manuscript is frozen at commit:

`f97a5536208115e26de9576339d16e72c130d24f`

Subsequent commits may harden repository metadata, citation information, documentation, and automated audit checks, but they must not alter the frozen scientific analysis artifacts listed below unless a new manuscript analysis is explicitly approved and documented.

## Frozen scientific paths

- `notebooks/`
- `data/splits/`
- `results/reference/`
- `tables/reference/`
- `figures/reference/`
- `scripts/download_data.py`
- `scripts/run_notebooks.py`
- `requirements.txt`
- `environment.yml`
- `docs/DATASET.md`
- `docs/REPRODUCIBILITY.md`
- `docs/NOTEBOOK_MAP.md`

GitHub Actions compares these paths against the scientific freeze commit so that metadata-only cleanup cannot silently change manuscript results.

## Completed audit items

- [x] Repository remains private during manuscript preparation.
- [x] Eleven canonical notebooks (`00`–`10`) are tracked under `notebooks/`.
- [x] Canonical notebooks are output-free and have cleared execution counts.
- [x] Notebook code cells pass static Python syntax checks.
- [x] Repository utility scripts are present and compile.
- [x] Public-data downloader verifies the manuscript SHA-256 checksums.
- [x] Frozen outer and inner fruit-disjoint split files are committed.
- [x] Outer split: 5 folds × 8 held-out physical fruits.
- [x] Inner split: 4 folds × 8 development fruits within each outer training set.
- [x] No outer-test fruit occurs in its corresponding inner cross-validation set.
- [x] Final reference JSON outputs are committed.
- [x] Selected manuscript tables are committed.
- [x] Selected manuscript figures are committed.
- [x] `requirements.txt` and `environment.yml` document the computational environment.
- [x] `docs/DATASET.md`, `docs/REPRODUCIBILITY.md`, and `docs/NOTEBOOK_MAP.md` document provenance and execution.
- [x] Hard-coded Google Drive / Colab / chat-specific notebook code is excluded.
- [x] Raw HSI archives, checkpoints, secret files, and common credential patterns are excluded from tracking.
- [x] `CITATION.cff` contains the current six-author manuscript author list.
- [x] Obsolete `CITATION.cff.template` placeholder file was removed.
- [x] GitHub Actions performs the automated repository audit on pushes and pull requests to `main`.

## Intentionally pending before public release / journal submission

- [ ] Perform one clean end-to-end reproduction from a fresh environment: clone → install → download public data → execute notebooks `00`–`10` → compare final outputs with `results/reference/`.
- [ ] Confirm the software license with all co-authors and the relevant institution; do not activate a license before that decision.
- [ ] Add the final software version and release date to `CITATION.cff` when the manuscript release is created.
- [ ] Create the manuscript repository release (recommended tag: `v1.0.0`).
- [ ] Archive the release in Zenodo or another suitable archival repository and record the DOI, if used by the target journal.
- [ ] Make the GitHub repository public at submission when compatible with the target journal's peer-review policy, or provide an anonymized/private reviewer route if required.
- [ ] Replace any manuscript wording that calls the repository "public" until the repository is actually public.
- [ ] Update the manuscript Code/Data Availability statement to cite the final release/DOI rather than only a moving branch.

## Manuscript traceability

The benchmark manifest records the final classical-model run, random seed `20260818`, 5,000 fruit-level bootstrap repetitions, the exact outer/inner split SHA-256 fingerprints, and the captured Python/NumPy/pandas versions. The repository audit is static; full computational reproduction still requires downloading the public DeepHS Fruit HSI archives and running the complete workflow.
