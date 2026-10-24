#!/usr/bin/env python3
"""Static release checks for the Persimmon HSI reproducibility repository (v1.0)."""

from __future__ import annotations

import csv
import hashlib
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
SCRIPT_DIR = ROOT / "scripts"

EXPECTED_NOTEBOOKS = [
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

EXPECTED_SCRIPTS = [
    "download_data.py",
    "run_notebooks.py",
    "verify_repository.py",
]

MANUSCRIPT_SCRIPT_DIR = ROOT / "manuscript" / "scripts"
EXPECTED_MANUSCRIPT_SCRIPTS = [
    "_common.py",
    "check_ridge_reproduction.py",
    "make_figures.py",
    "make_workflow_figure.py",
    "primary_contrasts.py",
    "simplification_vs_final.py",
]
OOF_ROOT = ROOT / "results" / "manuscript_oof"
EXPECTED_OOF = {
    "05_kaki_wavelength_selection_sensor_simplification": [
        "kaki_viscor_sparse_standard_oof.csv", "kaki_viscor_sparse_session_excluded_oof.csv"],
    "06_kaki_multivariate_virtual_sensor_design": [
        "kaki_virtual_sensor_standard_oof.csv", "kaki_virtual_sensor_session_excluded_oof.csv"],
    "08_kaki_within_fruit_delta_trajectory": [
        "kaki_delta_standard_oof.csv", "kaki_delta_session_excluded_oof.csv",
        "kaki_delta_standard_dummy_median_oof.csv", "kaki_delta_session_excluded_dummy_mean_oof.csv",
        "kaki_cross_sensor_delta_oof.csv"],
    "09_kaki_baseline_specificity_trajectory_complexity": [
        "kaki_baseline_complexity_standard_oof.csv", "kaki_baseline_complexity_session_excluded_oof.csv",
        "kaki_random_other_baseline_oof.csv", "kaki_standard_dummy_median_days_gt0_oof.csv",
        "kaki_session_excluded_dummy_mean_days_gt0_oof.csv"],
    "10_kaki_final_classical_ml_benchmark": [
        "kaki_final_benchmark_standard_oof.csv", "kaki_final_benchmark_session_excluded_oof.csv",
        "kaki_final_benchmark_standard_null_oof.csv", "kaki_final_benchmark_session_null_oof.csv"],
}
MANUSCRIPT_TABLES = [
    ROOT / "manuscript" / "tables" / "primary_contrasts_holm_bonferroni.csv",
    ROOT / "manuscript" / "tables" / "simplification_vs_final_full.csv",
]
MANUSCRIPT_FIGURES = [ROOT / "manuscript" / "figures" / f"Figure_{i}.{ext}" for i in range(1, 10) for ext in ("png", "pdf")]
RELEASE_FILES = [ROOT / "LICENSE", ROOT / "CITATION.cff", ROOT / "README.md", ROOT / "CHANGELOG.md"]

OUTER_SPLIT = ROOT / "data" / "splits" / "kaki_outer5_fruit_disjoint_v1.csv"
INNER_SPLIT = ROOT / "data" / "splits" / "kaki_inner4_within_outer5_fruit_disjoint_v1.csv"
EXPECTED_SPLIT_HASHES = {
    OUTER_SPLIT: "56013aaf85c546c8ac2df1d7db0552918a8687a5e510e42c73e099eb5fef8973",
    INNER_SPLIT: "785adc00e1a2f8a2fc6800a921390a0eaaf87b2cfc82cb04d892ab1ca3814e0b",
}

REQUIRED_RESULTS = [
    ROOT / "results" / "reference" / "kaki_final_classical_ml_benchmark_summary.json",
    ROOT / "results" / "reference" / "run_manifest.json",
]
REQUIRED_TABLES = [
    ROOT / "tables" / "reference" / "10_paired_fruit_bootstrap_algorithms.csv",
    ROOT / "tables" / "reference" / "14_best_standard_algorithm_by_task.csv",
    ROOT / "tables" / "reference" / "15_master_algorithm_metrics_for_manuscript.csv",
]
REQUIRED_FIGURES = [
    ROOT / "figures" / "reference" / "01_standard_benchmark_absolute.png",
    ROOT / "figures" / "reference" / "01_standard_benchmark_delta_snv.png",
    ROOT / "figures" / "reference" / "02_session_excluded_benchmark_absolute.png",
    ROOT / "figures" / "reference" / "02_session_excluded_benchmark_delta_snv.png",
]

FORBIDDEN_PATTERNS = {
    "Google Drive hard-coded path": r"/content/drive/MyDrive",
    "Colab import": r"google\.colab",
    "Chat review instruction": r"(subir|sube|enviar).{0,30}(chat|ZIP al chat)",
    "Potential OpenAI secret": r"\bsk-[A-Za-z0-9_-]{16,}\b",
    "GitHub token pattern": r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
}
NOTEBOOK_OR_CODE_ONLY_PATTERNS = {
    "Google Drive hard-coded path",
    "Colab import",
    "Chat review instruction",
}

FORBIDDEN_TRACKED_SUFFIXES = {
    ".zip", ".bin", ".hdr", ".torrent", ".tar", ".pt", ".pth", ".ckpt"
}
TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".yml", ".yaml", ".json", ".csv", ".cff", ".template"
}


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def audit_notebooks(errors: list[str]) -> None:
    actual = sorted(p.name for p in NOTEBOOK_DIR.glob("*.ipynb"))
    if actual != EXPECTED_NOTEBOOKS:
        errors.append(
            f"Notebook list/order mismatch. Expected {EXPECTED_NOTEBOOKS}; actual {actual}"
        )

    tracked_notebooks = sorted(
        p for p in subprocess.check_output(["git", "ls-files", "*.ipynb"], text=True).splitlines()
    )
    expected_paths = sorted(f"notebooks/{name}" for name in EXPECTED_NOTEBOOKS)
    if tracked_notebooks != expected_paths:
        errors.append(
            "Tracked notebooks must exist only under notebooks/. "
            f"Expected {expected_paths}; actual {tracked_notebooks}"
        )

    for name in EXPECTED_NOTEBOOKS:
        path = NOTEBOOK_DIR / name
        if not path.exists():
            continue
        try:
            nb = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{name}: invalid notebook JSON: {exc}")
            continue

        if "cells" not in nb or "nbformat" not in nb:
            errors.append(f"{name}: invalid notebook structure")
            continue

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


