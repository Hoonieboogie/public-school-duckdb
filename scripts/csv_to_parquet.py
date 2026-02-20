"""
csv_to_parquet.py - Convert CSV files from csvs/ into Parquet in parquets/

Usage:
    python scripts/csv_to_parquet.py

Requirements:
    pip install polars pyarrow
"""

import io
import polars as pl
from pathlib import Path

CSVS_DIR = Path(__file__).parent.parent / "csvs"
PARQUETS_DIR = Path(__file__).parent.parent / "parquets"


def main():
    PARQUETS_DIR.mkdir(exist_ok=True)

    csv_files = sorted(CSVS_DIR.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {CSVS_DIR}")
        print("Run 'python scripts/zip_to_csv.py' first.")
        return

    print(f"Found {len(csv_files)} CSV file(s)\n")

    for csv_path in csv_files:
        out_path = PARQUETS_DIR / (csv_path.stem + ".parquet")
        csv_mb = csv_path.stat().st_size / (1024 * 1024)
        print(f"Converting: {csv_path.name} ({csv_mb:.1f} MB)")

        try:
            df = pl.read_csv(csv_path, infer_schema_length=10000, ignore_errors=True)
        except pl.exceptions.ComputeError:
            # Korean government files are often CP949/EUC-KR encoded
            print("  (detected non-UTF-8 encoding, retrying as CP949...)")
            text = csv_path.read_bytes().decode("cp949")
            df = pl.read_csv(io.StringIO(text), infer_schema_length=10000, ignore_errors=True)
        df.write_parquet(out_path, compression="zstd")

        parquet_mb = out_path.stat().st_size / (1024 * 1024)
        ratio = csv_mb / parquet_mb
        print(f"  -> {out_path.name} ({parquet_mb:.1f} MB, {ratio:.1f}x smaller)\n")

    print("Done. Parquet files are in parquets/")
    print("Note: parquets/ is gitignored — these files stay local only.")


if __name__ == "__main__":
    main()
