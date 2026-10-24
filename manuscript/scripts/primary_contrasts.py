#!/usr/bin/env python3
"""Primary contrasts C1–C4 with family-wise error control (manuscript Section 2.12, Results 3.6–3.7).

C1  Δ-SNV vs absolute-spectrum Ridge, standard validation (days > 0)
C2  same comparison under session exclusion
C3  session-excluded Δ-SNV Ridge vs its matched null
C4  self-referenced multiband Δ-SNV vs scalar RMS-distance control

Paired fruit bootstrap (5000 resamples), unadjusted 95% and Bonferroni 98.75% percentile intervals,
two-sided bootstrap p-values with Holm step-down adjustment.
Output: manuscript/tables/primary_contrasts_holm_bonferroni.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from _common import NB09, NB10, OUT_TABLES, SEED, paired_bootstrap, parser, per_fruit_mae, read

FAMILY, ALPHA = 4, 0.05


def summarize(label: str, a: pd.Series, b: pd.Series, seed: int) -> dict:
    diff, bs = paired_bootstrap(a, b, seed)
    p = max(2 * min((bs >= 0).mean(), (bs <= 0).mean()), 1 / len(bs))
    q = 100 * ALPHA / FAMILY / 2
    return dict(contrast=label, n_fruits=len(diff), mean_diff=diff.mean(),
                ci95_low=np.percentile(bs, 2.5), ci95_high=np.percentile(bs, 97.5),
                ci_bonferroni_low=np.percentile(bs, q), ci_bonferroni_high=np.percentile(bs, 100 - q),
                p_boot=p, share_fruits_first_better=(diff < 0).mean())


def main() -> None:
    args = parser(__doc__.splitlines()[0]).parse_args()
    std = read(args.results_root, NB10, "kaki_final_benchmark_standard_oof.csv")
    ses = read(args.results_root, NB10, "kaki_final_benchmark_session_excluded_oof.csv")
    null = read(args.results_root, NB10, "kaki_final_benchmark_session_null_oof.csv")
    cx = read(args.results_root, NB09, "kaki_baseline_complexity_standard_oof.csv")

    def pick(df, task, gt0=False):
        g = df[(df.task == task) & (df.algorithm == "Ridge")]
        return g[g.storage_days > 0] if gt0 else g

    cxv = cx[cx.camera_type == "VIS_COR"]
    pairs = [
        ("C1 delta-SNV minus absolute, standard", pick(std, "delta_snv"), pick(std, "absolute", True)),
        ("C2 delta-SNV minus absolute, session-excluded", pick(ses, "delta_snv"), pick(ses, "absolute", True)),
        ("C3 delta-SNV minus matched null, session-excluded", pick(ses, "delta_snv"), null[null.task == "delta_snv"]),
        ("C4 multiband minus scalar RMS, self baseline", cxv[cxv.model == "self_multiband_delta_snv"],
         cxv[cxv.model == "self_scalar_rms"]),
    ]
    res = pd.DataFrame([summarize(lab, per_fruit_mae(a), per_fruit_mae(b), SEED + i)
                        for i, (lab, a, b) in enumerate(pairs)])
    holm, running = np.empty(len(res)), 0.0
    for rank, idx in enumerate(res.p_boot.sort_values().index):
        running = max(running, min(1.0, (len(res) - rank) * res.loc[idx, "p_boot"]))
        holm[idx] = running
    res["p_holm"] = holm
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    out = OUT_TABLES / "primary_contrasts_holm_bonferroni.csv"
    res.to_csv(out, index=False)
    print(res.round(3).to_string(index=False))
    print(f"written: {out.relative_to(OUT_TABLES.parents[1])}")


if __name__ == "__main__":
    main()
