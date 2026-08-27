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


def test_field08_is_fully_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    pending = [
        row for row in projects if row["parse_status"] == "pending_visual_column_confirmation"
    ]
    assert len(projects) == 22
    assert pending == []
    assert all(row["work_items"] for row in projects)
    assert all(
        row["source_location"] == f"PDF p.{row['source_printed_page'] + 3}" for row in projects
    )


def test_field08_structured_work_items_are_unique_and_complete():
    work_items = [item for project in load(REVIEW)["projects"] for item in project["work_items"]]
    ids = [item["work_item_id"] for item in work_items]

    assert len(work_items) == len(ids) == len(set(ids)) == 48
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field08_preserves_representative_source_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    sales = projects["chiba-f08-p004"]["work_items"][0]
    market = projects["chiba-f08-p006"]["work_items"][0]
    tourism = projects["chiba-f08-p010"]["work_items"][2]
    inbound = projects["chiba-f08-p011"]["work_items"][0]
    forest = projects["chiba-f08-p022"]["work_items"][1]

    assert sales["plan_text"] == "制度拡充 / 助成６件"
    assert market["plan_text"] == "事業者公募・選定 / 調査・設計"
    assert (
        tourism["target_text"] == "千葉市里山サイクリングマップの改訂 / イベント開催・出展３回/年"
    )
    assert inbound["current_text"] == "インバウンド団体バスツアー造成支援金交付数30件/年"
    assert inbound["plan_text"] == "ＯＴＡサイトでの市内ツアー販売支援事業15件"
    assert inbound["target_text"] == "ＯＴＡサイトでの市内ツアー販売支援事業５件/年"
    assert forest["target_text"].endswith("活動組織支援４組織")


def test_field08_evidence_closes_source_capture_to_189_of_189():
    evidence = load(EVIDENCE)

    assert evidence["identity_project_count"] == 22
    assert evidence["source_captured_project_count"] == 22
    assert evidence["structured_project_count"] == 22
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 48
    assert evidence["reconciliation"]["cumulative_source_captured_projects"] == 189
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 189
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 406
    assert len(evidence["visual_confirmed_promotions"]) == 10


def test_work_item_manifest_records_full_structuring_completion():
    manifest = load(MANIFEST)
    capture = manifest["work_item_source_capture"]
    structuring = manifest["work_item_structuring"]

    assert manifest["project_universe"] == 189
    assert manifest["project_identity_coverage"] == {"reviewed": 189, "remaining": 0}
    assert capture["projects_reviewed"] == 189
    assert capture["projects_remaining"] == 0
    assert sum(capture["field_counts_reviewed"].values()) == 189
    assert structuring == {
        "projects_structured": 189,
        "projects_pending_visual_column_confirmation": 0,
        "projects_not_yet_source_captured": 0,
        "structured_work_items": 406,
        "pending_review_ids": [],
    }
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
