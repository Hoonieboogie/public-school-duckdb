# Data Pipeline

Raw government zip files are stored in `zips/` and tracked in GitHub.
Generated CSV files live in `data/` and are **gitignored** (local only).

---

## Step 1 — Clone the repo

```bash
git clone git@github.com:Hoonieboogie/public-school-duckdb.git
cd public-school-duckdb
git checkout data-pipeline
```

---

## Step 2 — Unzip raw data

```bash
python scripts/unzip_data.py
```

This extracts all zip files from `zips/` into `data/`:

| Zip | CSV output | Size |
|-----|-----------|------|
| 0001. 공통_학교속성(09-23)(100%).zip | 공통_학교속성(09-23)_지역정보미제공.csv | ~81 MB |
| 0002. 유초중등학교개황(09-23)(100%).zip | 유초중등학교개황(09-23).csv | ~66 MB |
| 0003. 유초중등학급현황(09-23)(100%).zip | 유초중등학급현황(09-23).csv | ~41 MB |
| 0004. 유초중등학생현황(09-23)(100%).zip | 유초중등학생현황(09-23).csv | ~183 MB |
| 0005. 유초중등시설현황(09-23)(100%).zip | 유초중등시설현황(09-23).csv | ~67 MB |

---

## Step 3 — Verify

```bash
ls -lh data/
```

You should see 5 CSV files totalling ~435 MB.

---

## Folder Structure

```
public-school-duckdb/
├── zips/          # Raw zip files — tracked in GitHub
├── data/          # Generated CSVs — local only (gitignored)
├── scripts/
│   └── unzip_data.py   # Step 2 pipeline script
└── PIPELINE.md    # This file
```

---

## Future Steps (planned)

- **CSV → Parquet**: Convert CSVs to Parquet for faster querying with Polars/DuckDB
- **Parquet → DuckDB**: Load into DuckDB for KPI analysis
