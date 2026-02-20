"""Configuration loaded from environment / .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # src/schooldata/ → src/ → project root

load_dotenv(PROJECT_ROOT / ".env")

API_KEY: str = os.getenv("SCHOOLINFO_API_KEY", "")
DUCKDB_PATH: Path = Path(os.getenv("DUCKDB_PATH", PROJECT_ROOT / "data" / "school.duckdb"))
BASE_URL: str = "https://www.schoolinfo.go.kr/openApi.do"