def audit_scripts(errors: list[str]) -> None:
    actual = sorted(p.name for p in SCRIPT_DIR.glob("*.py"))
    if actual != sorted(EXPECTED_SCRIPTS):
        errors.append(
            f"Script inventory mismatch. Expected {sorted(EXPECTED_SCRIPTS)}; actual {actual}"
        )

    for name in EXPECTED_SCRIPTS:
        path = SCRIPT_DIR / name
        if not path.exists():
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append(f"Python syntax error in {path.relative_to(ROOT)}: {exc}")
        first_line = path.read_text(encoding="utf-8").splitlines()[0] if path.stat().st_size else ""
        if first_line != "#!/usr/bin/env python3":
            errors.append(f"Invalid script header in {path.relative_to(ROOT)}")


def audit_manuscript_materials(errors: list[str]) -> None:
    actual = sorted(p.name for p in MANUSCRIPT_SCRIPT_DIR.glob("*.py"))
    if actual != sorted(EXPECTED_MANUSCRIPT_SCRIPTS):
        errors.append(f"Manuscript script inventory mismatch. Expected {EXPECTED_MANUSCRIPT_SCRIPTS}; actual {actual}")
    for name in EXPECTED_MANUSCRIPT_SCRIPTS:
        path = MANUSCRIPT_SCRIPT_DIR / name
        if not path.exists():
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append(f"Python syntax error in {path.relative_to(ROOT)}: {exc}")
    required_cols = {"fruit_id", "storage_days", "y_true", "y_pred"}
    for folder, names in EXPECTED_OOF.items():
        for name in names:
            path = OOF_ROOT / folder / name
            if not path.exists():
                errors.append(f"Missing frozen OOF file: {path.relative_to(ROOT)}")
                continue
            with path.open("r", encoding="utf-8", newline="") as handle:
                header = set(next(csv.reader(handle)))
            if not required_cols <= header:
                errors.append(f"OOF file lacks {sorted(required_cols - header)}: {path.relative_to(ROOT)}")
    for path in MANUSCRIPT_TABLES + MANUSCRIPT_FIGURES + RELEASE_FILES:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"Missing release file: {path.relative_to(ROOT)}")
    lic = ROOT / "LICENSE"
    if lic.exists() and not lic.read_text(encoding="utf-8").startswith("MIT License"):
        errors.append("LICENSE must contain the MIT License text")


