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


def test_field06_has_six_structured_projects_and_nine_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row["parse_status"] == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]
    assert len(structured) == 6
    assert len(pending) == 9
    assert {row["review_id"] for row in pending} == {
        "chiba-f06-p001",
        "chiba-f06-p002",
        "chiba-f06-p004",
        "chiba-f06-p006",
        "chiba-f06-p007",
        "chiba-f06-p009",
        "chiba-f06-p011",
        "chiba-f06-p013",
        "chiba-f06-p014",
    }
    assert all(
        row["raw_table_text"].strip() and row["work_items"] == []
        for row in pending
    )


def test_field06_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 9
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field06_preserves_annual_increment_and_state_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    museum = projects["chiba-f06-p008"]["work_items"]
    para = projects["chiba-f06-p010"]["work_items"]
    top = projects["chiba-f06-p012"]["work_items"][0]
    urban = projects["chiba-f06-p015"]["work_items"][0]

    assert museum[0]["current_text"] == "―"
    assert museum[0]["plan_text"] == museum[0]["target_text"] == "構築"
    assert museum[1]["current_text"] == "包括連携協定締結"
    assert museum[1]["target_text"] == "開催1回/年"
    assert para[1]["current_text"] == "1回/年"
    assert para[1]["plan_text"] == para[1]["target_text"] == "2回/年"
    assert top["current_text"] == "100校/年"
    assert top["plan_text"] == "3校/年増"
    assert top["target_text"] == "109校/年"
    assert urban["current_text"] == "―"
    assert urban["plan_text"] == urban["target_text"] == "1回"


def test_field06_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)
    assert evidence["identity_project_count"] == 15
    assert evidence["source_captured_project_count"] == 15
    assert evidence["structured_project_count"] == 6
    assert evidence["pending_visual_column_confirmation_project_count"] == 9
    assert evidence["structured_work_item_count"] == 9
    assert evidence["reconciliation"] == {
        "official_field06_project_count": 15,
        "source_capture_coverage": "15/15",
        "structured_project_coverage": "6/15",
        "structured_work_item_count": 9,
        "pending_project_count": 9,
        "cumulative_source_captured_projects": 135,
        "cumulative_structured_projects": 97,
        "cumulative_structured_work_items": 209,
        "cumulative_pending_visual_projects": 38,
    }


def test_work_item_manifest_advances_through_field06_without_inflation():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    field06_pending = {
        "chiba-f06-p001",
        "chiba-f06-p002",
        "chiba-f06-p004",
        "chiba-f06-p006",
        "chiba-f06-p007",
        "chiba-f06-p009",
        "chiba-f06-p011",
        "chiba-f06-p013",
        "chiba-f06-p014",
    }

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] >= 135
    assert capture["projects_remaining"] == 189 - capture["projects_reviewed"]
    assert capture["field_counts_reviewed"]["environment_nature"] == 30
    assert capture["field_counts_reviewed"]["safety_security"] == 31
    assert capture["field_counts_reviewed"]["health_welfare"] == 18
    assert capture["field_counts_reviewed"]["children_education"] == 34
    assert capture["field_counts_reviewed"]["community"] == 7
    assert capture["field_counts_reviewed"]["culture_sports"] == 15
    assert sum(capture["field_counts_reviewed"].values()) == capture["projects_reviewed"]
    assert structuring["projects_structured"] >= 97
    assert structuring["projects_pending_visual_column_confirmation"] >= 38
    assert (
        structuring["projects_not_yet_source_captured"]
        == capture["projects_remaining"]
    )
    assert structuring["structured_work_items"] >= 209
    assert field06_pending <= set(structuring["pending_review_ids"])
