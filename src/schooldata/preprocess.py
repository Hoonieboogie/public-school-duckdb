"""Preprocessing layer: normalize, clean, and type-cast raw data.

Handles both API JSON records and legacy CSV DataFrames, producing
a unified schema per API type ready for Parquet output.

Usage::

    from schooldata.preprocess import preprocess

    df = preprocess("0", raw_records)   # API JSON list[dict]
    df = preprocess("0", csv_df)        # CSV DataFrame
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# ── Column mappings: CSV Korean headers → API field names ──────
# Extend these as you encounter new CSV formats.
_CSV_COLUMN_MAP: dict[str, dict[str, str]] = {
    "0": {  # 학교기본정보
        "학교코드": "SCHUL_CODE",
        "학교명": "SCHUL_NM",
        "시도코드": "LCTN_SC_CODE",
        "시도명": "LCTN_SC_NM",
        "주소": "ADRES_NM",
        "우편번호": "ZIP_CODE",
        "학교급코드": "SCHUL_KND_SC_CODE",
        "학교급": "SCHUL_KND_SC_NM",
        "설립구분": "FOND_SC_NM",
        "남녀공학구분": "COEDU_SC_NM",
        "전화번호": "USER_TELNO_SM",
        "홈페이지": "HMPG_ADRES",
        "설립일": "FOND_YMD",
    },
    "11": {  # 입학생 현황
        "학교코드": "SCHUL_CODE",
        "학교명": "SCHUL_NM",
        "남자입학생수": "BEAGE_BOY_FGR",
        "여자입학생수": "BEAGE_GIR_FGR",
    },
}

# ── Numeric columns per API type ──────────────────────────────
_NUMERIC_COLS: dict[str, list[str]] = {
    "0": [],
    "11": ["BEAGE_BOY_FGR", "BEAGE_GIR_FGR"],
    "2": ["COL_1", "COL_2", "COL_3"],
    "4": [],
    "5": [],
    "9": ["ITRT_TCR_TOT_FGR"],
    "13": [],
    "19": ["ASL_PTPT_STDNT_FGR"],
    "20": ["COL_4", "COL_5"],
    "22": [],
    "17": ["COM_CCCLA_FGR", "MMA_CCCLA_FGR"],
    "30": [],
}


def preprocess(
    api_type: str,
    data: list[dict[str, Any]] | pd.DataFrame,
    *,
    year: int | None = None,
) -> pd.DataFrame:
    """Normalize raw data into a clean DataFrame.

    Parameters
    ----------
    api_type : str
        API type code (e.g. "0" for 학교기본정보).
    data : list[dict] or DataFrame
        Raw API JSON records or a CSV-loaded DataFrame.
    year : int, optional
        Data year. If provided, added as a column for partitioning.

    Returns
    -------
    pd.DataFrame
        Cleaned, schema-normalized DataFrame.
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    if df.empty:
        logger.warning("Empty data for api_type=%s, year=%s", api_type, year)
        return df

    # 1) Rename CSV Korean headers → API field names
    col_map = _CSV_COLUMN_MAP.get(api_type, {})
    if col_map:
        reverse_map = {v: v for v in col_map.values()}  # keep API names as-is
        csv_rename = {k: v for k, v in col_map.items() if k in df.columns}
        if csv_rename:
            logger.info("Renaming CSV columns: %s", csv_rename)
            df = df.rename(columns=csv_rename)

    # 2) Strip whitespace from string columns
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    # 3) Cast numeric columns
    for col in _NUMERIC_COLS.get(api_type, []):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4) Deduplicate
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        logger.info("Dropped %d duplicate rows", dropped)

    # 5) Replace common null markers
    df = df.replace({"": None, "nan": None, "NaN": None, "None": None, "-": None})

    # 6) Add year column
    if year is not None:
        df["data_year"] = year

    logger.info(
        "Preprocessed api_type=%s: %d rows, %d columns",
        api_type, len(df), len(df.columns),
    )
    return df
