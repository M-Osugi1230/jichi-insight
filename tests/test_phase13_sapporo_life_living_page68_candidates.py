from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_life_living_page68_candidates.json"
EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_life_living_page68_candidates_evidence.json"
FINAL = ROOT / "data/catalog/sapporo_action_plan_life_living_page68_final_reconciliation.json"
FINAL_EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_life_living_page68_final_evidence.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_page68_preserves_historical_seven_candidate_snapshot():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]
    assert len(records) == summary["candidate_record_count"] == 7
    assert summary["main_project_candidate_count"] == 7
    assert summary["other_project_candidate_count"] == 0
    assert summary["known_final_name_change_count"] == 1
    assert all(record["draft_printed_page_label"] == 68 for record in records)


def test_page68_final_reconciliation_directly_promotes_exact_seven_rows():
    final = load(FINAL)
    summary = final["summary"]
    records = final["records"]
    assert final["status"] == "final_page68_direct_visual_review_complete"
    assert final["final_source"]["direct_visual_confirmation"] is True
    assert final["final_source"]["printed_page_label"] == 68
    assert len(records) == summary["reviewed_project_record_count"] == 7
    assert summary["field_reviewed_record_count_after"] == 85
    assert summary["action_plan_reviewed_count_before"] == 276
    assert summary["action_plan_reviewed_count_after"] == 283
    assert [record["page_order"] for record in records] == list(range(1, 8))


def test_page68_final_records_preserve_exact_cost_and_target_anchors():
    records = {record["id"]: record for record in load(FINAL)["records"]}
    assert records["inpatient_rights_advocacy_promotion"]["planned_project_cost_yen"] == 41_000_000
    assert records["disability_consultation_support"]["planned_project_cost_yen"] == 2_752_000_000
    assert records["disability_welfare_facility_development_subsidy"]["planned_project_cost_yen"] == 2_668_000_000
    assert records["severe_disability_medical_expense_subsidy"]["planned_project_cost_yen"] == 253_000_000
    assert records["cancer_social_activity_support"]["target_value"] == 70.5


def test_page68_final_confirms_cancer_name_change():
    final = load(FINAL)
    cancer = {record["id"]: record for record in final["records"]}["cancer_social_activity_support"]
    revision = final["revision_source"]
    assert revision["draft_project_name_ja"] == "がん対策推進事業"
    assert revision["final_project_name_ja"] == "がん患者の社会活動支援事業"
    assert cancer["project_name_ja"] == "がん患者の社会活動支援事業"


def test_page68_final_evidence_is_one_to_one():
    final = load(FINAL)
    evidence = load(FINAL_EVIDENCE)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(final["records"]) == 7
    assert {packet["project_id"] for packet in packets} == {record["id"] for record in final["records"]}
    assert all(packet["page_label"] == 68 for packet in packets)


def test_historical_candidate_evidence_remains_lineage_only():
    evidence = load(EVIDENCE)
    assert len(evidence["evidence_packets"]) == 7
    assert "do not promote" in evidence["evidence_boundary"]


def test_page68_remains_reviewed_inside_completed_599_identity_layer():
    index = load(SOURCE_INDEX)
    life = next(field for field in index["machizukuri_field_sources"] if field["field_id"] == "daily_life")
    queue = load(QUEUE_REGISTRY)
    assert life["field_total_project_count"] == 85
    assert life["reviewed_project_record_count"] == 85
    assert life["unresolved_project_record_count"] == 0
    assert 68 in life["reviewed_page_labels"]
    assert queue["candidate_fields"] == []
    assert index["summary"]["individual_project_records_reviewed"] == 599
    assert index["summary"]["remaining_action_plan_project_records"] == 0
