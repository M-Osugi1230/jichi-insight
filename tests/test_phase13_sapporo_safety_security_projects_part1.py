from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sapporo_action_plan_safety_security_projects_part1.json"
EVIDENCE_PATH = (
    ROOT / "data/evidence/sapporo_action_plan_safety_security_projects_part1_evidence.json"
)
SOURCE_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_safety_project_batch_has_exact_four_page80_records():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]

    assert catalog["official_code"] == "011002"
    assert catalog["field_id"] == "safety_security"
    assert catalog["source"]["source_page_label"] == 80
    assert catalog["source"]["pdf_page_index_0_based"] == 1
    assert catalog["summary"]["reviewed_project_record_count"] == 4
    assert [record["page_order"] for record in records] == [1, 2, 3, 4]
    assert [record["project_name_ja"] for record in records] == [
        "災害対策本部機能強化事業",
        "防災普及啓発推進事業",
        "地域防災活動推進事業",
        "備蓄物資整備事業",
    ]
    assert all(record["responsible_department_ja"] == "危機管理部" for record in records)
    assert all(record["review_status"] == "reviewed_core_fields" for record in records)


def test_sapporo_safety_project_batch_preserves_exact_costs_and_targets():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    headquarters = records["disaster_response_headquarters_function_enhancement"]
    assert headquarters["planned_project_cost_yen"] == 57_000_000
    assert headquarters["target_name_ja"] == "災害対策本部機能の維持率（日数）"
    assert (headquarters["baseline_year"], headquarters["baseline_value"]) == (2022, 100)
    assert (headquarters["target_year"], headquarters["target_value"]) == (2027, 100)

    awareness = records["disaster_prevention_awareness_promotion"]
    assert awareness["planned_project_cost_yen"] == 25_000_000
    assert awareness["target_name_ja"] == "災害に対する備えを行っている家庭の割合"
    assert (awareness["baseline_value"], awareness["target_value"]) == (90, 100)

    community = records["community_disaster_prevention_activity_promotion"]
    assert community["planned_project_cost_yen"] == 85_000_000
    assert community["target_name_ja"] == "防災活動を実施する自主防災組織の割合"
    assert (community["baseline_value"], community["target_value"]) == (80, 85)

    stockpile = records["emergency_stockpile_materials_development"]
    assert stockpile["planned_project_cost_yen"] == 901_000_000
    assert stockpile["target_name_ja"] == "備蓄食糧の充足率"
    assert (stockpile["baseline_value"], stockpile["target_value"]) == (90, 100)


def test_sapporo_safety_project_batch_has_one_to_one_evidence_packets():
    records = load(CATALOG_PATH)["records"]
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert evidence["source"]["source_page_label"] == 80
    assert evidence["source"]["review_method"] == "visual_page_review"
    assert len(packets) == len(records) == 4
    assert {record["id"] for record in records} == {packet["project_id"] for packet in packets}
    assert {record["evidence_id"] for record in records} == {
        packet["evidence_id"] for packet in packets
    }
    assert all(packet["evidence_status"] == "reviewed" for packet in packets)
    assert all(
        packet["boundary"] == "Project-description text is not promoted in this batch."
        for packet in packets
    )


def test_sapporo_safety_project_source_keeps_partial_review_depth():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    source = sources["sapporo-action-plan-2023-projects-safety-security"]

    assert source["source_kind"] == "pdf"
    assert source["page_count"] == 10
    assert source["review_status"] == "partial_record_review_in_progress"
    assert source["confidence"] == "high"
    assert "最初の4事業" in source["notes"]
    assert "残ページ" in source["notes"]


def test_sapporo_safety_project_batch_does_not_claim_full_599_coverage():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    fact = facts["action-plan-safety-security-project-records-part1"]

    assert catalog["summary"]["description_text_reviewed_count"] == 0
    assert catalog["summary"]["field_total_project_count_reviewed"] is False
    assert catalog["summary"]["action_plan_599_coverage_claimed"] is False
    assert "does not establish the total number of projects" in catalog["quality_boundary"]
    assert fact["value"] == 4
    assert fact["review_status"] == "reviewed_core_fields"
    assert "599事業全体" in fact["interpretation_boundary"]
    assert manifest["status"] == "review_in_progress"
