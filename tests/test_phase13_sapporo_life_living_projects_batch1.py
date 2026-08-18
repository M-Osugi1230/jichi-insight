from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch1.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch1_evidence.json"
EXECUTION_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_review_execution.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_batch1_historical_review_is_preserved_exactly():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]
    assert catalog["status"] == "reviewed_batch_at_declared_fields"
    assert len(records) == summary["reviewed_project_record_count"] == 15
    assert summary["main_project_record_count"] == 12
    assert summary["other_project_record_count"] == 3
    assert Counter(record["page_label"] for record in records) == {60: 4, 61: 7, 62: 3, 63: 1}
    assert [record["field_order"] for record in records] == list(range(1, 16))


def test_batch1_anchor_values_remain_stable():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}
    assert (
        records["community_comprehensive_support_center_function_strengthening"][
            "planned_project_cost_yen"
        ]
        == 8_867_000_000
    )
    assert (
        records["national_health_insurance_lifestyle_disease_prevention"][
            "planned_project_cost_yen"
        ]
        == 3_544_000_000
    )
    assert (
        records["administrative_procedure_online_promotion"]["planned_project_cost_yen"]
        == 42_000_000
    )


def test_batch1_evidence_remains_one_to_one():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    assert len(evidence["evidence_packets"]) == len(catalog["records"]) == 15
    assert evidence["revision_history_crosscheck"]["batch1_intersection"] is False


def test_current_life_living_state_is_complete_inside_599_identity_layer_and_v1():
    execution = load(EXECUTION_PATH)
    index = load(SOURCE_INDEX_PATH)
    daily = next(
        field for field in index["machizukuri_field_sources"] if field["field_id"] == "daily_life"
    )
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    readiness = load(READINESS_PATH)
    project_layer = next(
        layer
        for layer in readiness["verified_reviewed_layers"]
        if layer["layer"] == "action_plan_project_records"
    )

    assert execution["review_batches"][0]["reviewed_project_record_count"] == 15
    assert execution["reviewed_project_record_count"] == 85
    assert daily["reviewed_project_record_count"] == 85
    assert (
        sources["sapporo-action-plan-2023-projects-life-living"]["reviewed_project_record_count"]
        == 85
    )
    assert project_layer["state"] == "complete_final_identity_review"
    assert project_layer["reviewed_record_count"] == 599
    assert readiness["current_status"] == "reviewed_complete"
