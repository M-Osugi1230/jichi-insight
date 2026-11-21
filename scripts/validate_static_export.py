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
    ROOT / "data" / "catalog" / "hokkaido_prefecture_finance_sources.json",
    ROOT / "data" / "catalog" / "kanagawa_prefecture_finance_sources.json",
    ROOT / "data" / "catalog" / "saitama_prefecture_finance_sources.json",
    ROOT / "data" / "catalog" / "chiba_prefecture_finance_sources.json",
    ROOT / "data" / "catalog" / "hyogo_prefecture_finance_sources.json",
    ROOT / "data" / "catalog" / "aichi_prefecture_finance_sources.json",
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
    "assemblies/aichi-prefecture/index.html",
    "assemblies/nagoya-city/index.html",
    "assemblies/toyota-city/index.html",
    "assemblies/kanagawa-prefecture/index.html",
    "assemblies/yokohama-city/index.html",
    "assemblies/kawasaki-city/index.html",
    "assemblies/saitama-prefecture/index.html",
    "assemblies/saitama-city/index.html",
    "assemblies/kawaguchi-city/index.html",
    "compare/index.html",
    "corrections/index.html",
    "data-quality/index.html",
    "executives/index.html",
    "methodology/index.html",
    "municipalities/index.html",
    "municipalities/phase9/index.html",
    "municipalities/hokkaido/index.html",
    "municipalities/hokkaido-prefecture/index.html",
    "projects/index.html",
    "municipalities/miyagi/index.html",
    "municipalities/tokyo/index.html",
    "municipalities/aichi/index.html",
    "municipalities/aichi-prefecture/index.html",
    "municipalities/kanagawa-prefecture/index.html",
    "municipalities/saitama-prefecture/index.html",
    "municipalities/osaka/index.html",
    "municipalities/hiroshima/index.html",
    "municipalities/kagawa/index.html",
    "municipalities/okinawa/index.html",
    "municipalities/fukuoka-prefecture/index.html",
    "municipalities/fukuoka-city/index.html",
    "municipalities/kitakyushu-city/index.html",
    "sources/index.html",
    "review-progress/index.html",
    "robots.txt",
    "sitemap.xml",
    "manifest.webmanifest",
]

