"""Issue #6: Kitakyushu City three-year fiscal view data.

Pins the FY2022-FY2024 ordinary-account settlement records registered from
primary sources (the city's settlement cards, fiscal condition collections,
soundness-ratio publications and property statements), kept as a separate
series from the general-account records, and the FY2026 initial budget
refined in place to its enacted amounts (the budget book, thousand-yen
precision, corroborated by the assembly's February 2026 session results).
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

ADJUSTED_RATIO = "current_balance_ratio_excluding_temporary_bonds"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def fiscal_records() -> list[dict[str, Any]]:
    return load_json("data/reviewed/kitakyushu-city/fiscal_records.json")


def settlement_records() -> list[dict[str, Any]]:
    return load_json("data/reviewed/kitakyushu-city/settlement_records.json")


def all_records() -> list[dict[str, Any]]:
    return [*fiscal_records(), *settlement_records()]


def ordinary_by_year_metric() -> dict[tuple[int, str], dict[str, Any]]:
    return {
        (record["fiscal_year"], record["metric"]): record
        for record in settlement_records()
    }


def general_by_id() -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in fiscal_records()}


def test_city_uses_registered_vocabulary() -> None:
    schema = load_json("schemas/fiscal_record.schema.json")
    metrics = set(schema["properties"]["metric"]["enum"])
    used = {record["metric"] for record in all_records()}
    assert used <= metrics
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
    # The only vocabulary added for this city is the adjusted current
    # balance ratio printed on its settlement cards.
    assert ADJUSTED_RATIO in metrics


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
        2022: (605_369_946_000, 601_494_524_000, 179_669_924_000),
        2023: (617_806_572_000, 614_040_979_000, 181_081_993_000),
        2024: (626_051_961_000, 621_430_401_000, 180_177_794_000),
    }
    for year, (revenue, expenditure, tax) in expected.items():
        assert records[(year, "total_revenue")]["amount_yen"] == revenue
        assert records[(year, "total_expenditure")]["amount_yen"] == expenditure
        assert records[(year, "local_tax")]["amount_yen"] == tax


def test_balance_arithmetic_is_consistent() -> None:
    records = ordinary_by_year_metric()
    expected_balances = {
        2022: (3_875_422_000, 2_127_474_000, 1_747_948_000, 283_019_933_000),
        2023: (3_765_593_000, 1_537_293_000, 2_228_300_000, 287_670_566_000),
        2024: (4_621_560_000, 2_738_684_000, 1_882_876_000, 292_156_624_000),
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


def test_indicator_values_match_primary_sources() -> None:
    records = ordinary_by_year_metric()
    expected = {
        2022: (99.3, 10.4, 147.2, 0.7, 0.6, 929_396),
        2023: (97.1, 10.1, 143.2, 0.69, 0.8, 921_241),
        2024: (99.3, 10.6, 143.0, 0.69, 0.6, 913_577),
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


def test_adjusted_current_balance_ratio_skips_unobtained_fy2023() -> None:
    records = ordinary_by_year_metric()
    # The FY2023 settlement card is image-only, so the adjusted ratio
    # (excluding temporary fiscal measures bonds etc.) could not be
    # obtained for FY2023 and must not be registered for that year.
    assert (2023, ADJUSTED_RATIO) not in records
    assert records[(2022, ADJUSTED_RATIO)]["value"] == 106.1
    assert records[(2024, ADJUSTED_RATIO)]["value"] == 101.3
    for year in (2022, 2024):
        record = records[(year, ADJUSTED_RATIO)]
        assert record["unit"] == "percent"
        assert record["amount_yen"] is None
        assert "未取得" not in record["note"]
        assert "収録していない" in record["note"]


def test_population_reference_dates_are_stated() -> None:
    records = ordinary_by_year_metric()
    assert "令和5年1月1日現在" in records[(2022, "population")]["note"]
    assert "令和6年1月1日現在" in records[(2023, "population")]["note"]
    assert "令和7年1月1日現在" in records[(2024, "population")]["note"]


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
        2022: (68_337_831_000, 68_059_122_000),
        2023: (68_456_024_000, 68_111_956_000),
        2024: (70_692_504_000, 70_326_046_000),
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
        # The debt-service components printed on the card (principal,
        # interest, temporary-borrowing interest) exhaust the nature
        # debt-service figure.
        components = [
            item
            for item in record["breakdown"]
            if item["parent_key"] == "debt_service"
        ]
        assert (
            sum(item["amount_yen"] for item in components)
            == by_key["debt_service"]["amount_yen"]
        )
        # The "うち" lines are sub-items of their parents, not
        # additional expenses.
        assert by_key["staff_salaries"]["parent_key"] == "personnel"
        assert (
            by_key["staff_salaries"]["amount_yen"]
            < by_key["personnel"]["amount_yen"]
        )
        assert by_key["independent_construction"]["parent_key"] == "construction"
        assert (
            by_key["subsidized_construction"]["amount_yen"]
            + by_key["independent_construction"]["amount_yen"]
            < by_key["construction"]["amount_yen"]
        )


def test_fund_balance_uses_settlement_card_basis_only() -> None:
    records = ordinary_by_year_metric()
    # (card-basis total, card-basis fiscal adjustment fund,
    #  property-statement-basis fiscal adjustment fund)
    expected = {
        2022: (45_507_550_000, 15_576_376_000, "17,076,376千円"),
        2023: (50_719_235_000, 15_990_976_000, "16,390,976千円"),
        2024: (45_380_233_000, 14_133_776_000, "17,043,376千円"),
    }
    for year, (total, adjustment, property_value) in expected.items():
        funds = records[(year, "fund_balance")]
        assert funds["amount_yen"] == total
        assert breakdown_sum(funds) == funds["amount_yen"]
        assert len(funds["breakdown"]) == 3
        adjustment_item = next(
            item
            for item in funds["breakdown"]
            if item["key"] == "fiscal_adjustment_fund"
        )
        assert adjustment_item["amount_yen"] == adjustment
        # The registered balance is the settlement-card basis (MIC
        # three categories); the property-statement basis figure is a
        # different basis and appears only in the note, never mixed in.
        assert "決算カード基準" in funds["note"]
        assert property_value in funds["note"]
        assert "混ぜていない" in funds["note"]


def test_debt_balance_matches_primary_sources() -> None:
    records = ordinary_by_year_metric()
    expected = {
        2022: 1_014_124_299_000,
        2023: 1_008_758_183_000,
        2024: 1_002_178_426_000,
    }
    for year, total in expected.items():
        assert records[(year, "debt_balance")]["amount_yen"] == total


def test_ordinary_series_is_separate_from_general_account() -> None:
    records = ordinary_by_year_metric()
    general = general_by_id()
    # FY2024 exists in both series with different values; neither may
    # overwrite or be merged into the other.
    ordinary_revenue = records[(2024, "total_revenue")]["amount_yen"]
    general_revenue = general[
        "jp-local-401005-fiscal-2024-total-revenue"
    ]["amount_yen"]
    assert ordinary_revenue == 626_051_961_000
    assert general_revenue == 619_800_427_000
    assert ordinary_revenue != general_revenue
    assert "別系列" in records[(2024, "total_revenue")]["note"]
    # The FY2024 city tax coincides across the two series in this city;
    # the records still stay separate.
    assert records[(2024, "local_tax")]["amount_yen"] == general[
        "jp-local-401005-fiscal-2024-local-tax"
    ]["amount_yen"] == 180_177_794_000


def test_fy2026_budget_is_enacted_not_draft() -> None:
    general = general_by_id()
    revenue = general["jp-local-401005-fiscal-2026-total-revenue"]
    tax = general["jp-local-401005-fiscal-2026-local-tax"]
    expenditure = general["jp-local-401005-fiscal-2026-total-expenditure"]

    assert revenue["amount_yen"] == 647_684_000_000
    assert expenditure["amount_yen"] == 647_684_000_000
    # The enacted city tax at thousand-yen precision, replacing the
    # draft-stage hundred-million-yen rounded figure.
    assert tax["amount_yen"] == 192_462_010_000
    for record in (revenue, tax, expenditure):
        assert record["stage"] == "initial_budget"
        assert record["account_type"] == "general"
        # No record may still present itself as the draft budget; the
        # notes may mention the draft stage only as provenance.
        assert "予算案" not in (record["metric_label"] or "")
        assert "成立" in (record["note"] or "")
        assert "kitakyushu-budget-2026-book-pdf" in record["sources"]
    assert "kitakyushu-assembly-results-2026-02-pdf" in revenue["sources"]
    # The refinement stays within the draft's hundred-million-yen
    # rounding and is documented as a precision difference, not an
    # assembly amendment.
    assert abs(tax["amount_yen"] - 192_500_000_000) < 100_000_000
    assert "議会での修正による差異ではない" in tax["note"]


def test_city_loader_merges_the_settlement_series() -> None:
    loader = (ROOT / "apps/web/lib/kitakyushuFinance.ts").read_text(
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
    catalog = load_json("data/catalog/kitakyushu_finance_sources.json")
    source_ids = {record["id"] for record in catalog["records"]}
    expected = {
        "kitakyushu-settlement-card-2022-pdf",
        "kitakyushu-settlement-card-2023-pdf",
        "kitakyushu-settlement-card-2024-pdf",
        "kitakyushu-fiscal-collection-2022-xlsx",
        "kitakyushu-fiscal-collection-2023-xlsx",
        "kitakyushu-fiscal-collection-2024-xlsx",
        "kitakyushu-soundness-2022-pdf",
        "kitakyushu-soundness-2023-pdf",
        "kitakyushu-soundness-2024-pdf",
        "kitakyushu-property-statement-2022-pdf",
        "kitakyushu-property-statement-2023-pdf",
        "kitakyushu-property-statement-2024-pdf",
        "kitakyushu-budget-2026-book-pdf",
        "kitakyushu-assembly-results-2026-02-pdf",
    }
    assert expected <= source_ids
    for record in all_records():
        assert set(record["sources"]) <= source_ids | {
            source["id"]
            for catalog_path in (
                "data/catalog/official_sources.json",
            )
            for source in load_json(catalog_path)["records"]
        }
