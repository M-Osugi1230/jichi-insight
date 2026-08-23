from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
REVIEWED = ROOT / "data/reviewed/chiba-city"
EVD = ROOT / "data/evidence"
IDENTITIES = CAT / "chiba_current_project_identities_field08.json"
REVIEW = REVIEWED / "current_project_work_items_field08.json"
EVIDENCE = EVD / "chiba_current_project_work_items_field08_evidence.json"
MANIFEST = CAT / "chiba_current_project_work_item_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_field08_source_capture_covers_all_22_identity_projects_exactly():
    identities = load(IDENTITIES)["records"]
    projects = load(REVIEW)["projects"]
    assert len(identities) == len(projects) == 22
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field08_measure_codes_and_source_locations_match_identity_layer():
    identities = {row["review_id"]: row for row in load(IDENTITIES)["records"]}
    for project in load(REVIEW)["projects"]:
        identity = identities[project["review_id"]]
        assert project["measure_code"] == identity["measure_code"]
        assert project["source_location"] == identity["source_location"]


def test_field08_retains_12_structured_and_10_pending_until_its_visual_review():
    projects = load(REVIEW)["projects"]
    pending = [
        row
        for row in projects
        if row["parse_status"] == "pending_visual_column_confirmation"
    ]
    structured = [row for row in projects if row not in pending]

    assert len(structured) == 12
    assert len(pending) == 10
    assert {row["review_id"] for row in pending} == {
        "chiba-f08-p004",
        "chiba-f08-p006",
        "chiba-f08-p008",
        "chiba-f08-p009",
        "chiba-f08-p010",
        "chiba-f08-p011",
        "chiba-f08-p013",
        "chiba-f08-p014",
        "chiba-f08-p021",
        "chiba-f08-p022",
    }
    assert all(row["raw_table_text"].strip() for row in pending)
    assert all(row["work_items"] == [] for row in pending)


def test_field08_structured_work_items_are_unique_and_complete():
    work_items = [
        item
        for project in load(REVIEW)["projects"]
        for item in project["work_items"]
    ]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 27
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field08_preserves_representative_source_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    startup = projects["chiba-f08-p001"]["work_items"]
    location = projects["chiba-f08-p002"]["work_items"][0]
    employment = projects["chiba-f08-p007"]["work_items"][0]
    farming = projects["chiba-f08-p015"]["work_items"][0]

    assert startup[0]["current_text"] == "―"
    assert (startup[1]["current_text"], startup[1]["plan_text"], startup[1]["target_text"]) == (
        "１コース/年",
        "１コース/年増",
        "２コース/年",
    )
    assert (location["current_text"], location["plan_text"], location["target_text"]) == (
        "465件",
        "66件増",
        "531件",
    )
    assert employment["target_text"] == "実施場所２か所 / 実施回数３期/年"
    assert (farming["current_text"], farming["plan_text"], farming["target_text"]) == (
        "７ha",
        "13ha/年増",
        "20ha/年",
    )


def test_field08_evidence_closes_source_capture_to_189_of_189():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 22
    assert evidence["source_captured_project_count"] == 22
    assert evidence["structured_project_count"] == 12
    assert evidence["pending_visual_column_confirmation_project_count"] == 10
    assert evidence["structured_work_item_count"] == 27
    assert evidence["reconciliation"]["cumulative_source_captured_projects"] == 189


def test_work_item_manifest_keeps_source_capture_complete_as_visual_review_advances():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] == 189
    assert capture["projects_remaining"] == 0
    assert sum(capture["field_counts_reviewed"].values()) == 189
    assert structuring["projects_structured"] >= 131
    assert structuring["projects_pending_visual_column_confirmation"] <= 58
    assert structuring["projects_not_yet_source_captured"] == 0
    assert structuring["structured_work_items"] >= 280
    assert len(structuring["pending_review_ids"]) == (
        structuring["projects_pending_visual_column_confirmation"]
    )
    assert manifest["next_field"] is None


def test_all_work_item_review_files_partition_the_189_identity_projects_once():
    manifest = load(MANIFEST)
    captured_projects = []
    for relative_path in manifest["review_paths"]:
        captured_projects.extend(load(ROOT / relative_path)["projects"])

    identity_records = []
    for field_number in range(1, 9):
        path = CAT / f"chiba_current_project_identities_field{field_number:02d}.json"
        identity_records.extend(load(path)["records"])

    captured_ids = [row["review_id"] for row in captured_projects]
    identity_ids = [row["review_id"] for row in identity_records]

    assert len(captured_ids) == len(set(captured_ids)) == 189
    assert len(identity_ids) == len(set(identity_ids)) == 189
    assert set(captured_ids) == set(identity_ids)
