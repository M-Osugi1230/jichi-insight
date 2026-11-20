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
        "15自治体の Reviewed 事業レコード",
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
            "12議会", "大阪府議会", "大阪市会", "堺市議会",
            "北海道議会", "札幌市議会", "旭川市議会",
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


def main() -> int:
    args = parse_args()
    failures: list[str] = []
    required_files = (
        set(REQUIRED_FILES)
        | published_required_files()
        | hokkaido_cluster_project_detail_files()
        | osaka_cluster_project_detail_files()
        | kanagawa_cluster_project_detail_files()
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
    failures.extend(validate_osaka_cluster_sections())
    failures.extend(validate_kanagawa_cluster_sections())
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
