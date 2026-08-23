from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field03.json"
REVIEW = REVIEWED / "current_project_work_items_field03.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field03_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field03_source_capture_covers_all_18_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == len(projects) == 18
    assert len({row["review_id"] for row in projects}) == 18
    assert identity_pairs == project_pairs


def test_field03_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field03_all_18_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]

    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert all(row["work_items"] for row in projects)


def test_field03_has_33_unique_complete_work_items():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 33
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field03_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}

    animal = projects["chiba-f03-p004"]["work_items"]
    assert animal[0]["current_text"] == "基本設計 / 測量・境界確定 / 土質調査"
    assert animal[0]["plan_text"] == "実施設計 / 工事 / センター移転"
    assert animal[0]["target_text"] == "移転完了"
    assert animal[1]["current_text"] == "―"

    roads = projects["chiba-f03-p005"]["work_items"]
    assert roads[0]["current_text"] == roads[0]["plan_text"] == "道路整備4路線"
    assert roads[0]["target_text"] == (
        "2路線供用開始 / 1路線冠水対策工事完了 / 1路線用地取得完了 / 道路整備"
    )
    assert roads[1]["target_text"] == "供用開始"

    cemetery = projects["chiba-f03-p006"]["work_items"]
    assert cemetery[0]["plan_text"] == "工事・一部供用開始 / トイレ新築工事"
    assert cemetery[0]["target_text"] == "工事・一部供用開始 / トイレ設置"
    assert cemetery[2]["target_text"] == "認可"

    crematorium = projects["chiba-f03-p007"]["work_items"]
    assert crematorium[0]["plan_text"] == (
        "基本計画策定 / 環境アセスメント実施 / 都市計画決定"
    )
    assert crematorium[1]["plan_text"] == "解体実施設計 / 解体工事"
    assert crematorium[1]["target_text"] == "解体実施設計"


def test_field03_existing_increment_annual_and_dash_semantics_remain_intact():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    dental = projects["chiba-f03-p001"]["work_items"][1]
    facilities = projects["chiba-f03-p012"]["work_items"][0]
    farming = projects["chiba-f03-p014"]["work_items"][0]

    assert (dental["current_text"], dental["plan_text"], dental["target_text"]) == (
        "7校",
        "30校増",
        "37校",
    )
    assert facilities["plan_text"] == "3か所増 / 補助単価増額"
    assert farming["plan_text"] == farming["target_text"] == "奨励金5件/年"
    assert any(
        item["current_text"] == "―"
        for project in projects.values()
        for item in project["work_items"]
    )


def test_field03_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = evidence["visual_confirmed_promotions"]

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 18
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 33
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(promotions) == 4
    assert sum(row["structured_work_item_count"] for row in promotions) == 10
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 79
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 190
    assert evidence["reconciliation"]["cumulative_pending_visual_projects"] == 0


def test_field03_manifest_records_completed_field_and_current_progress():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]

    assert structuring["projects_structured"] >= 148
    assert structuring["projects_pending_visual_column_confirmation"] <= 41
    assert structuring["structured_work_items"] >= 328
    assert all(
        not review_id.startswith("chiba-f03-")
        for review_id in structuring["pending_review_ids"]
    )
