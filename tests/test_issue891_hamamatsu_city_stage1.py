"""Issue #891 (Hamamatsu City part): Shizuoka cluster stage 1.

Covers the FY2022-FY2024 ordinary-account settlements of Hamamatsu
City, cross-checked field by field between the MIC settlement cards
(Shizuoka edition) and the city's fiscal situation collections
(MIC-hosted Excel for designated cities), with the city-published
settlement cards supplying the third decimal of the fiscal strength
index, plus the mayor's term registration and the FY2026 initial-budget
local-tax record. Every figure of the two systems agreed; the future
burden ratio is printed as "-" in both systems (the burden is below
the appropriable resources), so it is kept as not_published.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/hamamatsu-city"
MID = "jp-local-221309"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_hamamatsu_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    # The official local-government code is 221309: the MIC settlement
    # cards carry the Hamamatsu City sheet under that code and the city
    # is a designated city.
    assert municipality["id"] == MID
    assert municipality["official_code"] == "221309"
    assert municipality["name_ja"] == "浜松市"
    assert municipality["data_status"] == "reviewed"


def _settlement_records() -> list[dict]:
    return load_json(BASE / "settlement_records.json")


def _by_year_metric(records: list[dict]) -> dict[tuple[int, str], dict]:
    return {(r["fiscal_year"], r["metric"]): r for r in records}


def test_hamamatsu_settlement_headlines() -> None:
    records = _settlement_records()
    assert len(records) == 51
    by = _by_year_metric(records)

    # Thousand-yen values as printed on the MIC cards; stored in yen.
    expected = {
        # fiscal_year: (revenue, expenditure, local_tax, standard fiscal
        # scale, fund balance total, debt balance) in thousand yen
        2022: (396006285, 381204906, 150582086, 218550571, 51077877, 249257808),
        2023: (424171006, 410056352, 152373340, 223069265, 37149702, 244418676),
        2024: (416549107, 403626364, 151900602, 228440968, 36768755, 238158797),
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
        fiscal_year = record["fiscal_year"]
        assert record["municipality_id"] == MID
        assert record["account_type"] == "ordinary"
        assert record["stage"] == "settlement"
        assert record["review_status"] == "reviewed"
        if record["metric"] == "fiscal_strength_index":
            # The third decimal is printed only on the city-published
            # card, so that card is the second source for this metric.
            assert record["sources"] == [
                f"hamamatsu-city-mic-settlement-card-fy{fiscal_year}",
                f"hamamatsu-city-settlement-card-fy{fiscal_year}",
            ]
        else:
            assert record["sources"] == [
                f"hamamatsu-city-mic-settlement-card-fy{fiscal_year}",
                f"hamamatsu-city-fiscal-situation-collection-fy{fiscal_year}",
            ]


def test_hamamatsu_settlement_arithmetic() -> None:
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
        breakdown = nature["breakdown"]
        for parent_key in ("mandatory_expenses", "capital_expenses"):
            children = {
                item["key"]: item["amount_yen"]
                for item in breakdown
                if item["parent_key"] == parent_key
            }
            assert sum(children.values()) == next(
                item["amount_yen"]
                for item in breakdown
                if item["key"] == parent_key
            )

        fund = by[(fiscal_year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert sum(item["amount_yen"] for item in fund["breakdown"]) == fund["amount_yen"]

        debt = by[(fiscal_year, "debt_balance")]
        assert len(debt["breakdown"]) == 2
        assert sum(item["amount_yen"] for item in debt["breakdown"]) == debt["amount_yen"]


def test_hamamatsu_settlement_breakdowns_handle_dash_categories() -> None:
    by = _by_year_metric(_settlement_records())
    for fiscal_year in (2022, 2023, 2024):
        purpose = {
            item["label"]: item["amount_yen"]
            for item in by[(fiscal_year, "expenditure_by_purpose")]["breakdown"]
        }
        # Both miscellaneous expenditures and the prior-year advance
        # appropriation are printed as "-" on the card in every year:
        # kept as null, never zero-filled.
        assert purpose["諸支出金"] is None
        assert purpose["前年度繰上充用金"] is None
        nature_labels = {
            item["label"]
            for item in by[(fiscal_year, "expenditure_by_nature")]["breakdown"]
        }
        # Dash categories of the nature table are omitted entirely.
        assert "前年度繰上充用金" not in nature_labels
        assert "失業対策事業費" not in nature_labels


def test_hamamatsu_settlement_ratios_are_published_values() -> None:
    by = _by_year_metric(_settlement_records())
    # The labelled (main) current-balance ratio is registered, not the
    # parenthesised variant that excludes the special revenue-shortfall
    # bonds and temporary fiscal measures bonds (96.3 / 95.1 / 95.1).
    assert by[(2022, "current_balance_ratio")]["value"] == 90.1
    assert by[(2023, "current_balance_ratio")]["value"] == 91.2
    assert by[(2024, "current_balance_ratio")]["value"] == 93.3
    assert by[(2022, "real_debt_service_ratio")]["value"] == 4.4
    assert by[(2023, "real_debt_service_ratio")]["value"] == 3.8
    assert by[(2024, "real_debt_service_ratio")]["value"] == 3.3
    assert by[(2022, "real_balance_ratio")]["value"] == 4.3
    assert by[(2023, "real_balance_ratio")]["value"] == 3.4
    assert by[(2024, "real_balance_ratio")]["value"] == 3.3
    # The fiscal strength index is printed to three decimals on the
    # city-published card (0.829 / 0.813 / 0.808); the MIC card's index
    # table prints only two decimals.
    assert by[(2022, "fiscal_strength_index")]["value"] == 0.829
    assert by[(2023, "fiscal_strength_index")]["value"] == 0.813
    assert by[(2024, "fiscal_strength_index")]["value"] == 0.808
    # The future burden ratio is "-" in both systems in every year
    # (future burden below the appropriable resources): the value is
    # not published and is never zero-filled.
    for fiscal_year in (2022, 2023, 2024):
        record = by[(fiscal_year, "future_burden_ratio")]
        assert record["value"] is None
        assert record["value_status"] == "not_published"
    # Resident-register population as of 1 January of the survey year
    # (the city card's 31 March figures use a different reference date).
    assert by[(2022, "population")]["value"] == 792704
    assert by[(2023, "population")]["value"] == 788985
    assert by[(2024, "population")]["value"] == 783924


def test_hamamatsu_settlement_packets_cover_every_record() -> None:
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


def test_hamamatsu_catalog_shape() -> None:
    catalog = load_json("data/catalog/hamamatsu_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 9
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "hamamatsu-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_hamamatsu_fy2026_local_tax_record() -> None:
    fiscal = load_json(BASE / "fiscal_records.json")
    by_id = {record["id"]: record for record in fiscal}
    record = by_id["jp-local-221309-fiscal-2026-local-tax"]
    assert record["fiscal_year"] == 2026
    assert record["account_type"] == "general"
    assert record["stage"] == "initial_budget"
    assert record["amount_yen"] == 160600000000
    assert record["sources"] == [
        "hamamatsu-budget-2026-bill",
        "hamamatsu-budget-2026",
    ]
    # The previously registered general-account total is unchanged.
    total = by_id["jp-local-221309-fiscal-2026-total-revenue"]
    assert total["amount_yen"] == 440100000000


def test_hamamatsu_mayor_term() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == "jp-local-221309-executive-2023-05-01"
    assert term["office"] == "mayor"
    assert term["person_name"] == "中野 祐介"
    assert term["term_start"] == "2023-05-01"
    # The expiry is printed directly in the Shizuoka prefectural
    # election commission's term list (令和9年4月30日).
    assert term["term_end"] == "2027-04-30"
    assert term["election_date"] == "2023-04-09"
    assert term["status"] == "current"
    # The manifesto link is deferred to stage 3 (bulletin check).
    assert term["manifesto_source_ids"] == []

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    election_claims = [
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    # The term record has no vote-count field; the count lives in the
    # evidence packet (246,745 votes, read from the commission's
    # image-only results PDF).
    assert "246,745" in election_claims[0]["statement"]
