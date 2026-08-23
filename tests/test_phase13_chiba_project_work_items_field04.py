from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field04.json"
REVIEW = REVIEWED / "current_project_work_items_field04.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field04_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field04_source_capture_covers_all_34_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == len(projects) == 34
    assert len({row["review_id"] for row in projects}) == 34
    assert identity_pairs == project_pairs


def test_field04_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field04_all_34_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]

    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field04_has_64_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 64
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field04_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    helper = projects["chiba-f04-p001"]["work_items"][0]
    assert helper["current_text"] == "実施"
    assert helper["plan_text"] == (
        "多胎児を妊娠・出産し、かつ早産となった家庭を対象にした利用期間の延長 / "
        "利用条件の緩和（子の入院時の利用 / 外出支援）"
    )
    assert helper["target_text"] == "支援拡充"

    west = projects["chiba-f04-p016"]["work_items"][0]
    assert west["current_text"] == "―"
    assert west["plan_text"] == "改修整備計画策定 / 基本設計 / 実施設計 / 機能移転検討"
    assert west["target_text"] == "実施設計完了"

    east = projects["chiba-f04-p017"]["work_items"][0]
    assert east["current_text"] == "基本設計完了 / 実施設計着手"
    assert east["plan_text"] == "実施設計 / 機能移転検討 / 新築工事"
    assert east["target_text"] == "本体工事完了"

    english = projects["chiba-f04-p019"]["work_items"]
    assert english[0]["current_text"] == "試行版に基づく授業実施 / 課題整理"
    assert english[0]["plan_text"] == "試行版に基づく授業実施 / 全校運用実施"
    assert english[0]["target_text"] == "全校運用実施"
    assert english[1]["current_text"] == "実証事業 2校"
    assert english[1]["plan_text"] == "実証事業 3校 / 研究発表 / 全中学校へ導入"
    assert english[1]["target_text"] == "全中学校へ導入"

    hvac = projects["chiba-f04-p021"]["work_items"]
    assert (hvac[0]["current_text"], hvac[0]["plan_text"], hvac[0]["target_text"]) == (
        "実施設計59校",
        "基本設計・実施設計108校",
        "実施設計 全校完了",
    )
    assert (hvac[1]["current_text"], hvac[1]["plan_text"], hvac[1]["target_text"]) == (
        "整備工事30校",
        "整備工事110校",
        "整備工事140校完了",
    )

    cabinet = projects["chiba-f04-p022"]["work_items"][0]
    assert cabinet["current_text"] == "―"
    assert cabinet["plan_text"] == "技術動向や現状の問題点等の調査・分析 / 整備計画策定"
    assert cabinet["target_text"] == "ＣＡＢＩＮＥＴ調達契約完了"

    placement = projects["chiba-f04-p025"]["work_items"][0]
    assert placement["current_text"] == "実施方針改訂"
    assert placement["plan_text"] == "実施方針改訂等の周知 / 実施"
    assert placement["target_text"] == "実施"

    diverse = projects["chiba-f04-p026"]["work_items"]
    assert (diverse[0]["current_text"], diverse[0]["plan_text"], diverse[0]["target_text"]) == (
        "実施設計",
        "解体工事",
        "解体工事完了",
    )
    assert diverse[1]["current_text"] == "―"
    assert diverse[1]["plan_text"] == "基本設計 / 実施設計 / 大規模改造工事"
    assert diverse[1]["target_text"] == "大規模改造工事"


def test_field04_existing_increment_annual_and_transition_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    childcare = projects["chiba-f04-p005"]["work_items"]
    assert childcare[0]["current_text"] == "54か所"
    assert childcare[0]["plan_text"] == "5か所増"
    assert childcare[0]["target_text"] == "59か所"
    assert childcare[5]["plan_text"] == "2件/年"

    temporary = projects["chiba-f04-p008"]["work_items"][0]
    assert temporary["current_text"] == "77か所（一般型33か所、余裕活用型44か所）"
    assert temporary["target_text"] == "86か所（一般型36か所、余裕活用型50か所）"

    club = projects["chiba-f04-p031"]["work_items"][0]
    assert club["current_text"] == "実証事業実施 / 課題整理・在り方検討"
    assert club["plan_text"] == club["target_text"] == "本格実施"

    support = projects["chiba-f04-p033"]["work_items"][2]
    assert support["current_text"] == "20校"
    assert support["plan_text"] == "4校増"
    assert support["target_text"] == "14校（アフタースクール10校移行）"


def test_field04_dash_variants_are_preserved_not_converted_to_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] in {"―", "－"}]

    assert len(dash_items) >= 15
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field04_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 34
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 64
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 8
    assert sum(row["structured_work_item_count"] for row in promotions) == 11
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 113
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 254
    assert evidence["reconciliation"]["cumulative_pending_visual_projects"] == 0


def test_field04_manifest_records_completed_field_and_current_progress():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]

    assert structuring["projects_structured"] >= 156
    assert structuring["projects_pending_visual_column_confirmation"] <= 33
    assert structuring["structured_work_items"] >= 339
    assert all(
        not review_id.startswith("chiba-f04-")
        for review_id in structuring["pending_review_ids"]
    )
