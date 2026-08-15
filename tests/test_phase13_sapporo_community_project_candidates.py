from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_community_project_candidates.json"
EVIDENCE = (
    ROOT / "data/evidence/sapporo_action_plan_community_project_candidates_evidence.json"
)
DENOMINATORS = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
READINESS = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"
POLICY_SOURCES = ROOT / "data/catalog/sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_community_candidate_inventory_has_exact_47_rows():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "community"
    assert catalog["status"] == (
        "draft_candidate_inventory_complete_47_final_identity_crosscheck_pending"
    )
    assert len(records) == summary["candidate_record_count"] == 47
    assert summary["main_project_candidate_count"] == 27
    assert summary["other_project_candidate_count"] == 20
    assert summary["goal6_candidate_count"] == 14
    assert summary["goal7_candidate_count"] == 33
    assert summary["reviewed_final_identity_count"] == 0
    assert summary["action_plan_reviewed_progress_increment"] == 0


def test_community_candidates_preserve_order_type_and_goal_counts():
    records = load(CATALOG)["records"]

    assert [record["candidate_order"] for record in records] == list(range(1, 48))
    assert len({record["id"] for record in records}) == 47
    assert Counter(record["goal"] for record in records) == {6: 14, 7: 33}
    assert Counter(record["record_type"] for record in records) == {
        "main_project": 27,
        "other_project": 20,
    }
    assert all(
        record["draft_pdf_page_index_0_based"]
        == record["draft_printed_page_label"] + 5
        for record in records
    )


def test_community_candidate_inventory_preserves_representative_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}

    multicultural = records["multicultural_coexistence_promotion"]
    assert multicultural["planned_project_cost_yen"] == 220_000_000
    assert multicultural["target_raw_ja"] == "2022：46％ ⇒ 2027：56％"

    associations = records["residents_organization_subsidy"]
    assert associations["planned_project_cost_yen"] == 1_662_000_000
    assert associations["target_raw_ja"] == "2022：685,726世帯 ⇒ 2027：717,251世帯"

    future_smile = records["future_smile_city_activity_promotion"]
    assert future_smile["planned_project_cost_yen"] == 1_855_000_000
    assert future_smile["record_type"] == "main_project"

    personal = records["personal_assistance"]
    assert personal["planned_project_cost_yen"] == 1_501_000_000
    assert personal["record_type"] == "other_project"
    assert "target_raw_ja" not in personal


def test_community_candidates_have_one_to_one_evidence():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 47
    assert {packet["candidate_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert len({packet["evidence_id"] for packet in packets}) == 47
    assert Counter(packet["record_type"] for packet in packets) == {
        "main_project": 27,
        "other_project": 20,
    }
    assert all(
        packet["evidence_status"] == "draft_candidate_location_reviewed"
        for packet in packets
    )
    assert "do not promote" in evidence["evidence_boundary"]


def test_community_final_denominator_matches_candidate_count_without_promotion():
    catalog = load(CATALOG)
    denominators = load(DENOMINATORS)
    community = next(
        field
        for field in denominators["field_denominators"]
        if field["field_id"] == "community"
    )

    assert community["final_project_count"] == 47
    assert catalog["final_field_denominator"]["project_count"] == 47
    assert catalog["summary"]["candidate_record_count"] == 47
    assert catalog["summary"]["reviewed_final_identity_count"] == 0
    assert catalog["final_source_boundary"]["fetch_status"] == "timeout"
    assert catalog["final_source_boundary"]["final_identity_crosscheck_status"] == (
        "pending"
    )
    assert "does not prove final row identity equality" in catalog["quality_boundary"]


def test_community_candidate_queue_does_not_increment_global_reviewed_count():
    index = load(SOURCE_INDEX)

    assert index["summary"]["individual_project_records_reviewed"] == 276
    assert index["summary"]["remaining_action_plan_project_records"] == 323


def test_community_candidate_queue_will_be_reflected_in_central_metadata():
    index = load(SOURCE_INDEX)
    community = next(
        field
        for field in index["machizukuri_field_sources"]
        if field["field_id"] == "community"
    )
    readiness = load(READINESS)
    layer = next(
        item
        for item in readiness["verified_reviewed_layers"]
        if item["layer"] == "action_plan_project_records"
    )
    sources = {record["id"]: record for record in load(POLICY_SOURCES)["records"]}

    assert community["field_total_project_count"] == 47
    assert community["candidate_project_record_count"] == 47
    assert community["candidate_main_project_record_count"] == 27
    assert community["candidate_other_project_record_count"] == 20
    assert community["reviewed_final_identity_count"] == 0
    assert layer["candidate_queue_total_record_count"] == 323
    assert layer["all_remaining_final_identities_have_candidate_rows"] is True
    assert sources["sapporo-action-plan-2023-projects-community"][
        "candidate_project_record_count"
    ] == 47
