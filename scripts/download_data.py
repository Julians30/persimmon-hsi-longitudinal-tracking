\
#!/usr/bin/env python3
"""Download the public DeepHS Fruit Kaki files used by the manuscript."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

BASE_URL = "https://cogsys.cs.uni-tuebingen.de/webprojects/DeepHS-Fruit-2023-Datasets"

FILES = {
    "Kaki.zip": {
        "url": f"{BASE_URL}/Kaki.zip",
        "sha256": "c388a528391e975c815f79859ef98f8966ecc06ec2426ec2d5bc6880efb717f6",
    },
    "annotations-upd-2024-01-09.zip": {
        "url": f"{BASE_URL}/annotations-upd-2024-01-09.zip",
        "sha256": "14275450e362684bc379a5aaf6c845cf82b0f9d5912036b9401d59a4b964a3f3",
    },
}


def sha256_file(path: Path, block_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(block_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def progress_hook(block_num: int, block_size: int, total_size: int) -> None:
    if total_size <= 0:
        return
    downloaded = min(block_num * block_size, total_size)
    pct = downloaded / total_size * 100
    print(f"\r  {pct:6.2f}%  {downloaded / 1024**2:,.1f} / {total_size / 1024**2:,.1f} MB", end="")


def download_one(name: str, out_dir: Path, force: bool = False) -> None:
    meta = FILES[name]
    target = out_dir / name

    if target.exists() and not force:
        digest = sha256_file(target)
        if digest == meta["sha256"]:
            print(f"{name}: already present and checksum verified.")
            return
        raise RuntimeError(
            f"{target} exists but SHA-256 does not match. "
            "Use --force only if you intentionally want to redownload it."
        )

    print(f"Downloading {name}")
    print(f"  Source: {meta['url']}")
    urllib.request.urlretrieve(meta["url"], target, reporthook=progress_hook)
    print()

    digest = sha256_file(target)
    if digest != meta["sha256"]:
        target.unlink(missing_ok=True)
        raise RuntimeError(
            f"Checksum mismatch for {name}. Expected {meta['sha256']}, got {digest}."
        )

    print(f"{name}: SHA-256 verified.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "raw",
        help="Destination directory (default: repository/data/raw).",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    args.data_dir.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        download_one(name, args.data_dir, force=args.force)

    print("All required public files are ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
