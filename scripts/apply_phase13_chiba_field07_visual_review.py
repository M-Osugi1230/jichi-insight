from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
TESTS = ROOT / "tests"

IDENTITIES = CAT / "chiba_current_project_identities_field07.json"
REVIEW = REVIEWED / "current_project_work_items_field07.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field07_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"
POLICY = CAT / "chiba_phase13_policy_review_manifest.json"
PLAN = REVIEWED / "plan_review.json"
QUEUE_BUILDER = ROOT / "scripts/build_chiba_work_item_visual_review_queue.py"

SOURCE_LOCATION_SEMANTICS = (
    "source_location follows the repository's existing zero-based PDF page-index convention; "
    "source_printed_page preserves the page number printed in the official booklet. "
    "For this PDF, Field 7 printed pages map to source_location index printed+3 and "
    "pdftoppm physical page printed+4."
)

PROMOTIONS = {
    "chiba-f07-p006": [
        {
            "work_item_id": "chiba-f07-p006-w001",
            "item_name": "グランドデザイン改定、（仮）中央公園プロムナード周辺のまちづくりビジョン策定",
            "current_text": "グランドデザイン改定（案）作成 / （仮）中央公園プロムナード周辺のまちづくりビジョン（案）作成 / 社会実験",
            "plan_text": "計画改定・計画策定 / 社会実験",
            "target_text": "グランドデザイン改定 / （仮）中央公園プロムナード周辺のまちづくりビジョン策定 / 社会実験",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p006-w002",
            "item_name": "中央公園プロムナード再編",
            "current_text": "駅前広場等概略検討 / 実証実験検討",
            "plan_text": "基本計画、基本設計、実施設計 / 実証実験設計、実証実験",
            "target_text": "実施設計完了",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p006-w003",
            "item_name": "意見交換の場等（中プロ・デザインラボ※）の開催",
            "current_text": "意見交換の場開催",
            "plan_text": "中プロ・デザインラボの開催4回/年",
            "target_text": "中プロ・デザインラボの開催4回/年",
            "parse_status": "reviewed_structured",
        },
        {
            "work_item_id": "chiba-f07-p006-w004",
            "item_name": "魅力ある景観の形成",
            "current_text": "機能や将来像の把握、課題の共有",
            "plan_text": "現況調査、目標・基準の検討 / 景観形成推進地区指定（中央公園プロムナード周辺）",
            "target_text": "地区基準の運用開始",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f07-p007": [
        {
            "work_item_id": "chiba-f07-p007-w001",
            "item_name": "公園再整備（西区域）",
            "current_text": "中区域再整備完了 / 東区域再整備着手 / 対象街区の一部取得",
            "plan_text": "詳細設計 / 整備 / 用地取得",
            "target_text": "整備完了",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p007-w002",
            "item_name": "周辺道路の再整備（中央21号線ほか）",
            "current_text": "道路占用物件移設一部完了",
            "plan_text": "実施設計 / 中央29号線安全対策工事 / 整備200m",
            "target_text": "整備完了",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f07-p011": [
        {
            "work_item_id": "chiba-f07-p011-w001",
            "item_name": "（仮称）幕張新都心まちづくり基本方針の策定",
            "current_text": "まちづくりの方向性検討（中心地区）",
            "plan_text": "まちづくりの方向性検討（公園・拡大地区等） / 基本方針検討 / アクションプラン検討",
            "target_text": "（仮称）幕張新都心まちづくり基本方針・アクションプランの策定",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p011-w002",
            "item_name": "中心地区エリアマネジメントの支援・連携",
            "current_text": "エリアマネジメント組織の組成",
            "plan_text": "公共空間利活用実証実験 / 公共空間利活用調査 / 公共空間利活用支援",
            "target_text": "エリアマネジメント組織による主体的な活動の実施",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p011-w003",
            "item_name": "幕張豊砂ウォーカブル*の推進",
            "current_text": "民間主体の体制確立 / 人工芝・ベンチの設置",
            "plan_text": "滞在環境社会実験 / 滞在環境整備 / サイン手法等社会実験",
            "target_text": "民間主体の体制によるウォーカブル推進",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f07-p013": [
        {
            "work_item_id": "chiba-f07-p013-w001",
            "item_name": "駅前広場改修",
            "current_text": "予備設計",
            "plan_text": "詳細設計 / 用地調整 / 改修",
            "target_text": "改修",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f07-p017": [
        {
            "work_item_id": "chiba-f07-p017-w001",
            "item_name": "路線バスの維持・再編",
            "current_text": "バス路線維持支援 / バス路線の再編に向けた路線見直しの方向性検討",
            "plan_text": "生活交通バス路線維持支援 / バス運行便数利用者数調査 / バス路線の見直し",
            "target_text": "生活交通バス路線維持、先行エリアでのバス路線の見直し",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p017-w002",
            "item_name": "運転手不足対策",
            "current_text": "２種免許取得支援 50人/年",
            "plan_text": "２種免許取得支援50人/年 / 新たな運転手確保支援（就職支援など）",
            "target_text": "２種免許取得50人/年 / 新たな運転手確保支援の実施",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p017-w003",
            "item_name": "グリーンスローモビリティの導入",
            "current_text": "本格運行3地区 / 実証調査1地区",
            "plan_text": "1台",
            "target_text": "本格運行4地区",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p017-w004",
            "item_name": "コミュニティバスの収支改善",
            "current_text": "泉地域、大宮台コミュニティバス運行",
            "plan_text": "泉地域、大宮台コミュニティ運行 / コミュニティバス収支改善調査",
            "target_text": "泉地域、大宮台コミュニティバス運行",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p017-w005",
            "item_name": "新たな地域公共交通導入に向けた社会実験",
            "current_text": "本格運行1地区 / 社会実験3地区",
            "plan_text": "本格運行3地区 / 社会実験2地区",
            "target_text": "本格運行3地区 / 社会実験2地区",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p017-w006",
            "item_name": "公共交通の利用促進（GTFS*化支援）",
            "current_text": "―",
            "plan_text": "3社",
            "target_text": "3社",
            "parse_status": "reviewed_structured",
        },
    ],
    "chiba-f07-p022": [
        {
            "work_item_id": "chiba-f07-p022-w001",
            "item_name": "自転車利活用の拠点設置",
            "current_text": "16か所",
            "plan_text": "46箇所",
            "target_text": "62か所",
            "parse_status": "reviewed_structured",
        },
        {
            "work_item_id": "chiba-f07-p022-w002",
            "item_name": "自転車走行環境の整備",
            "current_text": "自転車レーン等整備88.9km",
            "plan_text": "予備設計1.8km / 詳細設計3.3km / 整備9km",
            "target_text": "自転車レーン等整備97.9km",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p022-w003",
            "item_name": "放置自転車対策",
            "current_text": "自転車駐車場等整備147か所",
            "plan_text": "一時利用駐輪場10か所 / 自動二輪受け入れ8か所 / 立体駐輪場整備1か所 / 駐輪場用地取得1か所",
            "target_text": "自転車駐車場設備の充実",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f07-p023": [
        {
            "work_item_id": "chiba-f07-p023-w001",
            "item_name": "デジタル人材育成（こどもや若者の学びの場の創出）",
            "current_text": "デジタル人材育成プログラム実施",
            "plan_text": "デジタル人材育成プログラム / 学びの場の環境整備",
            "target_text": "実施・環境整備",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f07-p025": [
        {
            "work_item_id": "chiba-f07-p025-w001",
            "item_name": "多様な世代が安心して住み続けられる環境整備",
            "current_text": "団地内移動手段の検討",
            "plan_text": "団地内移動手段の検討・社会実験",
            "target_text": "方策実施の検討",
            "parse_status": "reviewed_source_wrap_preserved",
        },
        {
            "work_item_id": "chiba-f07-p025-w002",
            "item_name": "地域資源の活用",
            "current_text": "花見川と団地商店街の連携実施",
            "plan_text": "花見川サイクリングコースと団地商店街の連携等",
            "target_text": "花見川サイクリングコースと団地商店街の連携等",
            "parse_status": "reviewed_source_wrap_preserved",
        },
    ],
    "chiba-f07-p029": [
        {
            "work_item_id": "chiba-f07-p029-w001",
            "item_name": "配水管の整備",
            "current_text": "― / ―",
            "plan_text": "管網計算・実施設計 / 配水管の整備2.3km（富田町他）",
            "target_text": "配水管の整備2.3km",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
    "chiba-f07-p032": [
        {
            "work_item_id": "chiba-f07-p032-w001",
            "item_name": "中央処理区ポンプ場・中央浄化センターの再構築",
            "current_text": "水処理躯体改築４箇所・移設１箇所",
            "plan_text": "水処理施設（中央浄化）躯体移設２箇所・撤去３箇所 / 暫定滞水池改造（中央浄化）２箇所 / 雨水滞水池・分配槽撤去（中央浄化）２箇所 / 沈砂池・ポンプ棟実施設計（中央処理区）",
            "target_text": "水処理躯体改築４箇所・移設３箇所・撤去３箇所 / 暫定滞水池改造２箇所 / 雨水滞水池・分配槽撤去２箇所",
            "parse_status": "reviewed_source_wrap_preserved",
        }
    ],
}

VISUAL_METADATA = {
    "chiba-f07-p006": (98, 102, 4),
    "chiba-f07-p007": (98, 102, 2),
    "chiba-f07-p011": (100, 104, 3),
    "chiba-f07-p013": (101, 105, 1),
    "chiba-f07-p017": (107, 111, 6),
    "chiba-f07-p022": (110, 114, 3),
    "chiba-f07-p023": (112, 116, 1),
    "chiba-f07-p025": (116, 120, 2),
    "chiba-f07-p029": (118, 122, 1),
    "chiba-f07-p032": (119, 123, 1),
}

FIELD07_TEST = '''from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field07.json"
REVIEW = REVIEWED / "current_project_work_items_field07.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field07_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field07_source_capture_covers_all_32_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    assert len(identities) == len(projects) == 32
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field07_source_locations_are_normalized_without_losing_printed_pages():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    review = load(REVIEW)
    assert "zero-based PDF page-index" in review["source_location_semantics"]

    for project in review["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]
        assert project["source_printed_page"] == identity["source_printed_page"]
        page_index = int(project["source_location"].removeprefix("PDF p."))
        assert page_index == project["source_printed_page"] + 3


def test_field07_all_32_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 32
    assert all(
        row["parse_status"] != "pending_visual_column_confirmation" for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field07_has_68_unique_complete_work_items():
    work_items = [
        item for project in load(REVIEW)["projects"] for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 68
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field07_visual_promotions_preserve_representative_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    station = projects["chiba-f07-p006"]["work_items"]
    assert station[0]["current_text"] == (
        "グランドデザイン改定（案）作成 / （仮）中央公園プロムナード周辺の"
        "まちづくりビジョン（案）作成 / 社会実験"
    )
    assert station[1]["target_text"] == "実施設計完了"
    assert station[2]["plan_text"] == station[2]["target_text"] == (
        "中プロ・デザインラボの開催4回/年"
    )

    transit = projects["chiba-f07-p017"]["work_items"]
    assert transit[0]["target_text"] == (
        "生活交通バス路線維持、先行エリアでのバス路線の見直し"
    )
    assert transit[1]["current_text"] == "２種免許取得支援 50人/年"
    assert transit[5]["current_text"] == "―"
    assert transit[5]["plan_text"] == transit[5]["target_text"] == "3社"

    bicycle = projects["chiba-f07-p022"]["work_items"]
    assert bicycle[0]["plan_text"] == "46箇所"
    assert bicycle[1]["current_text"] == "自転車レーン等整備88.9km"
    assert bicycle[1]["plan_text"] == "予備設計1.8km / 詳細設計3.3km / 整備9km"
    assert bicycle[1]["target_text"] == "自転車レーン等整備97.9km"

    water = projects["chiba-f07-p029"]["work_items"][0]
    assert water["current_text"] == "― / ―"
    assert water["plan_text"] == "管網計算・実施設計 / 配水管の整備2.3km（富田町他）"
    assert water["target_text"] == "配水管の整備2.3km"

    sewer = projects["chiba-f07-p032"]["work_items"][0]
    assert sewer["current_text"] == "水処理躯体改築４箇所・移設１箇所"
    assert "沈砂池・ポンプ棟実施設計（中央処理区）" in sewer["plan_text"]
    assert sewer["target_text"].endswith("雨水滞水池・分配槽撤去２箇所")


def test_field07_existing_distance_increment_and_annual_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    kemigawa = projects["chiba-f07-p003"]["work_items"][0]
    special_zone = projects["chiba-f07-p024"]["work_items"][1]
    housing = projects["chiba-f07-p027"]["work_items"][0]
    sewer = projects["chiba-f07-p030"]["work_items"][0]

    assert (kemigawa["current_text"], kemigawa["plan_text"], kemigawa["target_text"]) == (
        "14,642m",
        "1,292m",
        "15,934m",
    )
    assert (special_zone["current_text"], special_zone["plan_text"], special_zone["target_text"]) == (
        "11件",
        "３件増",
        "14件",
    )
    assert (housing["current_text"], housing["plan_text"], housing["target_text"]) == (
        "７件/年",
        "５件/年増",
        "12件/年",
    )
    assert (sewer["current_text"], sewer["plan_text"], sewer["target_text"]) == (
        "12,607ha",
        "5.0ha",
        "12,612ha",
    )


def test_field07_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 32
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 68
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 10
    assert sum(row["structured_work_item_count"] for row in promotions) == 24
    assert evidence["reconciliation"] == {
        "official_field07_project_count": 32,
        "source_capture_coverage": "32/32",
        "structured_project_coverage": "32/32",
        "structured_work_item_count": 68,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 167,
        "cumulative_structured_projects": 167,
        "cumulative_structured_work_items": 358,
        "cumulative_pending_visual_projects": 0,
    }


def test_field07_manifest_advances_visual_review_to_final_field_only():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]
    assert structuring["projects_structured"] == 179
    assert structuring["projects_pending_visual_column_confirmation"] == 10
    assert structuring["structured_work_items"] == 385
    assert len(structuring["pending_review_ids"]) == 10
    assert all(review_id.startswith("chiba-f08-") for review_id in structuring["pending_review_ids"])
'''


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    require(count == 1, f"Expected exactly one {label} replacement, found {count}")
    return text.replace(old, new)


def parse_page(location: str) -> int:
    match = re.fullmatch(r"PDF p\.(\d+)", location)
    if not match:
        raise RuntimeError(f"Unexpected Field 7 source_location: {location}")
    return int(match.group(1))


def normalize_field07_locations() -> None:
    identities = load_json(IDENTITIES)
    for record in identities["records"]:
        printed = record.get("source_printed_page")
        if printed is None:
            printed = parse_page(record["source_location"])
        record["source_printed_page"] = printed
        record["source_location"] = f"PDF p.{printed + 3}"

    for repost in identities.get("displayed_reposts", []):
        printed = repost.get("source_printed_page")
        if printed is None:
            printed = parse_page(repost["source_location"])
        repost["source_printed_page"] = printed
        repost["source_location"] = f"PDF p.{printed + 3}"

    identities["source_location_semantics"] = SOURCE_LOCATION_SEMANTICS
    identities["quality_boundary"] = (
        "公式政策体系表は分野7を重複除外32事業とする。一次identityと再掲を分離し、"
        "source_locationはリポジトリ既存のzero-based PDF page-index規則へ正規化、"
        "source_printed_pageに冊子印刷ページを保持する。事業量・KGI/KPI・年度進捗・成果は"
        "identityレビューから推定しない。"
    )
    write_json(IDENTITIES, identities)


def promote_field07() -> None:
    identities = {row["review_id"]: row for row in load_json(IDENTITIES)["records"]}
    payload = load_json(REVIEW)
    require(payload["structured_project_count"] == 22, "Unexpected Field 7 structured pre-state")
    require(payload["pending_visual_column_confirmation_project_count"] == 10, "Unexpected Field 7 pending pre-state")
    require(payload["structured_work_item_count"] == 44, "Unexpected Field 7 work-item pre-state")

    by_id = {row["review_id"]: row for row in payload["projects"]}
    require(set(PROMOTIONS) == {rid for rid, row in by_id.items() if row["parse_status"] == "pending_visual_column_confirmation"}, "Field 7 pending IDs differ from verified promotions")

    for review_id, project in by_id.items():
        identity = identities[review_id]
        project["source_location"] = identity["source_location"]
        project["source_printed_page"] = identity["source_printed_page"]
        if review_id in PROMOTIONS:
            project["parse_status"] = "reviewed_structured"
            project.pop("raw_table_text", None)
            project["work_items"] = PROMOTIONS[review_id]

    payload["review_status"] = "reviewed_source_capture_and_structuring_complete"
    payload["structured_project_count"] = 32
    payload["pending_visual_column_confirmation_project_count"] = 0
    payload["structured_work_item_count"] = 68
    payload["source_location_semantics"] = SOURCE_LOCATION_SEMANTICS
    payload["quality_boundary"] = (
        "分野7の32 identityすべてをsource captureし、10件の視覚確認待ちも公式PDFレンダリング"
        "画像で列対応を直接確認した。32/32事業・68 work itemsをcurrent/plan/target列で構造化済み。"
        "source_locationは既存のzero-based PDF page-index規則へ正規化し、source_printed_pageに"
        "冊子印刷ページを保持する。未確認値の推定やダッシュの0変換は行わない。"
    )
    write_json(REVIEW, payload)


def update_evidence() -> None:
    evidence = load_json(EVIDENCE)
    projects = {row["review_id"]: row for row in load_json(REVIEW)["projects"]}
    identities = {row["review_id"]: row for row in load_json(IDENTITIES)["records"]}
    evidence["review_status"] = "reviewed_source_capture_and_structuring_complete"
    evidence["structured_project_count"] = 32
    evidence["pending_visual_column_confirmation_project_count"] = 0
    evidence["structured_work_item_count"] = 68
    evidence["pending_visual_column_confirmation"] = []
    evidence["source_location_semantics"] = SOURCE_LOCATION_SEMANTICS
    evidence["source_printed_page_range"] = "95-119"
    evidence["source_pdf_index_range"] = "98-122"
    evidence["visual_confirmed_promotions"] = []
    for review_id, (printed, physical, item_count) in VISUAL_METADATA.items():
        project = projects[review_id]
        identity = identities[review_id]
        require(identity["source_printed_page"] == printed, f"Printed page mismatch for {review_id}")
        require(project["source_location"] == f"PDF p.{printed + 3}", f"PDF index mismatch for {review_id}")
        evidence["visual_confirmed_promotions"].append(
            {
                "review_id": review_id,
                "project_name": project["project_name"],
                "source_location": project["source_location"],
                "source_printed_page": printed,
                "rendered_physical_page": physical,
                "structured_work_item_count": item_count,
            }
        )
    evidence["reconciliation"] = {
        "official_field07_project_count": 32,
        "source_capture_coverage": "32/32",
        "structured_project_coverage": "32/32",
        "structured_work_item_count": 68,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 167,
        "cumulative_structured_projects": 167,
        "cumulative_structured_work_items": 358,
        "cumulative_pending_visual_projects": 0,
    }
    evidence["quality_boundary"] = (
        "分野7の32事業すべての公式事業量表を確認し、残る10事業はSHA-256固定済み公式PDFから"
        "再レンダリングした実ページを直接確認してcurrent/plan/target列を確定した。分野1～7累計"
        "167事業は全件structured、358 work items、visual-confirmation pending 0。Field 7では"
        "印刷ページとPDF実ページのずれを明示し、既存source_location規則へ正規化した。"
    )
    write_json(EVIDENCE, evidence)


def update_global_control_layers() -> None:
    manifest = load_json(MANIFEST)
    structuring = manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 169, "Unexpected global structured pre-state")
    require(structuring["projects_pending_visual_column_confirmation"] == 20, "Unexpected global pending pre-state")
    require(structuring["structured_work_items"] == 361, "Unexpected global work-item pre-state")
    pending = [rid for rid in structuring["pending_review_ids"] if not rid.startswith("chiba-f07-")]
    require(len(pending) == 10 and all(rid.startswith("chiba-f08-") for rid in pending), "Unexpected remaining pending IDs")
    structuring["projects_structured"] = 179
    structuring["projects_pending_visual_column_confirmation"] = 10
    structuring["structured_work_items"] = 385
    structuring["pending_review_ids"] = pending
    manifest["quality_boundary"] = (
        "事業identity 189/189と全189事業の公式表source captureは完了。179事業・385 work itemsは"
        "current/plan/target列を構造化し、10事業は視覚的列確認待ち。分野1～7は公式PDFレンダリング"
        "画像で残件確認を終え167/167事業をstructured化した。残る10事業はすべて分野8で、専用"
        "visual review queueで追跡し、未確認値を推定しない。KGI/KPI・旧計画進捗・予算決算とは"
        "別レイヤーを維持する。"
    )
    write_json(MANIFEST, manifest)

    policy = load_json(POLICY)
    fact = next(row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items")
    fact["structured_project_count"] = 179
    fact["pending_visual_column_confirmation_project_count"] = 10
    fact["structured_work_item_count"] = 385
    fact["interpretation_boundary"] = (
        "全189事業の公式表source captureは完了。179事業・385 work itemsはcurrent/plan/targetを"
        "構造化済み。10事業は複数行セルの列境界を視覚確認待ちとして明示し、未確認値を推定しない。"
        "分野1～7は公式PDFレンダリング画像による残件確認を終え167/167事業をstructured化した。"
    )
    policy["remaining_work"][0] = (
        "現行第2次実施計画189事業の事業量source captureは完了。残る分野8の10事業を公式PDFの"
        "視覚確認で解消し、確認できたものだけproject-scoped work_itemsへ昇格する。"
    )
    policy["quality_boundary"] = (
        "Phase 13 Chiba review remains in progress beyond the completed project identity and source-capture "
        "layers. Project quantity source capture is 189/189 complete: 179 projects and 385 work items are "
        "structured, while 10 Field 8 projects remain explicitly pending visual column confirmation. Fields "
        "1 through 7 are fully structured at 167/167 projects after direct official-PDF rendered-page "
        "confirmation. Historical FY2024 progress remains tied to the 2023-2025 first implementation plan. "
        "Budget and settlement states remain separate. No independent policy-achievement judgment, causal "
        "attribution, version linkage, or automatic cross-city comparability is inferred."
    )
    write_json(POLICY, policy)

    plan = load_json(PLAN)
    universe = next(row for row in plan["records"] if row["id"] == "chiba-current-project-universe")
    universe["review_note"] = (
        "189事業のidentity層と事業量source captureは完了。179事業・385 work itemsを構造化、"
        "分野8の10事業を視覚列確認待ちとして別管理する。"
    )
    work_items = next(row for row in plan["records"] if row["id"] == "chiba-current-project-work-items")
    work_items["statement"] = (
        "現行189事業の取組項目、令和7年度末現況、計画内容、令和10年度末目標について全事業の"
        "source captureを完了。179事業・385 work itemsを構造化し、分野8の10事業は複数行セルの"
        "列境界を視覚確認待ちとして保持する。"
    )
    work_items["structured_project_count"] = 179
    work_items["pending_visual_column_confirmation_project_count"] = 10
    work_items["structured_work_item_count"] = 385
    work_items["review_note"] = (
        "source capture完了と3列構造化完了を分離する。分野1～7は公式PDFレンダリングページ画像で"
        "残件を直接確認し167/167事業をstructured化した。残る分野8の10事業は視覚確認なしに"
        "current/plan/targetを推定せず、ダッシュを0へ変換しない。"
    )
    plan["quality_boundary"] = (
        "Chiba Phase 13 has completed 189/189 project identity and project-quantity source capture. Of the "
        "current project quantity layer, 179 projects and 385 work items are structured while 10 Field 8 "
        "projects remain explicitly pending visual column confirmation. Fields 1 through 7 are fully structured "
        "at 167/167 projects after direct official-PDF rendered-page review. Historical FY2024 progress remains "
        "tied to the 2023-2025 first implementation plan. Policy indicators, project quantities, annual progress, "
        "budget, settlement, causal attribution, independent achievement judgments, and cross-city comparability "
        "remain distinct review units."
    )
    plan["next_action"] = (
        "Resolve the remaining 10 Field 8 project-quantity records pending visual column confirmation against "
        "the official second implementation plan. Promote only visually verified current/plan/2028-target "
        "column assignments; then review versioned linkage between the historical 360-project universe and "
        "current 189 projects, followed by conservative project-level budget/settlement linkage."
    )
    write_json(PLAN, plan)


def update_tests() -> None:
    (TESTS / "test_phase13_chiba_project_work_items_field07.py").write_text(
        FIELD07_TEST,
        encoding="utf-8",
    )

    alignment = TESTS / "test_phase13_chiba_project_work_item_alignment.py"
    text = alignment.read_text(encoding="utf-8")
    text = replace_once(text, '"structured_project_count": 169,', '"structured_project_count": 179,', "alignment structured")
    text = replace_once(text, '"pending_visual_column_confirmation_project_count": 20,', '"pending_visual_column_confirmation_project_count": 10,', "alignment pending")
    text = replace_once(text, '"structured_work_item_count": 361,', '"structured_work_item_count": 385,', "alignment work items")
    text = replace_once(
        text,
        'assert len(work_manifest["work_item_structuring"]["pending_review_ids"]) == 20',
        'assert len(work_manifest["work_item_structuring"]["pending_review_ids"]) == 10',
        "alignment pending list",
    )
    text = replace_once(
        text,
        "def test_chiba_field06_completion_advances_visual_review_to_field07():",
        "def test_chiba_field07_completion_advances_visual_review_to_field08():",
        "alignment test name",
    )
    text = replace_once(text, 'assert "20" in policy["remaining_work"][0]', 'assert "10" in policy["remaining_work"][0]', "alignment remaining")
    text = replace_once(text, 'assert "20" in plan["next_action"]', 'assert "10" in plan["next_action"]', "alignment next action")
    text = replace_once(
        text,
        '        "chiba-f06-",\n    )',
        '        "chiba-f06-",\n        "chiba-f07-",\n    )',
        "alignment completed fields",
    )
    alignment.write_text(text, encoding="utf-8")

    queue_test = TESTS / "test_phase13_chiba_project_work_item_visual_review_queue.py"
    text = queue_test.read_text(encoding="utf-8")
    text = text.replace("all_20_pending_projects", "all_10_pending_projects")
    text = replace_once(
        text,
        'assert len(queued_ids) == len(set(queued_ids)) == 20',
        'assert len(queued_ids) == len(set(queued_ids)) == 10',
        "queue pending count",
    )
    text = replace_once(
        text,
        "        0,\n        10,\n        10,\n    ]",
        "        0,\n        0,\n        10,\n    ]",
        "queue field counts",
    )
    text = replace_once(
        text,
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 20',
        'assert sum(batch["pending_count"] for batch in queue["batches"]) == 10',
        "queue batch sum",
    )
    text = replace_once(text, "assert len(structured_ids) == 169", "assert len(structured_ids) == 179", "queue structured IDs")
    text = replace_once(text, '"projects_structured": 169,', '"projects_structured": 179,', "queue source structured")
    text = replace_once(text, '"structured_work_items": 361,', '"structured_work_items": 385,', "queue source work items")
    text = replace_once(text, '"projects_pending_visual_column_confirmation": 20,', '"projects_pending_visual_column_confirmation": 10,', "queue source pending")
    start = text.index("def test_next_visual_batch_starts_with_field07_official_order():")
    text = text[:start] + '''def test_next_visual_batch_starts_with_field08_official_order():
    queue = load(QUEUE)

    assert queue["execution_order"] == "official_field_and_project_order"
    assert all(batch["pending_count"] == 0 for batch in queue["batches"][:7])
    assert queue["next_batch"] == {
        "field_code": "8",
        "field_name": "地域経済",
        "pending_review_ids": [
            "chiba-f08-p004",
            "chiba-f08-p006",
            "chiba-f08-p008",
            "chiba-f08-p009",
            "chiba-f08-p010",
            "chiba-f08-p011",
            "chiba-f08-p013",
            "chiba-f08-p014",
            "chiba-f08-p021",
            "chiba-f08-p022",
        ],
    }
    assert "推定しない" in queue["resolution_rule"]
    assert "10事業" in queue["quality_boundary"]
'''
    queue_test.write_text(text, encoding="utf-8")

    policy_test = TESTS / "test_phase13_chiba_policy_indicators.py"
    text = policy_test.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "def test_chiba_plan_review_reflects_field06_visual_completion():",
        "def test_chiba_plan_review_reflects_field07_visual_completion():",
        "policy test name",
    )
    text = replace_once(text, '== 169\n', '== 179\n', "policy structured")
    text = replace_once(text, '== 20\n', '== 10\n', "policy pending")
    text = replace_once(text, '== 361\n', '== 385\n', "policy work items")
    text = replace_once(text, 'assert "20" in review["next_action"]', 'assert "10" in review["next_action"]', "policy next action")
    policy_test.write_text(text, encoding="utf-8")


def validate() -> None:
    identities = load_json(IDENTITIES)
    review = load_json(REVIEW)
    manifest = load_json(MANIFEST)
    items = [item for project in review["projects"] for item in project["work_items"]]
    require(len(items) == 68, "Field 7 should contain 68 work items")
    require(all(project["parse_status"] != "pending_visual_column_confirmation" for project in review["projects"]), "Field 7 still contains pending projects")
    require(all("source_printed_page" in row for row in identities["records"]), "Field 7 identity printed pages incomplete")
    structuring = manifest["work_item_structuring"]
    require(structuring["projects_structured"] == 179, "Global structured should be 179")
    require(structuring["projects_pending_visual_column_confirmation"] == 10, "Global pending should be 10")
    require(structuring["structured_work_items"] == 385, "Global work items should be 385")
    require(all(rid.startswith("chiba-f08-") for rid in structuring["pending_review_ids"]), "Non-Field-8 pending ID remains")


def main() -> None:
    normalize_field07_locations()
    promote_field07()
    update_evidence()
    update_global_control_layers()
    update_tests()
    subprocess.run([sys.executable, str(QUEUE_BUILDER)], cwd=ROOT, check=True)
    validate()


if __name__ == "__main__":
    main()