BASE_PAGE_REQUIREMENTS: dict[str, list[str]] = {
    "index.html": [
        "自治体を検索",
        "508件の実績推移を公開",
        "資料ではなく、判断の順番でつなぐ。",
        "政策達成評価",
    ],
    "municipalities/index.html": [
        "あなたのまちの情報を探す。",
        "PHASE 9 COMPLETE",
        "目標・指標レコード",
        "Evidence Packet",
        "読みたいデータの深さ",
        "都道府県名・地域から探す。",
        "目標",
        "実績",
        "予算",
        "事業",
        "契約",
        "根拠を読む",
        "公式計画",
    ],
    "municipalities/phase9/index.html": [
        "38県の数値目標を、原文とEvidenceから読む。",
        "Evidence coverage",
        "比較不能を保持",
        "政策評価は未判定",
    ],
    "municipalities/hokkaido/index.html": [
        "北海道の政策指標を、原文と期間から読む。",
        "108 / 108のKPI本文Reviewedを完了",
        "年度別実績は未接続",
        "政策成果の達成率ではなく",
    ],
    "municipalities/hokkaido-prefecture/index.html": [
        "北海道総合計画の計画レビュー",
        "2026年度に成立した一般会計当初予算",
        "3年度の財政実績（普通会計）",
        "2026年3月19日に原案可決",
        "鈴木 直道",
        "Reviewed 公約原文：15件",
        "北海道議会の議案・表決・政務活動費・情報公開状況は段階4で登録済み",
        "重点事業は段階2で10系列の Reviewed レコードを登録済み",
        "基本評価調書の「予算額」",
        "決算額ではありません",
        "北海道の重点施策の予算・KPI・道の公式評価",
        "北海道の一次政策評価・総合判定",
        "まだ登録・評価していないこと",
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
    "municipalities/aichi-prefecture/index.html": [
        "あいちビジョン2030",
        "2026年度に成立した一般会計当初予算",
        "3年度の財政実績（普通会計）",
        "大村 秀章",
        "公約原文：選挙公報",
        "Reviewed 10件",
        "大村秀章知事の公約原文（選挙公報）",
        "ジブリパークの魅力発信",
        "low / inferred・要レビュー",
        "まだ登録・評価していないこと",
    ],
    "projects/index.html": [
        "22自治体の Reviewed 事業レコード",
        "千葉県｜登録事業", "千葉市｜登録事業",
        "登録単位：施策（10系列）", "登録単位：政策（10系列）",
        "令和7年度の施策評価シート", "分野単位のKGI/KPI",
        "埼玉県｜登録事業", "さいたま市｜登録事業", "川口市｜登録事業",
        "北海道｜登録事業",
        "札幌市｜登録事業",
        "旭川市｜登録事業",
        "神奈川県｜登録事業",
        "横浜市｜登録事業",
        "川崎市｜登録事業",
        "億円単位の公表値",
        "登録単位：施策群",
        "施策群単位の金額は公表していない",
        "第4期実施計画に対応する事業別当初予算額",
        "基本評価調書の「予算額」",
        "当初予算ベース",
        "決算額ではありません",
        "北海道の総合判定は道の一次政策評価の判定",
        "事業単位の公式評価は公表されていません",
        "独自評価や順位付けは行いません",
    ],
    "promises/index.html": [
        "北海道・鈴木 直道",
        "札幌市・秋元 克広",
        "旭川市・今津 寛介",
        "愛知県・大村 秀章",
        "Reviewed 公約原文 10件",
        "ジブリパークの魅力発信",
        "公式選挙公報",
        "low / inferred",
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
    "municipalities/okinawa/index.html": [
        "沖縄県の375指標を、主要指標と成果指標に分けて読む。",
        "Reviewed指標",
        "主要指標",
        "成果指標",
        "原資料の単位差を、推測で直さない。",
        "375指標を、階層・政策・値・属性から探す。",
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
    "review-progress/index.html": [
        "どこまで確認できたかも、公開する。",
        "Phase 15の現在地",
        "レビュー完了率",
        "自治体別のレビュー状況",
        "作業中の候補データ",
        "レビュー完了記録",
    ],
    "compare/index.html": [
        "同じ条件の数字だけで見る。",
        "規模の違いを、優劣へ変換しない。",
    ],
    "executives/index.html": [
        "北海道・知事",
        "鈴木 直道",
        "2023年4月23日",
        "首長評価の前に、任期と公約の根拠を固定する。",
        "現職名と任期が分かっても、実績評価はできない。",
    ],
    "assemblies/aichi-prefecture/index.html": [
        "愛知県議会",
        "令和8年6月愛知県議会定例会",
        "本会議の投票記録そのものではありません",
        "政務活動費",
        "視察",
    ],
    "assemblies/nagoya-city/index.html": [
        "名古屋市会",
        "第134号",
        "議決に参加できない",
        "68人分",
        "全会一致",
    ],
    "assemblies/toyota-city/index.html": [
        "豊田市議会",
        "令和8年9月豊田市議会定例会",
        "自民クラブは議長を除く・欠席1名",
        "政務活動費",
        "視察",
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
        "15,124件の内訳。",
        "目標から契約までの現在地。",
        "壊さない4つの境界。",
        "データ不足を、点数で埋めません。",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-path",
        default="",
        help="Expected deployment base path, such as /subpath.",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_source_count() -> int:
    return sum(len(load_json(path)["records"]) for path in SOURCE_CATALOG_PATHS)


def route_file(route: str) -> str:
    return f"{route.strip('/')}/index.html"


def published_required_files() -> set[str]:
    published = load_json(ROOT / "data/catalog/published_prefecture_pages.json")
    return {route_file(record["route"]) for record in published["records"]}


def nationwide_requirements() -> dict[str, list[str]]:
    coverage = load_json(ROOT / "data/catalog/prefecture_coverage.json")
    requirements: dict[str, list[str]] = {
        "municipalities/index.html": [
            *(record["name"] for record in coverage["records"]),
            "Reviewed",
            "Evidence Packet",
            "根拠を読む",
        ]
    }
    summary_path = ROOT / "data/catalog/phase9_review_summary.json"
    if not summary_path.is_file():
        return requirements

    summary = load_json(summary_path)
    requirements.setdefault("municipalities/phase9/index.html", []).extend(
        [
            str(summary["prefecture_count"]),
            str(summary["reviewed_target_statement_count"]),
            str(summary["evidence_packet_count"]),
            f"{summary['evidence_coverage_percent']}%",
        ]
    )
    for record in summary["records"]:
        requirements[route_file(record["route"])] = [
            record["name"],
            record["plan_title"],
            "Reviewed / Not comparable",
            "Evidence ID",
            "比較対象外の理由",
        ]
    return requirements


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
            f"宮城県では{linked_series}系列を直接接続し、{review_needed_series}系列を要確認",
            f"{annual_rows}",
        ],
    }


def reviewed_coverage_requirements() -> dict[str, list[str]]:
    phase9 = load_json(ROOT / "data/catalog/phase9_review_summary.json")
    manifest_fields = [
        ("hokkaido_policy_review_manifest.json", "reviewed_indicator_count"),
        ("miyagi_policy_review_manifest.json", "reviewed_target_group_count"),
        ("tokyo_policy_target_review_manifest.json", "reviewed_target_card_count"),
        ("aichi_policy_indicator_review_manifest.json", "reviewed_indicator_row_count"),
        (
            "osaka_beyond_expo_indicator_review_manifest.json",
            "reviewed_indicator_row_count",
        ),
        (
            "hiroshima_revised_vision_indicator_review_manifest.json",
            "reviewed_indicator_count",
        ),
        (
            "kagawa_extended_plan_indicator_review_manifest.json",
            "reviewed_indicator_count",
        ),
        (
            "okinawa_midterm_indicator_review_manifest.json",
            "reviewed_indicator_count",
        ),
    ]
    anchor_total = sum(
        load_json(ROOT / "data/catalog" / filename)[field]
        for filename, field in manifest_fields
    )
    fukuoka_total = sum(
        len(load_json(path)["items"])
        for path in (ROOT / "data/entities/policy").glob(
            "fukuoka_prefecture_initiative_*_targets.json"
        )
    )
    reviewed_total = (
        phase9["reviewed_target_statement_count"] + anchor_total + fukuoka_total
    )
    formatted_total = f"{reviewed_total:,}"
    return {
        "index.html": [formatted_total],
        "municipalities/index.html": [formatted_total],
        "data-quality/index.html": [formatted_total],
    }


def hokkaido_cluster_project_detail_files() -> set[str]:
    """Require each Reviewed Hokkaido cluster project series to export a detail page."""
    required: set[str] = set()
    for slug in (
        "hokkaido-prefecture", "sapporo-city", "asahikawa-city",
        "osaka-prefecture", "osaka-city", "sakai-city",
    ):
        records = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            item["series_id"] for item in records if item["review_status"] == "reviewed"
        }:
            required.add(f"projects/{slug}/{series}/index.html")
    return required


def normalized_html(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    return re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)


def kanagawa_cluster_project_detail_files() -> set[str]:
    """Require each Kanagawa cluster Reviewed project series to export."""
    files: set[str] = set()
    for slug in ("kanagawa-prefecture", "yokohama-city", "kawasaki-city"):
        records = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            item["series_id"] for item in records if item["review_status"] == "reviewed"
        }:
            files.add(f"projects/{slug}/{series}/index.html")
    return files


def validate_kanagawa_prefecture_page() -> list[str]:
    """Require the dedicated Kanagawa page to expose its own reviewed facts."""
    path = EXPORT_ROOT / "municipalities/kanagawa-prefecture/index.html"
    if not path.is_file():
        return ["Missing dedicated Kanagawa prefecture page."]
    content = normalized_html(path)
    required = (
        "新かながわグランドデザイン",
        "普通会計決算",
        "2022〜2024年度",
        "2026年度",
        "13プロジェクト",
        "1億円未満切捨て",
        "総合計画審議会による二次評価",
        "黒岩祐治知事",
        "神奈川県議会",
    )
    return [
        f"Kanagawa prefecture page is missing required copy: {phrase}"
        for phrase in required if phrase not in content
    ]


def validate_kanagawa_assembly_scope() -> list[str]:
    """Require the three Kanagawa cluster assembly pages and their distinct caveats."""
    expected = {
        "kanagawa-prefecture": (
            "神奈川県議会の賛否は会派別のみ公表",
            "▲は使われていません",
        ),
        "yokohama-city": (
            "委員会報告への賛否",
            "決算関係27件",
            "市会図書室での閲覧のみ",
        ),
        "kawasaki-city": (
            "無所属議員5名",
            "議会局での閲覧制度のみ",
            "陳情は委員会で審査され、本会議での表決対象ではありません",
        ),
    }
    failures: list[str] = []
    for slug, phrases in expected.items():
        path = EXPORT_ROOT / "assemblies" / slug / "index.html"
        if not path.is_file():
            failures.append(f"Missing Kanagawa cluster assembly page: {slug}")
            continue
        content = normalized_html(path)
        for phrase in phrases:
            if phrase not in content:
                failures.append(f"{slug} assembly page is missing required copy: {phrase}")
    return failures


def validate_kanagawa_cluster_sections() -> list[str]:
    """Check Kanagawa cluster project disclosures in the exported index."""
    failures: list[str] = []
    path = EXPORT_ROOT / "projects/index.html"
    if not path.is_file():
        return failures

    content = normalized_html(path)
    expected = (
        ("kanagawa-prefecture", "神奈川県", "億円単位の公表値"),
        ("yokohama-city", "横浜市", "登録単位：施策群"),
        ("kawasaki-city", "川崎市", "第4期実施計画"),
    )
    for slug, name, disclosure in expected:
        match = re.search(
            rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
            content,
            flags=re.DOTALL,
        )
        if match is None:
            failures.append(f"projects index is missing the {slug} section")
            continue
        section = match.group(1)
        if f"{name}｜登録事業" not in section:
            failures.append(f"projects index {slug} section is missing its heading")
        if disclosure not in section:
            failures.append(f"projects index {slug} section is missing disclosure: {disclosure}")

    for phrase in (
        "施策群単位の金額は公表していない",
        "施策群単位の公式評価",
        "第4期実施計画に対応する事業別当初予算額",
        "公式評価は未登録",
        "金額は未登録",
    ):
        if phrase not in content:
            failures.append(f"projects index is missing Kanagawa cluster disclosure: {phrase}")
    return failures


def validate_promise_section(
    slug: str, heading: str, status: str
) -> list[str]:
    """Validate reviewed/absent promises only within the municipality's section."""
    path = EXPORT_ROOT / "promises/index.html"
    if not path.is_file():
        return []

    content = normalized_html(path)
    section = re.search(
        rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
        content,
        flags=re.DOTALL,
    )
    if section is None:
        return [f"promises/index.html is missing the {slug} section (id={slug})"]
    section_html = section.group(1)
    failures = []
    if heading not in section_html:
        failures.append(f"{slug} promise section is missing its executive heading")
    if status not in section_html:
        failures.append(f"{slug} promise section does not show expected status: {status}")
    return failures


def validate_hokkaido_promise_scope() -> list[str]:
    """Hokkaido has 15 Reviewed promises; other municipalities cannot satisfy it."""
    return validate_promise_section(
        "hokkaido-prefecture", "北海道・鈴木 直道", "Reviewed 公約原文 15件"
    )


def validate_sapporo_promise_scope() -> list[str]:
    """Sapporo has 13 Reviewed mayor promises from the registered bulletin."""
    return validate_promise_section(
        "sapporo-city", "札幌市・秋元 克広", "Reviewed 公約原文 13件"
    )


def validate_asahikawa_promise_scope() -> list[str]:
    """Asahikawa has a reviewed mayor term but no registered manifesto."""
    return validate_promise_section(
        "asahikawa-city", "旭川市・今津 寛介", "公約原文：" + "未登録"
    )


def validate_yokohama_promise_scope() -> list[str]:
    """Yokohama has 12 reviewed promises for the current mayor's term."""
    return validate_promise_section(
        "yokohama-city", "横浜市・原澤 敦美", "Reviewed 公約原文 12件"
    )


def validate_kawasaki_promise_scope() -> list[str]:
    """Kawasaki has 13 reviewed promises for the current mayor's term."""
    return validate_promise_section(
        "kawasaki-city", "川崎市・福田 紀彦", "Reviewed 公約原文 13件"
    )



def osaka_cluster_project_detail_files() -> set[str]:
    """Require each Osaka cluster Reviewed project series to export."""
    files: set[str] = set()
    for slug in ("osaka-prefecture", "osaka-city", "sakai-city"):
        records = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            item["series_id"] for item in records if item["review_status"] == "reviewed"
        }:
            files.add(f"projects/{slug}/{series}/index.html")
    return files


