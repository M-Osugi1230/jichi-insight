from __future__ import annotations

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
    identity_pairs = {
        (row["review_id"], row["project_name"]) for row in identities
    }
    project_pairs = {
        (row["review_id"], row["project_name"]) for row in projects
    }

    assert len(identities) == 32
    assert len(projects) == 32
    assert len({row["review_id"] for row in projects}) == 32
    assert identity_pairs == project_pairs


def test_field07_measure_codes_and_source_locations_match_identity_layer():
    identities = {
        row["review_id"]: row for row in load(IDENTITIES)["records"]
    }
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field07_has_22_structured_projects_and_10_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row["parse_status"] == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 22
    assert len(pending) == 10
    assert {row["review_id"] for row in pending} == {
        "chiba-f07-p006",
        "chiba-f07-p007",
        "chiba-f07-p011",
        "chiba-f07-p013",
        "chiba-f07-p017",
        "chiba-f07-p022",
        "chiba-f07-p023",
        "chiba-f07-p025",
        "chiba-f07-p029",
        "chiba-f07-p032",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field07_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 44
    assert len(ids) == len(set(ids)) == 44
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field07_preserves_distance_increment_and_annual_semantics():
    projects = {
        row["review_id"]: row for row in load(REVIEW)["projects"]
    }
    kemigawa = projects["chiba-f07-p003"]["work_items"][0]
    higashimakuhari = projects["chiba-f07-p004"]["work_items"][0]
    special_zone = projects["chiba-f07-p024"]["work_items"][1]
    housing = projects["chiba-f07-p027"]["work_items"][0]
    sewer = projects["chiba-f07-p030"]["work_items"][0]
    rural = projects["chiba-f07-p031"]["work_items"][0]

    assert (
        kemigawa["current_text"],
        kemigawa["plan_text"],
        kemigawa["target_text"],
    ) == ("14,642m", "1,292m", "15,934m")
    assert (
        higashimakuhari["current_text"],
        higashimakuhari["plan_text"],
        higashimakuhari["target_text"],
    ) == ("4,929m", "741m", "5,670m")
    assert special_zone["current_text"] == "11件"
    assert special_zone["plan_text"] == "３件増"
    assert special_zone["target_text"] == "14件"
    assert housing["current_text"] == "７件/年"
    assert housing["plan_text"] == "５件/年増"
    assert housing["target_text"] == "12件/年"
    assert (
        sewer["current_text"],
        sewer["plan_text"],
        sewer["target_text"],
    ) == ("12,607ha", "5.0ha", "12,612ha")
    assert rural["current_text"] == "施設の再編３地区"
    assert rural["plan_text"] == "施設の再編２地区"
    assert rural["target_text"] == "施設の再編５地区"


def test_field07_dash_current_values_remain_missing_state_not_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]

    assert len(dash_items) >= 3
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field07_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 32
    assert evidence["source_captured_project_count"] == 32
    assert evidence["structured_project_count"] == 22
    assert evidence["pending_visual_column_confirmation_project_count"] == 10
    assert evidence["structured_work_item_count"] == 44
    assert evidence["reconciliation"] == {
        "official_field07_project_count": 32,
        "source_capture_coverage": "32/32",
        "structured_project_coverage": "22/32",
        "structured_work_item_count": 44,
        "pending_project_count": 10,
        "cumulative_source_captured_projects": 167,
        "cumulative_structured_projects": 119,
        "cumulative_structured_work_items": 253,
        "cumulative_pending_visual_projects": 48,
    }


def test_field07_manifest_advances_to_final_field_without_inflation():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    field07_pending = {
        "chiba-f07-p006",
        "chiba-f07-p007",
        "chiba-f07-p011",
        "chiba-f07-p013",
        "chiba-f07-p017",
        "chiba-f07-p022",
        "chiba-f07-p023",
        "chiba-f07-p025",
        "chiba-f07-p029",
        "chiba-f07-p032",
    }

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {
        "reviewed": 189,
        "remaining": 0,
    }
    assert capture["projects_reviewed"] >= 167
    assert capture["projects_remaining"] == 189 - capture["projects_reviewed"]
    assert capture["field_counts_reviewed"]["urban_transport"] == 32
    assert sum(capture["field_counts_reviewed"].values()) == capture["projects_reviewed"]
    assert structuring["projects_structured"] >= 119
    assert structuring["projects_pending_visual_column_confirmation"] >= len(
        field07_pending
    )
    assert (
        structuring["projects_not_yet_source_captured"]
        == capture["projects_remaining"]
    )
    assert structuring["structured_work_items"] >= 253
    assert field07_pending <= set(structuring["pending_review_ids"])
    if capture["projects_remaining"] == 22:
        assert manifest["next_field"] == {
            "field_code": "8",
            "field_name": "地域経済",
            "official_project_count": 22,
        }
