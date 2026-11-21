"""Issue #854 (Kobe City part): Hyogo cluster stage 1 — Kobe City settlements.

Covers the FY2022-FY2024 ordinary-account settlements of Kobe City,
cross-checked field by field between the MIC settlement cards (Hyogo
edition, print PDF and the MIC-published Excel edition) and the city's
fiscal situation collections, with arithmetic checks. Every figure of the
two systems agreed, so no value had to be adopted from one side only.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/kobe-city"
MID = "jp-local-281000"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_kobe_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 281000: the MIC settlement
    # cards carry the Kobe City sheet under that code (prefecture 28,
    # city 1000) and the city is a designated city.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "281000"
    assert municipality["name_ja"] == "神戸市"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_kobe_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard fiscal
        # scale, fund balance total, debt balance) in thousand yen
        2022: (976542111, 963856264, 314053786, 449411950, 87408720, 1158862890),
        2023: (952593692, 931550600, 321122432, 454912157, 90187196, 1136707207),
        2024: (1005169825, 984587697, 324372624, 463449254, 89859644, 1123240309),
    }
    for fiscal_year, (
        revenue,
        expenditure,
        local_tax,
        standard_scale,
        fund_total,
        debt_total,
    ) in expected.items():
        assert by[(fiscal_year, "total_revenue")]["amount_yen"] == revenue * 1000
        assert by[(fiscal_year, "total_expenditure")]["amount_yen"] == expenditure * 1000
        assert by[(fiscal_year, "local_tax")]["amount_yen"] == local_tax * 1000
        assert (
            by[(fiscal_year, "standard_fiscal_scale")]["amount_yen"]
            == standard_scale * 1000
        )
        assert by[(fiscal_year, "fund_balance")]["amount_yen"] == fund_total * 1000
        assert by[(fiscal_year, "debt_balance")]["amount_yen"] == debt_total * 1000
        for record in by.values():
            if record["fiscal_year"] != fiscal_year:
                continue
            assert record["municipality_id"] == MID
            assert record["account_type"] == "ordinary"
            assert record["stage"] == "settlement"
            assert record["review_status"] == "reviewed"
            assert record["sources"] == [
                f"kobe-city-mic-settlement-card-fy{fiscal_year}",
                f"kobe-city-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_kobe_settlement_arithmetic() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        revenue = by[(fiscal_year, "total_revenue")]["amount_yen"]
        expenditure = by[(fiscal_year, "total_expenditure")]["amount_yen"]
        formal = by[(fiscal_year, "formal_balance")]["amount_yen"]
        carryover = by[(fiscal_year, "carryover_resources")]["amount_yen"]
        real = by[(fiscal_year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real

        purpose = by[(fiscal_year, "expenditure_by_purpose")]
        assert (
            sum(
                item["amount_yen"] or 0
                for item in purpose["breakdown"]
            )
            == expenditure
        )
        nature = by[(fiscal_year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure
        mandatory = by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        children = {
            item["key"]: item["amount_yen"]
            for item in mandatory
            if item["parent_key"] == "mandatory_expenses"
        }
        assert sum(children.values()) == next(
            item["amount_yen"]
            for item in mandatory
            if item["key"] == "mandatory_expenses"
        )

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert sum(item["amount_yen"] for item in fund["breakdown"]) == fund["amount_yen"]

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_kobe_settlement_breakdowns_handle_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # The prior-year advance appropriation is printed as "-" on the
        # card in every year: kept as null, never zero-filled.
        assert purpose["前年度繰上充用金"] is None
        assert purpose["諸支出金"] is not None
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        # Dash categories of the nature table are omitted entirely.
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels


def test_kobe_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds (103.7 / 101.7 / 100.6).
    assert by[(2022, "current_balance_ratio")]["value"] == 97.1
    assert by[(2023, "current_balance_ratio")]["value"] == 97.6
    assert by[(2024, "current_balance_ratio")]["value"] == 98.7
    assert by[(2022, "real_debt_service_ratio")]["value"] == 4.8
    assert by[(2024, "real_debt_service_ratio")]["value"] == 4.9
    assert by[(2022, "future_burden_ratio")]["value"] == 60.9
    assert by[(2024, "future_burden_ratio")]["value"] == 64.5
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.77
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.76
    assert by[(2022, "real_balance_ratio")]["value"] == 0.3
    # Resident-register population as of 1 January of the survey year.
    assert by[(2022, "population")]["value"] == 1510917
    assert by[(2023, "population")]["value"] == 1500425
    assert by[(2024, "population")]["value"] == 1493543


def test_kobe_settlement_packets_cover_every_record() -> None:
    records = _settlement_records()
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert len(claim["source_ids"]) == 2


def test_kobe_catalog_shape() -> None:
    catalog = load_json("data/catalog/kobe_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 6
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "kobe-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
