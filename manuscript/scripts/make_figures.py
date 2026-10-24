#!/usr/bin/env python3
"""Figures 2–9 of the manuscript in one journal style.

Times-metric serif type (Liberation Serif), true print size (16 cm full width), 600 dpi PNG plus vector PDF,
black and grey only. Every value is recomputed from the out-of-fold predictions; Figures 3 and 7 also need the
fruit-day spectra written by notebook 01 to data/interim/ (they are skipped with a message if absent, because
the raw DeepHS data are not redistributed). Figure 6 uses the cross-sensor summary values of notebook 07.
Output: manuscript/figures/Figure_<n>.png and .pdf
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import NB08, NB09, NB10, OUT_FIGURES, fb_mae, parser, read

args = parser(__doc__.splitlines()[0]).parse_args()
OUT = OUT_FIGURES
OUT.mkdir(parents=True, exist_ok=True)
RES = args.results_root

plt.rcParams.update({
    "font.family": "Liberation Serif", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5, "legend.fontsize": 7, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 3, "ytick.major.size": 3, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "lines.linewidth": 1.0, "savefig.dpi": 600,
    "axes.unicode_minus": True,
})
FULL, HALF = 6.30, 3.50          # inches: full text width (16 cm), single column (~9 cm)
PH = 2.45                         # panel height
BAR = dict(color="0.80", edgecolor="black", linewidth=0.6, width=0.62)
REF = dict(color="black", ls=(0, (4, 2)), lw=0.8)
DAYS = [0, 1, 2, 3, 4, 6, 7, 8]
pfm = fb_mae


def label(ax, s):
    ax.text(-0.13, 1.04, s, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="left")


def bars(ax, names, vals, ref=None, ref_label=None, ylabel="Fruit-balanced MAE (days)", rot=0):
    x = np.arange(len(vals))
    ax.bar(x, vals, **BAR)
    for xi, v in zip(x, vals):
        if ref is not None and abs(v - ref) < 0.2:   # avoid collision with the reference line
            ax.text(xi, v - 0.04, f"{v:.3f}", ha="center", va="top", fontsize=6.8)
        else:
            ax.text(xi, v + 0.03, f"{v:.3f}", ha="center", va="bottom", fontsize=6.8)
    if ref is not None:
        ax.axhline(ref, **REF, label=f"{ref_label} ({ref:.3f})")
        ax.legend(loc="upper left", handlelength=2.2)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=rot, ha="right" if rot else "center")
    ax.set_ylabel(ylabel)
    top = max(list(vals) + ([ref] if ref else [])) * 1.22
    ax.set_ylim(0, top)


def save(fig, n):
    fig.savefig(OUT / f"Figure_{n}.png", dpi=600, facecolor="white")
    fig.savefig(OUT / f"Figure_{n}.pdf", facecolor="white")
    plt.close(fig)
    print(f"Figure {n} written")


def grey_days(days):
    """Sequential grey scale: earliest day light grey, latest day black."""
    return {d: str(round(0.72 * (1 - i / (len(days) - 1)), 2)) for i, d in enumerate(days)}


# ------------------------------------------------------------- data
spec_path = args.interim_dir / "kaki_fruit_day_spectra_VIS_COR.csv"
HAVE_SPECTRA = spec_path.exists()
if HAVE_SPECTRA:
    spec = pd.read_csv(spec_path)
    wl_cols = [c for c in spec.columns if c.startswith("wl_")]
    wl = np.array([float(c[3:]) for c in wl_cols])
    X = spec[wl_cols].to_numpy(float)
    day = spec.storage_days_model.to_numpy()
    fid = spec.fruit_id.to_numpy()
    Xs = (X - X.mean(1, keepdims=True)) / X.std(1, keepdims=True)
    base_raw = {f: X[i] for i, f in enumerate(fid) if day[i] == 0}
    base_snv = {f: Xs[i] for i, f in enumerate(fid) if day[i] == 0}
else:
    print(f"{spec_path} not found: Figures 3 and 7 skipped (run notebooks 00-01 after downloading the data)")

std = read(RES, NB10, "kaki_final_benchmark_standard_oof.csv")
ses = read(RES, NB10, "kaki_final_benchmark_session_excluded_oof.csv")
nul = read(RES, NB10, "kaki_final_benchmark_standard_null_oof.csv")

# ------------------------------------------------------------- Figure 2 (single column)
r2 = std[(std.task == "absolute") & (std.algorithm == "Ridge")]
counts = r2.groupby("storage_days").fruit_id.nunique().reindex(DAYS)
fig, ax = plt.subplots(figsize=(HALF, 2.3))
ax.bar(range(len(DAYS)), counts.values, **BAR)
for i, v in enumerate(counts.values):
    ax.text(i, v + 0.6, str(v), ha="center", va="bottom", fontsize=7)
ax.set_xticks(range(len(DAYS))); ax.set_xticklabels(DAYS)
ax.set_xlabel("Storage day"); ax.set_ylabel("Fruits observed"); ax.set_ylim(0, 46)
fig.tight_layout(pad=0.3); save(fig, 2)
print("Fig2 counts", counts.to_dict())

# ------------------------------------------------------------- Figure 3
if HAVE_SPECTRA:
    fig, ax = plt.subplots(1, 2, figsize=(FULL, PH))
    g = grey_days(DAYS)
    for d in DAYS:
        ax[0].plot(wl, X[day == d].mean(0), color=g[d], lw=0.9, label=f"Day {d}")
    ax[0].set_xlabel("Wavelength (nm)"); ax[0].set_ylabel("Mean reflectance")
    ax[0].legend(ncol=2, loc="upper left", handlelength=1.6, columnspacing=1.0)
    ax[0].set_xlim(wl.min(), wl.max())
    rms = pd.DataFrame({"day": day, "d": [np.sqrt(np.mean((X[i] - base_raw[f]) ** 2)) if f in base_raw else np.nan
                                          for i, f in enumerate(fid)]}).dropna()
    med, mean = rms.groupby("day").d.median().reindex(DAYS), rms.groupby("day").d.mean().reindex(DAYS)
    ax[1].plot(DAYS, med.values, color="black", marker="o", ms=3.5, label="Median")
    ax[1].plot(DAYS, mean.values, color="0.45", ls=(0, (4, 2)), marker="s", ms=3.5, mfc="white", label="Mean")
    ax[1].set_xticks(DAYS); ax[1].set_xlabel("Storage day"); ax[1].set_ylabel("RMS distance from day 0")
    ax[1].legend(loc="upper left")
    label(ax[0], "(a)"); label(ax[1], "(b)")
    fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 3)
    print("Fig3 median RMS", med.round(4).to_dict())

# ------------------------------------------------------------- Figure 4
s = std[(std.task == "absolute") & (std.algorithm == "Ridge")].copy()
s["ae"] = (s.y_true - s.y_pred).abs(); s["bias"] = s.y_pred - s.y_true
e = ses[(ses.task == "absolute") & (ses.algorithm == "Ridge")].copy()
e["ae"] = (e.y_true - e.y_pred).abs(); e["bias"] = e.y_pred - e.y_true
fig, ax = plt.subplots(1, 2, figsize=(FULL, PH))
rng = np.random.default_rng(0)
jit = rng.uniform(-0.12, 0.12, len(s))
ax[0].scatter(s.y_true + jit, s.y_pred, s=9, facecolors="none", edgecolors="black", linewidths=0.5)
ax[0].plot([-1, 9.5], [-1, 9.5], color="0.45", ls=(0, (4, 2)), lw=0.8, label="1:1 line")
ax[0].set_xlim(-0.6, 8.6); ax[0].set_ylim(-1.2, 9.2); ax[0].set_xticks(DAYS)
ax[0].set_xlabel("Observed storage day"); ax[0].set_ylabel("Predicted storage day"); ax[0].legend(loc="upper left")
by = s.groupby("storage_days").ae
ax[1].plot(by.mean().index, by.mean().values, color="black", marker="o", ms=3.5, label="Mean absolute error")
ax[1].plot(by.median().index, by.median().values, color="0.45", ls=(0, (4, 2)), marker="s", ms=3.5, mfc="white",
           label="Median absolute error")
ax[1].set_xticks(DAYS); ax[1].set_xlabel("Storage day"); ax[1].set_ylabel("Absolute error (days)")
ax[1].legend(loc="upper left")
label(ax[0], "(a)"); label(ax[1], "(b)")
fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 4)

# ------------------------------------------------------------- Figure 5
fig, ax = plt.subplots(1, 2, figsize=(FULL, PH))
for gdf, lab, kw in [(s, "Standard", dict(color="black", marker="o")),
                     (e, "Session-excluded", dict(color="0.45", ls=(0, (4, 2)), marker="s", mfc="white"))]:
    m = gdf.groupby("storage_days").ae.mean(); b = gdf.groupby("storage_days").bias.mean()
    ax[0].plot(m.index, m.values, ms=3.5, label=lab, **kw)
    ax[1].plot(b.index, b.values, ms=3.5, label=lab, **kw)
ax[1].axhline(0, color="black", lw=0.5)
ax[0].set_ylabel("MAE (days)"); ax[1].set_ylabel("Bias, predicted − observed (days)")
for a in ax:
    a.set_xticks(DAYS); a.set_xlabel("Storage day"); a.legend(loc="upper left" if a is ax[0] else "lower left")
label(ax[0], "(a)"); label(ax[1], "(b)")
fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 5)

# ------------------------------------------------------------- Figure 6 (values from the cross-sensor tables)
dummy_abs = pfm(nul[nul.task == "absolute"]) if "task" in nul.columns else None
fig, ax = plt.subplots(1, 2, figsize=(FULL, PH), gridspec_kw={"width_ratios": [4, 2.6]})
bars(ax[0], ["VIS\nwithin", "VIS_COR\nwithin", "VIS→VIS_COR", "VIS_COR→VIS"], [1.062, 0.804, 1.370, 1.349],
     ref=dummy_abs, ref_label="Dummy median")
bars(ax[1], ["VIS→VIS_COR", "VIS_COR→VIS"], [1.701, 1.499], ref=2.224, ref_label="Matched null")
label(ax[0], "(a)"); label(ax[1], "(b)")
fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 6)
print("Fig6 dummy", round(dummy_abs, 3))

# ------------------------------------------------------------- Figure 7
if HAVE_SPECTRA:
    fig, ax = plt.subplots(1, 2, figsize=(FULL, PH), gridspec_kw={"width_ratios": [4, 2.6]})
    dd = [d for d in DAYS if d > 0]
    g7 = grey_days(dd)
    for d in dd:
        m = np.mean([Xs[i] - base_snv[fid[i]] for i in range(len(fid)) if day[i] == d and fid[i] in base_snv], axis=0)
        ax[0].plot(wl, m, color=g7[d], lw=0.9, label=f"Day {d}")
    ax[0].axhline(0, color="black", lw=0.5)
    ax[0].set_xlim(wl.min(), wl.max())
    ax[0].set_xlabel("Wavelength (nm)"); ax[0].set_ylabel("Mean Δ-SNV")
    ax[0].legend(ncol=2, loc="upper left", handlelength=1.6, columnspacing=1.0)
    d8 = read(RES, NB08, "kaki_delta_standard_oof.csv"); d8 = d8[d8.camera_type == "VIS_COR"]
    dm = read(RES, NB08, "kaki_delta_standard_dummy_median_oof.csv")
    if "camera_type" in dm.columns:
        dm = dm[dm.camera_type == "VIS_COR"]
    v7 = [pfm(s[s.storage_days > 0]), pfm(d8[d8.representation == "delta_raw"]), pfm(d8[d8.representation == "delta_snv"])]
    bars(ax[1], ["Absolute", "Δ-raw", "Δ-SNV"], v7, ref=pfm(dm), ref_label="Dummy median")
    label(ax[0], "(a)"); label(ax[1], "(b)")
    fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 7)
    print("Fig7b", [round(v, 3) for v in v7], "dummy", round(pfm(dm), 3))

# ------------------------------------------------------------- Figure 8
cx = read(RES, NB09, "kaki_baseline_complexity_standard_oof.csv")
cx = cx[cx.camera_type == "VIS_COR"]
mm = cx.groupby("model").apply(fb_mae, include_groups=False)
ro = read(RES, NB09, "kaki_random_other_baseline_oof.csv")
ro = ro[ro.camera_type == "VIS_COR"]
ro_mean = ro.groupby("rep").apply(fb_mae, include_groups=False).mean()  # average over the 10 permutations
dm9 = read(RES, NB09, "kaki_standard_dummy_median_days_gt0_oof.csv")
if "camera_type" in dm9.columns:
    dm9 = dm9[dm9.camera_type == "VIS_COR"]
dmy = pfm(dm9)
fig, ax = plt.subplots(1, 2, figsize=(FULL, PH))
bars(ax[0], ["Self", "Training mean", "Random other"],
     [mm["self_multiband_delta_snv"], mm["training_mean_multiband_delta_snv"], ro_mean],
     ref=dmy, ref_label="Dummy median")
ax[0].set_xlabel("Day-0 baseline")
bars(ax[1], ["Multiband\nΔ-SNV", "RMS", "Spectral\nangle", "RMS +\nangle"],
     [mm["self_multiband_delta_snv"], mm["self_scalar_rms"], mm["self_scalar_angle"], mm["self_scalar_rms_angle"]],
     ref=dmy, ref_label="Dummy median")
label(ax[0], "(a)"); label(ax[1], "(b)")
fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 8)
print("Fig8", mm.round(3).to_dict(), "random", round(ro_mean, 3), "dummy", round(dmy, 3))

# ------------------------------------------------------------- Figure 9
t3 = std.groupby(["task", "algorithm"]).apply(fb_mae, include_groups=False).rename("fruit_balanced_mae").reset_index()
names = {"Ridge": "Ridge", "PLSR": "PLSR", "SVR_RBF": "SVR-RBF", "SVR-RBF": "SVR-RBF", "RandomForest": "Random\nForest",
         "ExtraTrees": "Extra\nTrees"}
fig, ax = plt.subplots(1, 2, figsize=(FULL, PH))
for a, task in zip(ax, ["absolute", "delta_snv"]):
    t = t3[t3.task == task].sort_values("fruit_balanced_mae")
    ref = pfm(nul[nul.task == task]) if "task" in nul.columns else None
    bars(a, [names.get(x, x) for x in t.algorithm], t.fruit_balanced_mae.values, ref=ref, ref_label="Dummy median")
    print("Fig9", task, dict(zip(t.algorithm, t.fruit_balanced_mae.round(3))), "dummy", round(ref, 3))
label(ax[0], "(a)"); label(ax[1], "(b)")
fig.tight_layout(pad=0.4, w_pad=2.0); save(fig, 9)
print("done")