def validate_osaka_cluster_sections() -> list[str]:
    """Require municipality-specific promises and project content in scoped sections."""
    failures: list[str] = []
    promise_statuses = (
        ("osaka-prefecture", "大阪府・吉村 洋文", "Reviewed 公約原文 7件"),
        ("osaka-city", "大阪市・横山 英幸", "Reviewed 公約原文 5件"),
        ("sakai-city", "堺市・永藤 英機", ("公約原文：" + "未登録")),
    )
    for slug, heading, status in promise_statuses:
        failures.extend(validate_promise_section(slug, heading, status))
    for slug, page, section_id, status in (
        (
            "osaka-prefecture", "municipalities/osaka/index.html",
            "osaka-executive-promises", "Reviewed 公約原文 7件",
        ),
        (
            "osaka-city", "municipalities/osaka-city/index.html",
            "mayor-promises", "Reviewed 公約原文：5件",
        ),
        (
            "sakai-city", "municipalities/sakai-city/index.html",
            "mayor-promises", "公約原文：" + "未登録",
        ),
    ):
        path = EXPORT_ROOT / page
        if not path.is_file():
            failures.append(f"Missing static export file: {page}")
            continue
        match = re.search(
            rf'<section\b(?=[^>]*\bid="{re.escape(section_id)}")[^>]*>(.*?)</section>',
            normalized_html(path), flags=re.DOTALL,
        )
        if match is None:
            failures.append(f"{slug} municipality page has no {section_id} section")
        elif status not in match.group(1):
            failures.append(f"{slug} municipality section missing status: {status}")

    projects_path = EXPORT_ROOT / "projects/index.html"
    if projects_path.is_file():
        content = normalized_html(projects_path)
        for slug, name in (
            ("osaka-prefecture", "大阪府"),
            ("osaka-city", "大阪市"),
            ("sakai-city", "堺市"),
        ):
            match = re.search(
                rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
                content, flags=re.DOTALL,
            )
            if match is None or f"{name}｜登録事業" not in match.group(1):
                failures.append(f"projects index is missing the {slug} section")
    return failures


