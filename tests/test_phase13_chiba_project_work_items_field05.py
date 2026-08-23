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

    assert len(identities) == 7
    assert len(projects) == 7
    assert len({row["review_id"] for row in projects}) == 7
    assert identity_pairs == project_pairs


def test_field05_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}

    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field05_has_three_structured_projects_and_four_explicit_pending_projects():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row.get("parse_status") == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 3
    assert len(pending) == 4
    assert {row["review_id"] for row in pending} == {
        "chiba-f05-p001",
        "chiba-f05-p003",
        "chiba-f05-p006",
        "chiba-f05-p007",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field05_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == 5
    assert len(ids) == len(set(ids)) == 5
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field05_preserves_annual_increment_and_compound_program_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    women = projects["chiba-f05-p002"]["work_items"][0]
    foreign = projects["chiba-f05-p004"]["work_items"]
    association = projects["chiba-f05-p005"]["work_items"][0]

    assert women["current_text"] == "―"
    assert women["plan_text"] == (
        "デジタル人材養成講座の開催1回/年 / 企業マッチング支援1回/年"
    )
    assert women["target_text"] == (
        "デジタル人材育成養成講座の開催1回/年 / 企業マッチング支援1回/年"
    )
    assert foreign[2]["plan_text"] == (
        "通訳派遣45件増/年 / 翻訳対応20件増/年 / "
        "災害時語学ボランティア派遣12回/年 / 多言語防災ガイドブック作成"
    )
    assert foreign[2]["target_text"] == foreign[2]["plan_text"]
    assert association["current_text"] == "検討"
    assert association["plan_text"] == "1回/年"
    assert association["target_text"] == "1回/年"


def test_field05_dash_current_values_remain_missing_state_not_zero():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    dash_items = [item for item in work_items if item["current_text"] == "―"]

    assert len(dash_items) == 3
    assert all(item["current_text"] != "0" for item in dash_items)


def test_field05_evidence_reconciles_local_and_cumulative_progress():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 7
    assert evidence["source_captured_project_count"] == 7
    assert evidence["structured_project_count"] == 3
    assert evidence["pending_visual_column_confirmation_project_count"] == 4
    assert evidence["structured_work_item_count"] == 5
    assert evidence["reconciliation"] == {
        "official_field05_project_count": 7,
        "source_capture_coverage": "7/7",
        "structured_project_coverage": "3/7",
        "structured_work_item_count": 5,
        "pending_project_count": 4,
        "cumulative_source_captured_projects": 120,
        "cumulative_structured_projects": 91,
        "cumulative_structured_work_items": 200,
        "cumulative_pending_visual_projects": 29,
    }


def test_field05_manifest_retains_progress_as_later_fields_advance():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]
    field05_pending = {
        "chiba-f05-p001",
        "chiba-f05-p003",
        "chiba-f05-p006",
        "chiba-f05-p007",
    }

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] >= 120
    assert capture["projects_remaining"] == 189 - capture["projects_reviewed"]
    assert capture["field_counts_reviewed"]["environment_nature"] == 30
    assert capture["field_counts_reviewed"]["safety_security"] == 31
    assert capture["field_counts_reviewed"]["health_welfare"] == 18
    assert capture["field_counts_reviewed"]["children_education"] == 34
    assert capture["field_counts_reviewed"]["community"] == 7
    assert sum(capture["field_counts_reviewed"].values()) == capture["projects_reviewed"]
    assert structuring["projects_structured"] >= 91
    assert structuring["projects_pending_visual_column_confirmation"] >= 29
    assert structuring["projects_not_yet_source_captured"] == capture["projects_remaining"]
    assert structuring["structured_work_items"] >= 200
    assert field05_pending <= set(structuring["pending_review_ids"])
