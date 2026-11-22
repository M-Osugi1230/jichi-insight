"""Issue #915 (Hiroshima City part): Hiroshima cluster stage 1.

Covers the FY2022-FY2024 ordinary-account settlements of Hiroshima
City, cross-checked field by field between the settlement cards the
city itself publishes on its official site and the city's fiscal
situation collections (Excel), with arithmetic checks. The cards
supply the third decimal of the fiscal strength index; the
population is registered as of 1 January from the collection's
summary table (its note 7), while the cards print the 31 March
figure. Also covers the stage-1 mayoral term registration and the
addition of the FY2026 initial budget's local tax (the total was
already registered at Phase 13 and matches the enacted budget).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/hiroshima-city"
MID = "jp-local-341002"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_hiroshima_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 341002: the settlement
    # cards carry Hiroshima City under that municipality number
    # (市町村番号 341002) and the city is a designated city.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "341002"
    assert municipality["name_ja"] == "広島市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def _expected_sources(fiscal_year: int) -> list[str]:
    return [
        f"hiroshima-city-settlement-card-fy{fiscal_year}",
        f"hiroshima-city-fiscal-situation-collection-fy{fiscal_year}",
    ]


def test_hiroshima_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard
        # fiscal scale, fund balance total, debt balance) in
        # thousand yen
        2022: (710147785, 705188318, 242137534, 342971969, 19741073, 1116204480),
        2023: (711658564, 707638369, 246715613, 348912170, 12675696, 1110569164),
        2024: (724426839, 720666916, 249905332, 358258463, 12598254, 1098519970),
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
        assert record["sources"] == _expected_sources(record["fiscal_year"])


def test_hiroshima_settlement_arithmetic() -> None:
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
        # The capital total also covers the "うち単独" sub-item's
        # parent (construction) exactly once: construction and
        # disaster recovery works sum to the capital total.
        assert sum(capital_children.values()) == breakdown["capital_expenses"]

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert (
            sum(item["amount_yen"] or 0 for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(fiscal_year, "debt_balance")]
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_hiroshima_settlement_breakdowns_handle_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Miscellaneous expenditures and the prior-year advance
        # appropriation are printed as "-" in both systems in every
        # year: kept as null, never zero-filled.
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
        fund = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "fund_balance")]["breakdown"]
        }
        # The debt-reduction fund has no balance in any year ("-" in
        # the collection's summary table): kept as null.
        assert fund["減債基金"] is None
        assert fund["財政調整基金"] is not None


def test_hiroshima_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not
    # the parenthesised variant that excludes the special deficit
    # bonds and temporary fiscal measures bonds.
    assert by[(2022, "current_balance_ratio")]["value"] == 98.2
    assert by[(2023, "current_balance_ratio")]["value"] == 98.7
    assert by[(2024, "current_balance_ratio")]["value"] == 97.3
    assert by[(2022, "real_debt_service_ratio")]["value"] == 9.8
    assert by[(2023, "real_debt_service_ratio")]["value"] == 9.6
    assert by[(2024, "real_debt_service_ratio")]["value"] == 8.8
    assert by[(2022, "future_burden_ratio")]["value"] == 164.8
    assert by[(2023, "future_burden_ratio")]["value"] == 165.4
    assert by[(2024, "future_burden_ratio")]["value"] == 161.3
    # The fiscal strength index keeps the third decimal printed on
    # the city's cards (the collections' summary tables print two
    # decimals: 0.80 / 0.78 / 0.77); it is not recomputed.
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.796
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.779
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.771
    assert by[(2022, "real_balance_ratio")]["value"] == 0.9
    assert by[(2023, "real_balance_ratio")]["value"] == 0.8
    assert by[(2024, "real_balance_ratio")]["value"] == 0.6
    # Resident-register population as of 1 January following the
    # fiscal year, per note 7 of the collections' summary tables
    # (the cards print the 31 March figure instead: 1,181,868 /
    # 1,175,327 / 1,170,275 — a different reference date, recorded
    # in the record notes rather than mixed in).
    assert by[(2022, "population")]["value"] == 1184731
    assert by[(2023, "population")]["value"] == 1178773
    assert by[(2024, "population")]["value"] == 1173543


def test_hiroshima_settlement_packets_cover_every_record() -> None:
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


def test_hiroshima_catalog_shape() -> None:
    catalog = load_json("data/catalog/hiroshima_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 8
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "hiroshima-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_hiroshima_fy2026_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 13 and
    # matches the enacted budget bill (Article 1) exactly, so it is
    # unchanged at stage 1.
    total = records["jp-local-341002-fiscal-2026-total-revenue"]
    assert total["amount_yen"] == 794_011_359_000

    # The FY2026 local tax was missing and is added. It is verified
    # against Table 1 of Bill No. 1 itself (the FY2026 general
    # account budget), which the council passed unamended
    # (原案可決) on 2026-03-26, so the printed bill value is the
    # enacted value.
    local_tax = records["jp-local-341002-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 271_949_021_000
    assert local_tax["sources"] == [
        "hiroshima-city-budget-bill-fy2026",
        "hiroshima-city-budget-council-results-fy2026",
    ]
    assert "原案可決" in local_tax["note"]


def test_hiroshima_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-341002-executive-2023-04-12"
    assert term["person_name"] == "松井 一實"
    # The start is the inauguration date printed in the city's
    # official list of past mayors (39th mayor, took office
    # 2023-04-12).
    assert term["term_start"] == "2023-04-12"
    # The expiry is stated directly in the Hiroshima Prefectural
    # Election Commission's official list of mayoral terms.
    assert term["term_end"] == "2027-04-11"
    assert term["election_date"] == "2023-04-09"
    # Stage 1 left the manifesto unconnected (the 2023 election
    # bulletin is not on the city's current site); stage 3
    # (Issue #921) located the Wayback Machine capture of the
    # city's official election-period URL and connected it.
    assert term["manifesto_source_ids"] == [
        "hiroshima-city-mayor-election-2023-bulletin"
    ]

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (258,336 votes in the 2023 election per
    # the city election commission's official record; the 295,038
    # figure circulating in secondary sources is wrong).
    assert "258,336票" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "hiroshima-pref-mayor-term-list"
    ]
    assert packet["open_questions"]
