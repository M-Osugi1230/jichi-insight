from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch2.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch2_evidence.json"
EXECUTION_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_review_execution.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_batch2_historical_review_is_preserved_exactly():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["status"] == "reviewed_batch_at_declared_fields"
    assert len(records) == summary["reviewed_project_record_count"] == 28
    assert summary["main_project_record_count"] == 28
    assert summary["other_project_record_count"] == 0
    assert Counter(record["page_label"] for record in records) == {64: 5, 65: 6, 66: 9, 67: 8}
    assert [record["field_order"] for record in records] == list(range(16, 44))


def test_batch2_anchor_values_remain_stable():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    center = records["administrative_affairs_center_operation"]
    assert center["planned_project_cost_yen"] == 1_876_000_000
    assert (center["baseline_value"], center["target_value"]) == (50_861, 130_000)

    digital = records["digital_environment_for_advanced_administrative_services"]
    assert digital["planned_project_cost_yen"] == 14_647_000_000
    assert (digital["baseline_value"], digital["target_value"]) == (22_008, 13_871)

    transport = records["disabled_transportation_expense_subsidy"]
    assert transport["target_year"] == 2026
    assert transport["target_value"] == "タクシー券・ガソリン券の電子申請実施"


def test_batch2_evidence_remains_one_to_one():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 28
    assert {packet["project_id"] for packet in packets} == {record["id"] for record in catalog["records"]}
    assert evidence["revision_history_crosscheck"]["batch2_intersection"] is False


def test_current_life_living_state_is_complete_without_regressing_batch2():
    execution = load(EXECUTION_PATH)
    index = load(SOURCE_INDEX_PATH)
    daily = next(field for field in index["machizukuri_field_sources"] if field["field_id"] == "daily_life")
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    readiness = load(READINESS_PATH)
    project_gate = next(gate for gate in readiness["blocking_gates"] if gate["id"] == "action-plan-project-records")

    assert execution["review_batches"][1]["reviewed_project_record_count"] == 28
    assert execution["status"] == "record_review_complete_at_declared_fields"
    assert execution["reviewed_project_record_count"] == 85
    assert daily["reviewed_project_record_count"] == 85
    assert daily["unresolved_project_record_count"] == 0
    assert daily["blocked_page_labels"] == []
    assert sources["sapporo-action-plan-2023-projects-life-living"]["reviewed_project_record_count"] == 85
    assert project_gate["reviewed_scope"] == 283
    assert project_gate["remaining_scope"] == 316
