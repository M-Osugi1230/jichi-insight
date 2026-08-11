from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
REGISTRY_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_outcome_reports_are_first_class_official_sources():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}

    prior = sources["sapporo-action-plan-2023-outcomes-2024-report"]
    current = sources["sapporo-action-plan-2023-outcomes-2025-report"]

    assert prior["organization"] == "札幌市"
    assert current["organization"] == "札幌市"
    assert prior["url"].startswith("https://www.city.sapporo.jp/")
    assert current["url"].startswith("https://www.city.sapporo.jp/")
    assert prior["measurement_fiscal_year"] == 2023
    assert current["measurement_fiscal_year"] == 2024
    assert prior["review_status"] == "reviewed_for_indicator_identity_and_prior_values"
    assert current["review_status"] == "aggregate_reviewed_record_values_pending"


def test_sapporo_current_report_contract_blocks_row_value_invention():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    current = sources["sapporo-action-plan-2023-outcomes-2025-report"]
    registry = load(REGISTRY_PATH)

    assert current["page_count"] == 3
    assert "個別2024年度実績値" in current["notes"]
    assert "推測せずpending" in current["notes"]
    assert registry["summary"]["current_value_reviewed_count"] == 0
    assert all(record["current_value_review_status"] == "pending" for record in registry["records"])


def test_sapporo_progress_page_and_current_pdf_aggregates_are_consistent():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    progress = sources["sapporo-action-plan-2023-progress-page"]
    registry = load(REGISTRY_PATH)
    summary = registry["summary"]

    assert "17上昇・8下降・1未集計" in progress["notes"]
    assert (
        summary["reported_2025_up_count"],
        summary["reported_2025_down_count"],
        summary["reported_2025_unaggregated_count"],
    ) == (17, 8, 1)
