#!/usr/bin/env python3
"""Execute the cleaned notebooks sequentially without modifying canonical sources."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    "00_data_audit.ipynb",
    "01_longitudinal_eda.ipynb",
    "02_fruit_disjoint_baselines.ipynb",
    "03_session_robustness.ipynb",
    "04_negative_controls.ipynb",
    "05_wavelength_selection.ipynb",
    "06_virtual_sensor_design.ipynb",
    "07_cross_sensor_transfer.ipynb",
    "08_within_fruit_delta.ipynb",
    "09_baseline_specificity.ipynb",
    "10_final_ml_benchmark.ipynb",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="First notebook index to execute (default: 0).",
    )
    parser.add_argument(
        "--stop",
        type=int,
        default=10,
        help="Last notebook index to execute, inclusive (default: 10).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=-1,
        help="Per-cell timeout for nbconvert; -1 disables the timeout.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "exports" / "executed_notebooks",
        help="Directory for executed notebook copies.",
    )
    args = parser.parse_args()

    if args.start < 0 or args.stop >= len(NOTEBOOKS) or args.start > args.stop:
        parser.error(f"Valid range is 0..{len(NOTEBOOKS) - 1} with start <= stop.")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PERSIMMON_HSI_ROOT"] = str(ROOT)

    for idx, name in enumerate(NOTEBOOKS):
        if idx < args.start or idx > args.stop:
            continue

        path = ROOT / "notebooks" / name
        output_name = f"{path.stem}.executed.ipynb"

        print("=" * 80)
        print(f"Executing {idx:02d}: {path}")
        print(f"Writing executed copy to: {output_dir / output_name}")
        print("=" * 80)

        command = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            f"--ExecutePreprocessor.timeout={args.timeout}",
            "--output",
            output_name,
            "--output-dir",
            str(output_dir),
            str(path),
        ]
        subprocess.run(command, check=True, cwd=ROOT, env=env)

    print("Execution completed. Canonical notebooks under notebooks/ were not modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
