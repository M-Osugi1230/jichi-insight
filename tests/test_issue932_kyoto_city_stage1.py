"""Issue #932: Kyoto cluster stage 1 — Kyoto City settlement and mayor term.

The settlement records cross-check two official series: the settlement
cards published by Kyoto City and the city's own 財政状況資料集 (both
ordinary account), with arithmetic checks on the published values.
The mayor's term endpoints are stated day-exact by official sources
(the city's list of past mayors and the Kyoto Prefectural Election
Commission's term-expiry list); the vote count is kept in the
executive evidence packet, as in the other clusters, not on the term
record itself.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CITY = ROOT / "data/reviewed/kyoto-city"
CATALOG = ROOT / "data/catalog/kyoto_city_finance_sources.json"
MID = "jp-local-261009"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance) -> list:
    schema = load(ROOT / "schemas" / schema_name)
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )


def settlement():
    return load(CITY / "settlement_records.json")


def by_year_metric():
    return {(r["fiscal_year"], r["metric"]): r for r in settlement()}


def test_settlement_records_cover_three_years_with_51_records():
    records = settlement()
    assert len(records) == 51
    assert {r["fiscal_year"] for r in records} == {2022, 2023, 2024}
    assert all(r["municipality_id"] == MID for r in records)
    assert all(r["review_status"] == "reviewed" for r in records)
    assert all(r["account_type"] == "ordinary" for r in records)
    for record in records:
        assert validate("fiscal_record.schema.json", record) == []
    by_key = by_year_metric()
    assert by_key[(2022, "total_revenue")]["amount_yen"] == 963_093_117_000
    assert by_key[(2023, "total_revenue")]["amount_yen"] == 966_938_909_000
    assert by_key[(2024, "total_revenue")]["amount_yen"] == 980_215_852_000
    assert by_key[(2024, "local_tax")]["amount_yen"] == 324_261_648_000
    assert by_key[(2024, "debt_balance")]["amount_yen"] == 1_272_193_711_000


def test_settlement_arithmetic_holds_on_published_values():
    by = by_year_metric()
    for year in (2022, 2023, 2024):
        revenue = by[(year, "total_revenue")]["amount_yen"]
        expenditure = by[(year, "total_expenditure")]["amount_yen"]
        formal = by[(year, "formal_balance")]["amount_yen"]
        carryover = by[(year, "carryover_resources")]["amount_yen"]
        real = by[(year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real

        purpose = by[(year, "expenditure_by_purpose")]
        assert (
            sum(item["amount_yen"] or 0 for item in purpose["breakdown"])
            == expenditure
        )
        nature = by[(year, "expenditure_by_nature")]
        top_level = [
            item for item in nature["breakdown"] if item["parent_key"] is None
        ]
        assert sum(item["amount_yen"] for item in top_level) == expenditure
        breakdown = {item["key"]: item["amount_yen"] for item in nature["breakdown"]}
        for parent in ("mandatory_expenses", "capital_expenses"):
            children = [
                item["amount_yen"]
                for item in nature["breakdown"]
                if item["parent_key"] == parent
            ]
            assert sum(children) == breakdown[parent]

        fund = by[(year, "fund_balance")]
        assert len(fund["breakdown"]) == 3
        assert (
            sum(item["amount_yen"] or 0 for item in fund["breakdown"])
            == fund["amount_yen"]
        )

        debt = by[(year, "debt_balance")]
        assert (
            sum(item["amount_yen"] or 0 for item in debt["breakdown"])
            == debt["amount_yen"]
        )


def test_unpublished_breakdown_values_are_null_not_zero():
    by_key = by_year_metric()
    # The 財政状況資料集 prints '－' (no balance) for the debt-reduction
    # fund in FY2022 and FY2023, so that breakdown item is null; the
    # published total still equals the sum of the published items.
    for year in (2022, 2023):
        fund = by_key[(year, "fund_balance")]
        item = next(i for i in fund["breakdown"] if i["key"] == "debt_reduction_fund")
        assert item["amount_yen"] is None
    fund2024 = by_key[(2024, "fund_balance")]
    item2024 = next(
        i for i in fund2024["breakdown"] if i["key"] == "debt_reduction_fund"
    )
    assert item2024["amount_yen"] == 2_716_625_000


def test_settlement_evidence_packets_match_records():
    records = settlement()
    packets = load(CITY / "settlement_evidence_packets.json")
    assert len(packets) == 51
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}
    catalog_ids = {r["id"] for r in load(CATALOG)["records"]}
    by_id = {r["id"]: r for r in records}
    for packet in packets:
        assert validate("evidence_packet.schema.json", packet) == []
        assert len(packet["claims"]) == 1
        claim = packet["claims"][0]
        assert claim["decision"] == "accepted"
        assert claim["source_ids"] == by_id[packet["subject_id"]]["sources"]
        assert set(claim["source_ids"]) <= catalog_ids


def test_kyoto_city_finance_catalog_is_registered():
    catalog = load(CATALOG)
    # Per-cluster finance catalogs are not governed by
    # schemas/source_catalog.schema.json (validate_repository.py
    # applies that schema only to the pilot catalogs); like the
    # Shizuoka and Hiroshima catalogs, this one is checked by shape.
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 8
    assert all(r["municipality_key"] == "kyoto-city" for r in catalog["records"])
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_fy2026_local_tax_record_matches_budget_explanation():
    fiscal = load(CITY / "fiscal_records.json")
    record = next(r for r in fiscal if r["id"] == f"{MID}-fiscal-2026-local-tax")
    assert record["metric"] == "local_tax"
    assert record["amount_yen"] == 356_307_000_000
    assert record["stage"] == "initial_budget"
    assert record["review_status"] == "reviewed"
    total = next(r for r in fiscal if r["id"] == f"{MID}-fiscal-2026-total-revenue")
    assert total["amount_yen"] == 1_007_967_000_000


def test_mayor_term_is_registered_with_official_endpoints():
    terms = load(ROOT / "data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == f"{MID}-executive-2024-02-25"
    assert term["office"] == "mayor"
    assert term["person_name"] == "松井 孝治"
    assert term["term_start"] == "2024-02-25"
    assert term["term_end"] == "2028-02-24"
    assert term["election_date"] == "2024-02-04"
    # Stage 1 leaves the manifesto unconnected; stage 3 transcribes
    # the 2024 election bulletin, which stage 0 confirmed still
    # exists on the Election Commission's current official page.
    assert term["manifesto_source_ids"] == []

    packets = load(ROOT / "data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (177,454 votes in the 2024 election, with
    # the candidate totals summing to 468,016 valid votes).
    assert "177,454票" in claims["election_date"]["statement"]
    assert "468,016" in claims["election_date"]["review_note"]
    assert claims["term_end"]["source_ids"] == ["kyoto-pref-mayor-term-list"]
