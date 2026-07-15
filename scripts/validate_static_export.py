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
    ROOT / "data" / "catalog" / "fukuoka_city_finance_sources.json",
    ROOT / "data" / "catalog" / "kitakyushu_finance_sources.json",
]

REQUIRED_FILES = [
    "index.html",
    "404.html",
    "about/index.html",
    "corrections/index.html",
    "data-quality/index.html",
    "methodology/index.html",
    "municipalities/index.html",
    "municipalities/fukuoka-prefecture/index.html",
    "municipalities/fukuoka-city/index.html",
    "municipalities/kitakyushu-city/index.html",
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


def require_copy(content: str, copies: list[str], label: str) -> list[str]:
    return [
        f"{label} is missing required copy: {copy}"
        for copy in copies
        if copy not in content
    ]


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
        failures.extend(
            require_copy(
                index,
                [
                    "約束・予算・実行・成果を、",
                    "公式資料の整備状況を見る",
                    "公開済み評価",
                ],
                "Home page",
            )
        )
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

    prefecture_path = (
        EXPORT_ROOT / "municipalities" / "fukuoka-prefecture" / "index.html"
    )
    if prefecture_path.is_file():
        failures.extend(
            require_copy(
                prefecture_path.read_text(encoding="utf-8"),
                [
                    "2.3兆円",
                    "8,308億円",
                    "5年間の「実績」",
                    "2020–2024 ordinary-account settlement",
                    "2兆937億円",
                    "普通会計",
                    "まだ評価していないこと",
                ],
                "Fukuoka Prefecture page",
            )
        )

    city_path = EXPORT_ROOT / "municipalities" / "fukuoka-city" / "index.html"
    if city_path.is_file():
        failures.extend(
            require_copy(
                city_path.read_text(encoding="utf-8"),
                [
                    "1兆1,318億円",
                    "4,263億円",
                    "2024 general-account settlement",
                    "1兆1,262億8,633万円",
                    "形式収支",
                    "まだ評価していないこと",
                ],
                "Fukuoka City page",
            )
        )

    kitakyushu_path = (
        EXPORT_ROOT / "municipalities" / "kitakyushu-city" / "index.html"
    )
    if kitakyushu_path.is_file():
        failures.extend(
            require_copy(
                kitakyushu_path.read_text(encoding="utf-8"),
                [
                    "6,476億8,400万円",
                    "1,925億円",
                    "2024 general-account settlement",
                    "619,800,427,000円",
                    "市税決算額",
                    "単純差額",
                    "まだ評価していないこと",
                ],
                "Kitakyushu City page",
            )
        )

    corrections_path = EXPORT_ROOT / "corrections" / "index.html"
    if corrections_path.is_file():
        failures.extend(
            require_copy(
                corrections_path.read_text(encoding="utf-8"),
                [
                    "誤りを直せることも、透明性の一部です。",
                    "訂正申請を開く",
                    "変更履歴を残します",
                ],
                "Corrections page",
            )
        )

    quality_path = EXPORT_ROOT / "data-quality" / "index.html"
    if quality_path.is_file():
        failures.extend(
            require_copy(
                quality_path.read_text(encoding="utf-8"),
                [
                    "件数ではなく、確認の深さを公開する。",
                    "Evidence coverage",
                    "Reviewed財政値に対応するEvidence Packetの割合。",
                    "データ不足を、点数で埋めません。",
                ],
                "Data quality page",
            )
        )

    if failures:
        print("Static export validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Static export validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
