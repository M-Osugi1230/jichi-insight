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
    assert catalog["source"]["source_page_label"] == 80
    assert catalog["summary"]["reviewed_project_record_count"] == 4
    assert [record["page_order"] for record in records] == [1, 2, 3, 4]
    assert [record["project_name_ja"] for record in records] == [
        "災害対策本部機能強化事業",
        "防災普及啓発推進事業",
        "地域防災活動推進事業",
        "備蓄物資整備事業",
    ]
    assert all(record["responsible_department_ja"] == "危機管理部" for record in records)


def test_sapporo_safety_project_batch_preserves_exact_costs_and_targets():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}
    assert (
        records["disaster_response_headquarters_function_enhancement"]["planned_project_cost_yen"]
        == 57_000_000
    )
    assert (
        records["disaster_prevention_awareness_promotion"]["planned_project_cost_yen"] == 25_000_000
    )
    assert (
        records["community_disaster_prevention_activity_promotion"]["planned_project_cost_yen"]
        == 85_000_000
    )
    assert (
        records["emergency_stockpile_materials_development"]["planned_project_cost_yen"]
        == 901_000_000
    )


def test_sapporo_safety_project_batch_has_one_to_one_evidence_packets():
    records = load(CATALOG_PATH)["records"]
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(records) == 4
    assert {record["id"] for record in records} == {packet["project_id"] for packet in packets}
    assert all(packet["evidence_status"] == "reviewed" for packet in packets)


def test_sapporo_safety_project_source_records_complete_field_review():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    source = sources["sapporo-action-plan-2023-projects-safety-security"]
    assert source["source_kind"] == "pdf"
    assert source["page_count"] == 10
    assert source["review_status"] == "reviewed_for_complete_field_project_inventory"
    assert source["confidence"] == "high"
    assert source["field_total_project_count"] == 70
    assert source["reviewed_project_record_count"] == 70
    assert source["reviewed_main_project_record_count"] == 43
    assert source["reviewed_other_project_record_count"] == 27
    assert source["unresolved_project_record_count"] == 0


def test_sapporo_part1_remains_historical_inside_completed_599_identity_layer():
    catalog = load(CATALOG_PATH)
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    fact = facts["action-plan-safety-security-project-records-part1"]
    complete = facts["action-plan-safety-security-project-records-complete"]
    all_projects = facts["action-plan-all-project-identities-complete"]

    assert catalog["summary"]["description_text_reviewed_count"] == 0
    assert catalog["summary"]["field_total_project_count_reviewed"] is False
    assert catalog["summary"]["action_plan_599_coverage_claimed"] is False
    assert fact["value"] == 4
    assert complete["value"] == 70
    assert complete["main_project_record_count"] == 43
    assert complete["other_project_record_count"] == 27
    assert all_projects["value"] == 599
    assert manifest["status"] == "review_in_progress"