def validate_hokkaido_assembly_scope() -> list[str]:
    """Check each assembly disclosure statement in its own exported section."""
    failures: list[str] = []
    expected = {
        "hokkaido-prefecture": {
            "votes": ["議員ごとの賛否は公表されていません", "会派ごとの賛否は公表されていません"],
            "expenses": ["集計値と閲覧制度のみが登録"],
            "trips": ["委員会視察・議員派遣の資料は公表されておらず"],
        },
        "sapporo-city": {
            "votes": ["会派別の賛否のみ公表", "議員個人別の賛否は公表されていません"],
            "expenses": ["領収書は閲覧申請形式のため登録対象外"],
        },
        "asahikawa-city": {
            "votes": ["賛否が分かれた8件のみ公表", "陳情の表決は採択への賛否"],
        },
    }
    for slug, sections in expected.items():
        path = EXPORT_ROOT / "assemblies" / slug / "index.html"
        if not path.is_file():
            failures.append(f"Missing static export file: assemblies/{slug}/index.html")
            continue
        content = normalized_html(path)
        for section_id, phrases in sections.items():
            section = re.search(
                rf'<section\b(?=[^>]*\bid="{re.escape(section_id)}")[^>]*>(.*?)</section>',
                content,
                flags=re.DOTALL,
            )
            if section is None:
                failures.append(f"{slug} missing assembly section: {section_id}")
                continue
            for phrase in phrases:
                if phrase not in section.group(1):
                    failures.append(f"{slug} {section_id} section missing required copy: {phrase}")

    path = EXPORT_ROOT / "municipalities/hokkaido-prefecture/index.html"
    if path.is_file():
        section = re.search(
            r'<section\b(?=[^>]*\bid="assembly")[^>]*>(.*?)</section>',
            normalized_html(path), flags=re.DOTALL,
        )
        required = ["北海道議会の議案・表決と情報公開", "委員会視察・議員派遣は公表されていない"]
        if section is None:
            failures.append("Hokkaido dedicated page is missing its assembly section")
        else:
            failures.extend(
                f"Hokkaido dedicated assembly section missing required copy: {phrase}"
                for phrase in required if phrase not in section.group(1)
            )
    path = EXPORT_ROOT / "assemblies/index.html"
    if path.is_file():
        content = normalized_html(path)
        for phrase in [
            "20議会", "埼玉県議会", "さいたま市議会", "川口市議会",
            "大阪府議会", "大阪市会", "堺市議会",
            "北海道議会", "札幌市議会", "旭川市議会",
            "神奈川県議会", "横浜市会", "川崎市議会",
            "千葉県議会", "千葉市議会",
        ]:
            if phrase not in content:
                failures.append(f"assemblies/index.html missing {phrase}")
    return failures

def validate_osaka_assembly_scope() -> list[str]:
    """Keep Osaka assembly disclosures scoped to each assembly and its page."""
    failures: list[str] = []
    expected = {
        "osaka-prefecture": {
            "votes": ["会派別", "議員個人別の賛否は公表されていません", "第1〜4項", "第5項"],
            "expenses": ["会派9・議員80", "89単位"],
        },
        "osaka-city": {
            "votes": ["会派別", "議員個人別の賛否は公表されていません"],
            "expenses": ["個人交付分", "市会図書室"],
        },
        "sakai-city": {
            "votes": ["主な議案", "10件", "その他の議案"],
            "proposals": ["陳情19件", "陳情回答綴"],
        },
    }
    for slug, sections in expected.items():
        path = EXPORT_ROOT / "assemblies" / slug / "index.html"
        if not path.is_file():
            failures.append(f"Missing static export file: assemblies/{slug}/index.html")
            continue
        content = normalized_html(path)
        for section_id, phrases in sections.items():
            section = re.search(
                rf'<section\b(?=[^>]*\bid="{re.escape(section_id)}")[^>]*>(.*?)</section>',
                content, flags=re.DOTALL,
            )
            if section is None:
                failures.append(f"{slug} missing assembly section: {section_id}")
                continue
            failures.extend(
                f"{slug} {section_id} missing required copy: {phrase}"
                for phrase in phrases if phrase not in section.group(1)
            )
    path = EXPORT_ROOT / "municipalities/osaka-prefecture/index.html"
    if path.is_file():
        content = normalized_html(path)
        section = re.search(
            r'<section\b(?=[^>]*\bid="assembly")[^>]*>(.*?)</section>',
            content, flags=re.DOTALL,
        )
        required = ["大阪府議会の議案・表決と情報公開", "請願第36号", "継続審査中"]
        if section is None:
            failures.append("Osaka prefecture page is missing its assembly section")
        else:
            failures.extend(
                f"Osaka prefecture assembly section missing: {phrase}"
                for phrase in required if phrase not in section.group(1)
            )
    return failures



def saitama_project_detail_files() -> set[str]:
    """Require each reviewed Saitama project series to have a static detail page."""
    required: set[str] = set()
    for slug in ("saitama-prefecture", "saitama-city", "kawaguchi-city"):
        records = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            record["series_id"] for record in records if record["review_status"] == "reviewed"
        }:
            required.add(f"projects/{slug}/{series}/index.html")
    return required


