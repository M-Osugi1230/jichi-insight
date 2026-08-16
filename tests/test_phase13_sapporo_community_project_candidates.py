from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_community_project_candidates.json"
EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_community_project_candidates_evidence.json"
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES = ROOT / "data/catalog/sapporo_policy_sources.json"
FINAL = ROOT / "data/catalog/sapporo_action_plan_community_final_reconciliation.json"
FINAL_EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_community_final_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_community_historical_candidate_inventory_has_exact_47_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]
    assert len(records) == summary["candidate_record_count"] == 47
    assert summary["main_project_candidate_count"] == 27
    assert summary["other_project_candidate_count"] == 20
    assert summary["goal6_candidate_count"] == 14
    assert summary["goal7_candidate_count"] == 33
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 27,
        "other_project": 20,
    }
    assert [record["candidate_order"] for record in records] == list(range(1, 48))


def test_community_candidate_inventory_preserves_representative_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    assert records["multicultural_coexistence_promotion"]["planned_project_cost_yen"] == 220_000_000
    assert records["residents_organization_subsidy"]["planned_project_cost_yen"] == 1_662_000_000
    assert (
        records["future_smile_city_activity_promotion"]["planned_project_cost_yen"] == 1_855_000_000
    )
    assert records["personal_assistance"]["planned_project_cost_yen"] == 1_501_000_000


def test_community_historical_candidates_have_one_to_one_evidence():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 47
    assert {packet["candidate_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }


def test_community_final_review_promotes_all_47_rows_after_direct_visual_check():
    final = load(FINAL)
    evidence = load(FINAL_EVIDENCE)
    denominators = load(DENOMINATORS)
    community_denominator = next(
        field for field in denominators["field_denominators"] if field["field_id"] == "community"
    )

    assert community_denominator["final_project_count"] == 47
    assert final["status"] == "final_field_direct_visual_review_complete"
    assert final["final_source"]["direct_visual_confirmation"] is True
    assert final["summary"]["reviewed_project_record_count"] == 47
    assert final["summary"]["main_project_record_count"] == 27
    assert final["summary"]["other_project_record_count"] == 20
    assert final["reconciliation"]["changed_identity_count"] == 0
    assert final["reconciliation"]["changed_cost_count"] == 0
    assert evidence["document_boundary"]["exact_match_rows"] == 47


def test_community_final_review_is_reflected_in_central_metadata():
    index = load(SOURCE_INDEX)
    community = next(
        field for field in index["machizukuri_field_sources"] if field["field_id"] == "community"
    )
    readiness = load(READINESS)
    layer = next(
        item
        for item in readiness["verified_reviewed_layers"]
        if item["layer"] == "action_plan_project_records"
    )
    sources = {record["id"]: record for record in load(POLICY_SOURCES)["records"]}

    assert community["reviewed_project_record_count"] == 47
    assert community["reviewed_main_project_record_count"] == 27
    assert community["reviewed_other_project_record_count"] == 20
    assert community["unresolved_project_record_count"] == 0
    assert layer["reviewed_record_count"] == 599
    assert (
        sources["sapporo-action-plan-2023-projects-community"]["reviewed_project_record_count"]
        == 47
    )
    assert index["summary"]["individual_project_records_reviewed"] == 599
