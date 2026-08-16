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
    center = records["community_comprehensive_support_center_function_strengthening"]
    assert center["planned_project_cost_yen"] == 8_867_000_000
    assert (center["baseline_value"], center["target_value"]) == (12.1, 15)

    nhi = records["national_health_insurance_lifestyle_disease_prevention"]
    assert nhi["planned_project_cost_yen"] == 3_544_000_000
    assert len(nhi["target_components"]) == 2

    online = records["administrative_procedure_online_promotion"]
    assert online["planned_project_cost_yen"] == 42_000_000
    assert (online["baseline_value"], online["target_value"]) == (30.8, 70)


def test_batch1_evidence_remains_one_to_one():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 15
    assert {packet["project_id"] for packet in packets} == {record["id"] for record in catalog["records"]}
    assert evidence["revision_history_crosscheck"]["batch1_intersection"] is False


def test_current_life_living_state_is_complete_without_regressing_batch1():
    execution = load(EXECUTION_PATH)
    index = load(SOURCE_INDEX_PATH)
    daily = next(field for field in index["machizukuri_field_sources"] if field["field_id"] == "daily_life")
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    readiness = load(READINESS_PATH)
    project_layer = next(layer for layer in readiness["verified_reviewed_layers"] if layer["layer"] == "action_plan_project_records")

    assert execution["review_batches"][0]["reviewed_project_record_count"] == 15
    assert execution["status"] == "record_review_complete_at_declared_fields"
    assert execution["reviewed_project_record_count"] == 85
    assert daily["reviewed_project_record_count"] == 85
    assert daily["unresolved_project_record_count"] == 0
    assert sources["sapporo-action-plan-2023-projects-life-living"]["reviewed_project_record_count"] == 85
    assert project_layer["reviewed_record_count"] == 283
    assert readiness["current_status"] == "review_in_progress"
