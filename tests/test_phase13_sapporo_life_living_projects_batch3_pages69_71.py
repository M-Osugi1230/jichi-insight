from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch3_pages69_71.json"
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch3_pages69_71_evidence.json"
)
FINAL68_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_page68_final_reconciliation.json"
)
EXECUTION_PATH = ROOT / "data/catalog/sapporo_action_plan_life_living_review_execution.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_historical_pages69_71_snapshot_keeps_exact_35_records():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]
    assert catalog["status"] == "reviewed_non_revision_pages_with_page68_blocked"
    assert len(records) == summary["reviewed_project_record_count"] == 35
    assert summary["main_project_record_count"] == 15
    assert summary["other_project_record_count"] == 20
    assert Counter(record["page_label"] for record in records) == {69: 7, 70: 8, 71: 20}
    assert [record["field_order"] for record in records] == list(range(44, 79))


def test_pages69_71_anchor_values_remain_stable():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}
    assert records["female_specific_cancer_exam_system"]["planned_project_cost_yen"] == 176_000_000
    assert records["road_snow_removal"]["planned_project_cost_yen"] == 110_277_000_000
    assert records["school_facility_barrier_free_improvement"]["target_value"] == 100


def test_pages69_71_evidence_remains_one_to_one_and_historical_boundary_is_explicit():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 35
    assert {packet["page_label"] for packet in packets} == {69, 70, 71}
    assert evidence["revision_history_crosscheck"]["blocked_page_68"] is True


def test_page68_is_now_directly_reconciled_and_batch3_execution_is_complete():
    final68 = load(FINAL68_PATH)
    execution = load(EXECUTION_PATH)
    batch3 = execution["review_batches"][2]
    assert final68["final_source"]["direct_visual_confirmation"] is True
    assert final68["summary"]["reviewed_project_record_count"] == 7
    assert execution["reviewed_project_record_count"] == 85
    assert batch3["reviewed_project_record_count"] == 42
    assert batch3["reviewed_pages"] == [68, 69, 70, 71]
    assert batch3["blocked_pages"] == []


def test_global_state_reflects_complete_life_living_inside_599_identity_layer():
    index = load(SOURCE_INDEX_PATH)
    daily = next(
        field for field in index["machizukuri_field_sources"] if field["field_id"] == "daily_life"
    )
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    readiness = load(READINESS_PATH)
    layer = next(
        item
        for item in readiness["verified_reviewed_layers"]
        if item["layer"] == "action_plan_project_records"
    )
    gate = next(
        item for item in readiness["blocking_gates"] if item["id"] == "action-plan-project-records"
    )

    assert daily["reviewed_project_record_count"] == 85
    assert daily["reviewed_main_project_record_count"] == 62
    assert daily["reviewed_other_project_record_count"] == 23
    assert daily["blocked_page_labels"] == []

    life = sources["sapporo-action-plan-2023-projects-life-living"]
    assert life["reviewed_project_record_count"] == 85
    assert life["blocked_printed_pages"] == []
    assert life["direct_final_page68_confirmation"] is True

    assert index["summary"]["individual_project_records_reviewed"] == 599
    assert index["summary"]["remaining_action_plan_project_records"] == 0
    assert layer["reviewed_record_count"] == 599
    assert gate["reviewed_scope"] == 599
    assert gate["remaining_scope"] == 0
    assert readiness["current_status"] == "review_in_progress"
