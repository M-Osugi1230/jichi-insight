from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART1_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_safety_security_projects_part1.json"
)
PART2_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_safety_security_projects_part2.json"
)
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_safety_security_projects_part2_evidence.json"
)
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_safety_part2_has_exact_66_rows_and_closes_field_to_70():
    part1 = load(PART1_PATH)
    part2 = load(PART2_PATH)
    records = part2["records"]
    summary = part2["summary"]

    assert part2["official_code"] == "011002"
    assert part2["field_id"] == "safety_security"
    assert part2["status"] == "reviewed_field_completion_batch"
    assert len(records) == summary["reviewed_project_record_count"] == 66
    assert summary["main_project_record_count"] == 39
    assert summary["other_project_record_count"] == 27
    assert summary["cumulative_field_project_record_count_with_part1"] == 70
    assert len(part1["records"]) + len(records) == 70
    assert summary["field_total_project_count_reviewed"] is True
    assert summary["intro_page_label"] == 79
    assert summary["intro_page_contains_project_rows"] is False
    assert summary["project_page_labels"] == list(range(80, 89))
    assert summary["action_plan_599_coverage_claimed"] is False


def test_sapporo_safety_part2_preserves_page_counts_and_field_order():
    records = load(PART2_PATH)["records"]
    page_counts = Counter(record["page_label"] for record in records)

    assert page_counts == {
        81: 9,
        82: 6,
        83: 15,
        84: 4,
        85: 6,
        86: 7,
        87: 13,
        88: 6,
    }
    assert [record["field_order"] for record in records] == list(range(5, 71))
    assert len({record["id"] for record in records}) == 66
    assert len({record["evidence_id"] for record in records}) == 66


def test_sapporo_safety_part2_keeps_main_and_other_project_depths_separate():
    records = load(PART2_PATH)["records"]
    main = [record for record in records if record["record_type"] == "main_project"]
    other = [record for record in records if record["record_type"] == "other_project"]

    assert len(main) == 39
    assert len(other) == 27
    assert all(record["review_status"] == "reviewed_core_fields" for record in main)
    assert all(record["review_status"] == "reviewed_identity_cost" for record in other)
    assert all("target_name_ja" in record for record in main)
    assert all("target_name_ja" not in record for record in other)
    assert all("baseline_value" not in record for record in other)
    assert all("target_value" not in record for record in other)


def test_sapporo_safety_part2_preserves_exact_cross_page_anchors():
    records = {record["id"]: record for record in load(PART2_PATH)["records"]}

    shelter = records["evacuation_site_improvement"]
    assert shelter["page_label"] == 81
    assert shelter["planned_project_cost_yen"] == 703_000_000
    assert (shelter["baseline_value"], shelter["target_value"]) == (2, 6)

    hospital = records["municipal_sapporo_hospital_function_enhancement"]
    assert hospital["page_label"] == 83
    assert hospital["baseline_value"] == "調査検討"
    assert hospital["target_value"] == "計画策定"
    assert hospital["target_year"] == 2024

    water = records["distribution_trunk_line_continuous_seismic_retrofit"]
    assert water["record_type"] == "other_project"
    assert water["page_label"] == 83
    assert water["planned_project_cost_yen"] == 29_029_000_000
    assert water["responsible_department_ja"] == "水)給水部"

    emergency = records["emergency_medical_system_improvement_strengthening"]
    assert emergency["page_label"] == 85
    assert emergency["baseline_value"] == 8791
    assert emergency["target_value"] == 6500

    fire = records["fire_response_capacity_strengthening"]
    assert fire["page_label"] == 86
    assert fire["baseline_value"] == 12
    assert fire["target_value"] == 100
    assert fire["target_year"] == 2024

    school = records["community_school_safety_system_improvement"]
    assert school["page_label"] == 88
    assert school["record_type"] == "other_project"
    assert school["planned_project_cost_yen"] == 50_000_000
    assert school["responsible_department_ja"] == "教)学校教育部"


def test_sapporo_safety_part2_has_one_to_one_page_evidence():
    records = load(PART2_PATH)["records"]
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["source"]["review_method"] == (
        "visual_page_review_of_220dpi_rendered_official_pdf"
    )
    assert evidence["source"]["source_page_labels"] == list(range(81, 89))
    assert evidence["document_boundary"]["printed_page_79_reviewed"] is True
    assert evidence["document_boundary"]["printed_page_79_contains_project_rows"] is False
    assert len(packets) == len(records) == 66
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in records
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in records
    }
    assert all(packet["evidence_status"] == "reviewed" for packet in packets)


def test_sapporo_safety_field_completion_does_not_complete_municipality():
    queue = load(QUEUE_PATH)
    sapporo = next(
        item for item in queue["execution_queue"] if item["official_code"] == "011002"
    )
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    safety = facts["action-plan-safety-security-project-records-complete"]
    all_projects = facts["action-plan-all-project-identities-complete"]
    targets = facts["progress-project-targets"]

    assert sapporo["status"] == "review_in_progress"
    assert manifest["status"] == "review_in_progress"
    assert safety["value"] == 70
    assert safety["review_status"] == "reviewed_field_complete_at_declared_fields"
    assert "599事業全体" in safety["interpretation_boundary"]
    assert all_projects["value"] == 599
    assert all_projects["review_status"] == "reviewed_complete"
    assert targets["denominator"] == 403
    assert targets["review_status"] == "reviewed_aggregate_only"
    assert any("403項目" in item for item in manifest["remaining_work"])
    assert "policy achievement" in load(PART2_PATH)["quality_boundary"]
