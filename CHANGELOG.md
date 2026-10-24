# Changelog

## v1.1.0 (2026-10-24)

- `notebooks/01_longitudinal_eda.ipynb`: the Kaki ENVI headers do not carry a wavelength vector, and the
  cleaned v1.0 reader stopped with an error in that case. The reader now uses the official DeepHS camera
  wavelength arrays (224 VIS and 249 VIS_COR bands, `core/spectral_io.py` of the DeepHS code base, commit
  5f47812), as described in Section 2.2 of the article, and checks agreement whenever a header does supply
  wavelengths. These arrays reproduce exactly the wavelength columns of the archived fruit-day spectra.
  No other notebook, split, or reference output changed.
- CI freeze check updated accordingly (notebook 01 excluded; all other frozen paths still compared with the
  benchmark commit).

## v1.0.0 (2026-10-24)

Release accompanying the article submitted to *Chemometrics and Intelligent Laboratory Systems*.

- Eleven analysis notebooks (00–10), frozen fruit-disjoint splits and reference benchmark outputs, unchanged
  since the benchmark run.
- Added `results/manuscript_oof/`: frozen out-of-fold predictions of notebooks 05, 06 and 08–10.
- Added `manuscript/`: scripts for the multiplicity-adjusted primary contrasts (C1–C4, Holm and Bonferroni),
  the spectral-simplification comparison against the final full-spectrum model, an independent re-fit check of
  the notebook 10 Ridge model, and Figures 1–9 of the article (PNG 600 dpi and PDF).
- Added the MIT License and updated `CITATION.cff` to the final author list.
- GitHub Actions now also recomputes the primary contrasts from the frozen predictions on every push.