def validate_saitama_data_facts() -> None:
    """Fail with an assert if the stated page facts diverge from reviewed data."""
    base = ROOT / "data" / "reviewed" / "saitama-prefecture"
    plan = load_json(base / "plan_review.json")
    identity = next(
        row for row in plan["records"] if row["evidence_role"] == "current_plan_identity"
    )
    structure = next(
        row for row in plan["records"] if row["evidence_role"] == "policy_structure"
    )
    assert "埼玉県5か年計画 ～日本一暮らしやすい埼玉へ～" in identity["title"], identity["title"]
    assert "令和4〜8年度" in identity["title"], identity["title"]
    assert structure["value"] == "3つの将来像／12の針路／54の分野別施策", structure["value"]
    budget = load_json(base / "fiscal_records.json")
    settlement = load_json(base / "settlement_records.json")
    assert len(budget) == 3, len(budget)
    assert len(settlement) == 51, len(settlement)
    assert all(
        x["stage"] == "initial_budget" and x["account_type"] == "general"
        and x["fiscal_year"] == 2026
        for x in budget
    )
    assert all(
        x["stage"] == "settlement" and x["account_type"] == "ordinary"
        and x["fiscal_year"] in (2022, 2023, 2024)
        for x in settlement
    )
    selection = load_json(ROOT / "data" / "catalog" / "saitama_priority_project_selection.json")
    assert selection["population"]["project_count"] == 54
    assert len(selection["selections"]) == 10
    for slug in ("saitama-prefecture", "saitama-city", "kawaguchi-city"):
        municipality = load_json(ROOT / "data" / "reviewed" / slug / "municipality.json")
        projects = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        assert municipality["data_status"] == "reviewed"
        reviewed_series = {
            project["series_id"] for project in projects if project["review_status"] == "reviewed"
        }
        assert len(reviewed_series) == 10
        assert all(project["municipality_id"] == municipality["id"] for project in projects)
        if slug != "saitama-city":
            assert all(
                budget_record["amount_yen"] is None
                for project in projects for budget_record in project["budget_records"]
            )
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    promises = load_json(ROOT / "data" / "entities" / "executives" / "promises.json")
    slug_counts = (("saitama-prefecture", 12), ("saitama-city", 12), ("kawaguchi-city", 26))
    for slug, expected in slug_counts:
        municipality = load_json(ROOT / "data" / "reviewed" / slug / "municipality.json")
        term_ids = {
            term["id"]
            for term in terms
            if term["municipality_id"] == municipality["id"]
            and term["status"] == "current"
            and term["review_status"] in ("reviewed", "verified")
        }
        assert term_ids, slug
        registered = [
            p
            for p in promises
            if p["executive_term_id"] in term_ids
            and p["review_status"] in ("reviewed", "verified")
        ]
        assert len(registered) == expected, (slug, len(registered), expected)
        assembly = load_json(
            ROOT / "data" / "reviewed" / slug / "assembly" / "assembly_records.json"
        )
        disclosure = load_json(
            ROOT / "data" / "reviewed" / slug / "assembly" / "disclosure_profiles.json"
        )
        assert len(assembly) == len(disclosure) == 1
        assert assembly[0]["municipality_id"] == municipality["id"]
        assert assembly[0]["review_status"] == disclosure[0]["review_status"] == "reviewed"
    kawaguchi = load_json(
        ROOT / "data" / "reviewed" / "kawaguchi-city" / "assembly" / "disclosure_profiles.json"
    )[0]
    member_votes = next(
        row["availability"] for row in kawaguchi["items"] if row["item"] == "member_votes"
    )
    assert member_votes == "not_published"
    faction_votes = next(
        row["availability"] for row in kawaguchi["items"] if row["item"] == "faction_votes"
    )
    assert faction_votes == "not_published"


def validate_saitama_export() -> list[str]:
    """Inspect each individual Saitama municipality/assembly section, not the whole document."""
    slug_counts = (("saitama-prefecture", 12), ("saitama-city", 12), ("kawaguchi-city", 26))
    failures: list[str] = []
    page = EXPORT_ROOT / "municipalities/saitama-prefecture/index.html"
    if page.is_file():
        content = normalized_html(page)
        required = {
            "plan-title": ("埼玉県5か年計画", "12の針路", "54の分野別施策"),
            "finance-headline-title": ("2026年度", "当初予算"),
            "priority-projects": ("10系列", "施策単位の金額", "指標単位の判定"),
            "governor-title": ("大野 元裕", "12件"),
            "assembly-title": ("議会運営委員会", "本会議の投票記録そのものではありません"),
        }
        for section_id, phrases in required.items():
            if section_id == "priority-projects":
                pattern = r'<section\b(?=[^>]*\bid="priority-projects")[^>]*>(.*?)</section>'
            else:
                pattern = (
                    rf'<section\b[^>]*>(?:(?!</section>).)*?<h2\b[^>]*\b'
                    rf'id="{re.escape(section_id)}"[^>]*>(?:(?!</h2>).)*</h2>(.*?)</section>'
                )
            match = re.search(pattern, content, flags=re.DOTALL)
            if match is None:
                failures.append(f"saitama prefecture missing section: {section_id}")
                continue
            for phrase in phrases:
                if phrase not in match.group(0):
                    failures.append(f"saitama prefecture {section_id} missing fact: {phrase}")
    projects = EXPORT_ROOT / "projects/index.html"
    if projects.is_file():
        html = normalized_html(projects)
        expected = {
            "saitama-prefecture": ("埼玉県｜登録事業", "施策単位"),
            "saitama-city": ("さいたま市｜登録事業", "事業"),
            "kawaguchi-city": ("川口市｜登録事業", "施策"),
        }
        for slug, phrases in expected.items():
            section = re.search(
                rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
                html, flags=re.DOTALL,
            )
            if section is None:
                failures.append(f"Saitama projects missing municipality section: {slug}")
                continue
            for phrase in phrases:
                if phrase not in section.group(1):
                    failures.append(f"Saitama projects {slug} missing registered fact: {phrase}")
    promises = EXPORT_ROOT / "promises/index.html"
    if promises.is_file():
        html = normalized_html(promises)
        for slug, count in slug_counts:
            section = re.search(
                rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
                html, flags=re.DOTALL,
            )
            if section is None or f"Reviewed 公約原文 {count}件" not in section.group(1):
                failures.append(
                    f"Saitama promises {slug} section missing {count} reviewed promises"
                )
    for slug, phrases in {
        "saitama-prefecture": ("議会運営委員会", "本会議の投票記録"),
        "saitama-city": ("無所属議員の個人名列", "会派"),
        "kawaguchi-city": ("公式公表なし", "not_published"),
    }.items():
        path = EXPORT_ROOT / "assemblies" / slug / "index.html"
        if not path.is_file():
            failures.append(f"Missing Saitama assembly page: {slug}")
            continue
        html = normalized_html(path)
        for phrase in phrases:
            if phrase not in html:
                failures.append(f"Saitama assembly {slug} missing disclosure: {phrase}")
    return failures



def chiba_project_detail_files() -> set[str]:
    """Require static detail pages for all reviewed Chiba project series."""
    required: set[str] = {
        "municipalities/chiba-prefecture/index.html",
        "assemblies/chiba-prefecture/index.html",
        "assemblies/chiba-city/index.html",
    }
    for slug in ("chiba-prefecture", "chiba-city"):
        records = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            record["series_id"] for record in records if record["review_status"] == "reviewed"
        }:
            required.add(f"projects/{slug}/{series}/index.html")
    return required


