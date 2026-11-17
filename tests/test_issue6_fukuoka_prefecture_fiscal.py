"""Issue #6 pilot: Fukuoka-prefecture three-year fiscal view data.

Pins the fiscal-record vocabulary extension (balances, breakdowns, funds,
debt, indicators, population) and the FY2022-FY2024 ordinary-account
settlement records registered from primary sources (Ministry of Internal
Affairs and Communications settlement tables, prefecture fund statements
and the prefecture settlement booklet).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2022, 2023, 2024)

NEW_METRICS = {
    "formal_balance",
    "real_balance",
    "carryover_resources",
    "standard_fiscal_scale",
    "expenditure_by_purpose",
    "expenditure_by_nature",
    "expenditure_by_nature_prefecture",
    "fund_balance_fiscal_adjustment",
}


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def settlement_records() -> list[dict[str, Any]]:
    return load_json("data/reviewed/fukuoka-prefecture/settlement_records.json")


def by_year_metric() -> dict[tuple[int, str], dict[str, Any]]:
    return {
        (record["fiscal_year"], record["metric"]): record
        for record in settlement_records()
    }


def test_fiscal_vocabulary_extension_is_registered_in_schema() -> None:
    schema = load_json("schemas/fiscal_record.schema.json")
    metrics = set(schema["properties"]["metric"]["enum"])

    assert metrics >= NEW_METRICS
    # Metrics that already existed in the vocabulary but were unused.
    assert {
        "fund_balance",
        "debt_balance",
        "real_balance_ratio",
        "fiscal_strength_index",
        "current_balance_ratio",
        "real_debt_service_ratio",
        "future_burden_ratio",
        "population",
    } <= metrics

    breakdown = schema["properties"]["breakdown"]
    assert breakdown["type"] == ["array", "null"]
    item = breakdown["items"]
    assert item["additionalProperties"] is False
    assert set(item["required"]) == {"key", "label", "amount_yen"}
    assert set(item["properties"]) == {
        "key",
        "label",
        "amount_yen",
        "parent_key",
        "note",
    }


def test_new_series_cover_fy2022_to_fy2024() -> None:
    records = by_year_metric()
    amount_metrics = [
        "local_tax",
        "formal_balance",
        "real_balance",
        "carryover_resources",
        "standard_fiscal_scale",
        "expenditure_by_purpose",
        "expenditure_by_nature",
        "fund_balance",
        "fund_balance_fiscal_adjustment",
        "debt_balance",
    ]
    for year in YEARS:
        for metric in amount_metrics:
            record = records[(year, metric)]
            assert record["amount_yen"] is not None
            assert record["unit"] == "yen"
            assert record["stage"] == "settlement"
            assert record["account_type"] == "ordinary"
            assert record["review_status"] == "reviewed"
    # The prefecture's own nature grouping is published only for FY2023/24.
    assert (2022, "expenditure_by_nature_prefecture") not in records
    for year in (2023, 2024):
        assert (year, "expenditure_by_nature_prefecture") in records


def test_indicators_use_value_not_amount() -> None:
    records = by_year_metric()
    expected_units = {
        "current_balance_ratio": "percent",
        "real_debt_service_ratio": "percent",
        "future_burden_ratio": "percent",
        "real_balance_ratio": "percent",
        "fiscal_strength_index": "index",
        "population": "persons",
    }
    for year in YEARS:
        for metric, unit in expected_units.items():
            record = records[(year, metric)]
            assert record["amount_yen"] is None
            assert record["value"] is not None
            assert record["unit"] == unit


def test_indicator_values_match_primary_sources() -> None:
    records = by_year_metric()
    expected = {
        2022: (96.2, 11.2, 250.7, 0.62027, 3.1, 5_104_921),
        2023: (97.3, 11.3, 248.4, 0.61396, 1.2, 5_095_379),
        2024: (95.6, 11.9, 245.3, 0.63618, 1.3, 5_086_957),
    }
    for year, (current, debt_ratio, burden, strength, real_ratio, pop) in (
        expected.items()
    ):
        assert records[(year, "current_balance_ratio")]["value"] == current
        assert records[(year, "real_debt_service_ratio")]["value"] == debt_ratio
        assert records[(year, "future_burden_ratio")]["value"] == burden
        assert records[(year, "fiscal_strength_index")]["value"] == strength
        assert records[(year, "real_balance_ratio")]["value"] == real_ratio
        assert records[(year, "population")]["value"] == pop


def test_balance_arithmetic_is_consistent() -> None:
    records = by_year_metric()
    for year in YEARS:
        revenue = records[(year, "total_revenue")]["amount_yen"]
        expenditure = records[(year, "total_expenditure")]["amount_yen"]
        formal = records[(year, "formal_balance")]["amount_yen"]
        carryover = records[(year, "carryover_resources")]["amount_yen"]
        real = records[(year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real


def test_refined_totals_match_thousand_yen_sources() -> None:
    records = by_year_metric()
    expected = {
        2022: (2_277_786_328_000, 2_203_057_341_000, 734_299_021_000),
        2023: (2_054_311_220_000, 1_993_404_740_000, 730_868_711_000),
        2024: (2_093_699_535_000, 2_032_626_014_000, 784_235_058_000),
    }
    previous_million_yen = {
        2022: (2_277_786_000_000, 2_203_057_000_000),
        2023: (2_054_311_000_000, 1_993_405_000_000),
        2024: (2_093_700_000_000, 2_032_626_000_000),
    }
    for year, (revenue, expenditure, tax) in expected.items():
        assert records[(year, "total_revenue")]["amount_yen"] == revenue
        assert records[(year, "total_expenditure")]["amount_yen"] == expenditure
        assert records[(year, "local_tax")]["amount_yen"] == tax
        old_revenue, old_expenditure = previous_million_yen[year]
        # Refinement stays within the earlier million-yen rounding range.
        assert abs(revenue - old_revenue) < 1_000_000
        assert abs(expenditure - old_expenditure) < 1_000_000


def breakdown_sum(record: dict[str, Any], parent_key: str | None = ...) -> int:
    items = record["breakdown"]
    if parent_key is not ...:
        items = [
            item for item in items if (item["parent_key"] or None) == parent_key
        ]
    return sum(item["amount_yen"] or 0 for item in items)


def test_purpose_breakdown_sums_to_total_expenditure() -> None:
    records = by_year_metric()
    for year in YEARS:
        record = records[(year, "expenditure_by_purpose")]
        assert len(record["breakdown"]) == 22
        assert breakdown_sum(record) == record["amount_yen"]
        assert record["amount_yen"] == records[(year, "total_expenditure")][
            "amount_yen"
        ]


def test_nature_breakdown_hierarchy_sums() -> None:
    records = by_year_metric()
    for year in YEARS:
        record = records[(year, "expenditure_by_nature")]
        assert breakdown_sum(record, None) == record["amount_yen"]
        by_key = {item["key"]: item for item in record["breakdown"]}
        for group in ("mandatory_expenses", "other_expenses", "capital_expenses"):
            children = [
                item
                for item in record["breakdown"]
                if item["parent_key"] == group and not item["label"].startswith("うち")
            ]
            assert (
                sum(item["amount_yen"] for item in children)
                == by_key[group]["amount_yen"]
            )


def test_prefecture_nature_grouping_is_kept_separate() -> None:
    records = by_year_metric()
    for year in (2023, 2024):
        record = records[(year, "expenditure_by_nature_prefecture")]
        assert breakdown_sum(record, None) == record["amount_yen"]
        assert "合算・混用しない" in record["note"]
        labels = {item["label"] for item in record["breakdown"]}
        assert "社会保障関係費" in labels
        standard = records[(year, "expenditure_by_nature")]
        standard_labels = {item["label"] for item in standard["breakdown"]}
        assert "社会保障関係費" not in standard_labels


def test_fund_and_debt_breakdowns_sum_and_carry_scope_notes() -> None:
    records = by_year_metric()
    for year in YEARS:
        funds = records[(year, "fund_balance")]
        assert breakdown_sum(funds) == funds["amount_yen"]
        assert "公債管理特別会計分" in funds["note"]

        trio = records[(year, "fund_balance_fiscal_adjustment")]
        assert breakdown_sum(trio) == trio["amount_yen"]
        assert trio["amount_yen"] != funds["amount_yen"]

        debt = records[(year, "debt_balance")]
        assert breakdown_sum(debt) == debt["amount_yen"]
        temp = next(
            item
            for item in debt["breakdown"]
            if item["key"] == "temporary_fiscal_measures_bonds"
        )
        assert "算出値" in temp["note"]


def test_real_balance_note_distinguishes_prefecture_headline_value() -> None:
    records = by_year_metric()
    for year in YEARS:
        note = records[(year, "real_balance")]["note"]
        assert "見出し値" in note
        assert "定義が異なる" in note


def test_new_sources_are_registered_in_catalog() -> None:
    catalog = load_json("data/catalog/fukuoka_finance_sources.json")
    source_ids = {record["id"] for record in catalog["records"]}
    expected = {
        "fukuoka-pref-soumu-settlement-2022-xlsx",
        "fukuoka-pref-soumu-settlement-2023-xlsx",
        "fukuoka-pref-soumu-settlement-2024-xlsx",
        "fukuoka-pref-fund-status-2022-pdf",
        "fukuoka-pref-fund-status-2023-pdf",
        "fukuoka-pref-fund-status-2024-pdf",
        "fukuoka-pref-settlement-2024-booklet-pdf",
    }
    assert expected <= source_ids
    for record in settlement_records():
        assert set(record["sources"]) <= source_ids


def test_finance_loader_exposes_generic_series_and_breakdowns() -> None:
    loader = (ROOT / "apps/web/lib/finance.ts").read_text(encoding="utf-8")
    for required in (
        "FiscalBreakdownItem",
        "breakdown?: FiscalBreakdownItem[] | null",
        "settlementSeries",
        "breakdownItems",
        "breakdownChildren",
    ):
        assert required in loader
