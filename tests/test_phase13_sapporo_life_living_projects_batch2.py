from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch2.json"
)
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch2_evidence.json"
)
EXECUTION_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_review_execution.json"
)
SOURCE_INDEX_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
)
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_life_living_batch2_has_exact_28_main_project_rows():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "daily_life"
    assert catalog["status"] == "reviewed_batch_at_declared_fields"
    assert len(records) == summary["reviewed_project_record_count"] == 28
    assert summary["main_project_record_count"] == 28
    assert summary["other_project_record_count"] == 0
    assert summary["field_total_project_count_reviewed"] is False
    assert summary["action_plan_599_coverage_claimed"] is False
    assert all(record["record_type"] == "main_project" for record in records)


def test_sapporo_life_living_batch2_preserves_page_and_field_order():
    records = load(CATALOG_PATH)["records"]
    page_counts = Counter(record["page_label"] for record in records)

    assert page_counts == {64: 5, 65: 6, 66: 9, 67: 8}
    assert [record["field_order"] for record in records] == list(range(16, 44))
    assert len({record["id"] for record in records}) == 28
    assert len({record["evidence_id"] for record in records}) == 28
    assert all("target_name_ja" in record for record in records)


def test_sapporo_life_living_batch2_preserves_exact_cross_page_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    center = records["administrative_affairs_center_operation"]
    assert center["page_label"] == 64
    assert center["planned_project_cost_yen"] == 1_876_000_000
    assert (center["baseline_value"], center["target_value"]) == (50_861, 130_000)

    digital = records["digital_environment_for_advanced_administrative_services"]
    assert digital["page_label"] == 65
    assert digital["planned_project_cost_yen"] == 14_647_000_000
    assert digital["baseline_value"] == 22_008
    assert digital["target_value"] == 13_871
    assert digital["unit"] == "ten_thousand_sheets"

    barrier = records["public_facility_barrier_free_promotion"]
    assert (barrier["baseline_value"], barrier["target_value"]) == (0, 65.9)

    bus = records["bus_terminal_facility_barrier_free_promotion"]
    assert bus["page_label"] == 66
    assert (bus["baseline_value"], bus["target_value"]) == (4, 5)

    self_reliance = records["people_in_financial_difficulty_self_reliance_support"]
    assert self_reliance["baseline_value"] == 11_746
    assert self_reliance["target_value"] == 6_400
    assert "without inferring" in self_reliance["interpretation_boundary"]

    workforce = records["care_workforce_securement_promotion"]
    assert workforce["page_label"] == 67
    assert (workforce["baseline_value"], workforce["target_value"]) == (50, 50)

    transport = records["disabled_transportation_expense_subsidy"]
    assert transport["target_year"] == 2026
    assert transport["target_value"] == "タクシー券・ガソリン券の電子申請実施"


def test_sapporo_life_living_batch2_has_one_to_one_evidence_and_revision_gate():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["source"]["url"].endswith("ap2023_2_3_2.pdf")
    assert evidence["source"]["source_page_labels"] == [64, 65, 66, 67]
    assert evidence["revision_history_crosscheck"]["batch2_intersection"] is False
    assert (
        evidence["revision_history_crosscheck"][
            "next_page_68_requires_direct_final_review"
        ]
        is True
    )
    assert len(packets) == len(catalog["records"]) == 28
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }


def test_sapporo_life_living_batch2_remains_reflected_after_later_progress():
    execution = load(EXECUTION_PATH)
    batch2 = execution["review_batches"][1]
    source_index = load(SOURCE_INDEX_PATH)
    daily = next(
        field
        for field in source_index["machizukuri_field_sources"]
        if field["field_id"] == "daily_life"
    )

    assert batch2["status"] == "reviewed_batch_complete_at_declared_fields"
    assert batch2["reviewed_project_record_count"] == 28
    assert batch2["main_project_record_count"] == 28
    assert execution["reviewed_project_record_count"] >= 43
    assert daily["reviewed_project_record_count"] >= 43
    assert daily["reviewed_main_project_record_count"] >= 40
    assert daily["reviewed_other_project_record_count"] >= 3
    assert set(range(60, 68)).issubset(set(daily["reviewed_page_labels"]))
    assert daily["field_total_project_count_reviewed"] is False
    assert daily["source_lineage"]["blocked_revision_page"] == 68

    assert source_index["summary"]["individual_project_records_reviewed"] >= 113
    assert source_index["summary"]["fully_reviewed_field_project_records"] == 70
    assert source_index["summary"]["partially_reviewed_field_project_records"] >= 43
    assert source_index["summary"]["remaining_action_plan_project_records"] == (
        599 - source_index["summary"]["individual_project_records_reviewed"]
    )


def test_sapporo_life_living_source_metadata_keeps_page68_gate_after_later_progress():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    final_source = sources["sapporo-action-plan-2023-projects-life-living"]
    revision_source = sources["sapporo-action-plan-2023-public-comment-results"]

    assert final_source["review_status"].startswith("reviewed_")
    assert final_source["reviewed_project_record_count"] >= 43
    assert final_source["reviewed_main_project_record_count"] >= 40
    assert final_source["reviewed_other_project_record_count"] >= 3
    assert 68 in final_source["blocked_printed_pages"]
    assert revision_source["listed_revision_locations"] == [
        "printed_page_2",
        "printed_page_56",
        "printed_page_68",
        "printed_pages_134_173",
    ]


def test_sapporo_readiness_never_regresses_below_batch2_milestone():
    readiness = load(READINESS_PATH)
    project_layer = next(
        layer
        for layer in readiness["verified_reviewed_layers"]
        if layer["layer"] == "action_plan_project_records"
    )
    project_gate = next(
        gate
        for gate in readiness["blocking_gates"]
        if gate["id"] == "action-plan-project-records"
    )

    assert readiness["current_status"] == "review_in_progress"
    assert project_layer["reviewed_record_count"] >= 113
    assert project_layer["active_partial_field_reviewed_record_count"] >= 43
    assert project_gate["required_scope"] == 599
    assert project_gate["reviewed_scope"] >= 113
    assert project_gate["remaining_scope"] == 599 - project_gate["reviewed_scope"]
    assert "403" in readiness["quality_boundary"]
    assert "citizen-perception" in readiness["quality_boundary"]
