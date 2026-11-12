#!/usr/bin/env python3
"""Supplementary Tables S1-S8 and Figure S1 of the Foods version.

Every value is a summary of outputs that already exist: the frozen out-of-fold predictions in
results/manuscript_oof/, the reference tables in tables/reference/, and the tables written by
simplification_vs_final.py and colour_index_baseline.py. No model is refitted here.
Output: manuscript/tables/supplement/Table_S<n>.csv (S1 configurations, S2-S3 day-level MAE/bias, S4 algorithm
contrasts, S5 spectral panels, S6 colour indices, S7 cross-sensor delta transfer, S8 longitudinal controls, both cameras) and manuscript/figures/Figure_S1.png/.pdf
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import NB05, NB06, NB08, NB09, NB10, OUT_FIGURES, OUT_TABLES, ROOT, fb_mae, parser, read

args = parser(__doc__.splitlines()[0]).parse_args()
R = args.results_root
OUT = OUT_TABLES / "supplement"
OUT.mkdir(parents=True, exist_ok=True)
DAYS = [0, 1, 2, 3, 4, 6, 7, 8]
ALG = ["Ridge", "PLSR", "SVR_RBF", "RandomForest", "ExtraTrees"]
ALGN = {"Ridge": "Ridge", "PLSR": "PLSR", "SVR_RBF": "SVR-RBF", "RandomForest": "Random Forest", "ExtraTrees": "Extra Trees"}
TASKN = {"absolute": "Single-scan", "delta_snv": "Δ-SNV"}
std = read(R, NB10, "kaki_final_benchmark_standard_oof.csv")
ses = read(R, NB10, "kaki_final_benchmark_session_excluded_oof.csv")


def short(cfg: str) -> str:
    c = json.loads(cfg)
    p = c.get("preprocessing", "")
    p = "" if p == "as_is" else p.upper() + ", "
    if "alpha" in c and "C" not in c:
        return f"{p}α = {c['alpha']:g}"
    if "n_components" in c:
        return f"{p}{c['n_components']} LV"
    if "C" in c:
        return f"{p}C = {c['C']:g}, γ = {c['gamma']}, ε = {c['epsilon']:g}"
    d = "none" if c["max_depth"] is None else int(c["max_depth"])
    return f"{p}depth {d}, leaf {c['min_samples_leaf']}, feat. {c['max_features']:g}"


rows = []
for prot, df in (("Standard", std), ("Session-excluded", ses)):
    for task in ("absolute", "delta_snv"):
        for a in ALG:
            g = df[(df.task == task) & (df.algorithm == a)].groupby("outer_fold").config_json.first()
            rows.append({"Protocol": prot, "Task": TASKN[task], "Algorithm": ALGN[a],
                         **{f"Fold {k + 1}": short(g[k]) for k in range(5)}})
S1 = pd.DataFrame(rows)


def by_day(df, stat):
    e = df.y_pred - df.y_true
    v = (e.abs() if stat == "mae" else e).groupby(df.storage_days).mean()
    return [f"{v[d]:.2f}" if d in v.index else "NA" for d in DAYS]


S2, S3 = [], []
for prot, df in (("Standard", std), ("Session-excluded", ses)):
    for task in ("absolute", "delta_snv"):
        for a in ALG:
            g = df[(df.task == task) & (df.algorithm == a)]
            base = {"Protocol": prot, "Task": TASKN[task], "Algorithm": ALGN[a]}
            S2.append({**base, **dict(zip([f"Day {d}" for d in DAYS], by_day(g, "mae")))})
            S3.append({**base, **dict(zip([f"Day {d}" for d in DAYS], by_day(g, "bias")))})
S2, S3 = pd.DataFrame(S2), pd.DataFrame(S3)
n_fr = std[(std.task == "absolute") & (std.algorithm == "Ridge")].groupby("storage_days").fruit_id.nunique()

S4 = pd.read_csv(ROOT / "tables" / "reference" / "10_paired_fruit_bootstrap_algorithms.csv")
parts = S4.comparison.str.split(" ", n=2, expand=True)
nm = lambda x: (x.replace("SVR_RBF", "SVR-RBF").replace("RandomForest", "Random Forest").replace("ExtraTrees", "Extra Trees")
                 .replace(" minus null", " − null model").replace(" minus ", " − ").replace("best(", "").replace(")", ""))
S4 = pd.DataFrame({
    "Protocol": parts[0].map({"standard": "Standard", "session_excluded": "Session-excluded"}),
    "Task": parts[1].map(TASKN), "Comparison": parts[2].map(nm),
    "Fruits": S4.n_fruits, "Mean difference (days)": S4.mean_delta_mae_days.map(lambda v: f"{v:+.3f}".replace("-", "−")),
    "95% CI": [f"{a:+.3f} to {b:+.3f}".replace("-", "−") for a, b in zip(S4.ci95_low, S4.ci95_high)],
    "First model better (% fruits)": (100 * S4.fraction_first_better).round(1)})

d_std = read(R, NB08, "kaki_delta_standard_oof.csv")
d_ses = read(R, NB08, "kaki_delta_session_excluded_oof.csv")
c_std = read(R, NB09, "kaki_baseline_complexity_standard_oof.csv")
c_ses = read(R, NB09, "kaki_baseline_complexity_session_excluded_oof.csv")
rnd = read(R, NB09, "kaki_random_other_baseline_oof.csv")
xs = read(R, NB08, "kaki_cross_sensor_delta_oof.csv")
lab = [("Δ-raw, same-fruit day 0", "delta", "delta_raw"), ("Δ-SNV, same-fruit day 0", "delta", "delta_snv"),
       ("Δ-SNV, development-mean day 0", "cx", "training_mean_multiband_delta_snv"),
       ("Δ-SNV, random other fruit's day 0 (mean ± SD, 10 draws)", "rnd", None),
       ("Scalar RMS distance from day 0", "cx", "self_scalar_rms"), ("Scalar L2 norm", "cx", "self_scalar_l2"),
       ("Scalar spectral angle", "cx", "self_scalar_angle"), ("RMS + spectral angle", "cx", "self_scalar_rms_angle")]
S5 = []
for name, src, key in lab:
    row = {"Representation": name}
    for cam in ("VIS", "VIS_COR"):
        for prot, dd, cc in (("Standard", d_std, c_std), ("Session-excluded", d_ses, c_ses)):
            col = f"{cam}, {prot}"
            if src == "delta":
                row[col] = f"{fb_mae(dd[(dd.camera_type == cam) & (dd.representation == key)]):.3f}"
            elif src == "cx":
                row[col] = f"{fb_mae(cc[(cc.camera_type == cam) & (cc.model == key)]):.3f}"
            else:
                g = rnd[(rnd.camera_type == cam) & (rnd.protocol == ("standard" if prot == "Standard" else "x"))]
                v = [fb_mae(x) for _, x in g.groupby("rep")]
                row[col] = f"{np.mean(v):.3f} ± {np.std(v, ddof=1):.3f}" if v else "NA"
    S5.append(row)
S5 = pd.DataFrame(S5)
S5x = pd.DataFrame([{"Direction": f"{s} → {t}", "Representation": r.replace("delta_", "Δ-").replace("snv", "SNV"),
                     "FB-MAE (days)": f"{fb_mae(g):.3f}"} for (s, t, r), g in xs.groupby(["source_camera", "target_camera", "representation"])])

sv = pd.read_csv(OUT_TABLES / "simplification_vs_final_full.csv")
vs = read(R, NB06, "kaki_virtual_sensor_standard_oof.csv")


def panel_name(m):
    m = m.replace("_session_excluded", "")
    if m.startswith("Sparse"):
        return "Native", "—", int(m.split("_k")[1])
    f, k = m.split("_FWHM")[1].split("_k")
    return "Virtual", f, int(k)


S6 = []
for model in sorted({m.replace("_session_excluded", "") for m in sv.model}, key=lambda m: (m[:1], panel_name(m)[1], panel_name(m)[2])):
    kind, fwhm, k = panel_name(model)
    a = sv[sv.model == model].iloc[0]
    b = sv[sv.model == model + "_session_excluded"].iloc[0]
    if kind == "Virtual":
        cen = vs[vs.model == model].groupby("outer_fold").panel_centers_nm.first()
        cnt = pd.Series([c for s in cen for c in s.split("|")]).value_counts()
        rec = ", ".join(f"{float(c):.0f}" for c in cnt[cnt >= 3].index) or "none"
    else:
        rec = "—"
    sg = lambda v: f"{v:+.3f}".replace("-", "−")
    S6.append({"Panel": kind, "FWHM (nm)": fwhm, "Channels": k,
               "FB-MAE, standard": f"{a.fb_mae:.3f}", "Difference vs full, standard [95% CI]": f"{sg(a.difference)} [{sg(a.ci95_low)}, {sg(a.ci95_high)}]",
               "FB-MAE, session-excluded": f"{b.fb_mae:.3f}", "Difference vs full, session-excluded [95% CI]": f"{sg(b.difference)} [{sg(b.ci95_low)}, {sg(b.ci95_high)}]",
               "Centers chosen in ≥3 of 5 folds (nm)": rec})
S6 = pd.DataFrame(S6)

ci = pd.read_csv(OUT_TABLES / "colour_index_baseline.csv")
S7 = pd.DataFrame({"Task": ci.task.map({"absolute": "Single-scan", "delta": "Tracking"}),
                   "Representation": ci.representation.map({"FULL": "Full spectrum", "ND2": "Two-band ND", "RGB3": "Broadband RGB"}),
                   "Protocol": ci.protocol.map({"standard": "Standard", "session_excluded": "Session-excluded"}),
                   "FB-MAE": ci.fb_mae.round(3), "MAE": ci.mae.round(3), "RMSE": ci.rmse.round(3), "R²": ci.r2.round(3),
                   "ρ": ci.spearman.round(3), "±1 day (%)": (100 * ci.within_1_day).round(1)})

for n, t in enumerate([S1, S2, S3, S4, S6, S7, S5x, S5], start=1):
    t.to_csv(OUT / f"Table_S{n}.csv", index=False)
pd.Series(n_fr).to_csv(OUT / "fruits_per_day.csv")

plt.rcParams.update({"font.family": "Liberation Serif", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7.5,
                     "ytick.labelsize": 7.5, "legend.fontsize": 7, "axes.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "savefig.dpi": 600, "axes.unicode_minus": True})
fig, ax = plt.subplots(1, 2, figsize=(6.30, 2.45))
rng = np.random.default_rng(20260818)
for i, (df, alg, title, col) in enumerate(((std, "PLSR", "(a)", "#2a78d6"), (ses, "Ridge", "(b)", "#eb6834"))):
    g = df[(df.task == "delta_snv") & (df.algorithm == alg)]
    x = g.y_true + rng.uniform(-0.15, 0.15, len(g))
    ax[i].scatter(x, g.y_pred, s=8, facecolors="none", edgecolors=col, linewidths=0.7)
    ax[i].plot([0, 9], [0, 9], color="#52514e", lw=0.9, ls=(0, (4, 2)))
    ax[i].set_xlim(0.3, 8.7); ax[i].set_ylim(-1, 10)
    ax[i].set_xticks([1, 2, 3, 4, 6, 7, 8])
    ax[i].set_xlabel("Observed storage day"); ax[i].set_ylabel("Predicted storage day")
    ax[i].text(-0.13, 1.04, title, transform=ax[i].transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax[i].text(0.04, 0.96, f"{alg}, FB-MAE {fb_mae(g):.3f} days", transform=ax[i].transAxes, va="top", fontsize=7)
fig.tight_layout(pad=0.4)
for ext in ("png", "pdf"):
    fig.savefig(OUT_FIGURES / f"Figure_S1.{ext}", facecolor="white")
print("tables:", [len(t) for t in (S1, S2, S3, S4, S5, S6, S7)])
print(S5.to_string(index=False)); print(S5x.to_string(index=False)); print(S6.to_string(index=False))
