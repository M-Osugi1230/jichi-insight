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
    "municipalities/tokyo/index.html",
    "municipalities/aichi/index.html",
    "municipalities/osaka/index.html",
    "municipalities/hiroshima/index.html",
    "municipalities/kagawa/index.html",
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
        "全国47都道府県から探す",
        "440件の実績推移を公開",
        "資料ではなく、判断の順番でつなぐ。",
        "Jichi Insight評価",
    ],
    "municipalities/index.html": [
        "47都道府県を、資料の深さから探す。",
        "全国の入口整備",
        "PHASE 7 DATA GATE",
        "いま、深く読める8都道府県。",
        "東京都の政策目標を見る",
        "愛知県の進捗指標を見る",
        "大阪府の政策指標を見る",
        "広島県の成果指標を見る",
        "香川県の計画指標を見る",
        "確認したい資料の深さ",
        "都道府県と、確認できる資料。",
        "政策計画",
        "実施計画",
        "KPI・数値目標",
        "年度評価",
        "予算・決算",
        "事業評価",
    ],
    "municipalities/hokkaido/index.html": [
        "北海道の政策指標を、原文と期間から読む。",
        "108 / 108のKPI本文Reviewedを完了",
        "年度別実績は未接続",
        "政策成果の達成率ではなく",
    ],
    "municipalities/miyagi/index.html": [
        "目標と実績を、同じものにしない。",
        "2つの目標を、混ぜない。",
        "年度実績を、指標ごとに確かめる。",
        "人口の社会増減（人）",
        "暮らしの満足度（宮城で暮らして良かったと思う県民の割合）（%）",
        "健康寿命（日常生活に制限のない期間の平均）（男性）（年）",
        "健康寿命（日常生活に制限のない期間の平均）（女性）（年）",
        "ここから先は、まだ評価しない。",
    ],
    "municipalities/tokyo/index.html": [
        "東京都の政策目標を、値と条件を変えずに読む。",
        "304目標カード",
        "60 / 60ページの政策目標カードReviewedを完了。",
        "25政策分野・304目標カードを横断検索。",
        "子供分野以外のグラフ点列は未正規化",
        "年度実績 未接続",
        "政策評価 未判定",
        "子供分野は、グラフ点列まで詳細Reviewed。",
        "取り決め有りと全体は母集団が異なる",
    ],
    "municipalities/aichi/index.html": [
        "愛知県の目標と年次現状値を、定義を変えずに読む。",
        "56指標",
        "62系列",
        "現状値接続",
        "再掲",
        "目標改定",
        "管理事業評価",
        "政策評価 未判定",
        "56指標を、政策方向・値・年度から探す。",
    ],
    "municipalities/osaka/index.html": [
        "大阪府の戦略目標とWell-Beingを、同じ点数にしない。",
        "83指標",
        "91系列",
        "名目GDP80兆円",
        "客観KPI",
        "主観・Well-Being",
        "初回調査待ち",
        "旧戦略の実績",
        "政策評価 未判定",
        "83指標を、レイヤー・分野・値から探す。",
    ],
    "municipalities/hiroshima/index.html": [
        "広島県の62指標を、改定後の定義と目標から読む。",
        "Reviewed指標",
        "現状値あり",
        "Evidence ID",
        "改定、未測定、定性目標を同じ数値にしない。",
        "62指標を、分野・値・年度・出典から探す。",
        "政策評価 未判定",
    ],
    "municipalities/kagawa/index.html": [
        "香川県の135指標を、延長前と延長後の目標から読む。",
        "Reviewed指標",
        "掲載位置",
        "目標更新",
        "計画延長を、単なる年度の置換にしない。",
        "135指標を、名称・値・変更状態から探す。",
        "政策評価 未判定",
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


def nationwide_requirements() -> dict[str, list[str]]:
    coverage = load_json(ROOT / "data/catalog/prefecture_coverage.json")
    published = load_json(ROOT / "data/catalog/published_prefecture_pages.json")
    required_files = {
        f"{record['route'].strip('/')}/index.html" for record in published["records"]
    }
    missing_required_files = required_files - set(REQUIRED_FILES)
    if missing_required_files:
        raise ValueError(
            "Published prefecture routes are missing from REQUIRED_FILES: "
            + ", ".join(sorted(missing_required_files))
        )

    return {
        "municipalities/index.html": [
            *(record["name"] for record in coverage["records"]),
            "自治体ページ公開中",
            "公開状態",
        ]
    }


def miyagi_requirements() -> dict[str, list[str]]:
    manifest = load_json(ROOT / "data/catalog/miyagi_policy_review_manifest.json")
    reviewed_groups = manifest["reviewed_target_group_count"]
    reviewed_series = manifest["reviewed_indicator_series_count"]
    linked_series = manifest["actual_linked_indicator_series_count"]
    review_needed_series = manifest["actual_linkage_review_needed_series_count"]
    annual_rows = manifest["actual_result_row_count"]
    remaining_groups = manifest["remaining_target_group_count"]
    remaining_series = manifest["remaining_indicator_series_count"]

    if remaining_groups == 0 and remaining_series == 0:
        municipality_copies = [
            f"{reviewed_groups}目標",
            f"{linked_series}系列",
            f"{review_needed_series}系列",
            f"{annual_rows}行",
        ]
    else:
        municipality_copies = [
            f"宮城県{reviewed_groups}目標を公開。",
            f"先頭{reviewed_groups}グループ・{reviewed_series}系列をReviewed化しました。",
            (
                f"宮城県の{reviewed_groups}目標を公開。"
                f"未Reviewedの{remaining_groups}目標も明示する。"
            ),
        ]

    return {
        "municipalities/index.html": municipality_copies,
        "municipalities/miyagi/index.html": [
            f"全{reviewed_groups}目標",
            f"{annual_rows}件の実績",
            f"現行計画の全{reviewed_groups}目標。",
        ],
        "data-quality/index.html": [
            f"Reviewed済み{reviewed_groups}グループすべてにEvidence Packetを付与。",
            f"柱1〜4・取組1〜18の全{reviewed_series}系列を一次資料と照合。",
            f"直接接続{linked_series}、要確認{review_needed_series}。",
            f"{annual_rows}",
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

    requirements = {
        path: list(copies) for path, copies in BASE_PAGE_REQUIREMENTS.items()
    }
    for dynamic_requirements in (nationwide_requirements(), miyagi_requirements()):
        for path, copies in dynamic_requirements.items():
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
