#!/usr/bin/env python3
"""Static pre-publication checks for the reproducibility repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"

EXPECTED = [
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

FORBIDDEN_PATTERNS = {
    "Google Drive hard-coded path": r"/content/drive/MyDrive",
    "Colab import": r"google\.colab",
    "Chat review instruction": r"(subir|sube|enviar).{0,30}(chat|ZIP al chat)",
    "Potential OpenAI secret": r"\bsk-[A-Za-z0-9_-]{16,}\b",
    "GitHub token pattern": r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
}


def main() -> int:
    errors: list[str] = []

    actual = sorted(p.name for p in NOTEBOOK_DIR.glob("*.ipynb"))
    if actual != EXPECTED:
        errors.append(f"Notebook list/order mismatch.\nExpected: {EXPECTED}\nActual: {actual}")

    for name in EXPECTED:
        path = NOTEBOOK_DIR / name
        if not path.exists():
            continue
        nb = json.loads(path.read_text(encoding="utf-8"))
        for i, cell in enumerate(nb.get("cells", [])):
            source = "".join(cell.get("source", []))
            for label, pattern in FORBIDDEN_PATTERNS.items():
                if re.search(pattern, source, flags=re.I | re.S):
                    errors.append(f"{name}, cell {i}: {label}")
            if cell.get("cell_type") == "code":
                if cell.get("outputs"):
                    errors.append(f"{name}, cell {i}: notebook output was not stripped")
                if cell.get("execution_count") is not None:
                    errors.append(f"{name}, cell {i}: execution_count is not null")
                try:
                    compile(source, f"{name}:cell{i}", "exec")
                except SyntaxError as exc:
                    errors.append(f"{name}, cell {i}: syntax error: {exc}")

    required_splits = [
        ROOT / "data" / "splits" / "kaki_outer5_fruit_disjoint_v1.csv",
        ROOT / "data" / "splits" / "kaki_inner4_within_outer5_fruit_disjoint_v1.csv",
    ]
    for path in required_splits:
        if not path.exists():
            errors.append(f"Missing frozen split: {path.relative_to(ROOT)}")

    raw_dir = ROOT / "data" / "raw"
    forbidden_raw_suffixes = {".zip", ".bin", ".hdr", ".torrent"}
    for path in raw_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in forbidden_raw_suffixes:
            errors.append(f"Large/raw file should not be committed: {path.relative_to(ROOT)}")

    if errors:
        print("Repository verification FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository verification PASSED.")
    print(f"- {len(EXPECTED)} cleaned notebooks")
    print("- no hard-coded Google Drive paths")
    print("- no Colab/chat-specific code")
    print("- all code cells compile statically")
    print("- frozen outer/inner splits present")
    print("- raw HSI archives absent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
