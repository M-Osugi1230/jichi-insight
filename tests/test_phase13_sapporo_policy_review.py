from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"
SOURCE_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
INVENTORY_PATH = ROOT / "data/indexed/sapporo-city/source_inventory.json"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_policy_review_uses_reviewed_official_sources():
    manifest = load(MANIFEST_PATH)
    sources = load(SOURCE_PATH)["records"]
    source_map = {record["id"]: record for record in sources}
    manifest_source_ids = set(manifest["source_ids"])
    fact_source_ids = {
        fact["source_id"]
        for fact in manifest["reviewed_facts"]
        if "source_id" in fact
    }

    assert manifest["official_code"] == "011002"
    assert manifest["status"] == "review_in_progress"
    assert manifest_source_ids.issubset(source_map)
    assert fact_source_ids.issubset(manifest_source_ids)
    assert all(record["organization"] == "札幌市" for record in sources)
    assert all(record["url"].startswith("https://www.city.sapporo.jp/") for record in sources)
    assert source_map["sapporo-action-plan-2023-page"]["review_status"] == "reviewed"
    assert source_map["sapporo-action-plan-2023-progress-page"]["review_status"] == "reviewed"
    assert source_map["sapporo-action-plan-2023-outcomes-2024-report"][
        "review_status"
    ] == "reviewed_for_indicator_identity_and_prior_values"
    current_report = source_map["sapporo-action-plan-2023-outcomes-2025-report"]
    assert current_report["review_status"] == "reviewed_for_indicator_current_values"
    assert current_report["confidence"] == "high"
    assert all(record["confidence"] == "high" for record in source_map.values())

    life_living = source_map["sapporo-action-plan-2023-projects-life-living"]
    assert life_living["review_status"] == "reviewed_batches1_2_project_inventory_in_progress"
    assert life_living["reviewed_project_record_count"] == 43
    assert life_living["reviewed_printed_pages"] == "60-67"

    draft = source_map["sapporo-action-plan-2023-public-comment-draft"]
    assert draft["review_status"] == "navigation_and_transcription_only"

    revisions = source_map["sapporo-action-plan-2023-public-comment-results"]
    assert revisions["review_status"] == "reviewed_for_final_revision_scope"
    assert revisions["listed_revision_locations"] == [
        "printed_page_2",
        "printed_page_56",
        "printed_page_68",
        "printed_pages_134_173",
    ]


def test_sapporo_action_plan_reviewed_facts_are_exact_and_bounded():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    assert facts["action-plan-period"]["value"] == "2023年度～2027年度"
    assert facts["action-plan-project-count"]["value"] == 599
    assert facts["action-plan-project-cost"]["value"] == 1_785_400_000_000

    outcomes = facts["progress-outcome-indicators"]
    assert outcomes["measurement_fiscal_year"] == 2024
    assert outcomes["numerator"] == 17
    assert outcomes["denominator"] == 26
    assert outcomes["reported_ratio_percent"] == 65.4
    assert "独自の達成判定" in outcomes["interpretation_boundary"]

    current_values = facts["outcome-indicator-current-values-2025-report"]
    assert current_values["value"] == 26
    assert current_values["reporting_year"] == 2025
    assert current_values["review_status"] == "reviewed"
    assert "すべてを2024年度値とは扱わない" in current_values["interpretation_boundary"]

    targets = facts["progress-project-targets"]
    assert targets["numerator"] == 394
    assert targets["denominator"] == 403
    assert targets["reported_ratio_percent"] == 97.8
    assert "因果関係" in targets["interpretation_boundary"]

    costs = facts["progress-project-cost"]
    assert costs["value"] == 998_300_000_000
    assert costs["reported_progress_percent"] == 55.9
    assert "決算額と予算額が混在" in costs["interpretation_boundary"]


def test_sapporo_inventory_now_resolves_action_plan_canonical_route():
    inventory = load(INVENTORY_PATH)
    sources = {source["id"]: source for source in inventory["sources"]}

    action_plan = sources["sapporo-action-plan-2023"]
    assert action_plan["status"] == "official_landing_verified"
    assert action_plan["official_url"] == (
        "https://www.city.sapporo.jp/chosei/actionplan2023.html"
    )
    assert action_plan["effective_period"] == "2023年度～2027年度"

    progress = sources["sapporo-action-plan-2023-progress"]
    assert progress["status"] == "official_landing_verified"
    assert progress["available_periods"] == ["2023年度実績", "2024年度実績"]


def test_sapporo_remains_phase13_in_progress_until_project_records_are_reviewed():
    queue = load(QUEUE_PATH)
    sapporo = next(
        item for item in queue["execution_queue"] if item["official_code"] == "011002"
    )
    statuses = [item["status"] for item in queue["execution_queue"]]
    manifest = load(MANIFEST_PATH)

    assert sapporo["status"] == "review_in_progress"
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    )
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    )
    assert len(manifest["remaining_work"]) == 4
    assert any("599" in item for item in manifest["remaining_work"])
    assert any("26" in item and "403" in item for item in manifest["remaining_work"])
