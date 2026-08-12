from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data/catalog/sapporo_policy_sources.json"
REGISTRY_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_registry.json"
CURRENT_VALUES_PATH = ROOT / "data/catalog/sapporo_outcome_indicator_2025_report_values.json"


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
    assert current["review_status"] == "reviewed_for_indicator_current_values"
    assert current["confidence"] == "high"


def test_sapporo_current_report_contract_has_complete_row_alignment_without_invention():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    current = sources["sapporo-action-plan-2023-outcomes-2025-report"]
    registry = load(REGISTRY_PATH)
    values = load(CURRENT_VALUES_PATH)

    assert current["page_count"] == 3
    assert "26ユニーク指標" in current["notes"]
    assert "17上昇・8下降・1未集計" in current["notes"]
    assert registry["summary"]["current_value_reviewed_count"] == 26
    assert all(
        record["current_value_review_status"] == "reviewed"
        for record in registry["records"]
    )
    assert values["status"] == "reviewed_current_values_complete"
    assert len(values["records"]) == 26
    assert "not recomputed by Jichi Insight" in values["quality_boundary"]


def test_sapporo_progress_page_and_current_pdf_aggregates_are_consistent():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    progress = sources["sapporo-action-plan-2023-progress-page"]
    registry = load(REGISTRY_PATH)
    values = load(CURRENT_VALUES_PATH)
    summary = registry["summary"]
    counts = Counter(record["source_trend_classification"] for record in values["records"])

    assert "17上昇・8下降・1未集計" in progress["notes"]
    assert (
        summary["reported_2025_up_count"],
        summary["reported_2025_down_count"],
        summary["reported_2025_unaggregated_count"],
    ) == (17, 8, 1)
    assert counts == {
        "source_reported_up": 17,
        "source_reported_down": 8,
        "source_reported_unaggregated": 1,
    }
