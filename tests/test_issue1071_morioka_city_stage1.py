"""Issue #1071: Iwate cluster stage 1 — Morioka City mayor term,
FY2026 local tax and the election-bulletin source search.

The settlement records (FY2022–FY2024, 51 records) were already
registered under the nationwide fiscal-detail programme (Issue
#691) with a two-series cross-check, so stage 1 leaves them
unchanged and only re-verifies their arithmetic here. The FY2026
initial-budget total was likewise already registered and matches
Article 1 of the budget bill book exactly, so stage 1 adds the
missing FY2026 local-tax record, verified against Table 1 of the
bill book itself (Bill No. 3, passed with a majority at the 2026
first regular session).

The mayor's term end (2027-09-01) is stated directly in the Iwate
Prefectural Election Commission's official term-expiry list (as of
2026-11-18); the start (2023-09-02) follows the Article 259
proviso chain anchored by that stated expiry, and no official
document stating the start day itself was located — the evidence
packet records the chain and the open question. The vote count
(65,701 votes per the city election commission's official record;
the 65,704 figure on Wikipedia is wrong) is kept in the executive
evidence packet, as in the other clusters.

The 2023 election bulletin is not extant on the Election
Commission's current official page and no Wayback capture of the
official URL was found. A copy exists on a private election site,
but its provenance cannot be verified against an official capture,
so the search is registered as no_stable_primary_source_found and
no manifesto source is connected; the provenance question is
revisited at stage 3.

Review and promotion judgements for this registration were made by
Muse under the owner's delegation of 2026-11-15 (the owner
explicitly delegated review to Muse); they are not the owner's
personal review.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CITY = ROOT / "data/reviewed/morioka-city"
CATALOG = ROOT / "data/catalog/morioka_city_finance_sources.json"
MID = "jp-local-032018"
TERM_ID = "jp-local-032018-executive-2023-09-02"
SEARCH_ID = "manifesto-source-search-morioka-city-2023"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance) -> list:
    schema = load(ROOT / "schemas" / schema_name)
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )


def test_morioka_city_identity() -> None:
    municipality = load(CITY / "municipality.json")
    assert municipality["id"] == MID
    assert municipality["official_code"] == "032018"
    assert municipality["name_ja"] == "盛岡市"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"


def test_settlement_records_unchanged_and_arithmetic_holds() -> None:
    records = load(CITY / "settlement_records.json")
    assert len(records) == 51
    assert {r["fiscal_year"] for r in records} == {2022, 2023, 2024}
    assert all(r["municipality_id"] == MID for r in records)
    assert all(r["review_status"] == "reviewed" for r in records)
    assert all(r["account_type"] == "ordinary" for r in records)
    for record in records:
        assert validate("fiscal_record.schema.json", record) == []
    by = {(r["fiscal_year"], r["metric"]): r for r in records}
    for year in (2022, 2023, 2024):
        revenue = by[(year, "total_revenue")]["amount_yen"]
        expenditure = by[(year, "total_expenditure")]["amount_yen"]
        formal = by[(year, "formal_balance")]["amount_yen"]
        carryover = by[(year, "carryover_resources")]["amount_yen"]
        real = by[(year, "real_balance")]["amount_yen"]
        assert revenue - expenditure == formal
        assert formal - carryover == real
    packets = load(CITY / "settlement_evidence_packets.json")
    assert len(packets) == 51
    assert {p["subject_id"] for p in packets} == {r["id"] for r in records}


def test_morioka_catalog_shape() -> None:
    catalog = load(CATALOG)
    assert catalog["scope"] == "phase15-core-capital-review"
    # Stage 1 added the budget bill book as the eleventh record.
    assert len(catalog["records"]) == 11
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "morioka-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
    bill = next(r for r in catalog["records"] if r["id"] == "morioka-budget-2026-bill")
    assert bill["url"].endswith("R8tousyoyosan.pdf")


def test_fy2026_local_tax_added_and_total_unchanged() -> None:
    records = {r["id"]: r for r in load(CITY / "fiscal_records.json")}
    packets = load(CITY / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 15 and
    # matches Article 1 of the budget bill book (Bill No. 3), so it
    # is unchanged.
    total = records[f"{MID}-fiscal-2026-total-expenditure"]
    assert total["amount_yen"] == 126_510_000_000
    assert total["stage"] == "initial_budget"

    # The FY2026 local tax was missing and is added. It is verified
    # against Table 1 of the bill book itself: the seven revenue
    # items printed for city tax sum to the registered total, and
    # the table's revenue total equals the Article 1 total. Bill
    # No. 3 was passed with a majority (可決（多数）, council
    # newsletter No. 241, p.8), so the printed bill value is the
    # enacted value.
    local_tax = records[f"{MID}-fiscal-2026-local-tax"]
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 44_944_674_000
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["review_status"] == "reviewed"
    assert local_tax["sources"] == [
        "morioka-budget-2026-bill",
        "morioka-budget-2026-pdf",
        "morioka-budget-2026-enactment",
    ]
    assert "可決（多数）" in local_tax["note"]
    assert validate("fiscal_record.schema.json", local_tax) == []
    items = [
        21_492_730,  # 市民税
        18_220_729,  # 固定資産税
        772_935,  # 軽自動車税
        1_998_531,  # 市たばこ税
        57_204,  # 入湯税
        2_323_927,  # 都市計画税
        78_618,  # 宿泊税
    ]
    assert sum(items) * 1000 == local_tax["amount_yen"]


def test_plan_review_unchanged_from_phase15() -> None:
    plan = load(CITY / "plan_review.json")
    assert {record["id"] for record in plan["records"]} == {
        "morioka-current-plan-period",
        "morioka-current-policy-structure",
        "morioka-implementation-plan-current-version",
        "morioka-implementation-rolling-structure",
        "morioka-fy2024-settlement-linkage",
    }


def test_mayor_term_and_votes() -> None:
    terms = load(ROOT / "data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == TERM_ID
    assert term["office"] == "mayor"
    assert term["person_name"] == "内舘 茂"
    # The start follows the Article 259 proviso chain anchored by
    # the officially stated current expiry; no official document
    # stating the start day itself was located.
    assert term["term_start"] == "2023-09-02"
    # The expiry is stated directly in the Iwate Prefectural
    # Election Commission's official term-expiry list (as of
    # 2026-11-18).
    assert term["term_end"] == "2027-09-01"
    assert term["election_date"] == "2023-08-13"
    # The bulletin could not be verified as a primary source, so
    # nothing is connected at stage 1 (revisited at stage 3).
    assert term["manifesto_source_ids"] == []
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load(ROOT / "data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (65,701 votes in the 2023 election per the
    # city election commission's official record, with the candidate
    # totals summing to 113,723 valid votes; Wikipedia's 65,704 is
    # a known error and is not used).
    assert "65,701票" in claims["election_date"]["statement"]
    assert "113,723" in claims["election_date"]["review_note"]
    assert "65,704" in claims["election_date"]["review_note"]
    assert claims["term_end"]["source_ids"] == ["iwate-pref-mayor-term-expiry-list"]
    assert any("2023年9月2日" in q for q in packet["open_questions"])


def test_bulletin_search_registered_as_not_found() -> None:
    searches = load(ROOT / "data/entities/executives/manifesto_source_searches.json")
    search = next(s for s in searches if s["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    # The bulletin is not extant on the commission's current page,
    # no Wayback capture of the official URL exists, and the
    # private-site copy cannot be digest-verified, so the search
    # honestly records that no verifiable primary source was found
    # instead of claiming the copy as located.
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["nonexistence_claim"] is False
    assert "morioka-city-mayor-election-2023-bulletin-copy" in (
        search["checked_source_ids"]
    )
    assert validate("manifesto_source_search.schema.json", search) == []

    packets = load(
        ROOT / "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(p for p in packets if p["subject_id"] == SEARCH_ID)
    assert packet["review_status"] == "reviewed"
    assert packet["open_questions"]
    assert validate("evidence_packet.schema.json", packet) == []


def test_morioka_web_wiring() -> None:
    executives = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"jp-local-032018": "morioka-city"' in executives
