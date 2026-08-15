from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_candidate_registry_covers_all_323_remaining_final_identities():
    registry = load(REGISTRY)
    summary = registry["summary"]

    assert registry["status"] == (
        "candidate_reconciliation_queue_complete_for_all_remaining_identities"
    )
    assert registry["final_reviewed_identity_count"] == 276
    assert registry["final_action_plan_project_count"] == 599
    assert registry["remaining_final_identity_count"] == 323
    assert summary["candidate_field_queue_count"] == 5
    assert summary["candidate_record_count"] == 323
    assert summary["candidate_main_project_record_count"] == 216
    assert summary["candidate_other_project_record_count"] == 107
    assert summary["candidate_reviewed_final_identity_increment"] == 0
    assert summary["final_reviewed_identity_count_remains"] == 276
    assert summary["all_remaining_final_identities_have_candidate_rows"] is True
    assert 276 + 323 == 599


def test_candidate_registry_has_exact_field_queue_partition():
    registry = load(REGISTRY)
    fields = {field["field_id"]: field for field in registry["candidate_fields"]}

    assert set(fields) == {
        "children_youth",
        "daily_life_page68",
        "community",
        "economy",
        "environment",
    }
    assert fields["children_youth"]["candidate_record_count"] == 121
    assert fields["daily_life_page68"]["candidate_record_count"] == 7
    assert fields["community"]["candidate_record_count"] == 47
    assert fields["economy"]["candidate_record_count"] == 74
    assert fields["environment"]["candidate_record_count"] == 74
    assert sum(field["candidate_record_count"] for field in fields.values()) == 323
    assert all(field["reviewed_final_identity_increment"] == 0 for field in fields.values())


def test_candidate_registry_reconciles_main_other_and_annual_target_denominators():
    structural = load(REGISTRY)["structural_reconciliation"]

    assert structural["reviewed_identity_count"] == 276
    assert structural["candidate_identity_count"] == 323
    assert structural["reviewed_plus_candidate_count"] == 599

    assert structural["reviewed_main_project_count"] == 190
    assert structural["candidate_main_project_count"] == 216
    assert structural["final_main_project_count"] == 406
    assert 190 + 216 == 406

    assert structural["reviewed_other_project_count"] == 86
    assert structural["candidate_other_project_count"] == 107
    assert structural["final_other_project_count"] == 193
    assert 86 + 107 == 193

    assert structural["final_main_plus_other_count"] == 599
    assert 406 + 193 == 599

    assert structural["annual_progress_target_item_count"] == 403
    assert structural["main_projects_without_target_count"] == 3
    assert structural["main_projects_minus_no_target_count"] == 403
    assert 406 - 3 == 403


def test_candidate_registry_never_changes_final_reviewed_progress():
    registry = load(REGISTRY)
    index = load(SOURCE_INDEX)

    assert registry["candidate_rows_do_not_increment_final_reviewed_count"] is True
    assert registry["summary"]["candidate_reviewed_final_identity_increment"] == 0
    assert index["summary"]["individual_project_records_reviewed"] == 276
    assert index["summary"]["remaining_action_plan_project_records"] == 323
    assert "excluded from the 276/599 final Reviewed identity count" in (
        registry["quality_boundary"]
    )
