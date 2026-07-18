#!/usr/bin/env python3
"""Validate the Next.js static export before publishing it."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = ROOT / "apps" / "web" / "out"

SOURCE_CATALOG_PATHS = [
    ROOT / "data" / "catalog" / "official_sources.json",
    ROOT / "data" / "catalog" / "fukuoka_finance_sources.json",
    ROOT / "data" / "catalog" / "fukuoka_city_finance_sources.json",
    ROOT / "data" / "catalog" / "kitakyushu_finance_sources.json",
    ROOT / "data" / "catalog" / "fukuoka_assembly_sources.json",
]

REQUIRED_FILES = [
    "index.html",
    "404.html",
    "about/index.html",
    "assemblies/index.html",
    "assemblies/fukuoka-prefecture/overseas-activities/index.html",
    "compare/index.html",
    "corrections/index.html",
    "data-quality/index.html",
    "executives/index.html",
    "methodology/index.html",
    "municipalities/index.html",
    "municipalities/hokkaido/index.html",
    "municipalities/miyagi/index.html",
    "municipalities/fukuoka-prefecture/index.html",
    "municipalities/fukuoka-city/index.html",
    "municipalities/kitakyushu-city/index.html",
    "sources/index.html",
    "robots.txt",
    "sitemap.xml",
    "manifest.webmanifest",
]

BASE_PAGE_REQUIREMENTS: dict[str, list[str]] = {
    "index.html": [
        "約束・予算・実行・成果を、",
        "全国47都道府県を探す",
        "Reviewed数値目標",
        "公開済み評価",
    ],
    "municipalities/index.html": [
        "全国47都道府県を、同じ品質段階で追う。",
        "公式入口確認済み",
        "現行計画確認済み",
        "Reviewed公開",
        "128目標グループ・149系列",
    ],
    "municipalities/hokkaido/index.html": [
        "北海道の政策指標を、原文と期間から読む。",
        "108 / 108のKPI本文Reviewedを完了",
        "年度別実績は未接続",
        "政策成果の達成率ではなく",
    ],
    "municipalities/miyagi/index.html": [
        "宮城県の政策目標を、原文・期間・未設定までそのまま読む。",
        "人口の社会増減（人）",
        "暮らしの満足度（宮城で暮らして良かったと思う県民の割合）（%）",
        "健康寿命（日常生活に制限のない期間の平均）（男性）（年）",
        "健康寿命（日常生活に制限のない期間の平均）（女性）（年）",
        "目標値の確認と、政策成果の評価を分ける。",
    ],
    "municipalities/fukuoka-prefecture/index.html": [
        "2.3兆円",
        "8,308億円",
        "普通会計",
        "まだ評価していないこと",
    ],
    "municipalities/fukuoka-city/index.html": [
        "1兆1,318億円",
        "4,263億円",
        "形式収支",
        "まだ評価していないこと",
    ],
    "municipalities/kitakyushu-city/index.html": [
        "6,476億8,400万円",
        "1,925億円",
        "市税決算額",
        "まだ評価していないこと",
    ],
    "compare/index.html": [
        "同じ条件の数字だけで見る。",
        "規模の違いを、優劣へ変換しない。",
    ],
    "executives/index.html": [
        "首長評価の前に、任期と公約の根拠を固定する。",
        "現職名と任期が分かっても、実績評価はできない。",
    ],
    "assemblies/index.html": [
        "議会を、質問数ではなく役割と根拠で見る。",
        "総合点や会派ランキングは出しません",
    ],
    "corrections/index.html": [
        "誤りを直せることも、透明性の一部です。",
        "変更履歴を残します",
    ],
    "data-quality/index.html": [
        "件数ではなく、確認の深さを公開する。",
        "Evidence coverage",
        "宮城県Reviewed KPI",
        "宮城県KPI Evidence",
        "データ不足を、点数で埋めません。",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-path",
        default="",
        help="Expected deployment base path, such as /jichi-insight.",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_source_count() -> int:
    return sum(len(load_json(path)["records"]) for path in SOURCE_CATALOG_PATHS)


def miyagi_requirements() -> dict[str, list[str]]:
    manifest = load_json(ROOT / "data/catalog/miyagi_policy_review_manifest.json")
    queue = load_json(ROOT / "data/catalog/wave1_policy_review_queue.json")
    miyagi_queue = next(
        item for item in queue["items"] if item["prefecture_code"] == "04"
    )
    reviewed_groups = manifest["reviewed_target_group_count"]
    reviewed_series = manifest["reviewed_indicator_series_count"]
    remaining_groups = manifest["remaining_target_group_count"]
    remaining_series = manifest["remaining_indicator_series_count"]

    if remaining_groups == 0 and remaining_series == 0:
        municipality_copies = [
            f"宮城県{reviewed_groups}目標のKPI本文を全件公開。次は年度実績との接続。",
            f"宮城県では{reviewed_groups}目標グループ・{reviewed_series}系列を全件Reviewed化しました。",
            f"宮城県の{reviewed_groups}目標を全件公開。年度実績は未接続と明示する。",
            miyagi_queue["next_action"],
        ]
    else:
        municipality_copies = [
            f"宮城県{reviewed_groups}目標を公開。",
            f"先頭{reviewed_groups}グループ・{reviewed_series}系列をReviewed化しました。",
            f"宮城県の{reviewed_groups}目標を公開。未Reviewedの{remaining_groups}目標も明示する。",
            miyagi_queue["next_action"],
        ]

    return {
        "municipalities/index.html": municipality_copies,
        "municipalities/miyagi/index.html": [
            f"公式の目標値No.1〜{reviewed_groups}を本文・数値・単位・期間まで照合済み。",
            f"目標1〜{reviewed_groups}を、政策上の所属と4つの時点から確認する。",
        ],
        "data-quality/index.html": [
            f"Reviewed済み{reviewed_groups}グループすべてにEvidence Packetを付与。",
            f"宮城県は残る{remaining_groups}グループ・{remaining_series}系列をReviewed化中。",
        ],
    }


def normalized_html(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (EXPORT_ROOT / relative_path).is_file():
            failures.append(f"Missing static export file: {relative_path}")

    requirements = {path: list(copies) for path, copies in BASE_PAGE_REQUIREMENTS.items()}
    for path, copies in miyagi_requirements().items():
        requirements.setdefault(path, []).extend(copies)

    for relative_path, copies in requirements.items():
        path = EXPORT_ROOT / relative_path
        if not path.is_file():
            continue
        content = normalized_html(path)
        for copy in copies:
            if copy not in content:
                failures.append(f"{relative_path} is missing required copy: {copy}")

        if relative_path == "index.html" and args.base_path:
            expected_prefix = f"{args.base_path}/_next/"
            if expected_prefix not in content:
                failures.append(
                    "Static export does not contain expected asset prefix: "
                    f"{expected_prefix}"
                )

    sources_path = EXPORT_ROOT / "sources/index.html"
    if sources_path.is_file():
        sources = normalized_html(sources_path)
        if str(catalog_source_count()) not in sources or "公式資料" not in sources:
            failures.append("Sources page does not expose the source catalog summary.")

    if failures:
        print("Static export validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Static export validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
