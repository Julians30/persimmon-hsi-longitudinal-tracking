#!/usr/bin/env python3
"""Figure 1: analytical workflow, black and white, Times-metric serif (matches manuscript typeface).

Drawn at the final printed width (16 cm text block) so that type sizes are true sizes:
block titles 8 pt bold, content 7 pt.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 6.30, 4.42  # inches
plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 7, "mathtext.fontset": "custom"})
K = "black"
TS, FS = 8.0, 7.0  # title / body pt

fig = plt.figure(figsize=(W, H), dpi=600)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
boxes = []


def box(x, y, w, h, title, lines, num=None, lw=0.6, ts=TS, fs=FS, ls="-", center=True):
    ax.add_patch(Rectangle((x, y), w, h, lw=lw, ec=K, fc="white", ls=ls, joinstyle="miter"))
    head = f"{num}. {title}" if num else title
    tx = x + w / 2 if center else x + 0.06
    ha = "center" if center else "left"
    ax.text(tx, y + h - 0.055, head, ha=ha, va="top", fontsize=ts, fontweight="bold", color=K)
    if lines:
        ax.text(tx, y + h - 0.055 - ts / 72 * 1.40, "\n".join(lines), ha=ha, va="top",
                fontsize=fs, color=K, linespacing=1.28)
    boxes.append((x, y, w, h))


def arrow(x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7,
                                 lw=0.7, color=K, shrinkA=0, shrinkB=0))


M = 0.03
GAP = 0.16
IW = W - 2 * M

# ---- row 1: data → extraction → representations ----
r1h = 0.78
r1y = H - M - r1h
w1 = (IW - 2 * GAP) / 3
x1 = [M + i * (w1 + GAP) for i in range(3)]
box(x1[0], r1y, w1, r1h, "Public dataset", [
    "DeepHS Fruit v2, persimmon subset",
    "40 fruits, 199 fruit-days, 793 cubes",
    "VIS (Specim FX10) and VIS_COR",
    "(Corning microHSI 410)"], num=1)
box(x1[1], r1y, w1, r1h, "Spectral extraction", [
    "Otsu mask on a 550/700/850 nm proxy",
    "Median fruit-pixel spectrum per view",
    "Front/back median: one fruit-day",
    "spectrum per camera"], num=2)
box(x1[2], r1y, w1, r1h, "Representations", [
    "Absolute spectrum (raw or SNV)",
    "Δ-raw and Δ-SNV relative to the",
    "same fruit at day 0",
    "Exploration: mean spectra, PCA"], num=3)
for i in range(2):
    arrow(x1[i] + w1, r1y + r1h / 2, x1[i + 1], r1y + r1h / 2)

# ---- row 2: validation framework (double-weight frame = core of the study) ----
r2h = 0.42
r2y = r1y - 0.22 - r2h
box(M, r2y, IW, r2h, "Frozen fruit-disjoint nested validation (shared by all analyses)", [
    "Outer: 5 folds × 8 test fruits.  Inner: 4 fruit-disjoint folds for preprocessing and hyperparameters.  "
    "Primary metric: FB-MAE"], num=4, lw=1.3, center=True)
for xc in (x1[0] + w1 / 2, x1[1] + w1 / 2, x1[2] + w1 / 2):
    pass
arrow(W / 2, r1y, W / 2, r2y + r2h)

# ---- row 3: two operational use cases ----
r3h = 0.50
r3y = r2y - 0.22 - r3h
w3 = (IW - GAP) / 2
x3 = [M, M + w3 + GAP]
box(x3[0], r3y, w3, r3h, "Use case A: single-scan screening", [
    "Absolute spectrum of an unseen fruit; no individual baseline",
    "199 fruit-days, 40 fruits"], lw=1.3, center=True)
box(x3[1], r3y, w3, r3h, "Use case B: longitudinal tracking", [
    "Δ-SNV relative to the same fruit at day 0",
    "159 fruit-days, 38 fruits"], lw=1.3, center=True)
for xc in (x3[0] + w3 / 2, x3[1] + w3 / 2):
    arrow(xc, r2y, xc, r3y + r3h)

# ---- row 4: robustness and control analyses (dashed group frame) ----
fh = 1.12
fy = r3y - 0.22 - fh
ax.add_patch(Rectangle((M, fy), IW, fh, lw=0.6, ec=K, fc="white", ls=(0, (4, 2))))
ax.text(W / 2, fy + fh - 0.055, "5. Robustness and control analyses (applied to use cases A and B)",
        ha="center", va="top", fontsize=TS, fontweight="bold", color=K)
g4 = 0.07
pad = 0.07
w4 = (IW - 2 * pad - 5 * g4) / 6
r4h = 0.70
r4y = fy + 0.08
items = [
    ("Session exclusion", ["Target day removed", "from development;", "matched null model"]),
    ("Negative controls", ["Background pixels;", "day-0 spectrum to", "predict terminal day"]),
    ("Baseline controls", ["Mean and mismatched", "day-0 baselines;", "scalar RMS, L2, angle"]),
    ("Simplification", ["Native bands, k ≤ 20;", "Gaussian virtual", "filters, k ≤ 10"]),
    ("Sensor transfer", ["Common 410–900 nm", "grid; development-", "only affine mapping"]),
    ("Model benchmark", ["Ridge, PLSR,", "SVR-RBF, Random", "Forest, Extra Trees"]),
]
for i, (t, ls) in enumerate(items):
    box(M + pad + i * (w4 + g4), r4y, w4, r4h, t, ls, ts=7.2, fs=6.8, center=True)
for xc in (x3[0] + w3 / 2, x3[1] + w3 / 2):
    arrow(xc, r3y, xc, fy + fh)

# ---- row 5: inference and reproducibility ----
r5h = 0.66
r5y = M
w5a = 3.95
box(M, r5y, w5a, r5h, "Statistical inference", [
    "Paired fruit-level bootstrap of per-fruit errors (5000 resamples)",
    "Primary contrasts C1–C4: Holm-adjusted p, Bonferroni 98.75% CI",
    "Remaining contrasts reported as exploratory"], num=6)
box(M + w5a + GAP, r5y, IW - w5a - GAP, r5h, "Reproducibility", [
    "Frozen split files with SHA-256 checks",
    "Notebooks 00–10 at a fixed commit",
    "Raw HSI from the official source"], num=7)
arrow(M + w5a / 2, fy, M + w5a / 2, r5y + r5h)
arrow(M + w5a, r5y + r5h / 2, M + w5a + GAP, r5y + r5h / 2)
assert r5y + r5h <= fy - 0.2, (r5y + r5h, fy)

fig.savefig(OUT / "Figure_1.png", dpi=600, facecolor="white")
fig.savefig(OUT / "Figure_1.pdf", facecolor="white")

# overflow check: every text inside its box and canvas
fig.canvas.draw()
r = fig.canvas.get_renderer()
inv = ax.transData.inverted()
bad = 0
for t in ax.texts:
    (tx0, ty0), (tx1, ty1) = inv.transform(t.get_window_extent(r))
    if tx1 > W - 0.01 or tx0 < 0.01:
        bad += 1; print("outside canvas:", t.get_text()[:40])
    for (x, y, w, h) in boxes:
        cx, cy = (tx0 + tx1) / 2, ty1
        if x <= cx <= x + w and y <= cy <= y + h + 0.01:
            if tx0 < x + 0.02 or tx1 > x + w - 0.02 or ty0 < y + 0.02:
                bad += 1; print("overflows box:", t.get_text()[:50])
print("overflow problems:", bad)
