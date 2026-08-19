# Notebook execution map

Run the notebooks in this order for a complete from-raw reproduction:

| Order | Notebook | Main purpose |
|---:|---|---|
| 00 | `00_data_audit.ipynb` | Audit raw archives, annotations, physical HSI records, day mapping, and build the master index |
| 01 | `01_longitudinal_eda.ipynb` | MASK V2 extraction, fruit-day spectra, longitudinal EDA, sensor/side QC |
| 02 | `02_fruit_disjoint_baselines.ipynb` | Freeze fruit-disjoint nested CV and establish Ridge/PLSR/SVR baselines |
| 03 | `03_session_robustness.ipynb` | Session-excluded stress test and matched null |
| 04 | `04_negative_controls.ipynb` | Background/session and baseline-survivorship negative controls |
| 05 | `05_wavelength_selection.ipynb` | Sparse wavelength-selection analysis |
| 06 | `06_virtual_sensor_design.ipynb` | Multivariate virtual filter / sensor simplification |
| 07 | `07_cross_sensor_transfer.ipynb` | VIS ↔ VIS_COR common-grid transfer and calibration |
| 08 | `08_within_fruit_delta.ipynb` | Same-fruit baseline-referenced longitudinal Δ trajectories |
| 09 | `09_baseline_specificity.ipynb` | Self vs mean vs random baseline and scalar-vs-multiband controls |
| 10 | `10_final_ml_benchmark.ipynb` | Final 5-algorithm benchmark with 8 metrics |

## Dependency highlights

- Notebook 01 depends on Notebook 00 outputs.
- Notebook 02 depends on Notebook 01 spectral caches.
- Notebooks 03–07 reuse the frozen splits produced by Notebook 02.
- Notebook 08 reuses outputs from 02 and 03.
- Notebook 09 uses the longitudinal representation established in 08.
- Notebook 10 uses the frozen spectral caches and splits and closes the classical ML benchmark.

The frozen split CSVs are also committed under `data/splits/` so manuscript partitions can be independently inspected.
