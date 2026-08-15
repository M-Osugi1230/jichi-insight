from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_sports_culture_projects.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_sports_culture_projects_evidence.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sports_culture_has_exact_complete_52_record_inventory():
    catalog = load(CATALOG_PATH)
    summary = catalog["summary"]
    records = catalog["records"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "sports_culture"
    assert catalog["status"] == "reviewed_complete_at_declared_fields"
    assert summary["field_total_project_count"] == 52
    assert summary["field_total_project_count_reviewed"] is True
    assert len(records) == summary["reviewed_project_record_count"] == 52
    assert summary["main_project_record_count"] == 37
    assert summary["other_project_record_count"] == 15
    assert summary["reviewed_page_labels"] == list(range(103, 111))
    assert summary["action_plan_599_coverage_claimed"] is False


def test_sports_culture_preserves_page_distribution_and_record_types():
    records = load(CATALOG_PATH)["records"]
    page_counts = Counter(record["page_label"] for record in records)

    assert page_counts == {
        103: 4,
        104: 6,
        105: 4,
        106: 7,
        107: 9,
        108: 4,
        109: 8,
        110: 10,
    }
    assert [record["field_order"] for record in records] == list(range(1, 53))
    assert len({record["id"] for record in records}) == 52
    assert len({record["evidence_id"] for record in records}) == 52
    assert sum(record["record_type"] == "main_project" for record in records) == 37
    assert sum(record["record_type"] == "other_project" for record in records) == 15


def test_sports_culture_preserves_exact_numeric_and_unset_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    athlete = records["athlete_discovery_development_utilization"]
    assert athlete["planned_project_cost_yen"] == 292_000_000
    assert (athlete["baseline_value"], athlete["target_value"]) == (12, 32)

    winter = records["winter_sports_promotion"]
    assert (winter["baseline_value"], winter["target_value"]) == (19, 25)

    olympics = records["winter_olympic_paralympic_related"]
    assert olympics["planned_project_cost_yen"] is None
    assert olympics["target_value"] is None
    assert olympics["unit"] == "not_set"

    dome = records["sports_facility_redevelopment"]
    assert dome["planned_project_cost_yen"] == 9_369_000_000
    assert dome["target_value"] == "実施"

    snow_resort = records["snow_resort_promotion"]
    assert snow_resort["baseline_value"] == 990_000
    assert snow_resort["target_value"] == 1_090_000

    pmf = records["pacific_music_festival"]
    assert pmf["planned_project_cost_yen"] == 1_618_000_000
    assert (pmf["baseline_value"], pmf["target_value"]) == (51.7, 55)

    art = records["international_art_festival"]
    assert (art["baseline_value"], art["target_value"]) == (4.2, 11.4)

    refresh = records["cultural_arts_facility_refresh"]
    assert refresh["record_type"] == "other_project"
    assert refresh["planned_project_cost_yen"] == 4_655_000_000
    assert "target_name_ja" not in refresh


def test_sports_culture_has_one_to_one_evidence_and_no_revision_intersection():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["document_boundary"]["printed_page_102_contains_project_rows"] is False
    assert evidence["document_boundary"]["printed_pages_103_110_project_rows_covered_here"] is True
    assert evidence["document_boundary"]["field_completion_claimed"] is True
    crosscheck = evidence["revision_history_crosscheck"]
    assert crosscheck["field_intersection"] is False
    assert crosscheck["draft_field_project_count"] == 52
    assert crosscheck["reviewed_record_count"] == 52
    assert crosscheck["counts_match"] is True
    assert len(packets) == len(catalog["records"]) == 52
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }
    assert {packet["page_label"] for packet in packets} == set(range(103, 111))


def test_sports_culture_advances_sapporo_to_at_least_200_of_599():
    index = load(SOURCE_INDEX_PATH)
    readiness = load(READINESS_PATH)
    sports = next(
        record
        for record in index["machizukuri_field_sources"]
        if record["field_id"] == "sports_culture"
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

    assert sports["reviewed_project_record_count"] == 52
    assert sports["field_total_project_count_reviewed"] is True
    assert index["summary"]["individual_project_records_reviewed"] >= 200
    assert index["summary"]["fully_reviewed_field_project_records"] >= 122
    assert project_layer["reviewed_record_count"] >= 200
    assert "sports-culture" in project_layer["completed_fields"]
    assert project_layer["completed_field_record_count"] >= 122
    assert project_gate["reviewed_scope"] >= 200
    assert project_gate["remaining_scope"] == 599 - project_gate["reviewed_scope"]
    assert readiness["current_status"] == "review_in_progress"


def test_sports_culture_source_registry_is_high_confidence_complete_field_source():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    sports = sources["sapporo-action-plan-2023-projects-sports-culture"]

    assert sports["review_status"] == "reviewed_for_complete_field_project_inventory"
    assert sports["confidence"] == "high"
    assert sports["page_count"] == 9
    assert sports["printed_page_range"] == "102-110"
    assert sports["reviewed_project_record_count"] == 52
    assert sports["reviewed_main_project_record_count"] == 37
    assert sports["reviewed_other_project_record_count"] == 15
    assert sports["field_total_project_count"] == 52
