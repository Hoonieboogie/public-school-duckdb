"""High-level data loading orchestrator.

Pipeline: API/CSV → Preprocess → Parquet + manifest.

Usage::

    from schooldata.loader import load_from_api, load_from_csv

    load_from_api("0", year=2026)                      # 전국 학교기본정보
    load_from_api("0", year=2026, sido_code="11")      # 서울만
    load_from_csv("0", "path/to/school_basic.csv", year=2023)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from schooldata.api_client import SchoolInfoClient
from schooldata.codes import API_TYPES
from schooldata.config import DUCKDB_PATH, PROJECT_ROOT
from schooldata.preprocess import preprocess

logger = logging.getLogger(__name__)

PARQUET_DIR = PROJECT_ROOT / "data" / "parquet"
MANIFEST_PATH = PROJECT_ROOT / "data" / "manifest.json"


# ── Manifest ───────────────────────────────────────────────────

def _read_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def _write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _update_manifest(api_type: str, year: int, source: str, row_count: int) -> None:
    manifest = _read_manifest()
    label = API_TYPES.get(api_type, api_type)
    manifest.setdefault(label, {})
    manifest[label][str(year)] = {
        "api_type": api_type,
        "source": source,
        "row_count": row_count,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_manifest(manifest)


# ── Parquet output ─────────────────────────────────────────────

def _write_parquet(api_type: str, year: int, df: pd.DataFrame) -> Path:
    label = API_TYPES.get(api_type, api_type)
    safe_label = label.replace("/", "_").replace(" ", "_")
    out_dir = PARQUET_DIR / safe_label
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{year}.parquet"
    df.to_parquet(out_path, index=False, engine="pyarrow")
    logger.info("Written %d rows → %s", len(df), out_path)
    return out_path


# ── API ingestion ──────────────────────────────────────────────

def load_from_api(
    api_type: str,
    *,
    year: int,
    sido_code: str | None = None,
    school_kind: str | None = None,
    api_key: str | None = None,
) -> Path:
    """Fetch from 학교알리미 API → preprocess → write Parquet.

    Returns the output Parquet file path.
    """
    label = API_TYPES.get(api_type, api_type)
    logger.info("=== API Ingest [%s] %s, year=%d ===", api_type, label, year)

    with SchoolInfoClient(api_key=api_key) as client:
        if sido_code:
            rows = client.fetch(api_type, sido_code=sido_code, school_kind=school_kind)
        else:
            rows = client.fetch_all_regions(api_type, school_kind=school_kind)

    df = preprocess(api_type, rows, year=year)
    out_path = _write_parquet(api_type, year, df)
    _update_manifest(api_type, year, "api", len(df))

    logger.info("=== Done [%s] %s ===", api_type, label)
    return out_path


# ── CSV ingestion ──────────────────────────────────────────────

def load_from_csv(
    api_type: str,
    csv_path: str | Path,
    *,
    year: int,
    encoding: str = "utf-8",
) -> Path:
    """Read a legacy CSV → preprocess → write Parquet.

    Returns the output Parquet file path.
    """
    label = API_TYPES.get(api_type, api_type)
    logger.info("=== CSV Ingest [%s] %s, year=%d, file=%s ===", api_type, label, year, csv_path)

    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    # Try utf-8 first, fall back to cp949 (common for Korean government CSVs)
    try:
        df_raw = pd.read_csv(csv_path, encoding=encoding, dtype=str)
    except UnicodeDecodeError:
        logger.info("UTF-8 failed, retrying with cp949 encoding")
        df_raw = pd.read_csv(csv_path, encoding="cp949", dtype=str)

    df = preprocess(api_type, df_raw, year=year)
    out_path = _write_parquet(api_type, year, df)
    _update_manifest(api_type, year, "csv", len(df))

    logger.info("=== Done [%s] %s ===", api_type, label)
    return out_path


# ── Status ─────────────────────────────────────────────────────

def show_manifest() -> None:
    """Print the current manifest."""
    manifest = _read_manifest()
    if not manifest:
        print("No data loaded yet.")
        return
    for label, years in sorted(manifest.items()):
        print(f"\n{label}:")
        for yr, info in sorted(years.items()):
            print(f"  {yr}: {info['source']}  ({info['row_count']} rows, {info['ingested_at'][:10]})")
