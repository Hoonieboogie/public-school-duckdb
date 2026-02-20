"""CLI entry point for data loading.

Usage::

    # Load from API
    python -m schooldata.cli api -t 0 --year 2026
    python -m schooldata.cli api -t 0 --year 2026 --sido 11

    # Load from CSV
    python -m schooldata.cli csv -t 0 --year 2021 --file path/to/data.csv

    # Show loaded datasets
    python -m schooldata.cli status

    # List available API types and codes
    python -m schooldata.cli list
"""

from __future__ import annotations

import argparse
import logging
import sys

from schooldata.codes import API_TYPES, SIDO_CODES
from schooldata.loader import load_from_api, load_from_csv, show_manifest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="학교알리미 Open API / CSV → Parquet pipeline",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    sub = parser.add_subparsers(dest="command")

    # ── api subcommand ─────────────────────────────────────────
    p_api = sub.add_parser("api", help="Fetch from 학교알리미 API → Parquet")
    p_api.add_argument("-t", "--api-type", required=True, help="API type code (e.g. 0)")
    p_api.add_argument("--year", type=int, required=True, help="Data year (e.g. 2026)")
    p_api.add_argument("-s", "--sido", help="시도코드 (omit for all regions)")
    p_api.add_argument("-k", "--school-kind", help="학교급구분코드")
    p_api.add_argument("--api-key", help="Override API key")

    # ── csv subcommand ─────────────────────────────────────────
    p_csv = sub.add_parser("csv", help="Load legacy CSV → Parquet")
    p_csv.add_argument("-t", "--api-type", required=True, help="API type code (e.g. 0)")
    p_csv.add_argument("--year", type=int, required=True, help="Data year (e.g. 2021)")
    p_csv.add_argument("-f", "--file", required=True, help="Path to CSV file")
    p_csv.add_argument("--encoding", default="utf-8", help="CSV encoding (default: utf-8)")

    # ── status subcommand ──────────────────────────────────────
    sub.add_parser("status", help="Show loaded datasets from manifest")

    # ── list subcommand ────────────────────────────────────────
    sub.add_parser("list", help="List available API types and 시도코드")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.command == "list":
        print("\n=== API Types ===")
        for code, name in sorted(API_TYPES.items(), key=lambda x: int(x[0])):
            print(f"  {code:>3s}  {name}")
        print("\n=== 시도코드 ===")
        for code, name in sorted(SIDO_CODES.items()):
            print(f"  {code}  {name}")

    elif args.command == "api":
        path = load_from_api(
            args.api_type,
            year=args.year,
            sido_code=args.sido,
            school_kind=args.school_kind,
            api_key=args.api_key,
        )
        print(f"\n✓ Written → {path}")
        show_manifest()

    elif args.command == "csv":
        path = load_from_csv(
            args.api_type,
            args.file,
            year=args.year,
            encoding=args.encoding,
        )
        print(f"\n✓ Written → {path}")
        show_manifest()

    elif args.command == "status":
        show_manifest()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
