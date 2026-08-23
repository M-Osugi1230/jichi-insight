from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field02.json"
REVIEW = REVIEWED / "current_project_work_items_field02.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field02_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field02_source_capture_covers_all_31_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    identity_pairs = {(row["review_id"], row["project_name"]) for row in identities}
    project_pairs = {(row["review_id"], row["project_name"]) for row in projects}

    assert len(identities) == 31
    assert len(projects) == 31
    assert len({row["review_id"] for row in projects}) == 31
    assert identity_pairs == project_pairs


def test_field02_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"].startswith("PDF p")


def test_field02_has_22_structured_projects_and_nine_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 22
    assert len(pending) == 9
    assert {row["review_id"] for row in pending} == {
        "chiba-f02-p001",
        "chiba-f02-p009",
        "chiba-f02-p012",
        "chiba-f02-p014",
        "chiba-f02-p016",
        "chiba-f02-p019",
        "chiba-f02-p023",
        "chiba-f02-p026",
        "chiba-f02-p028",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field02_structured_work_items_have_complete_raw_source_columns():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 54
    assert len(ids) == len(set(ids)) == 54
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field02_preserves_facility_and_route_semantics_as_source_text():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    drainage = {
        item["work_item_id"]: item
        for item in projects["chiba-f02-p006"]["work_items"]
    }
    sidewalk = {
        item["work_item_id"]: item
        for item in projects["chiba-f02-p030"]["work_items"]
    }

    assert drainage["chiba-f02-p006-w001"]["current_text"] == "6施設"
    assert drainage["chiba-f02-p006-w001"]["plan_text"] == "6施設"
    assert drainage["chiba-f02-p006-w001"]["target_text"] == "12施設"
    assert sidewalk["chiba-f02-p030-w001"]["current_text"] == (
        "4路線（令和7年度事業量）"
    )
    assert sidewalk["chiba-f02-p030-w003"]["target_text"] == (
        "5路線（供用開始1路線）"
    )


def test_field02_dash_current_values_are_preserved_not_converted_to_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]

    assert len(dash_items) >= 6
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field02_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 31
    assert evidence["source_captured_project_count"] == 31
    assert evidence["structured_project_count"] == 22
    assert evidence["pending_visual_column_confirmation_project_count"] == 9
    assert evidence["structured_work_item_count"] == 54
    assert evidence["reconciliation"] == {
        "official_field02_project_count": 31,
        "source_capture_coverage": "31/31",
        "structured_project_coverage": "22/31",
        "structured_work_item_count": 54,
        "pending_project_count": 9,
        "cumulative_source_captured_projects": 61,
        "cumulative_structured_projects": 48,
        "cumulative_structured_work_items": 119,
        "cumulative_pending_visual_projects": 13,
    }


def test_work_item_manifest_advances_through_field02_without_inflation():
    manifest = load(MANIFEST)

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert manifest["work_item_source_capture"] == {
        "projects_reviewed": 61,
        "projects_remaining": 128,
        "field_counts_reviewed": {
            "environment_nature": 30,
            "safety_security": 31,
        },
    }
    assert manifest["work_item_structuring"]["projects_structured"] == 48
    assert manifest["work_item_structuring"]["projects_pending_visual_column_confirmation"] == 13
    assert manifest["work_item_structuring"]["projects_not_yet_source_captured"] == 128
    assert manifest["work_item_structuring"]["structured_work_items"] == 119
    assert len(manifest["work_item_structuring"]["pending_review_ids"]) == 13
    assert manifest["next_field"] == {
        "field_code": "3",
        "field_name": "健康・福祉",
        "official_project_count": 18,
    }
