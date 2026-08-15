from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch3_pages69_71.json"
)
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch3_pages69_71_evidence.json"
)
EXECUTION_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_review_execution.json"
)
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_batch3_safe_pages_have_exact_35_records_and_keep_page68_blocked():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["status"] == "reviewed_non_revision_pages_with_page68_blocked"
    assert len(records) == summary["reviewed_project_record_count"] == 35
    assert summary["main_project_record_count"] == 15
    assert summary["other_project_record_count"] == 20
    assert summary["reviewed_page_labels"] == [69, 70, 71]
    assert summary["blocked_page_labels"] == [68]
    assert summary["field_total_project_count_reviewed"] is False
    assert catalog["source_verification"]["blocked_printed_page"] == 68
    assert catalog["source_verification"]["listed_revision_intersects_reviewed_pages"] is False


def test_batch3_safe_pages_preserve_exact_page_distribution_and_order():
    records = load(CATALOG_PATH)["records"]
    assert Counter(record["page_label"] for record in records) == {69: 7, 70: 8, 71: 20}
    assert [record["field_order"] for record in records] == list(range(44, 79))
    assert len({record["id"] for record in records}) == 35
    assert len({record["evidence_id"] for record in records}) == 35
    assert sum(record["record_type"] == "main_project" for record in records) == 15
    assert sum(record["record_type"] == "other_project" for record in records) == 20


def test_batch3_safe_pages_preserve_numeric_and_milestone_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    female = records["female_specific_cancer_exam_system"]
    assert female["planned_project_cost_yen"] == 176_000_000
    assert female["target_components"] == [
        {"component": "乳がん検診", "baseline_value": 15.9, "target_value": 18.0, "unit": "percent"},
        {"component": "子宮がん検診", "baseline_value": 27.9, "target_value": 30.3, "unit": "percent"},
    ]

    home = records["community_integrated_medical_care"]
    assert (home["baseline_value"], home["target_value"]) == (1416, 2399)

    snow = records["road_snow_removal"]
    assert snow["planned_project_cost_yen"] == 110_277_000_000
    assert (snow["baseline_value"], snow["target_value"]) == (77, 100)

    housing = records["sapporo_housing_basic_plan_formulation"]
    assert housing["target_value"] == "策定"
    assert housing["unit"] == "milestone"

    school = records["school_facility_barrier_free_improvement"]
    assert school["page_label"] == 70
    assert (school["baseline_value"], school["target_value"]) == (63, 100)

    final_other = records["capable_diverse_human_resources_securement"]
    assert final_other["page_label"] == 71
    assert final_other["planned_project_cost_yen"] == 90_000_000
    assert "target_name_ja" not in final_other


def test_batch3_safe_pages_evidence_is_one_to_one_and_excludes_page68():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["revision_history_crosscheck"]["reviewed_pages_intersection"] is False
    assert evidence["revision_history_crosscheck"]["blocked_page_68"] is True
    assert len(packets) == len(catalog["records"]) == 35
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }
    assert {packet["page_label"] for packet in packets} == {69, 70, 71}
    assert 68 not in {packet["page_label"] for packet in packets}


def test_batch3_safe_pages_advance_life_living_to_78_without_field_completion():
    execution = load(EXECUTION_PATH)
    batch3 = execution["review_batches"][2]
    index = load(SOURCE_INDEX_PATH)
    daily = next(
        field
        for field in index["machizukuri_field_sources"]
        if field["field_id"] == "daily_life"
    )

    assert execution["status"] == "record_review_in_progress_page68_blocked"
    assert execution["reviewed_project_record_count"] == 78
    assert batch3["status"] == "partially_reviewed_pages69_71_complete_page68_blocked"
    assert batch3["reviewed_project_record_count"] == 35
    assert batch3["blocked_pages"] == [68]

    assert daily["reviewed_project_record_count"] == 78
    assert daily["reviewed_main_project_record_count"] == 55
    assert daily["reviewed_other_project_record_count"] == 23
    assert daily["blocked_page_labels"] == [68]
    assert daily["field_total_project_count_reviewed"] is False


def test_batch3_safe_pages_advance_sapporo_to_148_of_599():
    index = load(SOURCE_INDEX_PATH)
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

    assert index["summary"]["individual_project_records_reviewed"] == 148
    assert index["summary"]["remaining_action_plan_project_records"] == 451
    assert index["summary"]["fully_reviewed_field_project_records"] == 70
    assert index["summary"]["partially_reviewed_field_project_records"] == 78

    assert project_layer["reviewed_record_count"] == 148
    assert project_layer["active_partial_field_reviewed_record_count"] == 78
    assert project_layer["active_partial_field_blocked_page"] == 68
    assert project_gate["reviewed_scope"] == 148
    assert project_gate["remaining_scope"] == 451
    assert project_gate["state"] == "in_progress_148_of_599"
    assert readiness["current_status"] == "review_in_progress"


def test_source_registry_records_78_reviewed_and_page68_block():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    life = sources["sapporo-action-plan-2023-projects-life-living"]
    revisions = sources["sapporo-action-plan-2023-public-comment-results"]

    assert life["review_status"] == "reviewed_78_records_page68_blocked"
    assert life["reviewed_project_record_count"] == 78
    assert life["reviewed_main_project_record_count"] == 55
    assert life["reviewed_other_project_record_count"] == 23
    assert life["reviewed_printed_pages"] == "60-67,69-71"
    assert life["blocked_printed_pages"] == [68]
    assert revisions["listed_revision_locations"] == [
        "printed_page_2",
        "printed_page_56",
        "printed_page_68",
        "printed_pages_134_173",
    ]
