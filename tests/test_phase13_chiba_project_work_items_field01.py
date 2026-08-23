from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field01.json"
PART01 = REVIEWED / "current_project_work_items_field01_part01.json"
PART02 = REVIEWED / "current_project_work_items_field01_part02.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field01_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def combined_projects():
    return load(PART01)["projects"] + load(PART02)["projects"]


def test_field01_source_capture_covers_all_30_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = combined_projects()
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == 30
    assert len(projects) == 30
    assert len({row["review_id"] for row in projects}) == 30
    assert identity_pairs == project_pairs


def test_field01_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in combined_projects():
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"].startswith("PDF p")


def test_field01_has_26_structured_projects_and_four_explicit_pending_projects():
    projects = combined_projects()
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 26
    assert len(pending) == 4
    assert {row["review_id"] for row in pending} == {
        "chiba-f01-p018",
        "chiba-f01-p020",
        "chiba-f01-p026",
        "chiba-f01-p029",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field01_structured_work_items_have_complete_raw_source_columns():
    work_items = [
        item
        for project in combined_projects()
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 65
    assert len(ids) == len(set(ids)) == 65
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field01_preserves_annual_increment_and_cumulative_semantics_as_text():
    projects = {row["review_id"]: row for row in combined_projects()}
    p002 = {item["work_item_id"]: item for item in projects["chiba-f01-p002"]["work_items"]}
    p008 = projects["chiba-f01-p008"]["work_items"][0]

    assert p002["chiba-f01-p002-w001"] == {
        "work_item_id": "chiba-f01-p002-w001",
        "item_name": "事業者向け省エネルギー設備導入に係る補助",
        "current_text": "15件/年",
        "plan_text": "10件増",
        "target_text": "25件/年",
        "parse_status": "reviewed_structured",
    }
    assert p008["current_text"] == "65.48ha"
    assert p008["plan_text"] == "6ha拡大"
    assert p008["target_text"] == "71.48ha"


def test_field01_dash_current_values_are_preserved_not_converted_to_zero():
    projects = {row["review_id"]: row for row in combined_projects()}
    dash_items = [
        item
        for project in projects.values()
        for item in project["work_items"]
        if item["current_text"] == "―"
    ]

    assert len(dash_items) >= 4
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field01_evidence_reconciles_source_capture_and_structuring():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 30
    assert evidence["source_captured_project_count"] == 30
    assert evidence["structured_project_count"] == 26
    assert evidence["pending_visual_column_confirmation_project_count"] == 4
    assert evidence["structured_work_item_count"] == 65
    assert evidence["reconciliation"] == {
        "official_field01_project_count": 30,
        "source_capture_coverage": "30/30",
        "structured_project_coverage": "26/30",
        "structured_work_item_count": 65,
        "pending_project_count": 4,
    }


def test_field01_work_item_manifest_retains_progress_as_later_fields_advance():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    field01_pending = {
        "chiba-f01-p018",
        "chiba-f01-p020",
        "chiba-f01-p026",
        "chiba-f01-p029",
    }

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] >= 30
    assert capture["projects_remaining"] == 189 - capture["projects_reviewed"]
    assert capture["field_counts_reviewed"]["environment_nature"] == 30
    assert sum(capture["field_counts_reviewed"].values()) == capture["projects_reviewed"]
    assert structuring["projects_structured"] >= 26
    assert structuring["projects_pending_visual_column_confirmation"] >= 4
    assert structuring["projects_not_yet_source_captured"] == capture["projects_remaining"]
    assert structuring["structured_work_items"] >= 65
    assert field01_pending <= set(structuring["pending_review_ids"])