def validate_chiba_data_facts() -> None:
    """Assert that Chiba page claims and selected project names match canonical Reviewed data."""
    cases = (
        ("chiba-prefecture", "chiba_priority_project_selection.json", "jp-local-120006"),
        ("chiba-city", "chiba_city_priority_project_selection.json", "jp-local-121002"),
    )
    for slug, selection_file, municipality_id in cases:
        projects = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        selection = load_json(ROOT / "data" / "catalog" / selection_file)
        reviewed = [record for record in projects if record["review_status"] == "reviewed"]
        assert len(reviewed) == 10, (slug, len(reviewed))
        assert len({record["series_id"] for record in reviewed}) == 10, slug
        assert all(record["municipality_id"] == municipality_id for record in reviewed), slug
        assert len(selection["selections"]) == 10, (slug, len(selection["selections"]))
        source_file = (
            "chiba_project_sources.json" if slug == "chiba-prefecture"
            else "chiba_city_project_sources.json"
        )
        source_catalog = load_json(ROOT / "data" / "catalog" / source_file)
        source_ids = {source["id"] for source in source_catalog["records"]}
        assert all(set(record["sources"]).issubset(source_ids) for record in reviewed), slug
        by_series = {record["series_id"]: record for record in reviewed}
        selected_series = {item["series_id"] for item in selection["selections"]}
        assert selected_series == set(by_series), (slug, selected_series ^ set(by_series))
        for item in selection["selections"]:
            record = by_series[item["series_id"]]
            assert item["official_title"] == record["official_title"], (
                slug, item["official_title"], record["official_title"]
            )
        if slug == "chiba-prefecture":
            assert selection["population"]["project_count"] == 41
            assert all(record["fiscal_year"] == 2025 for record in reviewed)
            assert all(record["official_evaluation"] is None for record in reviewed)
            kpis = load_json(ROOT / "data" / "reviewed" / slug / "project_kpis.json")
            assert len(kpis) == 26, len(kpis)
            assert all(kpi["project_id"] in {record["id"] for record in reviewed} for kpi in kpis)
            for record in reviewed:
                stages = {budget["kind"] for budget in record["budget_records"]}
                assert stages == {"revised_budget", "settlement"}, (record["id"], stages)
                assert all(budget["amount_yen"] is not None for budget in record["budget_records"])
                assert all(budget["fiscal_year"] == 2025 for budget in record["budget_records"])
                assert any("9月補正後" in budget["note"]
                    for budget in record["budget_records"]
                    if budget["kind"] == "revised_budget")
        else:
            population = selection["population"]
            assert population["field_count"] == 8
            assert population["policy_count"] == 23
            assert population["measure_count"] == 67
            assert population["project_count"] == 189
            assert all(record["fiscal_year"] == 2026 for record in reviewed)
            assert all(record["official_evaluation"] is None for record in reviewed)
            assert all(record["kpis"] == [] for record in reviewed)
            indicators = load_json(
                ROOT / "data" / "reviewed" / "chiba-city" / "current_policy_indicators.json"
            )
            assert indicators["official_code"] == "121002"
            assert indicators["review_status"] == (
                "reviewed_complete_policy_indicator_identity_and_values"
            )
            assert indicators["quantitative_indicator_count"] == 40
            assert len(indicators["fields"]) == 8
            assert all(
                len(record["budget_records"]) == 1
                and record["budget_records"][0]["kind"] == "initial_budget"
                and record["budget_records"][0]["fiscal_year"] == 2026
                and record["budget_records"][0]["amount_yen"] is None
                for record in reviewed
            )
    chiba_city_evidence = load_json(
        ROOT / "data" / "reviewed" / "chiba-city" / "project_evidence_packets.json"
    )
    assert len(chiba_city_evidence) == 10
    assert all(
        any(claim["field"] == "kpis" and "付け替えない" in claim["statement"]
            for claim in packet["claims"])
        for packet in chiba_city_evidence
    )


def validate_chiba_export() -> list[str]:
    """Check Chiba-specific wording inside each municipality section, not elsewhere on the page."""
    failures: list[str] = []
    page = EXPORT_ROOT / "projects/index.html"
    if not page.is_file():
        return failures
    html = normalized_html(page)
    expected = {
        "chiba-prefecture": (
            "千葉県｜登録事業", "登録単位：施策（10系列）", "41施策",
            "令和7年度", "9月補正後", "施策単位の公式評定",
        ),
        "chiba-city": (
            "千葉市｜登録事業", "登録単位：政策（10系列）", "23政策",
            "67施策", "189事業", "分野単位のKGI/KPI",
        ),
    }
    for slug, phrases in expected.items():
        section = re.search(
            rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
            html, flags=re.DOTALL,
        )
        if section is None:
            failures.append(f"Chiba projects missing municipality section: {slug}")
            continue
        for phrase in phrases:
            if phrase not in section.group(1):
                failures.append(f"Chiba projects {slug} missing registered fact: {phrase}")
        projects = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for record in projects:
            if record["review_status"] == "reviewed" and (
                record["official_title"] not in section.group(1)
            ):
                failures.append(
                    f"Chiba projects {slug} missing official title: {record['official_title']}"
                )
    return failures



