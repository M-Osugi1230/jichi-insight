from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_economy_project_candidates.json"
EVIDENCE = (
    ROOT / "data/evidence/sapporo_action_plan_economy_project_candidates_evidence.json"
)
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_economy_candidate_inventory_has_exact_74_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["field_id"] == "economy"
    assert catalog["status"] == (
        "draft_candidate_inventory_complete_74_final_identity_crosscheck_pending"
    )
    assert len(records) == summary["candidate_record_count"] == 74
    assert summary["main_project_candidate_count"] == 61
    assert summary["other_project_candidate_count"] == 13
    assert summary["goal10_candidate_count"] == 39
    assert summary["goal11_candidate_count"] == 19
    assert summary["goal12_candidate_count"] == 16
    assert summary["reviewed_final_identity_count"] == 0
    assert summary["action_plan_reviewed_progress_increment"] == 0


def test_economy_candidates_preserve_order_type_goal_and_page_mapping():
    records = load(CATALOG)["records"]

    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert len({record["id"] for record in records}) == 74
    assert Counter(record["goal"] for record in records) == {10: 39, 11: 19, 12: 16}
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 61,
        "other_project": 13,
    }
    assert all(
        record["draft_pdf_page_index_0_based"]
        == record["draft_printed_page_label"] + 5
        for record in records
    )


def test_economy_candidates_preserve_representative_cost_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}

    hometown = records["hometown_tax_utilization"]
    assert hometown["planned_project_cost_yen"] == 10_097_000_000

    new_mice = records["new_mice_facility_development"]
    assert new_mice["planned_project_cost_yen"] is None

    lending = records["sme_finance_fund_lending"]
    assert lending["planned_project_cost_yen"] == 440_547_000_000
    assert lending["record_type"] == "other_project"

    distribution = records["distribution_function_sales_channel_support"]
    assert distribution["planned_project_cost_yen"] == 26_952_000_000

    bidding = records["bidding_contract_system_improvement"]
    assert bidding["planned_project_cost_yen"] is None


def test_economy_candidates_have_exact_one_to_one_evidence_order():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 74
    assert [packet["candidate_order"] for packet in packets] == list(range(1, 75))
    assert len({packet["evidence_id"] for packet in packets}) == 74
    assert all(
        packet["draft_pdf_page_index_0_based"]
        == packet["draft_printed_page_label"] + 5
        for packet in packets
    )
    assert all(
        packet["evidence_status"] == "draft_candidate_location_reviewed"
        for packet in packets
    )
    assert "do not promote" in evidence["evidence_boundary"]


def test_economy_final_denominator_matches_candidate_count_without_promotion():
    catalog = load(CATALOG)
    denominators = load(DENOMINATORS)
    economy = next(
        field
        for field in denominators["field_denominators"]
        if field["field_id"] == "economy"
    )

    assert economy["final_project_count"] == 74
    assert catalog["final_field_denominator"]["project_count"] == 74
    assert catalog["summary"]["candidate_record_count"] == 74
    assert catalog["summary"]["reviewed_final_identity_count"] == 0
    assert catalog["final_source_boundary"]["fetch_status"] == "timeout"
    assert "does not prove final row identity equality" in catalog["quality_boundary"]


def test_economy_candidate_queue_is_registered_without_reviewed_increment():
    queue = load(QUEUE_REGISTRY)
    economy = next(
        field for field in queue["candidate_fields"] if field["field_id"] == "economy"
    )
    index = load(SOURCE_INDEX)

    assert economy["final_field_denominator"] == 74
    assert economy["candidate_record_count"] == 74
    assert economy["candidate_main_project_record_count"] == 61
    assert economy["candidate_other_project_record_count"] == 13
    assert economy["reviewed_final_identity_increment"] == 0
    assert queue["summary"]["candidate_record_count"] == 323
    assert queue["summary"]["candidate_reviewed_final_identity_increment"] == 0
    assert queue["final_reviewed_identity_count"] == 276
    assert index["summary"]["individual_project_records_reviewed"] == 276
