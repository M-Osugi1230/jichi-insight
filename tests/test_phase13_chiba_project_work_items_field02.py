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
    assert len(identities) == len(projects) == 31
    assert len({row["review_id"] for row in projects}) == 31
    assert identity_pairs == project_pairs


def test_field02_all_31_projects_are_structured_after_visual_review():
    projects = load(REVIEW)["projects"]
    assert all(row.get("parse_status") != "pending_visual_column_confirmation" for row in projects)
    assert all(row["work_items"] for row in projects)


def test_field02_has_76_unique_complete_work_items():
    work_items = [item for project in load(REVIEW)["projects"] for item in project["work_items"]]
    ids = [item["work_item_id"] for item in work_items]
    assert len(work_items) == len(ids) == len(set(ids)) == 76
    assert all(item["item_name"].strip() for item in work_items)
    assert all(item["current_text"].strip() for item in work_items)
    assert all(item["plan_text"].strip() for item in work_items)
    assert all(item["target_text"].strip() for item in work_items)
    assert {item["parse_status"] for item in work_items} <= {
        "reviewed_structured",
        "reviewed_source_wrap_preserved",
    }


def test_field02_visual_promotions_preserve_confirmed_table_semantics():
    projects = {row["review_id"]: row for row in load(REVIEW)["projects"]}
    assert projects["chiba-f02-p001"]["work_items"][0]["plan_text"] == (
        "高潮避難計画の策定 / 市民向け周知啓発 / 避難訓練の実施2地区"
    )
    assert projects["chiba-f02-p009"]["work_items"][0]["target_text"] == "新橋供用開始"
    assert projects["chiba-f02-p012"]["work_items"][0]["plan_text"] == (
        "整備5.84km / 管網計算、実施設計"
    )
    fire = projects["chiba-f02-p019"]["work_items"]
    assert [row["current_text"] for row in fire] == ["7基", "―", "―", "81か所"]
    assert [row["target_text"] for row in fire] == ["10基", "3基", "2基", "84か所"]
    roads = projects["chiba-f02-p028"]["work_items"]
    assert len(roads) == 7
    assert roads[4]["target_text"] == "設置完了"
    assert roads[6]["plan_text"] == roads[6]["target_text"] == "120基"


def test_field02_evidence_records_complete_visual_resolution():
    evidence = load(EVIDENCE)
    assert evidence["review_status"] == "reviewed_source_capture_and_structuring_complete"
    assert evidence["structured_project_count"] == 31
    assert evidence["pending_visual_column_confirmation_project_count"] == 0
    assert evidence["structured_work_item_count"] == 76
    assert evidence["pending_visual_column_confirmation"] == []
    assert len(evidence["visual_confirmed_promotions"]) == 9
    assert sum(row["structured_work_item_count"] for row in evidence["visual_confirmed_promotions"]) == 22
    assert evidence["reconciliation"]["cumulative_structured_projects"] == 61
    assert evidence["reconciliation"]["cumulative_structured_work_items"] == 157
    assert evidence["reconciliation"]["cumulative_pending_visual_projects"] == 0


def test_field02_manifest_records_completed_field_and_current_totals():
    manifest = load(MANIFEST)
    structuring = manifest["work_item_structuring"]
    assert structuring["projects_structured"] == 144
    assert structuring["projects_pending_visual_column_confirmation"] == 45
    assert structuring["structured_work_items"] == 318
    assert all(
        not review_id.startswith("chiba-f02-")
        for review_id in structuring["pending_review_ids"]
    )