def validate_chiba_cluster_data_facts() -> None:
    """Cross-check executive, finance, plan and assembly copy against canonical Chiba records."""
    terms = load_json(ROOT / "data" / "entities" / "executives" / "executive_terms.json")
    promises = load_json(ROOT / "data" / "entities" / "executives" / "promises.json")
    executive_evidence = load_json(
        ROOT / "data" / "entities" / "executives" / "evidence_packets.json"
    )
    prefecture_term_id = "jp-local-120006-executive-2025-04-05"
    city_term_id = "jp-local-121002-executive-2025-03-21"
    prefecture = next(t for t in terms if t["id"] == prefecture_term_id)
    city = next(t for t in terms if t["id"] == city_term_id)
    assert (
        prefecture["person_name"], prefecture["term_start"],
        prefecture["term_end"], prefecture["election_date"],
    ) == ("熊谷 俊人", "2025-04-05", "2029-04-04", "2025-03-16")
    assert (
        city["person_name"], city["term_start"],
        city["term_end"], city["election_date"],
    ) == ("神谷 俊一", "2025-03-21", "2029-03-20", "2025-03-16")
    for term in (prefecture, city):
        rows = [
            p for p in promises
            if p["executive_term_id"] == term["id"]
            and p["municipality_id"] == term["municipality_id"]
            and p["review_status"] == "reviewed"
        ]
        assert len(rows) == 25, (term["id"], len(rows))
    for term, vote_phrase in ((prefecture, "1,404,905票"), (city, "245,748票")):
        packet = next(p for p in executive_evidence if p["subject_id"] == term["id"])
        election_claim = next(
            claim for claim in packet["claims"] if claim["field"] == "election_date"
        )
        assert vote_phrase in election_claim["statement"], (term["id"], election_claim["statement"])

    plan = load_json(ROOT / "data" / "reviewed" / "chiba-prefecture" / "plan_review.json")
    structure = next(r for r in plan["records"] if r["id"] == "chiba-plan-policy-structure")
    assert all(
        x in structure["statement"]
        for x in ("6つの基本目標", "15の政策", "41の施策", "200の主な取組")
    )

    budget = load_json(ROOT / "data" / "reviewed" / "chiba-prefecture" / "fiscal_records.json")
    settlements = load_json(
        ROOT / "data" / "reviewed" / "chiba-prefecture" / "settlement_records.json"
    )
    assert len([
        r for r in budget
        if r["review_status"] == "reviewed" and r["stage"] == "initial_budget"
        and r["fiscal_year"] == 2026 and r["account_type"] == "general"
    ]) == 3
    ordinary = [
        r for r in settlements
        if r["review_status"] == "reviewed" and r["stage"] == "settlement"
        and r["account_type"] == "ordinary"
    ]
    assert len(ordinary) == 51
    assert {r["fiscal_year"] for r in ordinary} == {2022, 2023, 2024}

    for (
        slug, municipality_id, proposal_count, vote_count,
        faction_count, expense_count, trip_count, seat_count,
    ) in (
        ("chiba-prefecture", "jp-local-120006", 51, 51, 700, 110, 47, 95),
        ("chiba-city", "jp-local-121002", 57, 55, 275, 48, 26, 50),
    ):
        base = ROOT / "data" / "reviewed" / slug / "assembly"
        assembly = load_json(base / "assembly_records.json")
        assert len(assembly) == 1 and assembly[0]["municipality_id"] == municipality_id
        assert assembly[0]["seat_count"] == seat_count
        roster_count = sum(faction["member_count"] for faction in assembly[0]["factions"])
        if slug == "chiba-prefecture":
            assert roster_count == 87 and roster_count + 2 == 89
        else:
            assert roster_count == 50
        assert len(load_json(base / "proposals.json")) == proposal_count
        assert len(load_json(base / "votes.json")) == vote_count
        assert len(load_json(base / "faction_votes.json")) == faction_count
        assert len(load_json(base / "political_activity_expenses.json")) == expense_count
        assert len(load_json(base / "inspection_trips.json")) == trip_count

    pref_base = ROOT / "data" / "reviewed" / "chiba-prefecture" / "assembly"
    proposals = load_json(pref_base / "proposals.json")
    pending = [p for p in proposals if p["outcome"] == "pending"]
    assert len(pending) == 1 and pending[0]["title"] == "決算認定について"
    disclosure = load_json(pref_base / "disclosure_profiles.json")[0]
    faction_note = next(
        item["note"] for item in disclosure["items"] if item["item"] == "faction_votes"
    )
    assert all(x in faction_note for x in ("原案に反対", "賛成会派等の内訳", "採択することに賛成"))


def validate_chiba_cluster_export() -> list[str]:
    failures: list[str] = []
    page = EXPORT_ROOT / "municipalities/chiba-prefecture/index.html"
    if page.is_file():
        html = normalized_html(page)
        required = (
            "千葉県総合計画 ～千葉の未来をともに創る～",
            "基本目標6", "政策15", "施策41",
            "2026年度に成立した一般会計当初予算",
            "2022〜2024年度の普通会計決算", "51件",
            "熊谷 俊人", "2025年4月5日", "2029年4月4日",
            "1,404,905票", "25件", "千葉県議会", "継続審査中",
            "神谷 俊一", "2025年3月21日", "2029年3月20日", "245,748票",
        )
        for phrase in required:
            if phrase not in html:
                failures.append(f"Chiba prefecture page missing registered fact: {phrase}")
        reviewed_projects = load_json(
            ROOT / "data" / "reviewed" / "chiba-prefecture" / "projects.json"
        )
        for record in reviewed_projects:
            if record["review_status"] == "reviewed" and record["official_title"] not in html:
                failures.append(
                    f"Chiba prefecture page missing reviewed project title: "
                    f"{record['official_title']}"
                )
    assemblies_page = EXPORT_ROOT / "assemblies/index.html"
    if assemblies_page.is_file():
        html = normalized_html(assemblies_page)
        for phrase in ("20議会", "千葉県議会", "千葉市議会"):
            if phrase not in html:
                failures.append(f"Assemblies index missing Chiba fact: {phrase}")
    for slug, phrases in {
        "chiba-prefecture": ("千葉県議会", "議案表", "発議案表", "請願表", "95人／89人"),
        "chiba-city": ("千葉市議会", "57件", "55件"),
    }.items():
        path = EXPORT_ROOT / "assemblies" / slug / "index.html"
        if path.is_file():
            html = normalized_html(path)
            for phrase in phrases:
                if phrase not in html:
                    failures.append(f"Chiba assembly page {slug} missing fact: {phrase}")
    promises_page = EXPORT_ROOT / "promises/index.html"
    if promises_page.is_file():
        html = normalized_html(promises_page)
        for phrase in ("千葉県・熊谷 俊人", "千葉市・神谷 俊一"):
            if phrase not in html:
                failures.append(f"Promises page missing Chiba executive: {phrase}")
        if html.count("Reviewed 公約原文 25件") < 2:
            failures.append(
                "Promises page does not show 25 reviewed promises "
                "for both Chiba executives"
            )
    return failures



def hyogo_cluster_project_detail_files() -> set[str]:
    """Export every Reviewed Hyogo and Kobe series, without inventing a new route."""
    required: set[str] = set()
    for slug in ("hyogo-prefecture", "kobe-city"):
        projects = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for series in {
            project["series_id"] for project in projects
            if project["review_status"] == "reviewed"
        }:
            required.add(f"projects/{slug}/{series}/index.html")
    return required


