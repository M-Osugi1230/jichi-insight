"""Issue #6: Fukuoka City three-year fiscal view data.

Pins the FY2022-FY2024 ordinary-account settlement records registered from
primary sources (Fukuoka Prefecture municipal fiscal trend tables, the
Ministry of Internal Affairs and Communications settlement card, the city
assembly secretariat settlement materials and the city's settlement card),
kept as a separate series from the general-account records, and the
FY2026 initial budget refined in place to its enacted amounts (official
gazette, thousand-yen precision).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
YEARS = (2022, 2023, 2024)

AMOUNT_METRICS = [
    "total_revenue",
    "total_expenditure",
    "local_tax",
    "formal_balance",
    "carryover_resources",
    "real_balance",
    "standard_fiscal_scale",
    "expenditure_by_purpose",
    "expenditure_by_nature",
    "fund_balance",
    "debt_balance",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def fiscal_records() -> list[dict[str, Any]]:
    return load_json("data/reviewed/fukuoka-city/fiscal_records.json")


def settlement_records() -> list[dict[str, Any]]:
    return load_json("data/reviewed/fukuoka-city/settlement_records.json")


def all_records() -> list[dict[str, Any]]:
    return [*fiscal_records(), *settlement_records()]


def ordinary_by_year_metric() -> dict[tuple[int, str], dict[str, Any]]:
    return {
        (record["fiscal_year"], record["metric"]): record
        for record in settlement_records()
    }


def general_by_id() -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in fiscal_records()}


def test_city_uses_only_registered_vocabulary() -> None:
    schema = load_json("schemas/fiscal_record.schema.json")
    metrics = set(schema["properties"]["metric"]["enum"])
    used = {record["metric"] for record in all_records()}
    assert used <= metrics
    # The city registration adds no new vocabulary beyond the pilot's.
    assert {
        "formal_balance",
        "real_balance",
        "carryover_resources",
        "standard_fiscal_scale",
        "expenditure_by_purpose",
        "expenditure_by_nature",
        "fund_balance",
        "debt_balance",
        "real_balance_ratio",
        "fiscal_strength_index",
        "current_balance_ratio",
        "real_debt_service_ratio",
        "future_burden_ratio",
        "population",
    } <= used


def test_new_series_cover_fy2022_to_fy2024() -> None:
    records = ordinary_by_year_metric()
    for year in YEARS:
        for metric in AMOUNT_METRICS:
            record = records[(year, metric)]
            assert record["amount_yen"] is not None
            assert record["unit"] == "yen"
            assert record["stage"] == "settlement"
            assert record["review_status"] == "reviewed"


def test_indicators_use_value_not_amount() -> None:
    records = ordinary_by_year_metric()
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


def test_totals_match_primary_sources() -> None:
    records = ordinary_by_year_metric()
    expected = {
        2022: (1_142_879_419_000, 1_124_508_359_000, 358_265_739_000),
        2023: (1_123_213_196_000, 1_104_890_536_000, 369_936_718_000),
        2024: (1_131_768_029_000, 1_113_379_745_000, 383_742_341_000),
    }
    for year, (revenue, expenditure, tax) in expected.items():
        assert records[(year, "total_revenue")]["amount_yen"] == revenue
        assert records[(year, "total_expenditure")]["amount_yen"] == expenditure
        assert records[(year, "local_tax")]["amount_yen"] == tax


def test_balance_arithmetic_is_consistent() -> None:
    records = ordinary_by_year_metric()
    expected_balances = {
        2022: (18_371_060_000, 8_503_521_000, 9_867_539_000, 442_104_112_000),
        2023: (18_322_660_000, 8_960_297_000, 9_362_363_000, 453_616_210_000),
        2024: (18_388_284_000, 8_943_321_000, 9_444_963_000, 470_514_285_000),
    }
    for year, (formal, carryover, real, scale) in expected_balances.items():
        assert records[(year, "formal_balance")]["amount_yen"] == formal
        assert records[(year, "carryover_resources")]["amount_yen"] == carryover
        assert records[(year, "real_balance")]["amount_yen"] == real
        assert records[(year, "standard_fiscal_scale")]["amount_yen"] == scale
        revenue = records[(year, "total_revenue")]["amount_yen"]
        expenditure = records[(year, "total_expenditure")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real


def test_fy2023_real_balance_documents_the_source_discrepancy() -> None:
    record = ordinary_by_year_metric()[(2023, "real_balance")]
    assert record["amount_yen"] == 9_362_363_000
    note = record["note"]
    # The prefecture text reading (9,362,361) was rejected in favour of the
    # city settlement card, which also matches the arithmetic.
    assert "9,362,361" in note
    assert "9,362,363" in note
    # The general-account real balance (9,362,362) is a different series and
    # must not be unified with the ordinary-account value.
    assert "9,362,362" in note
    assert "統一・修正はしない" in note


def test_indicator_values_match_primary_sources() -> None:
    records = ordinary_by_year_metric()
    expected = {
        2022: (93.6, 8.4, 74.3, 0.88, 2.2, 1_581_398),
        2023: (94.1, 8.0, 66.9, 0.865, 2.1, 1_594_659),
        2024: (93.6, 7.7, 58.8, 0.868, 2.0, 1_609_050),
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


def test_fy2022_fiscal_strength_index_keeps_two_decimal_precision() -> None:
    record = ordinary_by_year_metric()[(2022, "fiscal_strength_index")]
    assert record["value"] == 0.88
    # Every primary source prints only two decimals for FY2022; the record
    # must not pretend to a third decimal.
    assert "小数第2位" in record["note"]
    assert "未取得" in record["note"]


def test_population_reference_dates_differ_by_year() -> None:
    records = ordinary_by_year_metric()
    assert "令和5年1月1日現在" in records[(2022, "population")]["note"]
    assert "令和6年3月31日現在" in records[(2023, "population")]["note"]
    assert "令和7年3月31日現在" in records[(2024, "population")]["note"]
    for year in YEARS:
        assert "基準日" in records[(year, "population")]["note"]


def breakdown_sum(record: dict[str, Any], parent_key: str | None = ...) -> int:
    items = record["breakdown"]
    if parent_key is not ...:
        items = [
            item for item in items if (item["parent_key"] or None) == parent_key
        ]
    return sum(item["amount_yen"] or 0 for item in items)


def test_purpose_breakdown_sums_to_total_expenditure() -> None:
    records = ordinary_by_year_metric()
    for year in YEARS:
        record = records[(year, "expenditure_by_purpose")]
        # 13 published categories plus the not-applicable prior-year
        # advance appropriation row (null).
        assert len(record["breakdown"]) == 14
        assert breakdown_sum(record) == record["amount_yen"]
        assert record["amount_yen"] == records[(year, "total_expenditure")][
            "amount_yen"
        ]
        advance = next(
            item
            for item in record["breakdown"]
            if item["key"] == "prior_year_advance_appropriation"
        )
        assert advance["amount_yen"] is None


def test_purpose_and_nature_debt_service_are_different_classifications() -> None:
    records = ordinary_by_year_metric()
    expected = {
        2022: (104_115_730_000, 103_769_910_000),
        2023: (98_855_175_000, 98_469_691_000),
        2024: (97_556_573_000, 97_266_169_000),
    }
    for year, (purpose_debt, nature_debt) in expected.items():
        purpose = records[(year, "expenditure_by_purpose")]
        nature = records[(year, "expenditure_by_nature")]
        purpose_item = next(
            item for item in purpose["breakdown"] if item["key"] == "debt_service"
        )
        nature_item = next(
            item for item in nature["breakdown"] if item["key"] == "debt_service"
        )
        assert purpose_item["amount_yen"] == purpose_debt
        assert nature_item["amount_yen"] == nature_debt
        assert purpose_item["amount_yen"] != nature_item["amount_yen"]


def test_nature_breakdown_hierarchy_sums() -> None:
    records = ordinary_by_year_metric()
    for year in YEARS:
        record = records[(year, "expenditure_by_nature")]
        assert breakdown_sum(record, None) == record["amount_yen"]
        by_key = {item["key"]: item for item in record["breakdown"]}
        for group in ("mandatory_expenses", "capital_expenses"):
            children = [
                item
                for item in record["breakdown"]
                if item["parent_key"] == group
            ]
            assert (
                sum(item["amount_yen"] for item in children)
                == by_key[group]["amount_yen"]
            )
        # The "うち単独事業費" line is a sub-item of construction, not an
        # additional expense.
        assert (
            by_key["independent_construction"]["parent_key"] == "construction"
        )
        assert (
            by_key["independent_construction"]["amount_yen"]
            < by_key["construction"]["amount_yen"]
        )


def test_fund_and_debt_breakdowns_sum() -> None:
    records = ordinary_by_year_metric()
    expected_funds = {
        2022: 119_840_054_000,
        2023: 124_012_113_000,
        2024: 132_902_629_000,
    }
    expected_debt = {
        2022: (1_134_566_282_000, 399_564_727_000),
        2023: (1_105_392_640_000, 385_837_084_000),
        2024: (1_076_385_624_000, 370_765_218_000),
    }
    for year in YEARS:
        funds = records[(year, "fund_balance")]
        assert funds["amount_yen"] == expected_funds[year]
        assert breakdown_sum(funds) == funds["amount_yen"]
        assert len(funds["breakdown"]) == 3

        debt = records[(year, "debt_balance")]
        total, temporary = expected_debt[year]
        assert debt["amount_yen"] == total
        assert breakdown_sum(debt) == debt["amount_yen"]
        temp_item = next(
            item
            for item in debt["breakdown"]
            if item["key"] == "temporary_fiscal_measures_bonds"
        )
        assert temp_item["amount_yen"] == temporary
        excluding = next(
            item
            for item in debt["breakdown"]
            if item["key"] == "bonds_excluding_temporary_fiscal"
        )
        assert excluding["amount_yen"] == total - temporary
        # The excluding figure is derived by subtraction and must say so.
        assert "算出値" in excluding["note"]


def test_ordinary_series_is_separate_from_general_account() -> None:
    records = ordinary_by_year_metric()
    general = general_by_id()
    # FY2024 exists in both series with different values; neither may
    # overwrite or be merged into the other.
    ordinary_revenue = records[(2024, "total_revenue")]["amount_yen"]
    general_revenue = general[
        "jp-local-401307-fiscal-2024-total-revenue"
    ]["amount_yen"]
    assert ordinary_revenue == 1_131_768_029_000
    assert general_revenue == 1_126_286_330_000
    assert ordinary_revenue != general_revenue
    assert "別系列" in records[(2024, "total_revenue")]["note"]


def test_fy2026_budget_is_enacted_not_draft() -> None:
    general = general_by_id()
    revenue = general["jp-local-401307-fiscal-2026-total-revenue"]
    tax = general["jp-local-401307-fiscal-2026-local-tax"]
    expenditure = general["jp-local-401307-fiscal-2026-total-expenditure"]

    assert revenue["amount_yen"] == 1_131_811_000_000
    assert expenditure["amount_yen"] == 1_131_811_000_000
    assert tax["amount_yen"] == 426_320_009_000
    for record in (revenue, tax, expenditure):
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        # No record may still present itself as the draft budget; the
        # notes may mention the draft stage only as provenance.
        assert "予算案" not in (record["metric_label"] or "")
        assert "成立" in (record["note"] or "")
        assert "fukuoka-city-gazette-budget-2026-pdf" in record["sources"]
    # The refinement stays within the draft's hundred-million-yen rounding.
    assert abs(revenue["amount_yen"] - 1_131_800_000_000) < 100_000_000
    assert abs(tax["amount_yen"] - 426_300_000_000) < 100_000_000


def test_city_loader_merges_the_settlement_series() -> None:
    loader = (ROOT / "apps/web/lib/fukuokaCityFinance.ts").read_text(
        encoding="utf-8"
    )
    for required in (
        "settlement_records.json",
        "settlement_evidence_packets.json",
        "settlementRecords as FiscalRecord[]",
        "settlementEvidencePackets as EvidencePacket[]",
    ):
        assert required in loader


def test_new_sources_are_registered_in_city_catalog() -> None:
    catalog = load_json("data/catalog/fukuoka_city_finance_sources.json")
    source_ids = {record["id"] for record in catalog["records"]}
    expected = {
        "fukuoka-city-pref-fiscal-trend-pdf",
        "fukuoka-city-soumu-settlement-card-2022-pdf",
        "fukuoka-city-assembly-settlement-2023-pdf",
        "fukuoka-city-soumu-fiscal-overview-2022-pdf",
        "fukuoka-city-gazette-budget-2026-pdf",
        "fukuoka-city-assembly-newsletter-171",
        "fukuoka-city-settlement-2023-booklet-pdf",
    }
    assert expected <= source_ids
    for record in all_records():
        assert set(record["sources"]) <= source_ids | {
            source["id"]
            for catalog_path in (
                "data/catalog/official_sources.json",
                "data/catalog/fukuoka_finance_sources.json",
            )
            for source in load_json(catalog_path)["records"]
        }
