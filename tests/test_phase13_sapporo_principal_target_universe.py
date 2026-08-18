from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/catalog/sapporo_principal_project_target_universe_registry.json"
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_target_universe_reconciles_406_main_projects_to_403_targets():
    registry = load(REGISTRY)
    structural = registry["structural_reconciliation"]

    assert registry["status"] == "target_universe_boundary_complete_403"
    assert structural["final_project_identity_count"] == 599
    assert structural["final_main_project_count"] == 406
    assert structural["final_other_project_count"] == 193
    assert structural["main_projects_without_configured_target_count"] == 3
    assert structural["principal_project_target_count"] == 403
    assert 406 - 3 == 403


def test_field_target_counts_match_exact_main_project_deficits():
    fields = load(REGISTRY)["field_target_universe"]

    assert len(fields) == 8
    assert sum(row["final_main_project_count"] for row in fields) == 406
    assert sum(row["official_target_count"] for row in fields) == 403
    assert sum(row["without_target_count"] for row in fields) == 3

    deficits = {
        row["field_id"]: row["without_target_count"]
        for row in fields
        if row["without_target_count"]
    }
    assert deficits == {
        "children_youth": 1,
        "economy": 1,
        "sports_culture": 1,
    }


def test_exact_three_non_target_main_project_ids_are_locked():
    registry = load(REGISTRY)
    records = registry["main_projects_without_configured_target"]

    assert len(records) == 3
    assert {record["project_id"] for record in records} == {
        "school_lunch_fee_burden_reduction",
        "new_mice_facility_development",
        "sapporo_dome_surrounding_area_utilization",
    }
    assert {record["field_id"] for record in records} == {
        "children_youth",
        "economy",
        "sports_culture",
    }


def test_explicit_targetless_rows_preserve_blank_target_semantics():
    records = {
        record["project_id"]: record
        for record in load(REGISTRY)["main_projects_without_configured_target"]
    }

    school_lunch = records["school_lunch_fee_burden_reduction"]
    assert school_lunch["target_name_ja"] == "－"
    assert school_lunch["target_raw_ja"] == "2022：－ ⇒ 2027：－"

    dome = records["sapporo_dome_surrounding_area_utilization"]
    assert dome["target_name_ja"] == "－"
    assert dome["target_raw_ja"] == "2022：－ ⇒ 2027：－"


def test_target_membership_boundary_does_not_infer_current_status():
    registry = load(REGISTRY)

    assert "distinct from current 2025 target status" in registry["status_boundary"]
    assert "does not assign" in registry["status_boundary"]
    assert "current-status coverage at 8/403" in registry["quality_boundary"]


def test_readiness_completes_v1_without_inventing_395_current_statuses():
    readiness = load(READINESS)
    gate = next(
        item
        for item in readiness["blocking_gates"]
        if item["id"] == "principal-project-target-records"
    )

    assert gate["required_scope"] == 403
    assert gate["reviewed_scope"] == 8
    assert gate["remaining_scope"] == 395
    assert gate["remaining_scope_for_v1_completion"] == 0
    assert gate["state"] == "complete_to_central_publication_boundary_8_named_395_deferred"
    assert readiness["current_status"] == "reviewed_complete"