def audit_splits(errors: list[str]) -> None:
    for path, expected_hash in EXPECTED_SPLIT_HASHES.items():
        if not path.exists():
            errors.append(f"Missing frozen split: {path.relative_to(ROOT)}")
            continue
        observed_hash = sha256_file(path)
        if observed_hash != expected_hash:
            errors.append(
                f"Frozen split hash mismatch for {path.relative_to(ROOT)}: "
                f"expected {expected_hash}, got {observed_hash}"
            )

    if not OUTER_SPLIT.exists() or not INNER_SPLIT.exists():
        return

    outer_rows = read_csv_rows(OUTER_SPLIT)
    inner_rows = read_csv_rows(INNER_SPLIT)

    outer_fruits = [int(row["fruit_id"]) for row in outer_rows]
    if len(outer_rows) != 40 or len(set(outer_fruits)) != 40 or set(outer_fruits) != set(range(1, 41)):
        errors.append("Outer split must contain each physical fruit ID 1..40 exactly once")

    outer_by_fold: dict[int, set[int]] = {}
    for row in outer_rows:
        fold = int(row["outer_fold"])
        outer_by_fold.setdefault(fold, set()).add(int(row["fruit_id"]))
    if set(outer_by_fold) != set(range(5)):
        errors.append(f"Outer split folds must be 0..4; got {sorted(outer_by_fold)}")
    for fold in range(5):
        if len(outer_by_fold.get(fold, set())) != 8:
            errors.append(f"Outer fold {fold} must contain 8 test fruits")

    all_fruits = set(range(1, 41))
    for outer_fold in range(5):
        rows = [row for row in inner_rows if int(row["outer_fold"]) == outer_fold]
        development_fruits = {int(row["fruit_id"]) for row in rows}
        held_out = outer_by_fold.get(outer_fold, set())
        expected_development = all_fruits - held_out
        if development_fruits != expected_development:
            errors.append(
                f"Inner split for outer fold {outer_fold} does not exactly match the 32 non-test fruits"
            )
        inner_by_fold: dict[int, set[int]] = {}
        for row in rows:
            inner_by_fold.setdefault(int(row["inner_fold"]), set()).add(int(row["fruit_id"]))
        if set(inner_by_fold) != set(range(4)):
            errors.append(f"Inner folds for outer fold {outer_fold} must be 0..3")
        for inner_fold in range(4):
            if len(inner_by_fold.get(inner_fold, set())) != 8:
                errors.append(
                    f"Outer fold {outer_fold}, inner fold {inner_fold} must contain 8 fruits"
                )
        if held_out & development_fruits:
            errors.append(f"Outer-test fruit leakage detected for outer fold {outer_fold}")


def audit_reference_outputs(errors: list[str]) -> None:
    for path in REQUIRED_RESULTS:
        if not path.exists():
            errors.append(f"Missing reference result: {path.relative_to(ROOT)}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")

    for path in REQUIRED_TABLES:
        if not path.exists() or path.stat().st_size == 0:
            errors.append(f"Missing/empty reference table: {path.relative_to(ROOT)}")

    png_magic = b"\x89PNG\r\n\x1a\n"
    for path in REQUIRED_FIGURES:
        if not path.exists():
            errors.append(f"Missing reference figure: {path.relative_to(ROOT)}")
            continue
        with path.open("rb") as handle:
            if handle.read(8) != png_magic:
                errors.append(f"Invalid PNG signature: {path.relative_to(ROOT)}")


def audit_tracked_files(errors: list[str]) -> None:
    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    for item in tracked:
        path = ROOT / item
        p = Path(item)
        lower_parts = {part.lower() for part in p.parts}

        if p.suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES:
            errors.append(f"Large/private artifact must not be tracked: {item}")
        if p.name.lower().startswith(".env"):
            errors.append(f"Environment secret file must not be tracked: {item}")
        if "secrets" in lower_parts or "config" in lower_parts:
            errors.append(f"Private configuration directory must not be tracked: {item}")
        if p.suffix.lower() in {".pem", ".key"}:
            errors.append(f"Private key material must not be tracked: {item}")

        # The verifier intentionally stores the patterns it searches for, so it must not
        # scan its own source text for those same patterns.
        if item == "scripts/verify_repository.py":
            continue

        if path.is_file() and path.stat().st_size <= 1_000_000 and (
            p.suffix.lower() in TEXT_SUFFIXES or p.name == ".gitignore"
        ):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in FORBIDDEN_PATTERNS.items():
                # Historical audit documentation may legitimately mention old Colab/Drive
                # strings. Those patterns are enforced in notebooks and active Python code,
                # while credential-token patterns are scanned across all tracked text files.
                if label in NOTEBOOK_OR_CODE_ONLY_PATTERNS and p.suffix.lower() != ".py":
                    continue
                if re.search(pattern, text, flags=re.I | re.S):
                    errors.append(f"{item}: {label}")


def main() -> int:
    errors: list[str] = []

    audit_notebooks(errors)
    audit_scripts(errors)
    audit_manuscript_materials(errors)
    audit_splits(errors)
    audit_reference_outputs(errors)
    audit_tracked_files(errors)

    if errors:
        print("Repository verification FAILED:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository verification PASSED.")
    print(f"- {len(EXPECTED_NOTEBOOKS)} cleaned canonical notebooks")
    print(f"- {len(EXPECTED_SCRIPTS)} repository utility scripts compile")
    print("- no stored notebook outputs or execution counts")
    print(f"- {len(EXPECTED_MANUSCRIPT_SCRIPTS)} manuscript scripts compile; frozen OOF files, tables and Figures 1-9 present")
    print("- MIT LICENSE, CITATION.cff, README.md and CHANGELOG.md present")
    print("- no hard-coded Google Drive / Colab / chat-specific notebook code")
    print("- frozen outer/inner split hashes match the manuscript audit")
    print("- 5x8 outer fruit-disjoint and 4x8 inner-fold structure verified")
    print("- no outer-test fruit appears in its corresponding inner CV")
    print("- required reference JSON, tables, and PNG figures are present and valid")
    print("- no tracked raw HSI archives, checkpoints, secret files, or credential patterns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
