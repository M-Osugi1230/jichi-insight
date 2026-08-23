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

    assert len(identities) == 18
    assert len(projects) == 18
    assert len({row["review_id"] for row in projects}) == 18
    assert identity_pairs == project_pairs


def test_field03_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field03_has_14_structured_projects_and_four_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 14
    assert len(pending) == 4
    assert {row["review_id"] for row in pending} == {
        "chiba-f03-p004",
        "chiba-f03-p005",
        "chiba-f03-p006",
        "chiba-f03-p007",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field03_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 23
    assert len(ids) == len(set(ids)) == 23
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field03_preserves_increment_annual_and_state_semantics_as_source_text():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    dental = projects["chiba-f03-p001"]["work_items"]
    facilities = projects["chiba-f03-p012"]["work_items"]
    farming = projects["chiba-f03-p014"]["work_items"]
    support = projects["chiba-f03-p015"]["work_items"]

    assert dental[1]["current_text"] == "7校"
    assert dental[1]["plan_text"] == "30校増"
    assert dental[1]["target_text"] == "37校"
    assert facilities[0]["plan_text"] == "3か所増 / 補助単価増額"
    assert farming[0]["plan_text"] == "奨励金5件/年"
    assert farming[0]["target_text"] == "奨励金5件/年"
    assert support[0]["plan_text"] == (
        "利用日ごとの加算 / 入浴実施への加算 / 送迎実施への加算"
    )
    assert support[0]["target_text"] == "各加算の実施"


def test_field03_dash_values_remain_missing_state_not_numeric_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]

    assert len(dash_items) >= 10
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field03_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 18
    assert evidence["source_captured_project_count"] == 18
    assert evidence["structured_project_count"] == 14
    assert evidence["pending_visual_column_confirmation_project_count"] == 4
    assert evidence["structured_work_item_count"] == 23
    assert evidence["reconciliation"] == {
        "official_field03_project_count": 18,
        "source_capture_coverage": "18/18",
        "structured_project_coverage": "14/18",
        "structured_work_item_count": 23,
        "pending_project_count": 4,
        "cumulative_source_captured_projects": 79,
        "cumulative_structured_projects": 62,
        "cumulative_structured_work_items": 142,
        "cumulative_pending_visual_projects": 17,
    }


def test_field03_manifest_retains_progress_as_later_fields_advance():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    field03_pending = {
        "chiba-f03-p004",
        "chiba-f03-p005",
        "chiba-f03-p006",
        "chiba-f03-p007",
    }

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] >= 79
    assert capture["projects_remaining"] == 189 - capture["projects_reviewed"]
    assert capture["field_counts_reviewed"]["environment_nature"] == 30
    assert capture["field_counts_reviewed"]["safety_security"] == 31
    assert capture["field_counts_reviewed"]["health_welfare"] == 18
    assert sum(capture["field_counts_reviewed"].values()) == capture["projects_reviewed"]
    assert structuring["projects_structured"] >= 62
    assert structuring["projects_pending_visual_column_confirmation"] >= 17
    assert structuring["projects_not_yet_source_captured"] == capture["projects_remaining"]
    assert structuring["structured_work_items"] >= 142
    assert field03_pending <= set(structuring["pending_review_ids"])
