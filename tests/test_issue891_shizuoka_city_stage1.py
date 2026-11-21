"""Issue #891 (Shizuoka City part): Shizuoka cluster stage 1.

Covers the FY2022-FY2024 ordinary-account settlements of Shizuoka
City, cross-checked field by field between the MIC settlement cards
(Shizuoka edition), the MIC-hosted fiscal situation collections for
designated cities, and the city's own published settlement cards,
with arithmetic checks. The city-published cards supply the third
decimal of the fiscal strength index and document the different
reference date of the population figure. Also covers the stage-1
mayoral term registration and the addition of the FY2026 initial
budget's local tax (the total was already registered at Phase 13 and
matches the enacted budget).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/shizuoka-city"
MID = "jp-local-221007"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_shizuoka_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 221007: the MIC settlement
    # cards carry the Shizuoka City sheet under that code and the city
    # is a designated city.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "221007"
    assert municipality["name_ja"] == "静岡市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def _expected_sources(fiscal_year: int, metric: str) -> list[str]:
    mic = f"shizuoka-city-mic-settlement-card-fy{fiscal_year}"
    if metric in {"fiscal_strength_index", "population"}:
        # The fiscal strength index is registered at the third decimal
        # printed on the city's own card (the MIC card and the fiscal
        # situation collection print two decimals), and the population
        # note records the reference-date difference against the same
        # city card.
        return [mic, f"shizuoka-city-settlement-card-fy{fiscal_year}"]
    return [mic, f"shizuoka-city-fiscal-situation-collection-fy{fiscal_year}"]


def test_shizuoka_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard fiscal
        # scale, fund balance total, debt balance) in thousand yen
        2022: (360822341, 349544762, 139820869, 193465064, 38562056, 442951378),
        2023: (364751312, 352593594, 141996245, 197591090, 42975683, 441791590),
        2024: (386462288, 375251244, 141926166, 203028710, 40945422, 437956472),
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


def test_shizuoka_settlement_arithmetic() -> None:
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


def test_shizuoka_settlement_breakdowns_handle_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Miscellaneous expenditures and the prior-year advance
        # appropriation are printed as "-" on the card in every year:
        # kept as null, never zero-filled.
        assert purpose["諸支出金"] is None
        assert purpose["前年度繰上充用金"] is None
        assert purpose["民生費"] is not None
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        # Dash categories of the nature table are omitted entirely.
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels


def test_shizuoka_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not a
    # parenthesised variant.
    assert by[(2022, "current_balance_ratio")]["value"] == 93.1
    assert by[(2023, "current_balance_ratio")]["value"] == 92.8
    assert by[(2024, "current_balance_ratio")]["value"] == 95.3
    assert by[(2022, "real_debt_service_ratio")]["value"] == 6.3
    assert by[(2023, "real_debt_service_ratio")]["value"] == 6.1
    assert by[(2024, "real_debt_service_ratio")]["value"] == 5.9
    assert by[(2022, "future_burden_ratio")]["value"] == 34.3
    assert by[(2023, "future_burden_ratio")]["value"] == 31.9
    assert by[(2024, "future_burden_ratio")]["value"] == 30.9
    # The fiscal strength index keeps the third decimal printed on the
    # city's card (the MIC card and the collection print 0.85 / 0.83 /
    # 0.82); it is not recomputed.
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.849
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.827
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.817
    assert by[(2022, "real_balance_ratio")]["value"] == 3.5
    assert by[(2023, "real_balance_ratio")]["value"] == 3.4
    assert by[(2024, "real_balance_ratio")]["value"] == 3.4
    # Resident-register population as of 1 January following the
    # fiscal year (the city card prints the 31 March figure instead:
    # 669,617 / 662,686 / 655,542 — a different reference date,
    # recorded in the record notes rather than mixed in).
    assert by[(2022, "population")]["value"] == 683739
    assert by[(2023, "population")]["value"] == 677736
    assert by[(2024, "population")]["value"] == 672775


def test_shizuoka_settlement_packets_cover_every_record() -> None:
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


def test_shizuoka_catalog_shape() -> None:
    catalog = load_json("data/catalog/shizuoka_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 9
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "shizuoka-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_shizuoka_fy2026_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 13 and
    # matches the enacted budget's summary table exactly, so it is
    # unchanged at stage 1.
    total = records["jp-local-221007-fiscal-2026-total-revenue"]
    assert total["amount_yen"] == 403_500_000_000

    # The FY2026 local tax from the budget overview's summary table
    # was missing and is added. Bill No. 46 (the FY2026 general
    # account budget) had its amendment rejected and the original
    # bill passed by majority on 2026-03-19.
    local_tax = records["jp-local-221007-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 148_938_000_000
    assert local_tax["sources"] == [
        "shizuoka-budget-2026-overview-pdf",
        "shizuoka-budget-2026-enactment-results",
    ]
    assert "可決" in local_tax["note"]


def test_shizuoka_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-221007-executive-2023-04-13"
    assert term["person_name"] == "難波 喬司"
    assert term["term_start"] == "2023-04-13"
    # The expiry is stated directly in the Shizuoka Prefectural
    # Election Commission's official list of mayoral terms.
    assert term["term_end"] == "2027-04-12"
    assert term["election_date"] == "2023-04-09"
    # Stage 1 leaves the manifesto unconnected; the bulletin is
    # connected at stage 3.
    assert term["manifesto_source_ids"] == []

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (149,117 votes in the 2023 election, with
    # the ward breakdown summing to the same total).
    assert "149,117票" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "shizuoka-pref-mayor-term-list"
    ]
    # The one open question at stage 1 is the current location of the
    # 2023 election bulletin PDF, to be confirmed at stage 3.
    assert len(packet["open_questions"]) == 1
    assert "選挙公報" in packet["open_questions"][0]
