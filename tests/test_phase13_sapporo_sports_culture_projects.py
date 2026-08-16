from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_sports_culture_projects.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_sports_culture_projects_evidence.json"
RECONCILIATION_PATH = ROOT / "data/catalog/sapporo_action_plan_sports_culture_final_reconciliation.json"
DENOMINATORS_PATH = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sports_culture_preserves_52_row_draft_candidate_inventory():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    assert len(records) == 52
    assert Counter(record["page_label"] for record in records) == {103: 4, 104: 6, 105: 4, 106: 7, 107: 9, 108: 4, 109: 8, 110: 10}
    assert len({record["id"] for record in records}) == 52
    assert sum(record["record_type"] == "main_project" for record in records) == 37
    assert sum(record["record_type"] == "other_project" for record in records) == 15


def test_sports_culture_final_denominator_is_51_not_52():
    denominators = load(DENOMINATORS_PATH)
    sports = next(field for field in denominators["field_denominators"] if field["field_id"] == "sports_culture")
    assert sports["final_project_count"] == 51
    assert denominators["draft_comparison"]["sports_culture_draft_project_count"] == 52
    assert denominators["draft_comparison"]["sports_culture_final_project_count"] == 51
    assert denominators["draft_comparison"]["net_project_count_change"] == -1
    assert denominators["plan_total"]["final_project_count"] == 599


def test_sports_culture_reconciliation_directly_confirms_excluded_olympic_candidate():
    catalog = load(CATALOG_PATH)
    reconciliation = load(RECONCILIATION_PATH)
    candidate_ids = {record["id"] for record in catalog["records"]}
    excluded = reconciliation["reconciliation"]["excluded_draft_candidate"]

    assert reconciliation["status"] == "final_denominator_and_excluded_row_directly_confirmed"
    assert reconciliation["final_denominator"]["project_count"] == 51
    assert reconciliation["final_field_source"]["directly_checked_page_label"] == 104
    assert reconciliation["final_field_source"]["direct_visual_confirmation"] is True
    assert reconciliation["reconciliation"]["net_row_change"] == -1
    assert reconciliation["reconciliation"]["effective_final_project_count"] == 51
    assert reconciliation["reconciliation"]["effective_main_project_count"] == 36
    assert reconciliation["reconciliation"]["effective_other_project_count"] == 15
    assert excluded["id"] == "winter_olympic_paralympic_related"
    assert excluded["project_name_ja"] == "冬季オリンピック・パラリンピック関係事業"
    assert excluded["id"] in candidate_ids
    assert excluded["direct_final_page_confirmation"] is True
    assert excluded["final_inclusion_status"] == "directly_confirmed_absent_from_final_printed_page_104"
    assert reconciliation["reconciliation"]["confidence"] == "direct_final_visual"
    assert reconciliation["reconciliation"]["residual_uncertainty"] is None
    assert reconciliation["reconciliation"]["final_page104_observed_rows"]["winter_olympic_paralympic_related_present"] is False
    assert len(candidate_ids - {excluded["id"]}) == 51


def test_sports_culture_candidate_evidence_remains_one_to_one_historical_lineage():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 52
    assert {packet["project_id"] for packet in packets} == {record["id"] for record in catalog["records"]}
    assert load(RECONCILIATION_PATH)["final_denominator"]["project_count"] == 51


def test_sports_culture_keeps_representative_candidate_numeric_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}
    assert records["athlete_discovery_development_utilization"]["planned_project_cost_yen"] == 292_000_000
    assert records["winter_olympic_paralympic_related"]["planned_project_cost_yen"] is None
    assert records["sports_facility_redevelopment"]["planned_project_cost_yen"] == 9_369_000_000
    assert records["pacific_music_festival"]["planned_project_cost_yen"] == 1_618_000_000


def test_sports_culture_effective_inventory_is_51_in_completed_599_layer():
    index = load(SOURCE_INDEX_PATH)
    readiness = load(READINESS_PATH)
    sports = next(record for record in index["machizukuri_field_sources"] if record["field_id"] == "sports_culture")
    project_layer = next(layer for layer in readiness["verified_reviewed_layers"] if layer["layer"] == "action_plan_project_records")

    assert sports["field_total_project_count"] == 51
    assert sports["reviewed_project_record_count"] == 51
    assert sports["reviewed_main_project_record_count"] == 36
    assert sports["reviewed_other_project_record_count"] == 15
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["reconciliation_confidence"] == "direct_final_visual"
    assert sports["direct_final_page104_confirmation"] is True
    assert index["summary"]["individual_project_records_reviewed"] == 599
    assert project_layer["reviewed_record_count"] == 599
    assert project_layer["sports_culture_direct_final_page104_confirmation"] is True
    assert readiness["current_status"] == "review_in_progress"


def test_sports_culture_source_registry_exposes_direct_final_reconciliation():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    sports = sources["sapporo-action-plan-2023-projects-sports-culture"]
    overview = sources["sapporo-action-plan-2023-final-overview"]
    assert overview["review_status"] == "reviewed_for_final_field_project_denominators"
    assert sports["review_status"] == "reviewed_final_51_direct_final_reconciliation"
    assert sports["field_total_project_count"] == 51
    assert sports["reviewed_project_record_count"] == 51
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["direct_final_page104_confirmation"] is True
