#!/usr/bin/env python3
"""Independent check: refit the notebook 10 single-scan Ridge from the fruit-day spectra and compare with the OOF file.

Re-implements the nested, fruit-disjoint selection (raw/SNV x alpha grid, inner FB-MAE) with the frozen splits
and reports the largest prediction difference against the frozen notebook 10 out-of-fold predictions.
Requires data/interim/kaki_fruit_day_spectra_VIS_COR.csv (written by notebook 01).
"""
import itertools
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from _common import NB10, ROOT, parser, read

ap = parser(__doc__.splitlines()[0])
ap.add_argument("--camera", default="VIS_COR", choices=["VIS", "VIS_COR"])
args = ap.parse_args()
CAM = args.camera
R = ROOT / "data" / "splits"
spec = pd.read_csv(args.interim_dir / f"kaki_fruit_day_spectra_{CAM}.csv")
wl = [c for c in spec.columns if c.startswith("wl_")]
outer = pd.read_csv(R / "kaki_outer5_fruit_disjoint_v1.csv")
inner = pd.read_csv(R / "kaki_inner4_within_outer5_fruit_disjoint_v1.csv")


def snv(X):
    m = X.mean(1, keepdims=True)
    s = X.std(1, keepdims=True)
    s[(~np.isfinite(s)) | (s == 0)] = 1.0
    return (X - m) / s


def fit_predict(Xtr, ytr, Xte, prep, alpha):
    if prep == "snv":
        Xtr, Xte = snv(Xtr), snv(Xte)
    sc = StandardScaler().fit(Xtr)
    return Ridge(alpha=alpha).fit(sc.transform(Xtr), ytr).predict(sc.transform(Xte))


def fbmae(fruit, yt, yp):
    return pd.Series(np.abs(yt - yp)).groupby(np.asarray(fruit)).mean().mean()


rows = []
for f in sorted(outer.outer_fold.unique()):
    test_f = set(outer.loc[outer.outer_fold == f, "fruit_id"])
    dev = spec[~spec.fruit_id.isin(test_f)]
    te = spec[spec.fruit_id.isin(test_f)]
    ia = inner[inner.outer_fold == f]
    best = None
    for prep, alpha in itertools.product(["raw", "snv"], [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]):
        fr, yt, yp = [], [], []
        for k in sorted(ia.inner_fold.unique()):
            vf = set(ia.loc[ia.inner_fold == k, "fruit_id"])
            tr, va = dev[~dev.fruit_id.isin(vf)], dev[dev.fruit_id.isin(vf)]
            p = fit_predict(tr[wl].to_numpy(float), tr.storage_days_model.to_numpy(float),
                            va[wl].to_numpy(float), prep, alpha)
            fr += list(va.fruit_id); yt += list(va.storage_days_model); yp += list(p)
        score = fbmae(fr, np.array(yt, float), np.array(yp))
        if best is None or score < best[0] - 1e-12:
            best = (score, prep, alpha)
    p = fit_predict(dev[wl].to_numpy(float), dev.storage_days_model.to_numpy(float),
                    te[wl].to_numpy(float), best[1], best[2])
    rows.append(pd.DataFrame({"outer_fold": f, "fruit_id": te.fruit_id.values,
                              "storage_days": te.storage_days_model.values,
                              "y_true": te.storage_days_model.values.astype(float), "y_pred": p,
                              "prep": best[1], "alpha": best[2]}))
mine = pd.concat(rows)
if CAM != "VIS_COR":
    print(CAM, "final-protocol Ridge FB-MAE:", round(fbmae(mine.fruit_id, mine.y_true.values, mine.y_pred.values), 4))
    print(mine.groupby("outer_fold")[["prep", "alpha"]].first()); sys.exit()
arch = read(args.results_root, NB10, "kaki_final_benchmark_standard_oof.csv")
arch = arch[(arch.task == "absolute") & (arch.algorithm == "Ridge")]
m = mine.merge(arch[["fruit_id", "storage_days", "y_pred", "config_json"]], on=["fruit_id", "storage_days"],
               suffixes=("_mine", "_archived"))
print("rows matched:", len(m), "of", len(mine))
print("max |diff| in predictions:", float(np.abs(m.y_pred_mine - m.y_pred_archived).max()))
print("FB-MAE reproduced:", round(fbmae(mine.fruit_id, mine.y_true.values, mine.y_pred.values), 4))
print(mine.groupby("outer_fold")[["prep", "alpha"]].first())
print(arch.groupby("outer_fold").config_json.first())
