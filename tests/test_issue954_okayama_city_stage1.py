"""Issue #954: Okayama cluster stage 1 — Okayama City settlement and mayor term.

The settlement records cross-check two official series: the Ministry of
Internal Affairs and Communications' 財政状況資料集 for Okayama City and
the city's own settlement overview 『決算（案）の概要及び岡山市の財政状況』
(both ordinary account), with arithmetic checks on the published values.
The mayor's term end is stated in the Okayama Prefectural Election
Commission's term-expiry list; the start follows the Article 259 proviso
chain anchored by the city election commission's statement of the
previous term's expiry. The vote count is kept in the executive evidence
packet, as in the other clusters, not on the term record itself.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CITY = ROOT / "data/reviewed/okayama-city"
CATALOG = ROOT / "data/catalog/okayama_city_finance_sources.json"
MID = "jp-local-331007"


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
    assert by_key[(2022, "total_revenue")]["amount_yen"] == 391_046_068_000
    assert by_key[(2023, "total_revenue")]["amount_yen"] == 392_169_186_000
    assert by_key[(2024, "total_revenue")]["amount_yen"] == 407_872_192_000
    assert by_key[(2024, "local_tax")]["amount_yen"] == 134_225_241_000
    assert by_key[(2024, "debt_balance")]["amount_yen"] == 338_939_637_000


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
                item["amount_yen"] or 0
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


def test_unpublished_values_are_null_not_zero():
    by_key = by_year_metric()
    # The future burden ratio is printed as '－' (no value) in both
    # official series for all three years, because the future burden
    # amount is below the available funding; it is recorded as
    # not_published, never as zero.
    for year in (2022, 2023, 2024):
        record = by_key[(year, "future_burden_ratio")]
        assert record["value"] is None
        assert record["amount_yen"] is None
        assert record["value_status"] == "not_published"
    # Disaster-recovery items are '－' in FY2022 and FY2023 and carry a
    # published value (1,485 thousand yen) only in FY2024.
    for year in (2022, 2023):
        purpose = by_key[(year, "expenditure_by_purpose")]
        item = next(
            i for i in purpose["breakdown"] if i["key"] == "disaster_recovery"
        )
        assert item["amount_yen"] is None
        nature = by_key[(year, "expenditure_by_nature")]
        works = next(
            i for i in nature["breakdown"] if i["key"] == "disaster_recovery_works"
        )
        assert works["amount_yen"] is None
    purpose2024 = by_key[(2024, "expenditure_by_purpose")]
    item2024 = next(
        i for i in purpose2024["breakdown"] if i["key"] == "disaster_recovery"
    )
    assert item2024["amount_yen"] == 1_485_000


def test_fiscal_strength_index_uses_city_three_decimal_values():
    by_key = by_year_metric()
    # The city's overview prints the index to three decimals; the MIC
    # collection's summary table prints two decimals and agrees after
    # rounding. The published values are registered, not recomputed.
    assert by_key[(2022, "fiscal_strength_index")]["value"] == 0.757
    assert by_key[(2023, "fiscal_strength_index")]["value"] == 0.742
    assert by_key[(2024, "fiscal_strength_index")]["value"] == 0.738


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


def test_okayama_city_finance_catalog_is_registered():
    catalog = load(CATALOG)
    # Per-cluster finance catalogs are not governed by
    # schemas/source_catalog.schema.json (validate_repository.py
    # applies that schema only to the pilot catalogs); like the
    # Kyoto and Hiroshima catalogs, this one is checked by shape.
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 8
    assert all(r["municipality_key"] == "okayama-city" for r in catalog["records"])
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"


def test_fy2026_records_match_supplementary_budget_pre_amounts():
    fiscal = load(CITY / "fiscal_records.json")
    # The exact thousand-yen initial-budget figures are the
    # '補正前の額' of the June 2026 supplementary budget (Bill No. 99,
    # enacted 2026-06-23), whose first table restates the enacted
    # initial budget. The total supersedes the Phase 13 value derived
    # from the council newsletter's ten-thousand-yen precision figure.
    total = next(r for r in fiscal if r["id"] == f"{MID}-fiscal-2026-total-revenue")
    assert total["metric"] == "total_revenue"
    assert total["amount_yen"] == 429_863_382_000
    assert total["stage"] == "initial_budget"
    assert total["review_status"] == "reviewed"
    record = next(r for r in fiscal if r["id"] == f"{MID}-fiscal-2026-local-tax")
    assert record["metric"] == "local_tax"
    assert record["amount_yen"] == 143_589_274_000
    assert record["stage"] == "initial_budget"
    assert record["review_status"] == "reviewed"


def test_mayor_term_is_registered_with_official_endpoints():
    terms = load(ROOT / "data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == f"{MID}-executive-2025-10-09"
    assert term["office"] == "mayor"
    assert term["person_name"] == "大森 雅夫"
    assert term["term_start"] == "2025-10-09"
    assert term["term_end"] == "2029-10-08"
    assert term["election_date"] == "2025-10-05"
    # Stage 1 leaves the manifesto unconnected: stage 0 (Issue #949)
    # confirmed the 2025 election bulletin was published, but whether
    # the bulletin PDF is still reachable on the city's current site
    # is unverified, so stage 3 confirms its survival and connects it.
    assert term["manifesto_source_ids"] == []

    packets = load(ROOT / "data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (89,183 votes in the 2025 election, with
    # the four candidates' totals summing to 206,374 valid votes).
    assert "89,183票" in claims["election_date"]["statement"]
    assert "206,374" in claims["election_date"]["review_note"]
    assert claims["term_end"]["source_ids"] == ["okayama-pref-mayor-term-list"]
    assert claims["term_start"]["source_ids"] == [
        "okayama-city-mayor-election-2025-schedule"
    ]
