"""HTTP client for the 학교알리미 Open API.

Usage::

    from schooldata.api_client import SchoolInfoClient

    client = SchoolInfoClient(api_key="YOUR_KEY")
    rows = client.fetch("0", sido_code="11")        # 서울 학교기본정보
    rows = client.fetch_all_regions("0")             # 전국 학교기본정보
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from schooldata.codes import SIDO_CODES, SCHOOL_KIND_CODES
from schooldata.config import API_KEY, BASE_URL

logger = logging.getLogger(__name__)


class SchoolInfoClient:
    """Thin wrapper around the 학교알리미 REST API."""

    def __init__(self, api_key: str | None = None, timeout: float = 30.0):
        self.api_key = api_key or API_KEY
        if not self.api_key:
            raise ValueError(
                "API key is required. Set SCHOOLINFO_API_KEY in .env "
                "or pass api_key= to the constructor."
            )
        self._client = httpx.Client(timeout=timeout)

    # ── core fetch ─────────────────────────────────────────────
    def fetch(
        self,
        api_type: str,
        *,
        sido_code: str | None = None,
        sgg_code: str | None = None,
        school_kind: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch a single API page and return the list of records."""
        params: dict[str, str] = {
            "apiKey": self.api_key,
            "apiType": api_type,
        }
        if sido_code:
            params["sidoCode"] = sido_code
        if sgg_code:
            params["sggCode"] = sgg_code
        if school_kind:
            params["schulKndCode"] = school_kind

        resp = self._client.get(BASE_URL, params=params)
        resp.raise_for_status()
        body = resp.json()

        if body.get("resultCode") != "success":
            msg = body.get("resultMsg", "unknown error")
            logger.warning("API returned non-success: %s (params=%s)", msg, params)
            return []

        return body.get("list", [])

    # ── bulk helpers ───────────────────────────────────────────
    def fetch_all_regions(
        self,
        api_type: str,
        *,
        school_kind: str | None = None,
        delay: float = 0.3,
    ) -> list[dict[str, Any]]:
        """Iterate over all 시도 codes and collect rows.

        A short *delay* between calls avoids hammering the server.
        """
        all_rows: list[dict[str, Any]] = []
        for sido_code, sido_name in SIDO_CODES.items():
            logger.info("Fetching apiType=%s  sido=%s (%s)", api_type, sido_code, sido_name)
            rows = self.fetch(api_type, sido_code=sido_code, school_kind=school_kind)
            all_rows.extend(rows)
            logger.info("  → %d rows", len(rows))
            if delay > 0:
                time.sleep(delay)
        logger.info("Total rows for apiType=%s: %d", api_type, len(all_rows))
        return all_rows

    def fetch_all_school_kinds(
        self,
        api_type: str,
        *,
        sido_code: str | None = None,
        delay: float = 0.3,
    ) -> list[dict[str, Any]]:
        """Iterate over all school-kind codes for a given region."""
        all_rows: list[dict[str, Any]] = []
        for kind_code, kind_name in SCHOOL_KIND_CODES.items():
            logger.info("Fetching apiType=%s  schulKnd=%s (%s)", api_type, kind_code, kind_name)
            rows = self.fetch(api_type, sido_code=sido_code, school_kind=kind_code)
            all_rows.extend(rows)
            logger.info("  → %d rows", len(rows))
            if delay > 0:
                time.sleep(delay)
        return all_rows

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SchoolInfoClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
