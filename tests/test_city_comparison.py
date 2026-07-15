from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_records(path: str) -> list[dict[str, object]]:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def selected_record(
    records: list[dict[str, object]],
    fiscal_year: int,
    stage: str,
    metric: str,
) -> dict[str, object]:
    matches = [
        record
        for record in records
        if record["fiscal_year"] == fiscal_year
        and record["stage"] == stage
        and record["metric"] == metric
    ]
    assert len(matches) == 1
    return matches[0]


def test_city_comparison_uses_matching_scope() -> None:
    fukuoka = load_records("data/reviewed/fukuoka-city/fiscal_records.json")
    kitakyushu = load_records("data/reviewed/kitakyushu-city/fiscal_records.json")
    comparable = [
        (2026, "initial_budget", "total_revenue"),
        (2026, "initial_budget", "local_tax"),
        (2024, "settlement", "total_revenue"),
        (2024, "settlement", "total_expenditure"),
    ]

    for fiscal_year, stage, metric in comparable:
        left = selected_record(fukuoka, fiscal_year, stage, metric)
        right = selected_record(kitakyushu, fiscal_year, stage, metric)
        assert left["account_type"] == right["account_type"] == "general"
        assert left["unit"] == right["unit"] == "yen"
        assert left["review_status"] == right["review_status"] == "reviewed"


def test_city_comparison_does_not_require_missing_tax_settlement() -> None:
    fukuoka = load_records("data/reviewed/fukuoka-city/fiscal_records.json")
    assert not any(
        record["fiscal_year"] == 2024
        and record["stage"] == "settlement"
        and record["metric"] == "local_tax"
        for record in fukuoka
    )
