#!/usr/bin/env python3
"""Validate the Next.js static export before publishing it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "apps" / "web" / "out"

SOURCE_CATALOG_PATHS = [
    ROOT / "data" / "catalog" / "official_sources.json",
    ROOT / "data" / "catalog" / "fukuoka_finance_sources.json",
]

REQUIRED_FILES = [
    "index.html",
    "404.html",
    "about/index.html",
    "methodology/index.html",
    "municipalities/index.html",
    "municipalities/fukuoka-prefecture/index.html",
    "sources/index.html",
    "robots.txt",
    "sitemap.xml",
    "manifest.webmanifest",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-path",
        default="",
        help="Expected deployment base path, such as /jichi-insight.",
    )
    return parser.parse_args()


def catalog_source_count() -> int:
    total = 0
    for path in SOURCE_CATALOG_PATHS:
        with path.open(encoding="utf-8") as handle:
            total += len(json.load(handle)["records"])
    return total


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = EXPORT_ROOT / relative_path
        if not path.is_file():
            failures.append(f"Missing static export file: {relative_path}")

    index_path = EXPORT_ROOT / "index.html"
    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        required_copy = [
            "約束・予算・実行・成果を、",
            "公式資料の整備状況を見る",
            "公開済み評価",
        ]
        for copy in required_copy:
            if copy not in index:
                failures.append(f"Home page is missing required copy: {copy}")

        if args.base_path:
            expected_asset_prefix = f"{args.base_path}/_next/"
            if expected_asset_prefix not in index:
                failures.append(
                    "Static export does not contain the expected base-path asset prefix: "
                    f"{expected_asset_prefix}"
                )

    sources_path = EXPORT_ROOT / "sources" / "index.html"
    if sources_path.is_file():
        sources = sources_path.read_text(encoding="utf-8")
        expected_count = str(catalog_source_count())
        if expected_count not in sources or "公式資料" not in sources:
            failures.append(
                "Sources page does not expose the current source catalog summary."
            )

    fukuoka_path = EXPORT_ROOT / "municipalities" / "fukuoka-prefecture" / "index.html"
    if fukuoka_path.is_file():
        fukuoka = fukuoka_path.read_text(encoding="utf-8")
        required_fukuoka_copy = [
            "2.3兆円",
            "8,308億円",
            "5年間の「実績」",
            "2兆937億円",
            "2020年度",
            "2024年度",
            "普通会計",
            "まだ評価していないこと",
            "PDFの2ページ目",
        ]
        for copy in required_fukuoka_copy:
            if copy not in fukuoka:
                failures.append(f"Fukuoka page is missing required copy: {copy}")

    if failures:
        print("Static export validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Static export validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
