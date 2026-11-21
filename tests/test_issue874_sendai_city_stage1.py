"""Issue #874 (Sendai City part): Miyagi cluster stage 1 — Sendai settlements.

Covers the FY2022-FY2024 ordinary-account settlements of Sendai City,
cross-checked field by field between the MIC settlement cards (Miyagi
edition) and Miyagi Prefecture's settlement overview (the prefecture
publishes no fiscal situation collection for designated cities), with
arithmetic checks. The city-published settlement cards (final edition)
supply the third decimal of the fiscal strength index and document the
different reference date of the population figure. Also covers the
stage-1 mayoral term registration and the correction of the FY2026
initial-budget total to the enacted bill's exact figure.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/sendai-city"
MID = "jp-local-041009"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 041009: the MIC settlement
    # cards carry the Sendai City sheet under that code and the city is
    # a designated city.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "041009"
    assert municipality["name_ja"] == "仙台市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def _expected_sources(fiscal_year: int, metric: str) -> list[str]:
    mic = f"sendai-city-mic-settlement-card-fy{fiscal_year}"
    if metric in {"fiscal_strength_index", "population"}:
        # The fiscal strength index is registered at the third decimal
        # printed on the city's own final-edition card (the MIC card
        # prints two decimals), and the population note records the
        # reference-date difference against the same city card.
        return [mic, f"sendai-city-settlement-card-fy{fiscal_year}"]
    return [mic, f"sendai-city-miyagi-settlement-overview-fy{fiscal_year}"]


def test_sendai_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard fiscal
        # scale, fund balance total, debt balance) in thousand yen
        2022: (590227702, 582541084, 224908035, 287874499, 131467205, 762635866),
        2023: (592650350, 583937600, 229301308, 293468229, 126807094, 759896848),
        2024: (624902682, 616736747, 233179032, 299118178, 117619814, 757422978),
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
    for record in records:
        assert record["municipality_id"] == MID
        assert record["account_type"] == "ordinary"
        assert record["stage"] == "settlement"
        assert record["review_status"] == "reviewed"
        assert record["sources"] == _expected_sources(
            record["fiscal_year"], record["metric"]
        )


def test_sendai_settlement_arithmetic() -> None:
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
            sum(item["amount_yen"] or 0 for item in purpose["breakdown"])
            == expenditure
        )
        nature = by[(fiscal_year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure
        breakdown = {item["key"]: item["amount_yen"] for item in nature["breakdown"]}
        children = {
            item["key"]: item["amount_yen"]
            for item in nature["breakdown"]
            if item["parent_key"] == "mandatory_expenses"
        }
        assert sum(children.values()) == breakdown["mandatory_expenses"]
        capital_children = {
            item["key"]: item["amount_yen"]
            for item in nature["breakdown"]
            if item["parent_key"] == "capital_expenses"
        }
        assert sum(capital_children.values()) == breakdown["capital_expenses"]

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert sum(item["amount_yen"] for item in fund["breakdown"]) == fund["amount_yen"]

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_sendai_settlement_breakdowns_handle_dash_categories() -> None:
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


def test_sendai_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the temporary fiscal measures
    # bonds and similar items.
    assert by[(2022, "current_balance_ratio")]["value"] == 98.7
    assert by[(2023, "current_balance_ratio")]["value"] == 97.0
    assert by[(2024, "current_balance_ratio")]["value"] == 98.8
    assert by[(2022, "real_debt_service_ratio")]["value"] == 6.5
    assert by[(2023, "real_debt_service_ratio")]["value"] == 6.1
    assert by[(2024, "real_debt_service_ratio")]["value"] == 4.9
    assert by[(2022, "future_burden_ratio")]["value"] == 57.5
    assert by[(2023, "future_burden_ratio")]["value"] == 52.3
    assert by[(2024, "future_burden_ratio")]["value"] == 44.6
    # The fiscal strength index keeps the third decimal printed on the
    # city's final-edition card (the MIC card prints 0.89 / 0.88 /
    # 0.87); it is not recomputed.
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.891
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.877
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.873
    assert by[(2022, "real_balance_ratio")]["value"] == 1.2
    assert by[(2023, "real_balance_ratio")]["value"] == 1.4
    assert by[(2024, "real_balance_ratio")]["value"] == 1.0
    # Resident-register population as of 1 January of the survey year
    # (the city card prints the 31 March figure instead: 1,063,008 /
    # 1,061,717 / 1,060,008 — a different reference date, recorded in
    # the record notes rather than mixed in).
    assert by[(2022, "population")]["value"] == 1067486
    assert by[(2023, "population")]["value"] == 1066362
    assert by[(2024, "population")]["value"] == 1064142


def test_sendai_settlement_packets_cover_every_record() -> None:
    records = _settlement_records()
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }
    by_id = {record["id"]: record for record in records}
    for packet in packets:
        assert packet["review_status"] == "reviewed"
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert claim["source_ids"] == by_id[packet["subject_id"]]["sources"]


def test_sendai_catalog_shape() -> None:
    catalog = load_json("data/catalog/sendai_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 9
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "sendai-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_sendai_fy2026_budget_correction_and_local_tax() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The Phase 13 registration carried the announcement's rounded
    # figure (7,306億円). The budget bill itself (第14号議案,
    # Article 1) states 730,647,000 thousand yen; stage 1 corrected
    # the record to the bill's exact value and recorded the change in
    # the evidence packet.
    total = records["jp-local-041009-fiscal-2026-total-revenue"]
    assert total["amount_yen"] == 730_647_000_000
    assert "sendai-city-budget-2026-bill" in total["sources"]
    assert "原案通り可決" in total["note"]
    total_packet = next(
        p for p in packets if p["subject_id"] == total["id"]
    )
    assert "730,647,000千円に是正した" in total_packet["claims"][0]["review_note"]

    # The FY2026 local tax from the bill's revenue table (its itemised
    # breakdown sums to the same total) was missing and is added.
    local_tax = records["jp-local-041009-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 254_846_000_000
    assert "原案通り可決" in local_tax["note"]


def test_sendai_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-041009-executive-2025-08-22"
    assert term["person_name"] == "郡 和子"
    assert term["term_start"] == "2025-08-22"
    # The expiry is stated directly in the Miyagi prefectural election
    # commission's term-expiry list (verified against the PDF itself),
    # so no open cross-check remains for Sendai.
    assert term["term_end"] == "2029-08-21"
    assert term["election_date"] == "2025-08-03"
    assert term["manifesto_source_ids"] == []

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (204,844 votes in the 2025 election).
    assert "204,844票" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "sendai-city-mayor-term-expiry-list"
    ]
    # The only open question is the stage-3 bulletin connection; the
    # term-expiry cross-check that remains open for other
    # municipalities is complete for Sendai.
    assert len(packet["open_questions"]) == 1
    assert "選挙公報" in packet["open_questions"][0]
