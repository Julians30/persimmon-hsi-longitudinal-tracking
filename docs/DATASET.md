# Dataset provenance

## Source

This study reanalyzes the **DeepHS Fruit v2** public hyperspectral dataset, using the Kaki/Persimmon subset.

Official project repository:
- https://github.com/cogsys-tuebingen/deephs_fruit

Official dataset directory:
- https://cogsys.cs.uni-tuebingen.de/webprojects/DeepHS-Fruit-2023-Datasets/

Required files:
- `Kaki.zip`
- `annotations-upd-2024-01-09.zip`

## File integrity used in the manuscript analysis

- `Kaki.zip`
  - SHA-256: `c388a528391e975c815f79859ef98f8966ecc06ec2426ec2d5bc6880efb717f6`
  - Approximate size: 2.2 GB
- `annotations-upd-2024-01-09.zip`
  - SHA-256: `14275450e362684bc379a5aaf6c845cf82b0f9d5912036b9401d59a4b964a3f3`

Notebook 00 recomputes and checks these hashes.

## Experimental unit reconstructed for this study

The public annotations were audited and reconstructed as a longitudinal panel:

- 40 physical persimmon fruits
- 199 unique fruit × day observations
- 793 physical HSI cubes
- VIS: 395 cubes
- VIS_COR: 398 cubes

Only the v2 physical records from `train_all_v2.json`, `val_v2.json`, and `test_v2.json` are used. `train_only_labeled_v2.json` is a labeled subset of `train_all_v2.json` and must not be appended as an independent set.

## Storage-day mapping

The verified experimental mapping used as the temporal target is:

| Day code | storage_days_model |
|---|---:|
| day_1_m3 | 0 |
| day_2_m3 | 1 |
| day_3_m3 | 2 |
| day_4_m3 | 3 |
| day_5_m3 | 4 |
| day_7_m3 | 6 |
| day_8_m3 | 7 |
| day_9_m3 | 8 |

There is no target day 5. The verified experimental index is used rather than recomputing elapsed calendar days.

## Original publication

Varga, L. A.; Makowski, J.; Zell, A. *Measuring the Ripeness of Fruit with Hyperspectral Imaging and Deep Learning*. IJCNN 2021. DOI: 10.1109/IJCNN52387.2021.9533728.

The current study addresses a different question: continuous postharvest storage-time tracking with fruit-disjoint longitudinal validation, session stress tests, baseline-referenced trajectories, spectral simplification, and cross-sensor transfer.
