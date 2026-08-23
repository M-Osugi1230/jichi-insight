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
    assert len(identities) == len(projects) == 30
    assert {(row["review_id"], row["project_name"]) for row in identities} == {
        (row["review_id"], row["project_name"]) for row in projects
    }


def test_field01_all_30_projects_and_81_work_items_are_structured():
    projects = combined_projects()
    work_items = [item for project in projects for item in project["work_items"]]
    ids = [item["work_item_id"] for item in work_items]

    assert all(
        row.get("parse_status") != "pending_visual_column_confirmation"
        for row in projects
    )
    assert len(work_items) == len(ids) == len(set(ids)) == 81
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)


def test_field01_key_source_semantics_and_visual_rows_remain_exact():
    projects = {row["review_id"]: row for row in combined_projects()}
    p002 = projects["chiba-f01-p002"]["work_items"][0]
    park = projects["chiba-f01-p018"]["work_items"]
    minato = projects["chiba-f01-p020"]["work_items"][0]
    zoo = projects["chiba-f01-p026"]["work_items"]

    assert (p002["current_text"], p002["plan_text"], p002["target_text"]) == (
        "15件/年",
        "10件増",
        "25件/年",
    )
    assert park[1]["plan_text"] == "測量・基本設計 / 実施設計 / 施設整備"
    assert park[3]["target_text"] == (
        "多目的広場実施設計完了 / 関係者との意見交換実施 / サウンディング調査完了"
    )
    assert minato["target_text"] == "再整備基本計画策定 / サウンディング調査*"
    assert len(zoo) == 7
    assert zoo[6]["plan_text"] == zoo[6]["target_text"]
    assert any(
        item["current_text"] == "―" for project in projects.values() for item in project["work_items"]
    )


def test_field01_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    promotions = {row["review_id"]: row for row in evidence["visual_confirmed_promotions"]}

    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 30
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 81
    assert evidence["pending_visual_column_confirmation"] == []
    assert set(promotions) == {
        "chiba-f01-p018",
        "chiba-f01-p020",
        "chiba-f01-p026",
        "chiba-f01-p029",
    }


def test_field01_manifest_stays_complete_as_later_fields_advance():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]

    assert manifest["project_universe"] == 189
    assert manifest["work_item_source_capture"]["projects_reviewed"] == 189
    assert structuring["projects_structured"] >= 144
    assert structuring["projects_pending_visual_column_confirmation"] <= 45
    assert structuring["projects_not_yet_source_captured"] == 0
    assert structuring["structured_work_items"] >= 318
    assert all(
        not review_id.startswith("chiba-f01-")
        for review_id in structuring["pending_review_ids"]
    )
