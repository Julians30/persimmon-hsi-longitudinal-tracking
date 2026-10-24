# Changelog

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
