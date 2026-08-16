from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"
SOURCE_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
INVENTORY_PATH = ROOT / "data/indexed/sapporo-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
READINESS_PATH = ROOT / "data/catalog/sapporo_phase13_completion_readiness.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_policy_review_uses_reviewed_official_sources():
    manifest = load(MANIFEST_PATH)
    sources = load(SOURCE_PATH)["records"]
    source_map = {record["id"]: record for record in sources}
    manifest_source_ids = set(manifest["source_ids"])
    fact_source_ids = {fact["source_id"] for fact in manifest["reviewed_facts"] if "source_id" in fact}

    assert manifest["official_code"] == "011002"
    assert manifest["status"] == "review_in_progress"
    assert manifest_source_ids.issubset(source_map)
    assert fact_source_ids.issubset(source_map)
    assert all(record["organization"] == "札幌市" for record in sources)
    assert all(record["url"].startswith("https://www.city.sapporo.jp/") for record in sources)
    assert all(record["confidence"] == "high" for record in sources)

    assert source_map["sapporo-action-plan-2023-page"]["review_status"] == "reviewed"
    assert source_map["sapporo-action-plan-2023-final-overview"]["review_status"] == "reviewed_for_final_field_project_denominators"

    children = source_map["sapporo-action-plan-2023-projects-children-youth"]
    assert children["field_total_project_count"] == 121
    assert children["reviewed_project_record_count"] == 121
    assert children["direct_final_all_pages_confirmation"] is True

    life = source_map["sapporo-action-plan-2023-projects-life-living"]
    assert life["field_total_project_count"] == 85
    assert life["reviewed_project_record_count"] == 85
    assert life["blocked_printed_pages"] == []
    assert life["direct_final_page68_confirmation"] is True

    community = source_map["sapporo-action-plan-2023-projects-community"]
    assert community["reviewed_project_record_count"] == 47
    assert community["direct_final_all_pages_confirmation"] is True

    economy = source_map["sapporo-action-plan-2023-projects-economy"]
    assert economy["reviewed_project_record_count"] == 74
    assert economy["direct_final_all_pages_confirmation"] is True

    sports = source_map["sapporo-action-plan-2023-projects-sports-culture"]
    assert sports["review_status"] == "reviewed_final_51_direct_final_reconciliation"
    assert sports["field_total_project_count"] == 51
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["direct_final_page104_confirmation"] is True

    environment = source_map["sapporo-action-plan-2023-projects-environment"]
    assert environment["reviewed_project_record_count"] == 74
    assert environment["final_department_correction_count"] == 5

    draft = source_map["sapporo-action-plan-2023-public-comment-draft"]
    assert draft["review_status"] == "navigation_and_transcription_only"


def test_sapporo_action_plan_reviewed_facts_are_exact_and_bounded():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    assert facts["action-plan-period"]["value"] == "2023年度～2027年度"
    assert facts["action-plan-project-count"]["value"] == 599
    assert facts["action-plan-project-cost"]["value"] == 1_785_400_000_000

    complete = facts["action-plan-all-project-identities-complete"]
    assert complete["value"] == 599
    assert complete["main_project_record_count"] == 406
    assert complete["other_project_record_count"] == 193

    outcomes = facts["progress-outcome-indicators"]
    assert outcomes["measurement_fiscal_year"] == 2024
    assert outcomes["numerator"] == 17
    assert outcomes["denominator"] == 26
    assert outcomes["reported_ratio_percent"] == 65.4

    current_values = facts["outcome-indicator-current-values-2025-report"]
    assert current_values["value"] == 26
    assert current_values["reporting_year"] == 2025

    targets = facts["progress-project-targets"]
    assert targets["numerator"] == 394
    assert targets["denominator"] == 403
    assert targets["reported_ratio_percent"] == 97.8
    assert targets["review_status"] == "reviewed_aggregate_only"

    costs = facts["progress-project-cost"]
    assert costs["value"] == 998_300_000_000
    assert costs["reported_progress_percent"] == 55.9
    assert "決算額と予算額が混在" in costs["interpretation_boundary"]


def test_sapporo_inventory_now_resolves_action_plan_canonical_route():
    inventory = load(INVENTORY_PATH)
    sources = {source["id"]: source for source in inventory["sources"]}
    action_plan = sources["sapporo-action-plan-2023"]
    assert action_plan["status"] == "official_landing_verified"
    assert action_plan["official_url"] == "https://www.city.sapporo.jp/chosei/actionplan2023.html"
    assert action_plan["effective_period"] == "2023年度～2027年度"
    progress = sources["sapporo-action-plan-2023-progress"]
    assert progress["status"] == "official_landing_verified"


def test_sapporo_action_plan_identity_gate_is_complete_but_city_remains_in_progress():
    queue = load(QUEUE_PATH)
    sapporo = next(item for item in queue["execution_queue"] if item["official_code"] == "011002")
    manifest = load(MANIFEST_PATH)
    readiness = load(READINESS_PATH)
    identity_gate = next(item for item in readiness["blocking_gates"] if item["id"] == "action-plan-project-records")
    target_gate = next(item for item in readiness["blocking_gates"] if item["id"] == "principal-project-target-records")

    assert sapporo["status"] == "review_in_progress"
    assert manifest["status"] == "review_in_progress"
    assert identity_gate["state"] == "complete_599_of_599_final_identity_review"
    assert identity_gate["reviewed_scope"] == 599
    assert identity_gate["remaining_scope"] == 0
    assert target_gate["state"] == "not_complete"
    assert target_gate["required_scope"] == 403
    assert readiness["current_status"] == "review_in_progress"
