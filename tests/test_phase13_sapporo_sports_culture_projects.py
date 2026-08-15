from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_sports_culture_projects.json"
EVIDENCE_PATH = ROOT / "data/evidence/sapporo_action_plan_sports_culture_projects_evidence.json"
RECONCILIATION_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_sports_culture_final_reconciliation.json"
)
DENOMINATORS_PATH = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sports_culture_preserves_52_row_draft_candidate_inventory():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "sports_culture"
    assert len(records) == 52
    assert Counter(record["page_label"] for record in records) == {
        103: 4,
        104: 6,
        105: 4,
        106: 7,
        107: 9,
        108: 4,
        109: 8,
        110: 10,
    }
    assert len({record["id"] for record in records}) == 52
    assert sum(record["record_type"] == "main_project" for record in records) == 37
    assert sum(record["record_type"] == "other_project" for record in records) == 15


def test_sports_culture_final_denominator_is_51_not_52():
    denominators = load(DENOMINATORS_PATH)
    sports = next(
        field
        for field in denominators["field_denominators"]
        if field["field_id"] == "sports_culture"
    )

    assert sports["final_project_count"] == 51
    assert denominators["draft_comparison"]["sports_culture_draft_project_count"] == 52
    assert denominators["draft_comparison"]["sports_culture_final_project_count"] == 51
    assert denominators["draft_comparison"]["net_project_count_change"] == -1
    assert denominators["plan_total"]["field_count_sum"] == 599
    assert denominators["plan_total"]["final_project_count"] == 599


def test_sports_culture_reconciliation_excludes_only_olympic_bid_candidate():
    catalog = load(CATALOG_PATH)
    reconciliation = load(RECONCILIATION_PATH)
    candidate_ids = {record["id"] for record in catalog["records"]}
    excluded = reconciliation["reconciliation"]["excluded_draft_candidate"]

    assert reconciliation["status"] == "final_denominator_reconciled_high_confidence"
    assert reconciliation["final_denominator"]["project_count"] == 51
    assert reconciliation["draft_candidate_inventory"]["project_count"] == 52
    assert reconciliation["reconciliation"]["net_row_change"] == -1
    assert reconciliation["reconciliation"]["effective_final_project_count"] == 51
    assert reconciliation["reconciliation"]["effective_main_project_count"] == 36
    assert reconciliation["reconciliation"]["effective_other_project_count"] == 15
    assert excluded["id"] == "winter_olympic_paralympic_related"
    assert excluded["project_name_ja"] == "冬季オリンピック・パラリンピック関係事業"
    assert excluded["id"] in candidate_ids
    assert excluded["direct_final_page_confirmation"] is False
    assert reconciliation["reconciliation"]["confidence"] == "high"
    assert "high-confidence" in reconciliation["reconciliation"]["residual_uncertainty"]

    effective_ids = candidate_ids - {excluded["id"]}
    assert len(effective_ids) == 51


def test_sports_culture_candidate_evidence_remains_one_to_one_and_is_not_final_denominator():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 52
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert evidence["revision_history_crosscheck"]["draft_field_project_count"] == 52
    assert evidence["revision_history_crosscheck"]["reviewed_record_count"] == 52
    # The original Evidence file is a draft-candidate inventory. The final denominator
    # is authoritative only through the final overview + reconciliation overlay.
    assert load(RECONCILIATION_PATH)["final_denominator"]["project_count"] == 51


def test_sports_culture_keeps_representative_candidate_numeric_anchors():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    athlete = records["athlete_discovery_development_utilization"]
    assert athlete["planned_project_cost_yen"] == 292_000_000
    assert (athlete["baseline_value"], athlete["target_value"]) == (12, 32)

    winter = records["winter_sports_promotion"]
    assert (winter["baseline_value"], winter["target_value"]) == (19, 25)

    olympics = records["winter_olympic_paralympic_related"]
    assert olympics["planned_project_cost_yen"] is None
    assert olympics["target_value"] is None

    dome = records["sports_facility_redevelopment"]
    assert dome["planned_project_cost_yen"] == 9_369_000_000

    pmf = records["pacific_music_festival"]
    assert pmf["planned_project_cost_yen"] == 1_618_000_000
    assert (pmf["baseline_value"], pmf["target_value"]) == (51.7, 55)


def test_sports_culture_effective_inventory_is_51_in_central_index_and_readiness():
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

    assert sports["field_total_project_count"] == 51
    assert sports["reviewed_project_record_count"] == 51
    assert sports["reviewed_main_project_record_count"] == 36
    assert sports["reviewed_other_project_record_count"] == 15
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["reconciliation_confidence"] == "high"
    assert sports["direct_final_page104_confirmation"] is False

    assert index["summary"]["individual_project_records_reviewed"] >= 276
    assert index["summary"]["fully_reviewed_field_project_records"] >= 198
    assert project_layer["reviewed_record_count"] >= 276
    assert project_layer["sports_culture_reconciliation_confidence"] == "high"
    assert readiness["current_status"] == "review_in_progress"


def test_sports_culture_source_registry_exposes_reconciliation_limit():
    sources = {record["id"]: record for record in load(POLICY_SOURCES_PATH)["records"]}
    sports = sources["sapporo-action-plan-2023-projects-sports-culture"]
    overview = sources["sapporo-action-plan-2023-final-overview"]

    assert overview["review_status"] == "reviewed_for_final_field_project_denominators"
    assert sports["review_status"] == "reviewed_final_51_high_confidence_reconciliation"
    assert sports["field_total_project_count"] == 51
    assert sports["reviewed_project_record_count"] == 51
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["direct_final_page104_confirmation"] is False
