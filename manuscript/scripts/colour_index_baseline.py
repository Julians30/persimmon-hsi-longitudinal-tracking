#!/usr/bin/env python3
"""Colour-index baselines: does a simple colorimeter-like feature set match the full VIS_COR spectrum?

Added for the Foods version. Same frozen fruit-disjoint outer/inner splits, same Ridge grid, same inner
fruit-balanced MAE selection and same session-excluded protocol as notebook 10 (re-implemented here and checked
against the archived notebook 10 Ridge predictions before the new representations are evaluated).

Representations (VIS_COR, 408-901 nm)
  FULL      full 249-band spectrum (absolute task: raw or SNV chosen in the inner loop; delta task: delta-SNV)
  ND2       normalized difference of two 10-nm bands, (R680 - R550) / (R680 + R550): red chlorophyll absorption
            versus green reflectance, a standard colour/chlorophyll index (bands fixed a priori, not selected)
  RGB3      broadband blue/green/red reflectance (mean of 410-500, 500-600 and 600-700 nm), i.e. a simulated
            RGB camera or tristimulus colorimeter; absolute task: raw or chromaticity (r, g, b) chosen in the
            inner loop; delta task: change in chromaticity relative to the same fruit at day 0
Delta task features are always the difference between the fruit-day and the same fruit's day-0 features.
Output: manuscript/tables/colour_index_baseline.csv (metrics) and colour_index_contrasts.csv (paired bootstrap)
Requires data/interim/kaki_fruit_day_spectra_VIS_COR.csv (written by notebook 01).
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from _common import NB10, OUT_TABLES, ROOT, SEED, paired_bootstrap, parser, per_fruit_mae, read

args = parser(__doc__.splitlines()[0]).parse_args()
spec = pd.read_csv(args.interim_dir / "kaki_fruit_day_spectra_VIS_COR.csv").sort_values(
    ["fruit_id", "storage_days_model"]).reset_index(drop=True)
wl_cols = [c for c in spec.columns if c.startswith("wl_")]
wl = np.array([float(c[3:]) for c in wl_cols])
X = spec[wl_cols].to_numpy(float)
outer = pd.read_csv(ROOT / "data" / "splits" / "kaki_outer5_fruit_disjoint_v1.csv")
inner = pd.read_csv(ROOT / "data" / "splits" / "kaki_inner4_within_outer5_fruit_disjoint_v1.csv")
ALPHAS = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]


def snv(Z):
    mu, sd = Z.mean(1, keepdims=True), Z.std(1, keepdims=True)
    sd[(~np.isfinite(sd)) | (sd == 0)] = 1.0
    return (Z - mu) / sd


def band(lo, hi):
    return X[:, (wl >= lo) & (wl <= hi)].mean(1)


R550, R680 = band(545, 555), band(675, 685)
ND2 = ((R680 - R550) / (R680 + R550))[:, None]
RGB = np.column_stack([band(410, 500), band(500, 600), band(600, 700)])


def chroma(Z):
    return Z / Z.sum(1, keepdims=True)


ABS = {"FULL": {"raw": X, "snv": snv(X)}, "ND2": {"as_is": ND2}, "RGB3": {"raw": RGB, "chroma": chroma(RGB)}}
DELTA_SRC = {"FULL": snv(X), "ND2": ND2, "RGB3": chroma(RGB)}

meta = spec[["fruit_id", "storage_days_model"]].rename(columns={"storage_days_model": "y"})
base_idx = {f: i for i, (f, d) in enumerate(zip(meta.fruit_id, meta.y)) if d == 0}
later = meta[meta.y > 0].index.to_numpy()
later = np.array([i for i in later if meta.fruit_id[i] in base_idx])
b_of = np.array([base_idx[meta.fruit_id[i]] for i in later])
DEL = {k: {"as_is": v[later] - v[b_of]} for k, v in DELTA_SRC.items()}
TASKS = {"absolute": (meta.reset_index(drop=True), ABS), "delta": (meta.loc[later].reset_index(drop=True), DEL)}
assert len(TASKS["delta"][0]) == 159 and TASKS["delta"][0].fruit_id.nunique() == 38


def fit_predict(Xtr, ytr, Xte, alpha):
    sc = StandardScaler().fit(Xtr)
    return Ridge(alpha=alpha).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xte))


def fbmae(f, y, p):
    return pd.Series(np.abs(y - p)).groupby(np.asarray(f)).mean().mean()


def dbmae(y, p):
    return pd.Series(np.abs(y - p)).groupby(np.asarray(y)).mean().mean()


def run(task, rep, protocol):
    m, allb = TASKS[task]
    blocks = allb[rep]
    f_all, y_all = m.fruit_id.to_numpy(int), m.y.to_numpy(float)
    configs = list(itertools.product(blocks.keys(), ALPHAS))
    rows = []
    for of in range(5):
        test = set(outer.loc[outer.outer_fold == of, "fruit_id"].astype(int))
        dev = ~np.isin(f_all, list(test))
        ia = inner[inner.outer_fold == of]
        best = None
        for ci, (prep, a) in enumerate(configs):
            Z = blocks[prep]
            ff, yy, pp = [], [], []
            for k in range(4):
                val = set(ia.loc[ia.inner_fold == k, "fruit_id"].astype(int))
                va = dev & np.isin(f_all, list(val))
                tr = dev & ~np.isin(f_all, list(val))
                if protocol == "standard":
                    pp.append(fit_predict(Z[tr], y_all[tr], Z[va], a)); ff.append(f_all[va]); yy.append(y_all[va])
                else:
                    for d in sorted(np.unique(y_all[va])):
                        v2, t2 = va & (y_all == d), tr & (y_all != d)
                        pp.append(fit_predict(Z[t2], y_all[t2], Z[v2], a)); ff.append(f_all[v2]); yy.append(y_all[v2])
            ff, yy, pp = map(np.concatenate, (ff, yy, pp))
            rank = (fbmae(ff, yy, pp), dbmae(yy, pp), np.abs(yy - pp).mean(), ci)
            if best is None or rank < best[0]:
                best = (rank, prep, a)
        _, prep, a = best
        Z = blocks[prep]
        te = np.isin(f_all, list(test))
        if protocol == "standard":
            p = fit_predict(Z[dev], y_all[dev], Z[te], a)
            rows.append(pd.DataFrame(dict(fruit_id=f_all[te], storage_days=y_all[te].astype(int), y_true=y_all[te],
                                          y_pred=p, outer_fold=of, config=f"{prep}/{a}")))
        else:
            for d in sorted(np.unique(y_all[te])):
                t2, e2 = dev & (y_all != d), te & (y_all == d)
                p = fit_predict(Z[t2], y_all[t2], Z[e2], a)
                rows.append(pd.DataFrame(dict(fruit_id=f_all[e2], storage_days=int(d), y_true=y_all[e2], y_pred=p,
                                              outer_fold=of, config=f"{prep}/{a}")))
    out = pd.concat(rows, ignore_index=True)
    out["task"], out["representation"], out["protocol"] = task, rep, protocol
    return out


oof = pd.concat([run(t, r, p) for t in TASKS for r in ("FULL", "ND2", "RGB3") for p in ("standard", "session_excluded")],
                ignore_index=True)

arch = {"standard": read(args.results_root, NB10, "kaki_final_benchmark_standard_oof.csv"),
        "session_excluded": read(args.results_root, NB10, "kaki_final_benchmark_session_excluded_oof.csv")}
for prot, a in arch.items():
    for t, at in (("absolute", "absolute"), ("delta", "delta_snv")):
        ref = a[(a.task == at) & (a.algorithm == "Ridge")][["fruit_id", "storage_days", "y_pred"]]
        mine = oof[(oof.task == t) & (oof.representation == "FULL") & (oof.protocol == prot)]
        mm = mine.merge(ref, on=["fruit_id", "storage_days"], suffixes=("", "_arch"))
        assert len(mm) == len(mine) == len(ref), (prot, t, len(mm), len(mine), len(ref))
        dmax = float(np.abs(mm.y_pred - mm.y_pred_arch).max())
        print(f"reproduction {t:8s} {prot:16s} n={len(mm)} max|diff|={dmax:.2e}")
        assert dmax < 1e-6

met = []
for (t, r, p), g in oof.groupby(["task", "representation", "protocol"], sort=False):
    y, q = g.y_true.to_numpy(), g.y_pred.to_numpy()
    met.append(dict(task=t, representation=r, protocol=p, n=len(g), n_fruits=g.fruit_id.nunique(),
                    fb_mae=fbmae(g.fruit_id, y, q), mae=np.abs(y - q).mean(),
                    rmse=float(np.sqrt(((y - q) ** 2).mean())),
                    r2=1 - ((y - q) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                    spearman=pd.Series(y).corr(pd.Series(q), method="spearman"),
                    within_1_day=(np.abs(y - q) <= 1).mean(), configs=";".join(sorted(g.config.unique()))))
met = pd.DataFrame(met)

con = []
i = 0
for t in TASKS:
    for p in ("standard", "session_excluded"):
        full = per_fruit_mae(oof[(oof.task == t) & (oof.representation == "FULL") & (oof.protocol == p)])
        for r in ("ND2", "RGB3"):
            other = per_fruit_mae(oof[(oof.task == t) & (oof.representation == r) & (oof.protocol == p)])
            diff, bs = paired_bootstrap(full, other, SEED + 100 + i); i += 1
            con.append(dict(task=t, protocol=p, contrast=f"FULL minus {r}", n_fruits=len(diff), mean_diff=diff.mean(),
                            ci95_low=np.percentile(bs, 2.5), ci95_high=np.percentile(bs, 97.5),
                            share_fruits_full_better=(diff < 0).mean()))
con = pd.DataFrame(con)
OUT_TABLES.mkdir(parents=True, exist_ok=True)
met.to_csv(OUT_TABLES / "colour_index_baseline.csv", index=False)
con.to_csv(OUT_TABLES / "colour_index_contrasts.csv", index=False)
oof.to_csv(OUT_TABLES / "colour_index_oof.csv", index=False)
print(met.drop(columns="configs").round(3).to_string(index=False))
print(con.round(3).to_string(index=False))
