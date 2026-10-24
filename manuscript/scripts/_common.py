#!/usr/bin/env python3
"""Shared paths and helpers for the manuscript post-processing scripts.

By default every script reads the frozen out-of-fold (OOF) predictions committed under
``results/manuscript_oof/``. After re-running notebooks 05–10 from the raw data, pass
``--results-root results`` to use the regenerated outputs instead (same sub-folder names).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "results" / "manuscript_oof"
DEFAULT_INTERIM = ROOT / "data" / "interim"
OUT_TABLES = ROOT / "manuscript" / "tables"
OUT_FIGURES = ROOT / "manuscript" / "figures"

NB05 = "05_kaki_wavelength_selection_sensor_simplification"
NB06 = "06_kaki_multivariate_virtual_sensor_design"
NB08 = "08_kaki_within_fruit_delta_trajectory"
NB09 = "09_kaki_baseline_specificity_trajectory_complexity"
NB10 = "10_kaki_final_classical_ml_benchmark"

N_BOOT = 5000
SEED = 20260818  # same seed as the analysis notebooks


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS,
                   help="folder containing the notebook result sub-folders (default: frozen OOF files)")
    p.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM,
                   help="folder with kaki_fruit_day_spectra_<camera>.csv written by notebook 01")
    return p


def read(results_root: Path, notebook_dir: str, name: str) -> pd.DataFrame:
    path = results_root / notebook_dir / name
    if not path.exists():
        raise FileNotFoundError(f"missing input {path}; run the corresponding notebook or use the frozen files")
    return pd.read_csv(path)


def per_fruit_mae(df: pd.DataFrame) -> pd.Series:
    """Mean absolute error of each physical fruit (the unit of the fruit-balanced MAE)."""
    return (df["y_true"] - df["y_pred"]).abs().groupby(df["fruit_id"]).mean()


def fb_mae(df: pd.DataFrame) -> float:
    """Fruit-balanced MAE: average over fruits of the within-fruit MAE (Equation 2)."""
    return float(per_fruit_mae(df).mean())


def paired_bootstrap(a: pd.Series, b: pd.Series, seed: int, n_boot: int = N_BOOT) -> tuple[np.ndarray, np.ndarray]:
    """Resample fruits with replacement; return per-fruit differences a-b and bootstrap means."""
    ids = sorted(set(a.index) & set(b.index))
    diff = a.loc[ids].to_numpy(float) - b.loc[ids].to_numpy(float)
    rng = np.random.default_rng(seed)
    boots = np.array([diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(n_boot)])
    return diff, boots
