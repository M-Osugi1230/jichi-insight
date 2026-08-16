from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_economy_project_candidates.json"
EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_economy_project_candidates_evidence.json"
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"
FINAL = ROOT / "data/catalog/sapporo_action_plan_economy_final_reconciliation.json"
FINAL_EVIDENCE = ROOT / "data/evidence/sapporo_action_plan_economy_final_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_economy_historical_candidate_inventory_has_exact_74_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]
    assert len(records) == summary["candidate_record_count"] == 74
    assert summary["main_project_candidate_count"] == 61
    assert summary["other_project_candidate_count"] == 13
    assert summary["goal10_candidate_count"] == 39
    assert summary["goal11_candidate_count"] == 19
    assert summary["goal12_candidate_count"] == 16
    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 61,
        "other_project": 13,
    }


def test_economy_candidates_preserve_representative_cost_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    assert records["hometown_tax_utilization"]["planned_project_cost_yen"] == 10_097_000_000
    assert records["new_mice_facility_development"]["planned_project_cost_yen"] is None
    assert records["sme_finance_fund_lending"]["planned_project_cost_yen"] == 440_547_000_000
    assert (
        records["distribution_function_sales_channel_support"]["planned_project_cost_yen"]
        == 26_952_000_000
    )


def test_economy_historical_candidates_have_exact_one_to_one_evidence_order():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 74
    assert [packet["candidate_order"] for packet in packets] == list(range(1, 75))
    assert len({packet["evidence_id"] for packet in packets}) == 74


def test_economy_final_review_promotes_all_74_rows_after_direct_visual_check():
    final = load(FINAL)
    evidence = load(FINAL_EVIDENCE)
    denominators = load(DENOMINATORS)
    economy_denominator = next(
        field for field in denominators["field_denominators"] if field["field_id"] == "economy"
    )

    assert economy_denominator["final_project_count"] == 74
    assert final["status"] == "final_field_direct_visual_review_complete"
    assert final["final_source"]["direct_visual_confirmation"] is True
    assert final["summary"]["reviewed_project_record_count"] == 74
    assert final["summary"]["main_project_record_count"] == 61
    assert final["summary"]["other_project_record_count"] == 13
    assert final["reconciliation"]["changed_identity_count"] == 0
    assert final["reconciliation"]["changed_department_count"] == 0
    assert final["reconciliation"]["changed_cost_count"] == 0
    assert evidence["document_boundary"]["exact_match_rows"] == 74


def test_economy_final_review_is_reflected_in_global_metadata():
    queue = load(QUEUE_REGISTRY)
    index = load(SOURCE_INDEX)
    economy = next(
        field for field in index["machizukuri_field_sources"] if field["field_id"] == "economy"
    )

    assert queue["candidate_fields"] == []
    assert queue["final_reviewed_identity_count"] == 599
    assert economy["reviewed_project_record_count"] == 74
    assert economy["reviewed_main_project_record_count"] == 61
    assert economy["reviewed_other_project_record_count"] == 13
    assert economy["unresolved_project_record_count"] == 0
    assert index["summary"]["individual_project_records_reviewed"] == 599
