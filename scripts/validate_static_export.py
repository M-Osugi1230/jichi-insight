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

PAGE_REQUIREMENTS: dict[str, tuple[str, list[str]]] = {
    "index.html": (
        "Home page",
        [
            "約束・予算・実行・成果を、",
            "全国47都道府県を探す",
            "全国版を構築中",
            "Reviewed数値目標",
            "公開済み評価",
        ],
    ),
    "municipalities/index.html": (
        "Nationwide coverage page",
        [
            "全国47都道府県を、同じ品質段階で追う。",
            "都道府県・計画名から探す",
            "公式入口確認済み",
            "現行計画確認済み",
            "Reviewed公開",
            "都道府県を表示",
            "KPI位置確認済み・本文レビュー中",
            "128目標グループ・149系列",
            "次は柱3の目標69〜71",
        ],
    ),
    "municipalities/fukuoka-prefecture/index.html": (
        "Fukuoka Prefecture page",
        [
            "2.3兆円",
            "8,308億円",
            "5年間の「実績」",
            "2020–2024 ordinary-account settlement",
            "普通会計",
            "まだ評価していないこと",
        ],
    ),
    "municipalities/hokkaido/index.html": (
        "Hokkaido policy indicator page",
        [
            "北海道の政策指標を、原文と期間から読む。",
            "108 / 108のKPI本文Reviewedを完了",
            "指標名・政策分野から探す",
            "比較上の注意あり",
            "年度別実績は未接続",
            "政策成果の達成率ではなく",
        ],
    ),
    "municipalities/miyagi/index.html": (
        "Miyagi policy target page",
        [
            "宮城県の政策目標を、原文・期間・未設定までそのまま読む。",
            "公式の目標値No.1〜68を本文・数値・単位・期間まで照合済み。",
            "目標1〜68を、政策上の所属と4つの時点から確認する。",
            "全国平均正答率とのかい離（小学6年生）（ポイント）",
            "不登校児童生徒のうち学習支援を受けている児童生徒の割合",
            "目標値の確認と、政策成果の評価を分ける。",
        ],
    ),
    "municipalities/fukuoka-city/index.html": (
        "Fukuoka City page",
        [
            "1兆1,318億円",
            "4,263億円",
            "2024 general-account settlement",
            "形式収支",
            "まだ評価していないこと",
        ],
    ),
    "municipalities/kitakyushu-city/index.html": (
        "Kitakyushu City page",
        [
            "6,476億8,400万円",
            "1,925億円",
            "2024 general-account settlement",
            "619,800,427,000円",
            "市税決算額",
            "単純差額",
            "まだ評価していないこと",
        ],
    ),
    "compare/index.html": (
        "City comparison page",
        [
            "同じ条件の数字だけで見る。",
            "比較できる範囲を先に固定する。",
            "確認済みの同条件4指標",
            "規模の違いを、優劣へ変換しない。",
            "人口・行政需要・面積・産業構造を補正する前に優劣を付けない",
        ],
    ),
    "executives/index.html": (
        "Executive registry page",
        [
            "首長評価の前に、任期と公約の根拠を固定する。",
            "服部 誠太郎",
            "高島 宗一郎",
            "武内 和久",
            "公約原文の登録",
            "現職名と任期が分かっても、実績評価はできない。",
        ],
    ),
    "assemblies/index.html": (
        "Assemblies page",
        [
            "議会を、質問数ではなく役割と根拠で見る。",
            "福岡県議会の海外活動",
            "海外活動台帳を見る",
            "総合点や会派ランキングは出しません",
        ],
    ),
    "assemblies/fukuoka-prefecture/overseas-activities/index.html": (
        "Overseas activities page",
        [
            "海外活動の公開状況",
            "「活動があった」と「説明できる」を分ける。",
            "福岡県議会・ハワイ州議会友好訪問団",
            "福岡県議会・バンコク都議会友好訪問団",
            "費用を確認できず",
            "報告書未掲載",
            "契約手続きは、見直し方針と実施結果を分けて追う。",
            "海外活動の総合点は出しません",
        ],
    ),
    "corrections/index.html": (
        "Corrections page",
        [
            "誤りを直せることも、透明性の一部です。",
            "訂正申請を開く",
            "変更履歴を残します",
        ],
    ),
    "data-quality/index.html": (
        "Data quality page",
        [
            "件数ではなく、確認の深さを公開する。",
            "Evidence coverage",
            "Reviewed財政値に対応するEvidence Packetの割合。",
            "宮城県KPI位置",
            "目標グループ。個別系列は149件、掲載5ページ。",
            "宮城県複数系列",
            "追加系列21件。位置は確認済み、本文はReviewed化中。",
            "柱1〜2・取組1〜9の系列85件を一次資料と照合。",
            "Reviewed済み68グループすべてにEvidence Packetを付与。",
            "データ不足を、点数で埋めません。",
        ],
    ),
}


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
    normalized_content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    return [
        f"{label} is missing required copy: {copy}"
        for copy in copies
        if copy not in normalized_content
    ]


def main() -> int:
    args = parse_args()
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (EXPORT_ROOT / relative_path).is_file():
            failures.append(f"Missing static export file: {relative_path}")

    for relative_path, (label, copies) in PAGE_REQUIREMENTS.items():
        path = EXPORT_ROOT / relative_path
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            failures.extend(require_copy(content, copies, label))
            if relative_path == "index.html" and args.base_path:
                expected_asset_prefix = f"{args.base_path}/_next/"
                if expected_asset_prefix not in content:
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

    if failures:
        print("Static export validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Static export validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
