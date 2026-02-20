# docs/

This folder contains all reference documentation for the project.

---

## Files

### `PIPELINE.md`
Step-by-step guide to run the data pipeline locally.
Covers: zip → csv → parquet conversion with exact commands.

### `DATA_SOURCES.md`
English reference for all 5 datasets.
Covers: source URL, row counts, column groups, file sizes, join examples.

### `초중등교육통계.md`
Korean column-level specification for all 5 datasets.
Covers: every column name, Korean description, and analysis use cases per dataset.
Use this when writing queries — look up which column belongs to which file.

### `시도시군구코드.md`
Administrative region code reference table (시도 + 시군구).
Covers: all 17 시도 and their 시군구 with 2-digit and 5-digit codes.
Use this when filtering data by region or building map visualizations.

---

## Quick Reference

| Question | Go to |
|----------|-------|
| How do I run the pipeline? | `PIPELINE.md` |
| What columns does dataset 0004 have? | `초중등교육통계.md` |
| What is the code for 경기도 수원시? | `시도시군구코드.md` |
| How big are the files? What's the join key? | `DATA_SOURCES.md` |
