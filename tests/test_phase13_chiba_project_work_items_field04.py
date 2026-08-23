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

    assert len(identities) == 34
    assert len(projects) == 34
    assert len({row["review_id"] for row in projects}) == 34
    assert identity_pairs == project_pairs


def test_field04_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field04_has_26_structured_projects_and_eight_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 26
    assert len(pending) == 8
    assert {row["review_id"] for row in pending} == {
        "chiba-f04-p001",
        "chiba-f04-p016",
        "chiba-f04-p017",
        "chiba-f04-p019",
        "chiba-f04-p021",
        "chiba-f04-p022",
        "chiba-f04-p025",
        "chiba-f04-p026",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field04_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 53
    assert len(ids) == len(set(ids)) == 53
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field04_preserves_increment_annual_component_and_transition_semantics():
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


def test_field04_preserves_source_reported_nonmonotonic_after_school_transition():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
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

    assert len(dash_items) >= 12
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field04_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 34
    assert evidence["source_captured_project_count"] == 34
    assert evidence["structured_project_count"] == 26
    assert evidence["pending_visual_column_confirmation_project_count"] == 8
    assert evidence["structured_work_item_count"] == 53
    assert evidence["reconciliation"] == {
        "official_field04_project_count": 34,
        "source_capture_coverage": "34/34",
        "structured_project_coverage": "26/34",
        "structured_work_item_count": 53,
        "pending_project_count": 8,
        "cumulative_source_captured_projects": 113,
        "cumulative_structured_projects": 88,
        "cumulative_structured_work_items": 195,
        "cumulative_pending_visual_projects": 25,
    }


def test_work_item_manifest_advances_through_field04_without_inflation():
    manifest = load(MANIFEST)

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert manifest["work_item_source_capture"] == {
        "projects_reviewed": 113,
        "projects_remaining": 76,
        "field_counts_reviewed": {
            "environment_nature": 30,
            "safety_security": 31,
            "health_welfare": 18,
            "children_education": 34,
        },
    }
    assert manifest["work_item_structuring"]["projects_structured"] == 88
    assert manifest["work_item_structuring"]["projects_pending_visual_column_confirmation"] == 25
    assert manifest["work_item_structuring"]["projects_not_yet_source_captured"] == 76
    assert manifest["work_item_structuring"]["structured_work_items"] == 195
    assert len(manifest["work_item_structuring"]["pending_review_ids"]) == 25
    assert manifest["next_field"] == {
        "field_code": "5",
        "field_name": "地域社会",
        "official_project_count": 7,
    }
