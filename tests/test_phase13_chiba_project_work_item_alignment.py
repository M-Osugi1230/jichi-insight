from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_MANIFEST = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"
WORK_ITEM_MANIFEST = ROOT / "data/catalog/chiba_current_project_work_item_review_manifest.json"
PLAN_REVIEW = ROOT / "data/reviewed/chiba-city/plan_review.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_policy_manifest_links_project_work_item_manifest():
    policy = load(POLICY_MANIFEST)
    work_items = load(WORK_ITEM_MANIFEST)

    assert policy["project_work_item_review_manifest_path"] == (
        "data/catalog/chiba_current_project_work_item_review_manifest.json"
    )
    assert work_items["work_item_source_capture"] == {
        "projects_reviewed": 189,
        "projects_remaining": 0,
        "field_counts_reviewed": {
            "environment_nature": 30,
            "safety_security": 31,
            "health_welfare": 18,
            "children_education": 34,
            "community": 7,
            "culture_sports": 15,
            "urban_transport": 32,
            "local_economy": 22,
        },
    }


def test_chiba_project_work_item_progress_reconciles_across_control_layers():
    policy = load(POLICY_MANIFEST)
    plan = load(PLAN_REVIEW)
    work_manifest = load(WORK_ITEM_MANIFEST)
    policy_fact = next(
        row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items"
    )
    plan_fact = next(
        row for row in plan["records"] if row["id"] == "chiba-current-project-work-items"
    )
    structuring = work_manifest["work_item_structuring"]

    expected = {
        "source_captured_project_count": 189,
        "structured_project_count": 135,
        "pending_visual_column_confirmation_project_count": 54,
        "structured_work_item_count": 296,
    }
    for key, value in expected.items():
        assert policy_fact[key] == value
        assert plan_fact[key] == value

    assert structuring["projects_structured"] == expected["structured_project_count"]
    assert structuring["projects_pending_visual_column_confirmation"] == (
        expected["pending_visual_column_confirmation_project_count"]
    )
    assert structuring["structured_work_items"] == expected["structured_work_item_count"]
    assert structuring["projects_not_yet_source_captured"] == 0


def test_chiba_source_capture_completion_does_not_claim_full_structuring():
    policy = load(POLICY_MANIFEST)
    work_manifest = load(WORK_ITEM_MANIFEST)
    fact = next(
        row for row in policy["reviewed_facts"] if row["id"] == "chiba-current-project-work-items"
    )

    assert fact["review_status"] == "reviewed_source_capture_complete_structuring_partial"
    assert fact["source_captured_project_count"] == 189
    assert fact["structured_project_count"] < fact["project_universe"]
    assert work_manifest["next_field"] is None
    assert len(work_manifest["work_item_structuring"]["pending_review_ids"]) == 54


def test_chiba_field01_completion_advances_visual_review_to_field02():
    policy = load(POLICY_MANIFEST)
    plan = load(PLAN_REVIEW)
    work_manifest = load(WORK_ITEM_MANIFEST)

    assert "54" in policy["remaining_work"][0]
    assert "視覚確認" in policy["remaining_work"][0]
    assert "54" in plan["next_action"]
    assert "visual column confirmation" in plan["next_action"]
    assert "versioned linkage" in plan["next_action"]
    assert "budget/settlement linkage" in plan["next_action"]
    assert all(
        not review_id.startswith("chiba-f01-")
        for review_id in work_manifest["work_item_structuring"]["pending_review_ids"]
    )
