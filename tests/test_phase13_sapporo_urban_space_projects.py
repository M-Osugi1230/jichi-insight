from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_urban_space_projects.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_urban_space_projects_evidence.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_urban_space_has_exact_complete_77_record_inventory():
    catalog = load(CATALOG_PATH)
    summary = catalog["summary"]
    records = catalog["records"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "urban_space"
    assert catalog["status"] == "reviewed_complete_at_declared_fields"
    assert summary["field_total_project_count"] == 77
    assert summary["field_total_project_count_reviewed"] is True
    assert len(records) == summary["reviewed_project_record_count"] == 77
    assert summary["main_project_record_count"] == 56
    assert summary["other_project_record_count"] == 21
    assert summary["goal18_record_count"] == 24
    assert summary["goal19_record_count"] == 23
    assert summary["goal20_record_count"] == 30
    assert summary["reviewed_page_labels"] == list(range(122, 133))
    assert summary["action_plan_599_coverage_claimed"] is False


def test_urban_space_preserves_exact_page_distribution_and_goal_counts():
    records = load(CATALOG_PATH)["records"]
    page_counts = Counter(record["page_label"] for record in records)
    goal_counts = Counter(record["goal"] for record in records)

    assert page_counts == {
        122: 2,
        123: 8,
        124: 8,
        125: 6,
        126: 3,
        127: 8,
        128: 8,
        129: 4,
        130: 4,
        131: 8,
        132: 18,
    }
    assert goal_counts == {18: 24, 19: 23, 20: 30}
    assert [record["field_order"] for record in records] == list(range(1, 78))
    assert len({record["id"] for record in records}) == 77
    assert len({record["evidence_id"] for record in records}) == 77
    assert sum(record["record_type"] == "main_project" for record in records) == 56
    assert sum(record["record_type"] == "other_project" for record in records) == 21


def test_urban_space_preserves_key_numeric_milestone_and_direction_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    public_transport = records["public_transport_network_security"]
    assert public_transport["planned_project_cost_yen"] == 10_132_000_000
    assert (public_transport["baseline_value"], public_transport["target_value"]) == (
        235_000,
        235_000,
    )

    streetcar = records["streetcar_utilization_promotion"]
    assert streetcar["planned_project_cost_yen"] == 6_203_000_000
    assert (streetcar["baseline_value"], streetcar["target_value"]) == (33, 47)

    vacant = records["vacant_house_measures"]
    assert (vacant["baseline_value"], vacant["target_value"]) == (223, 219)
    assert "独自判定しない" in vacant["interpretation_boundary"]

    station = records["kita5_nishi1_nishi2_redevelopment"]
    assert station["planned_project_cost_yen"] == 39_009_000_000
    assert station["target_value"] == "整備継続"

    subway = records["subway_sapporo_station_improvement"]
    assert subway["planned_project_cost_yen"] == 12_957_000_000
    assert subway["target_value"] == "駅躯体完成"

    cemetery = records["municipal_cemetery_operation_improvement"]
    assert (cemetery["baseline_value"], cemetery["target_value"]) == (16, 6)

    crematorium = records["crematorium_operation_system"]
    assert (crematorium["baseline_value"], crematorium["target_value"]) == (64, 30)
    assert crematorium["unit"] == "minutes"

    school = records["school_facility_new_reconstruction"]
    assert school["planned_project_cost_yen"] == 60_714_000_000
    assert school["target_value"] == 13

    sewer = records["sewer_facility_reconstruction"]
    assert sewer["record_type"] == "other_project"
    assert sewer["planned_project_cost_yen"] == 134_528_000_000
    assert "target_name_ja" not in sewer


def test_urban_space_has_one_to_one_evidence_and_revision_non_intersection():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    boundary = evidence["document_boundary"]
    assert boundary["final_pdf_page_count"] == 12
    assert boundary["printed_page_121_contains_project_rows"] is False
    assert boundary["printed_pages_122_132_project_rows_covered_here"] is True
    assert boundary["direct_final_visual_checks"] == [121, 122]
    assert boundary["field_completion_claimed"] is True

    crosscheck = evidence["revision_history_crosscheck"]
    assert crosscheck["urban_space_printed_page_range"] == "121-132"
    assert crosscheck["field_intersection"] is False
    assert crosscheck["draft_field_project_count"] == 77
    assert crosscheck["reviewed_record_count"] == 77
    assert crosscheck["counts_match"] is True

    assert len(packets) == len(catalog["records"]) == 77
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }
    assert {packet["page_label"] for packet in packets} == set(range(122, 133))


def test_urban_space_remains_complete_after_sports_denominator_correction():
    index = load(SOURCE_INDEX_PATH)
    readiness = load(READINESS_PATH)
    urban = next(
        record
        for record in index["machizukuri_field_sources"]
        if record["field_id"] == "urban_space"
    )
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

    assert urban["content_review_status"] == "record_review_complete_at_declared_fields"
    assert urban["reviewed_project_record_count"] == 77
    assert urban["reviewed_main_project_record_count"] == 56
    assert urban["reviewed_other_project_record_count"] == 21
    assert urban["field_total_project_count"] == 77
    assert urban["field_total_project_count_reviewed"] is True
    assert urban["source_lineage"]["final_pdf_visual_checks"] == [121, 122]
    assert urban["source_lineage"]["listed_revision_intersects_field"] is False

    assert index["summary"]["individual_project_records_reviewed"] == 276
    assert index["summary"]["fully_reviewed_field_project_records"] == 198
    assert index["summary"]["partially_reviewed_field_project_records"] == 78
    assert index["summary"]["remaining_action_plan_project_records"] == 323

    assert project_layer["reviewed_record_count"] == 276
    assert "urban-space" in project_layer["completed_fields"]
    assert project_layer["completed_field_record_count"] == 198
    assert project_gate["reviewed_scope"] == 276
    assert project_gate["remaining_scope"] == 323
    assert project_gate["state"] == "in_progress_276_of_599"
    assert readiness["current_status"] == "review_in_progress"


def test_urban_space_source_registry_is_high_confidence_complete_field_source():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    urban = sources["sapporo-action-plan-2023-projects-urban-space"]

    assert urban["review_status"] == "reviewed_for_complete_field_project_inventory"
    assert urban["confidence"] == "high"
    assert urban["page_count"] == 12
    assert urban["printed_page_range"] == "121-132"
    assert urban["reviewed_project_record_count"] == 77
    assert urban["reviewed_main_project_record_count"] == 56
    assert urban["reviewed_other_project_record_count"] == 21
    assert urban["field_total_project_count"] == 77
    assert urban["reviewed_printed_pages"] == "122-132"
    assert urban["direct_final_visual_checks"] == [121, 122]
