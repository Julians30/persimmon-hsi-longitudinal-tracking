#!/usr/bin/env python3
"""Sparse native-band and virtual-filter panels referenced to the final full-spectrum Ridge (Table 5, Section 3.4).

Each panel's fruit-balanced MAE is compared with the notebook 10 full-spectrum VIS_COR Ridge under the same
protocol (standard or session-excluded) using the paired fruit bootstrap (5000 resamples, 95% percentile CI).
Output: manuscript/tables/simplification_vs_final_full.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from _common import NB05, NB06, NB10, OUT_TABLES, SEED, paired_bootstrap, parser, per_fruit_mae, read


def main() -> None:
    args = parser(__doc__.splitlines()[0]).parse_args()
    std = read(args.results_root, NB10, "kaki_final_benchmark_standard_oof.csv")
    ses = read(args.results_root, NB10, "kaki_final_benchmark_session_excluded_oof.csv")
    full = {
        "standard": per_fruit_mae(std[(std.task == "absolute") & (std.algorithm == "Ridge")]),
        "session_excluded": per_fruit_mae(ses[(ses.task == "absolute") & (ses.algorithm == "Ridge")]),
    }
    sets = [
        ("native", "standard", read(args.results_root, NB05, "kaki_viscor_sparse_standard_oof.csv")),
        ("native", "session_excluded", read(args.results_root, NB05, "kaki_viscor_sparse_session_excluded_oof.csv")),
        ("virtual", "standard", read(args.results_root, NB06, "kaki_virtual_sensor_standard_oof.csv")),
        ("virtual", "session_excluded", read(args.results_root, NB06, "kaki_virtual_sensor_session_excluded_oof.csv")),
    ]
    rows = []
    for kind, protocol, df in sets:
        for i, (model, g) in enumerate(df.groupby("model")):
            a = per_fruit_mae(g)
            diff, bs = paired_bootstrap(a, full[protocol], SEED + i)
            rows.append(dict(panel_type=kind, protocol=protocol, model=model, fb_mae=a.mean(),
                             full_spectrum_fb_mae=full[protocol].mean(), difference=diff.mean(),
                             ci95_low=np.percentile(bs, 2.5), ci95_high=np.percentile(bs, 97.5)))
    res = pd.DataFrame(rows).sort_values(["panel_type", "protocol", "fb_mae"])
    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    out = OUT_TABLES / "simplification_vs_final_full.csv"
    res.to_csv(out, index=False)
    print(res.round(3).to_string(index=False))
    print(f"written: {out.relative_to(OUT_TABLES.parents[1])}")


if __name__ == "__main__":
    main()
