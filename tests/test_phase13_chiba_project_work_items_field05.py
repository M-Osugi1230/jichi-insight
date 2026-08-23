from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field05.json"
REVIEW = REVIEWED / "current_project_work_items_field05.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field05_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field05_source_capture_covers_all_seven_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == len(projects) == 7
    assert len({row["review_id"] for row in projects}) == 7
    assert identity_pairs == project_pairs


def test_field05_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field05_all_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert len(projects) == 7
    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field05_has_13_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 13
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field05_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    fair = projects["chiba-f05-p001"]["work_items"]
    assert (fair[0]["current_text"], fair[0]["plan_text"], fair[0]["target_text"]) == (
        "認定申請に向けた準備",
        "認定申請",
        "認定取得",
    )
    assert fair[1]["current_text"] == "フェアトレード産品取扱店の調査"
    assert fair[1]["plan_text"] == fair[1]["target_text"] == "ポスター・ステッカー・のぼり作成"
    assert fair[2]["current_text"] == "―"
    assert fair[2]["plan_text"] == fair[2]["target_text"] == "出前講座3回/年 / 販売会2回/年"
    assert fair[3]["current_text"] == "―"
    assert fair[3]["plan_text"] == "制度創設 / 推進員認定20人"
    assert fair[3]["target_text"] == "推進員認定20人"

    support = projects["chiba-f05-p003"]["work_items"][0]
    assert support["current_text"] == "アウトリーチ支援（訪問） / 電話及びＳＮＳ相談 / 居場所の確保"
    assert support["plan_text"] == (
        "アウトリーチ支援（巡回等）、自立支援・アフターケアの拡充、ステップハウスの運営 / "
        "関係機関連携会議の開催2回/年"
    )
    assert support["target_text"] == (
        "困難な問題を抱える女性への支援体制の強化 / 関係機関連携会議の開催2回/年"
    )

    chishiro = projects["chiba-f05-p006"]["work_items"][0]
    assert chishiro["current_text"] == "実施設計"
    assert chishiro["plan_text"] == "建築工事 / 外構工事"
    assert chishiro["target_text"] == "建築工事、外構工事"

    toke = projects["chiba-f05-p007"]["work_items"]
    assert (toke[0]["current_text"], toke[0]["plan_text"], toke[0]["target_text"]) == (
        "―",
        "基本設計 / 実施設計 / 建築工事",
        "建築工事",
    )
    assert (toke[1]["current_text"], toke[1]["plan_text"], toke[1]["target_text"]) == (
        "―",
        "解体設計 / 解体工事",
        "解体工事完了",
    )


def test_field05_existing_annual_increment_and_compound_program_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    women = projects["chiba-f05-p002"]["work_items"][0]
    foreign = projects["chiba-f05-p004"]["work_items"]
    association = projects["chiba-f05-p005"]["work_items"][0]

    assert women["current_text"] == "―"
    assert women["plan_text"] == "デジタル人材養成講座の開催1回/年 / 企業マッチング支援1回/年"
    assert women["target_text"] == "デジタル人材育成養成講座の開催1回/年 / 企業マッチング支援1回/年"
    assert foreign[2]["plan_text"] == (
        "通訳派遣45件増/年 / 翻訳対応20件増/年 / 災害時語学ボランティア派遣12回/年 / "
        "多言語防災ガイドブック作成"
    )
    assert foreign[2]["target_text"] == foreign[2]["plan_text"]
    assert association["current_text"] == "検討"
    assert association["plan_text"] == association["target_text"] == "1回/年"


def test_field05_dash_current_values_remain_missing_state_not_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]
    assert len(dash_items) == 7
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field05_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 7
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 13
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 4
    assert sum(row["structured_work_item_count"] for row in promotions) == 8
    assert evidence["reconciliation"] == {
        "official_field05_project_count": 7,
        "source_capture_coverage": "7/7",
        "structured_project_coverage": "7/7",
        "structured_work_item_count": 13,
        "pending_project_count": 0,
        "cumulative_source_captured_projects": 120,
        "cumulative_structured_projects": 120,
        "cumulative_structured_work_items": 267,
        "cumulative_pending_visual_projects": 0,
    }


def test_field05_manifest_records_completed_field_and_current_progress():
    structuring = load(MANIFEST)["work_item_structuring"]
    assert structuring["projects_structured"] >= 160
    assert structuring["projects_pending_visual_column_confirmation"] <= 29
    assert structuring["structured_work_items"] >= 347
    assert all(
        not review_id.startswith("chiba-f05-")
        for review_id in structuring["pending_review_ids"]
    )
