"""DuckDB connection manager — reads from Parquet files.

DuckDB serves as the query engine over Parquet, not as a storage layer.

Usage::

    from schooldata.db import get_connection, query, list_datasets

    con = get_connection()
    df = query(con, "학교기본정보", "SELECT * FROM data WHERE SCHUL_KND_SC_NM = '초등학교'")
    list_datasets(con)
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from schooldata.config import PROJECT_ROOT

logger = logging.getLogger(__name__)

PARQUET_DIR = PROJECT_ROOT / "data" / "parquet"


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return an in-memory DuckDB connection for querying Parquet files."""
    return duckdb.connect(":memory:")


def _parquet_glob(dataset: str, year: int | None = None) -> str:
    """Build a glob path for read_parquet()."""
    safe = dataset.replace("/", "_").replace(" ", "_")
    base = PARQUET_DIR / safe
    if year:
        return str(base / f"{year}.parquet")
    return str(base / "*.parquet")


def query(
    con: duckdb.DuckDBPyConnection,
    dataset: str,
    sql: str,
    *,
    year: int | None = None,
) -> duckdb.DuckDBPyRelation:
    """Run a SQL query against a Parquet-backed dataset.

    The Parquet files are exposed as a table named ``data`` within the query.

    Parameters
    ----------
    con : DuckDBPyConnection
    dataset : str
        Dataset name matching the Parquet subdirectory (e.g. "학교기본정보").
    sql : str
        SQL query. Reference the data as ``data`` table.
        Example: "SELECT * FROM data WHERE LCTN_SC_NM = '서울특별시'"
    year : int, optional
        Restrict to a single year's Parquet file.

    Example::

        con = get_connection()
        result = query(con, "학교기본정보", "SELECT * FROM data LIMIT 5")
        print(result.df())
    """
    glob = _parquet_glob(dataset, year)
    full_sql = f"WITH data AS (SELECT * FROM read_parquet('{glob}', filename=true)) {sql}"
    return con.sql(full_sql)


def query_all(
    con: duckdb.DuckDBPyConnection,
    datasets: list[str],
    sql: str,
) -> duckdb.DuckDBPyRelation:
    """Run a SQL query joining multiple datasets.

    Each dataset is registered as a CTE named by its sanitized label.

    Example::

        result = query_all(con, ["학교기본정보", "입학생_현황"],
            \"\"\"SELECT a.SCHUL_CODE, a.SCHUL_NM, b.BEAGE_BOY_FGR
               FROM 학교기본정보 a JOIN 입학생_현황 b USING (SCHUL_CODE)\"\"\")
    """
    ctes = []
    for ds in datasets:
        glob = _parquet_glob(ds)
        safe = ds.replace("/", "_").replace(" ", "_")
        ctes.append(f"{safe} AS (SELECT * FROM read_parquet('{glob}', filename=true))")
    full_sql = f"WITH {', '.join(ctes)} {sql}"
    return con.sql(full_sql)


def list_datasets(con: duckdb.DuckDBPyConnection | None = None) -> list[dict]:
    """List available Parquet datasets with row counts per year."""
    results = []
    if not PARQUET_DIR.exists():
        return results

    for ds_dir in sorted(PARQUET_DIR.iterdir()):
        if not ds_dir.is_dir():
            continue
        files = sorted(ds_dir.glob("*.parquet"))
        years = [f.stem for f in files]
        total_rows = 0
        for f in files:
            try:
                c = duckdb.connect(":memory:")
                count = c.sql(f"SELECT COUNT(*) FROM read_parquet('{f}')").fetchone()[0]
                total_rows += count
                c.close()
            except Exception:
                pass
        results.append({
            "dataset": ds_dir.name,
            "years": years,
            "total_rows": total_rows,
        })
    return results
