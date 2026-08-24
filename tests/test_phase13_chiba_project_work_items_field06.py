from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field06.json"
REVIEW = REVIEWED / "current_project_work_items_field06.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field06_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field06_source_capture_covers_all_15_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    assert len(identities) == len(projects) == 15
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field06_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field06_all_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 15
    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field06_has_23_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 23
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field06_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    art = projects["chiba-f06-p001"]["work_items"]
    assert art[0]["current_text"] == "事業者決定"
    assert art[0]["plan_text"] == "公園整備等 / イベント実施"
    assert art[0]["target_text"] == "公園整備完了 / イベント実施"
    assert art[1]["current_text"] == "事業者決定"
    assert art[1]["target_text"] == "アーティスト・イン・レジデンス運営"

    festival = projects["chiba-f06-p002"]["work_items"][0]
    assert festival["current_text"] == "千葉国際芸術祭2025の実施"
    assert festival["plan_text"] == (
        "千葉開府900年企画の実施 / トリエンナーレ形式による定期開催"
    )
    assert festival["target_text"] == "トリエンナーレ形式による定期開催"

    hall = projects["chiba-f06-p004"]["work_items"]
    assert hall[0]["current_text"] == "基本計画修正"
    assert hall[0]["plan_text"] == "基本計画修正 / 基本設計 / 実施設計"
    assert hall[0]["target_text"] == "実施設計"
    assert hall[1]["current_text"] == "―"
    assert hall[1]["plan_text"] == "用地測量・境界確定 / 不動産鑑定"
    assert hall[1]["target_text"] == "不動産鑑定"

    site = projects["chiba-f06-p006"]["work_items"][0]
    assert site["current_text"] == "検討"
    assert site["plan_text"] == "基本計画策定 / 基本設計 / 実施設計"
    assert site["target_text"] == (
        "史跡整備基本計画策定 / 北貝塚貝層断面観覧施設実施設計完了 / "
        "史跡環境整備実施設計完了"
    )

    museum = projects["chiba-f06-p007"]["work_items"]
    assert museum[0]["current_text"] == "事業者決定"
    assert museum[0]["plan_text"] == "基本設計 / 実施設計 / 工事 / 解体工事"
    assert museum[0]["target_text"] == "工事"
    assert museum[1]["current_text"] == "（連絡歩道橋及び周遊路）測量 / 不動産鑑定"
    assert museum[1]["target_text"] == (
        "（連絡歩道橋及び周遊路）工事 / （歩道改良）詳細設計"
    )

    history = projects["chiba-f06-p009"]["work_items"]
    assert (history[0]["current_text"], history[0]["plan_text"], history[0]["target_text"]) == (
        "編集",
        "編集 / 刊行",
        "刊行",
    )
    assert (history[1]["current_text"], history[1]["plan_text"], history[1]["target_text"]) == (
        "編集",
        "編集",
        "編集",
    )

    pools = projects["chiba-f06-p011"]["work_items"]
    assert pools[0]["current_text"] == "PFI導入可能性調査"
    assert pools[0]["plan_text"] == "事業者選定 / 基本設計 / 実施設計 / 整備工事"
    assert pools[0]["target_text"] == "整備工事"
    assert (
        pools[1]["current_text"]
        == pools[1]["plan_text"]
        == pools[1]["target_text"]
        == "基礎調査"
    )

    arena = projects["chiba-f06-p013"]["work_items"][0]
    assert arena["current_text"] == "基本協定締結"
    assert arena["plan_text"] == (
        "アドバイザリー業務委託 / 事業者選定 / 基盤整備支援 / 民間事業者による整備"
    )
    assert arena["target_text"] == "民間事業者による整備"

    events = projects["chiba-f06-p014"]["work_items"][0]
    assert events["current_text"] == "負担金支援１件/年"
    assert events["plan_text"] == "負担金支援１件/年 / 補助金制度創設 / 補助金支援２件/年"
    assert events["target_text"] == "負担金支援１件/年 / 補助金支援２件/年"


def test_field06_existing_annual_increment_and_state_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    museum = projects["chiba-f06-p008"]["work_items"]
    para = projects["chiba-f06-p010"]["work_items"]
    top = projects["chiba-f06-p012"]["work_items"][0]
    urban = projects["chiba-f06-p015"]["work_items"][0]

    assert museum[0]["current_text"] == "―"
    assert museum[1]["target_text"] == "開催1回/年"
    assert para[1]["current_text"] == "1回/年"
    assert para[1]["plan_text"] == para[1]["target_text"] == "2回/年"
    assert top["current_text"] == "100校/年"
    assert top["plan_text"] == "3校/年増"
    assert top["target_text"] == "109校/年"
    assert urban["current_text"] == "―"
    assert urban["plan_text"] == urban["target_text"] == "1回"


def test_field06_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 15
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 23
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 9
    assert sum(row["structured_work_item_count"] for row in promotions) == 14
    assert evidence["reconciliation"] == {
        "official_field06_project_count": 15,
        "source_capture_coverage": "15/15",
        "structured_project_coverage": "15/15",
        "structured_work_item_count": 23,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 135,
        "cumulative_structured_projects": 135,
        "cumulative_structured_work_items": 290,
        "cumulative_pending_visual_projects": 0,
    }


def test_field06_manifest_records_completed_field_and_current_progress():
    structuring = load(MANIFEST)["work_item_structuring"]
    assert structuring["projects_structured"] >= 169
    assert structuring["projects_pending_visual_column_confirmation"] <= 20
    assert structuring["structured_work_items"] >= 361
    assert all(
        not review_id.startswith("chiba-f06-")
        for review_id in structuring["pending_review_ids"]
    )
