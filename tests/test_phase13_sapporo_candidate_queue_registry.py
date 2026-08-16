from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_candidate_registry_is_exhausted_after_599_final_identities():
    registry = load(REGISTRY)
    summary = registry["summary"]

    assert registry["status"] == (
        "candidate_reconciliation_queue_complete_no_remaining_action_plan_identities"
    )
    assert registry["final_reviewed_identity_count"] == 599
    assert registry["final_action_plan_project_count"] == 599
    assert registry["remaining_final_identity_count"] == 0
    assert registry["candidate_fields"] == []
    assert summary["candidate_field_queue_count"] == 0
    assert summary["candidate_record_count"] == 0
    assert summary["candidate_main_project_record_count"] == 0
    assert summary["candidate_other_project_record_count"] == 0
    assert summary["candidate_reviewed_final_identity_increment"] == 0
    assert summary["final_reviewed_identity_count_remains"] == 599


def test_resolution_history_preserves_all_final_promotions():
    history = load(REGISTRY)["resolution_history"]
    assert [(item["field_id"], item["resolved_record_count"]) for item in history] == [
        ("daily_life_page68", 7),
        ("community", 47),
        ("economy", 74),
        ("environment", 74),
        ("children_youth", 121),
    ]
    assert history[0]["reviewed_count_before"] == 276
    assert history[-1]["reviewed_count_after"] == 599
    assert history[-1]["reviewed_count_before"] == 478


def test_candidate_registry_reconciles_final_main_other_and_annual_target_denominators():
    structural = load(REGISTRY)["structural_reconciliation"]

    assert structural["reviewed_identity_count"] == 599
    assert structural["candidate_identity_count"] == 0
    assert structural["reviewed_plus_candidate_count"] == 599

    assert structural["reviewed_main_project_count"] == 406
    assert structural["candidate_main_project_count"] == 0
    assert structural["final_main_project_count"] == 406

    assert structural["reviewed_other_project_count"] == 193
    assert structural["candidate_other_project_count"] == 0
    assert structural["final_other_project_count"] == 193

    assert structural["final_main_plus_other_count"] == 599
    assert 406 + 193 == 599

    assert structural["annual_progress_target_item_count"] == 403
    assert structural["main_projects_without_target_count"] == 3
    assert structural["main_projects_minus_no_target_count"] == 403
    assert 406 - 3 == 403


def test_source_index_and_candidate_registry_agree_on_zero_remaining_identities():
    registry = load(REGISTRY)
    index = load(SOURCE_INDEX)

    assert registry["candidate_rows_do_not_increment_final_reviewed_count"] is True
    assert index["summary"]["individual_project_records_reviewed"] == 599
    assert index["summary"]["remaining_action_plan_project_records"] == 0
    assert index["summary"]["candidate_project_records_pending_final_identity_crosscheck_total"] == 0
    assert index["summary"]["candidate_fields_pending_final_identity_crosscheck"] == []
    assert "all 599 final project identities" in registry["quality_boundary"]
