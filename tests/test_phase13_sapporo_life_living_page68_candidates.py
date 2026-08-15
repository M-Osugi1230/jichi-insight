from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sapporo_action_plan_life_living_page68_candidates.json"
EVIDENCE = (
    ROOT / "data/evidence/sapporo_action_plan_life_living_page68_candidates_evidence.json"
)
SOURCE_INDEX = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = ROOT / "data/catalog/sapporo_action_plan_candidate_queue_registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_life_living_page68_has_exact_seven_main_candidates_without_promotion():
    catalog = load(CATALOG)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["field_id"] == "daily_life"
    assert catalog["status"] == (
        "draft_candidate_inventory_complete_7_revised_final_identity_crosscheck_pending"
    )
    assert len(records) == summary["candidate_record_count"] == 7
    assert summary["main_project_candidate_count"] == 7
    assert summary["other_project_candidate_count"] == 0
    assert summary["known_final_name_change_count"] == 1
    assert summary["reviewed_final_identity_count"] == 0
    assert summary["action_plan_reviewed_progress_increment"] == 0
    assert all(record["record_type"] == "main_project" for record in records)
    assert all(record["draft_printed_page_label"] == 68 for record in records)
    assert all(record["draft_pdf_page_index_0_based"] == 73 for record in records)


def test_life_living_page68_preserves_exact_candidate_cost_and_target_anchors():
    records = {record["id"]: record for record in load(CATALOG)["records"]}

    rights = records["inpatient_rights_advocacy_promotion"]
    assert rights["planned_project_cost_yen"] == 41_000_000
    assert rights["target_raw_ja"] == "2022：1人 ⇒ 2027：9人"

    consultation = records["disability_consultation_support"]
    assert consultation["planned_project_cost_yen"] == 2_752_000_000
    assert consultation["target_raw_ja"] == "2022：－ ⇒ 2027：5,640件"

    facilities = records["disability_welfare_facility_development_subsidy"]
    assert facilities["planned_project_cost_yen"] == 2_668_000_000
    assert facilities["target_raw_ja"] == "2022：69件 ⇒ 2027：79件"

    medical = records["severe_disability_medical_expense_subsidy"]
    assert medical["planned_project_cost_yen"] == 253_000_000
    assert medical["target_raw_ja"] == "2022：精神通院のみ ⇒ 2024：精神入通院"

    cancer = records["cancer_social_activity_support"]
    assert cancer["planned_project_cost_yen"] == 110_000_000
    assert cancer["target_raw_ja"] == "2022：－ ⇒ 2027：70.5％"


def test_life_living_page68_records_official_cancer_name_change_without_overclaiming():
    catalog = load(CATALOG)
    records = {record["id"]: record for record in catalog["records"]}
    cancer = records["cancer_social_activity_support"]
    revision = catalog["revision_source"]

    assert cancer["draft_project_name_ja"] == "がん対策推進事業"
    assert cancer["candidate_project_name_ja"] == "がん患者の社会活動支援事業"
    assert cancer["revision_status"] == (
        "official_public_comment_final_name_and_description_change_recorded"
    )
    assert revision["known_changed_candidate_id"] == "cancer_social_activity_support"
    assert revision["draft_project_name_ja"] == "がん対策推進事業"
    assert revision["final_project_name_ja"] == "がん患者の社会活動支援事業"
    assert revision["listed_changed_fields"] == ["project_name", "project_description_text"]
    assert revision["target_change_listed"] is False
    assert revision["cost_change_listed"] is False


def test_life_living_page68_has_one_to_one_candidate_evidence():
    catalog = load(CATALOG)
    evidence = load(EVIDENCE)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 7
    assert {packet["candidate_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert len({packet["evidence_id"] for packet in packets}) == 7
    assert all(packet["draft_printed_page_label"] == 68 for packet in packets)
    assert all(packet["draft_pdf_page_index_0_based"] == 73 for packet in packets)
    cancer_packet = next(
        packet
        for packet in packets
        if packet["candidate_id"] == "cancer_social_activity_support"
    )
    assert cancer_packet["evidence_status"] == (
        "draft_candidate_location_reviewed_with_official_final_name_change"
    )
    assert "do not promote" in evidence["evidence_boundary"]


def test_life_living_page68_candidates_cover_exact_unresolved_denominator_without_promotion():
    catalog = load(CATALOG)
    index = load(SOURCE_INDEX)
    life = next(
        field
        for field in index["machizukuri_field_sources"]
        if field["field_id"] == "daily_life"
    )
    queue = load(QUEUE_REGISTRY)
    queued = next(
        field
        for field in queue["candidate_fields"]
        if field["field_id"] == "daily_life_page68"
    )

    assert catalog["final_field_denominator"]["project_count"] == 85
    assert catalog["final_field_denominator"]["reviewed_project_record_count"] == 78
    assert catalog["final_field_denominator"]["unresolved_project_record_count"] == 7
    assert life["field_total_project_count"] == 85
    assert life["reviewed_project_record_count"] == 78
    assert life["unresolved_project_record_count"] == 7
    assert queued["candidate_record_count"] == 7
    assert queued["candidate_main_project_record_count"] == 7
    assert queued["candidate_other_project_record_count"] == 0
    assert queued["reviewed_final_identity_increment"] == 0
    assert index["summary"]["individual_project_records_reviewed"] == 276
    assert index["summary"]["remaining_action_plan_project_records"] == 323
