# Data Pipeline

## Folder Structure

```
data/
├── zips/            # Raw zip files — tracked in GitHub (upload manually)
├── csvs/            # Extracted CSVs — local only (gitignored)
└── raw_parquets/    # Converted Parquets — local only (gitignored)
```

---

## Step 1 — Clone the repo

```bash
git clone git@github.com:Hoonieboogie/public-school-duckdb.git
cd public-school-duckdb
git checkout data-pipeline
```

---

## Step 2 — Zip → CSV

```bash
python scripts/zip_to_csv.py
```

Extracts all zip files from `data/zips/` into `data/csvs/`:

| Zip | CSV output | Size |
|-----|-----------|------|
| 0001. 공통_학교속성(09-23)(100%).zip | 공통_학교속성(09-23)_지역정보미제공.csv | ~81 MB |
| 0002. 유초중등학교개황(09-23)(100%).zip | 유초중등학교개황(09-23).csv | ~66 MB |
| 0003. 유초중등학급현황(09-23)(100%).zip | 유초중등학급현황(09-23).csv | ~41 MB |
| 0004. 유초중등학생현황(09-23)(100%).zip | 유초중등학생현황(09-23).csv | ~183 MB |
| 0005. 유초중등시설현황(09-23)(100%).zip | 유초중등시설현황(09-23).csv | ~67 MB |

---

## Step 3 — CSV → Parquet

```bash
pip install polars pyarrow
python scripts/csv_to_parquet.py
```

Converts all CSVs from `data/csvs/` into compressed Parquet files in `data/raw_parquets/`.
Uses ZSTD compression — expect **5-10x smaller** files with full predicate and
projection pushdown for Polars and DuckDB queries.

---

## Step 4 — Verify

```bash
ls -lh data/csvs/          # ~435 MB total
ls -lh data/raw_parquets/  # ~37 MB total
```

---

## Why Parquet over CSV?

| | CSV | Parquet |
|--|-----|---------|
| Size | ~435 MB | ~37 MB |
| Column skipping on disk | No | Yes |
| Row group skipping | No | Yes |
| Polars lazy scan | Full scan | Optimized I/O |
| DuckDB query | Full scan | Optimized I/O |
