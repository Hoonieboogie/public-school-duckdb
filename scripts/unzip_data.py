"""
unzip_data.py - Extract raw zip files from zips/ into data/

Usage:
    python scripts/unzip_data.py
"""

import zipfile
import os
from pathlib import Path

ZIPS_DIR = Path(__file__).parent.parent / "zips"
DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    DATA_DIR.mkdir(exist_ok=True)

    zip_files = sorted(ZIPS_DIR.glob("*.zip"))

    if not zip_files:
        print(f"No zip files found in {ZIPS_DIR}")
        return

    print(f"Found {len(zip_files)} zip file(s)\n")

    for zip_path in zip_files:
        print(f"Extracting: {zip_path.name}")
        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.infolist():
                z.extract(member, DATA_DIR)
                size_mb = member.file_size / (1024 * 1024)
                print(f"  -> {member.filename} ({size_mb:.1f} MB)")
        print()

    print("Done. CSV files are in data/")
    print("Note: data/ is gitignored — these files stay local only.")


if __name__ == "__main__":
    main()
