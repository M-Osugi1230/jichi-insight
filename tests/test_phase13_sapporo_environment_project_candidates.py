from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_environment_project_candidates.json"
EVIDENCE = (
    ROOT / "data/evidence/sapporo_action_plan_environment_project_candidates_evidence.json"
)
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_environment_candidate_inventory_has_exact_74_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["field_id"] == "environment"
    assert catalog["status"] == (
        "draft_candidate_inventory_complete_74_final_identity_crosscheck_pending"
    )
    assert len(records) == summary["candidate_record_count"] == 74
    assert summary["main_project_candidate_count"] == 47
    assert summary["other_project_candidate_count"] == 27
    assert summary["goal16_candidate_count"] == 48
    assert summary["goal17_candidate_count"] == 26
    assert summary["reviewed_final_identity_count"] == 0
    assert summary["action_plan_reviewed_progress_increment"] == 0


def test_environment_candidates_preserve_order_type_goal_and_page_mapping():
    records = load(CATALOG)["records"]

    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert len({record["id"] for record in records}) == 74
    assert Counter(record["goal"] for record in records) == {16: 48, 17: 26}
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 47,
        "other_project": 27,
    }
    assert all(
        record["draft_pdf_page_index_0_based"]
        == record["draft_printed_page_label"] + 5
        for record in records
    )


def test_environment_candidates_preserve_representative_cost_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}

    gx = records["gx_investment_promotion"]
    assert gx["planned_project_cost_yen"] is None

    hydrogen = records["hydrogen_utilization_promotion"]
    assert hydrogen["planned_project_cost_yen"] == 3_953_000_000

    school_led = records["school_lighting_led_conversion"]
    assert school_led["planned_project_cost_yen"] == 9_387_000_000

    komaoka = records["komaoka_incineration_plant_renewal"]
    assert komaoka["planned_project_cost_yen"] == 46_197_000_000
    assert komaoka["record_type"] == "other_project"

    park = records["community_park_redevelopment"]
    assert park["planned_project_cost_yen"] == 6_890_000_000


def test_environment_candidates_have_exact_one_to_one_evidence_order():
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


def test_environment_final_denominator_matches_candidate_count_without_promotion():
    catalog = load(CATALOG)
    denominators = load(DENOMINATORS)
    environment = next(
        field
        for field in denominators["field_denominators"]
        if field["field_id"] == "environment"
    )

    assert environment["final_project_count"] == 74
    assert catalog["final_field_denominator"]["project_count"] == 74
    assert catalog["summary"]["candidate_record_count"] == 74
    assert catalog["summary"]["reviewed_final_identity_count"] == 0
    assert catalog["final_source_boundary"]["fetch_status"] == "timeout"
    assert "does not prove final row identity equality" in catalog["quality_boundary"]


def test_environment_candidate_queue_is_registered_without_reviewed_increment():
    queue = load(QUEUE_REGISTRY)
    environment = next(
        field
        for field in queue["candidate_fields"]
        if field["field_id"] == "environment"
    )
    index = load(SOURCE_INDEX)

    assert environment["final_field_denominator"] == 74
    assert environment["candidate_record_count"] == 74
    assert environment["candidate_main_project_record_count"] == 47
    assert environment["candidate_other_project_record_count"] == 27
    assert environment["reviewed_final_identity_increment"] == 0
    assert queue["summary"]["candidate_record_count"] == 316
    assert queue["summary"]["candidate_reviewed_final_identity_increment"] == 0
    assert queue["final_reviewed_identity_count"] == 276
    assert index["summary"]["individual_project_records_reviewed"] == 276