def validate_hyogo_cluster_data_facts() -> None:
    """Registration units and missing values must agree with Reviewed source data."""
    cases = (
        ("hyogo-prefecture", "jp-local-280003",
         "hyogo_priority_project_selection.json", "hyogo_project_sources.json", 2025),
        ("kobe-city", "jp-local-281000",
         "kobe_city_priority_project_selection.json", "kobe_city_project_sources.json", 2026),
    )
    for slug, municipality_id, selection_name, sources_name, year in cases:
        directory = ROOT / "data" / "reviewed" / slug
        municipality = load_json(directory / "municipality.json")
        projects = load_json(directory / "projects.json")
        kpis = load_json(directory / "project_kpis.json")
        packets = load_json(directory / "project_evidence_packets.json")
        selection = load_json(ROOT / "data" / "catalog" / selection_name)
        sources = load_json(ROOT / "data" / "catalog" / sources_name)
        source_ids = {record["id"] for record in sources["records"]}
        assert municipality["id"] == municipality_id
        assert municipality["data_status"] == "reviewed"
        assert len(projects) == len(packets) == len(selection["selections"]) == 10
        assert len({project["series_id"] for project in projects}) == 10
        assert kpis == []
        assert {packet["subject_id"] for packet in packets} == {
            project["id"] for project in projects
        }
        by_id = {project["id"]: project for project in projects}
        for entry in selection["selections"]:
            project = by_id[entry["project_id"]]
            assert entry["series_id"] == project["series_id"]
            assert entry["official_title"] == project["official_title"]
        for project in projects:
            assert project["municipality_id"] == municipality_id
            assert project["fiscal_year"] == year
            assert project["review_status"] == "reviewed"
            assert project["official_evaluation"] is None
            assert project["kpis"] == []
            assert set(project["sources"]).issubset(source_ids)
            assert len(project["budget_records"]) == 1
            budget = project["budget_records"][0]
            assert budget["kind"] == "initial_budget"
            assert budget["fiscal_year"] == year
            assert budget["amount_yen"] is None  # not zero
        assert all(packet["review_status"] == "reviewed" for packet in packets)
        if slug == "hyogo-prefecture":
            assert selection["population"]["project_count"] == 66
            assert len(selection["selection_rule"]["pillars"]) == 3
            assert {item["direction_number"] for item in selection["selections"]} == set(range(1, 9))
            assert all(
                any(claim["field"] == "registration_unit" and "取組方針" in claim["statement"]
                    for claim in packet["claims"])
                for packet in packets
            )
        else:
            population = selection["population"]
            assert (population["direction_count"], population["policy_count"],
                    population["measure_count"], population["unique_measure_count"],
                    population["kpi_count"]) == (3, 14, 80, 62, 21)
            assert len(selection["rule"]["pillars"]) == 3
            assert all(
                any(claim["field"] == "registration_unit" and "基本政策" in claim["statement"]
                    for claim in packet["claims"])
                for packet in packets
            )


def validate_hyogo_cluster_export() -> list[str]:
    """Check required copy and actual official titles *within* each municipality section."""
    failures: list[str] = []
    path = EXPORT_ROOT / "projects/index.html"
    if not path.is_file():
        return failures
    html = normalized_html(path)
    if "22自治体の Reviewed 事業レコード" not in html:
        failures.append("Projects index must show 22 Reviewed municipalities")
    scopes = {
        "hyogo-prefecture": (
            "兵庫県｜登録事業", "登録単位：取組方針項目（10系列）",
            "取組方針66項目", "固有64項目", "187指標",
            "金額・公式評定・KPIは未公表",
        ),
        "kobe-city": (
            "神戸市｜登録事業", "登録単位：基本政策（10系列）",
            "基本政策14件", "主な施策80件", "62件",
            "方向性単位のKPI21件", "Well-Being指標",
        ),
    }
    for slug, required_phrases in scopes.items():
        section = re.search(
            rf'<section\b(?=[^>]*\bid="{re.escape(slug)}")[^>]*>(.*?)</section>',
            html, flags=re.DOTALL,
        )
        if section is None:
            failures.append(f"Missing Hyogo cluster projects section: {slug}")
            continue
        content = section.group(1)
        for phrase in required_phrases:
            if phrase not in content:
                failures.append(f"Hyogo projects {slug} missing scoped copy: {phrase}")
        projects = load_json(ROOT / "data" / "reviewed" / slug / "projects.json")
        for project in projects:
            if project["review_status"] == "reviewed" and project["official_title"] not in content:
                failures.append(
                    f"Hyogo projects {slug} missing official title: {project['official_title']}"
                )
    return failures


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    validate_saitama_data_facts()
    validate_chiba_data_facts()
    validate_chiba_cluster_data_facts()
    validate_hyogo_cluster_data_facts()
    required_files = (
        set(REQUIRED_FILES)
        | published_required_files()
        | hokkaido_cluster_project_detail_files()
        | osaka_cluster_project_detail_files()
        | kanagawa_cluster_project_detail_files()
        | saitama_project_detail_files()
        | chiba_project_detail_files()
        | hyogo_cluster_project_detail_files()
        | {"municipalities/osaka-prefecture/index.html"}
        | {
            f"assemblies/{slug}/index.html"
            for slug in ("osaka-prefecture", "osaka-city", "sakai-city")
        }
        | {
            f"assemblies/{slug}/index.html"
            for slug in ("hokkaido-prefecture", "sapporo-city", "asahikawa-city")
        }
    )

    for relative_path in sorted(required_files):
        if not (EXPORT_ROOT / relative_path).is_file():
            failures.append(f"Missing static export file: {relative_path}")

    requirements = {
        path: list(copies) for path, copies in BASE_PAGE_REQUIREMENTS.items()
    }
    for dynamic_requirements in (
        nationwide_requirements(),
        miyagi_requirements(),
        reviewed_coverage_requirements(),
    ):
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

    failures.extend(validate_hokkaido_promise_scope())
    failures.extend(validate_sapporo_promise_scope())
    failures.extend(validate_asahikawa_promise_scope())
    failures.extend(validate_yokohama_promise_scope())
    failures.extend(validate_kawasaki_promise_scope())
    failures.extend(validate_osaka_cluster_sections())
    failures.extend(validate_kanagawa_cluster_sections())
    failures.extend(validate_kanagawa_prefecture_page())
    failures.extend(validate_kanagawa_assembly_scope())
    failures.extend(validate_saitama_export())
    failures.extend(validate_chiba_export())
    failures.extend(validate_chiba_cluster_export())
    failures.extend(validate_hyogo_cluster_export())
    failures.extend(validate_hokkaido_assembly_scope())
    failures.extend(validate_osaka_assembly_scope())

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
