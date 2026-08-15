from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_life_living_projects_batch1.json"
)
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_life_living_projects_batch1_evidence.json"
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


def test_sapporo_life_living_batch1_has_exact_reviewed_rows():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "daily_life"
    assert catalog["status"] == "reviewed_batch_at_declared_fields"
    assert len(records) == summary["reviewed_project_record_count"] == 15
    assert summary["main_project_record_count"] == 12
    assert summary["other_project_record_count"] == 3
    assert summary["field_total_project_count_reviewed"] is False
    assert summary["action_plan_599_coverage_claimed"] is False
    assert summary["intro_page_label"] == 59
    assert summary["intro_page_contains_project_rows"] is False


def test_sapporo_life_living_batch1_preserves_page_order_and_depth():
    records = load(CATALOG_PATH)["records"]
    page_counts = Counter(record["page_label"] for record in records)

    assert page_counts == {60: 4, 61: 7, 62: 3, 63: 1}
    assert [record["field_order"] for record in records] == list(range(1, 16))
    assert len({record["id"] for record in records}) == 15
    assert len({record["evidence_id"] for record in records}) == 15

    main = [record for record in records if record["record_type"] == "main_project"]
    other = [record for record in records if record["record_type"] == "other_project"]
    assert len(main) == 12
    assert len(other) == 3
    assert all("target_name_ja" in record for record in main)
    assert all("target_name_ja" not in record for record in other)
    assert all(
        record["review_status"] == "reviewed_identity_cost_revision_crosschecked"
        for record in other
    )


def test_sapporo_life_living_batch1_preserves_exact_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    center = records["community_comprehensive_support_center_function_strengthening"]
    assert center["page_label"] == 60
    assert center["planned_project_cost_yen"] == 8_867_000_000
    assert (center["baseline_value"], center["target_value"]) == (12.1, 15)

    nhi = records["national_health_insurance_lifestyle_disease_prevention"]
    assert nhi["page_label"] == 61
    assert nhi["planned_project_cost_yen"] == 3_544_000_000
    assert len(nhi["target_components"]) == 2
    assert nhi["target_components"][0]["baseline_value"] == 36.8
    assert nhi["target_components"][0]["target_value"] == 33.8
    assert nhi["target_components"][1]["target_relation"] == "greater_than"

    wellness = records["wellness_promotion"]
    assert wellness["planned_project_cost_yen"] == 126_000_000
    assert (wellness["baseline_value"], wellness["target_value"]) == (20_000, 200_000)

    library_dx = records["library_dx_study"]
    assert library_dx["target_year"] == 2024
    assert library_dx["target_value"] == "実施"

    reading_plan = records["sapporo_reading_library_plan_2027_formulation"]
    assert reading_plan["record_type"] == "other_project"
    assert reading_plan["page_label"] == 62
    assert reading_plan["planned_project_cost_yen"] == 4_000_000

    online = records["administrative_procedure_online_promotion"]
    assert online["page_label"] == 63
    assert online["planned_project_cost_yen"] == 42_000_000
    assert (online["baseline_value"], online["target_value"]) == (30.8, 70)


def test_sapporo_life_living_batch1_has_one_to_one_evidence_and_lineage():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["source"]["url"].endswith("ap2023_2_3_2.pdf")
    assert evidence["source"]["source_page_labels"] == [59, 60, 61, 62, 63]
    assert (
        evidence["document_boundary"]["printed_page_59_contains_project_rows"] is False
    )
    assert evidence["revision_history_crosscheck"]["batch1_intersection"] is False
    assert evidence["revision_history_crosscheck"]["listed_revision_locations"] == [
        "printed_page_2",
        "printed_page_56",
        "printed_page_68",
        "printed_pages_134_173",
    ]
    assert len(packets) == len(catalog["records"]) == 15
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }
    assert all(
        packet["evidence_status"] == "reviewed_revision_history_crosschecked"
        for packet in packets
    )


def test_sapporo_life_living_batch1_remains_reflected_after_later_batches():
    execution = load(EXECUTION_PATH)
    batch1 = execution["review_batches"][0]
    source_index = load(SOURCE_INDEX_PATH)
    daily = next(
        field
        for field in source_index["machizukuri_field_sources"]
        if field["field_id"] == "daily_life"
    )
    safety = next(
        field
        for field in source_index["machizukuri_field_sources"]
        if field["field_id"] == "safety_security"
    )

    assert batch1["status"] == "reviewed_batch_complete_at_declared_fields"
    assert batch1["reviewed_project_record_count"] == 15
    assert execution["source_history"]["batch1_revision_intersection"] is False

    assert daily["field_total_project_count"] == 85
    assert daily["field_total_project_count_reviewed"] is True
    assert daily["reviewed_project_record_count"] >= 15
    assert daily["unresolved_project_record_count"] == 7
    assert safety["reviewed_project_record_count"] == 70
    assert source_index["summary"]["individual_project_records_reviewed"] >= 85
    assert source_index["summary"]["fully_reviewed_field_project_records"] >= 70
    assert source_index["summary"]["partially_reviewed_field_project_records"] >= 15


def test_sapporo_life_living_source_metadata_preserves_lineage_roles():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}

    final_source = sources["sapporo-action-plan-2023-projects-life-living"]
    draft_source = sources["sapporo-action-plan-2023-public-comment-draft"]
    revision_source = sources["sapporo-action-plan-2023-public-comment-results"]

    assert final_source["review_status"] == "reviewed_78_of_final_85_page68_blocked"
    assert final_source["page_count"] == 13
    assert final_source["field_total_project_count"] == 85
    assert final_source["reviewed_project_record_count"] == 78
    assert final_source["unresolved_project_record_count"] == 7
    assert draft_source["review_status"] == "navigation_and_transcription_only"
    assert revision_source["review_status"] == "reviewed_for_public_comment_revision_scope_only"
    assert "全変更を網羅" in revision_source["notes"]


def test_sapporo_readiness_never_regresses_below_batch1_milestone():
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
    assert project_layer["reviewed_record_count"] >= 85
    assert project_layer["active_partial_field_final_denominator"] == 85
    assert project_layer["active_partial_field_unresolved_record_count"] == 7
    assert project_gate["required_scope"] == 599
    assert project_gate["reviewed_scope"] >= 85
    assert project_gate["remaining_scope"] == 599 - project_gate["reviewed_scope"]
    assert "403" in readiness["quality_boundary"]
    assert "citizen-perception" in readiness["quality_boundary"]
