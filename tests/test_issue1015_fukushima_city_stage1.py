"""Issue #1015: Fukushima cluster stage 1 — Fukushima City mayor term
and FY2026 city tax.

The settlement records (FY2022–FY2024, 51 records) were already
registered under the nationwide fiscal-detail programme (Issue #691)
with a two-series cross-check, so stage 1 leaves them unchanged and
only re-verifies their arithmetic here. The FY2026 initial-budget
total was likewise already registered and matches the stage-0
inventory exactly, so stage 1 adds the missing FY2026 local-tax
record, verified against the revenue table of the city's official
budget overview (thousand-yen precision) and the council's enactment
of Bill No. 5 (原案可決, 2026-03-27).

The mayor's term starts on 2025-12-08, stated directly in the city's
official inauguration press release (the predecessor retired on
2025-12-07); the expiry (2029-12-07) follows the Article 259 proviso
chain anchored by that officially stated previous expiry, and the
cross-check against the Fukushima Prefectural Election Commission's
term-expiry list remains outstanding. The vote count is kept in the
executive evidence packet, as in the other clusters, not on the term
record itself. The 2025 election bulletin is extant on the Election
Commission's current official page, so the source search is
registered as source_registered at stage 1; transcription, promise
records and the manifesto connection are stage 3 work.

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
CITY = ROOT / "data/reviewed/fukushima-city"
CATALOG = ROOT / "data/catalog/fukushima_city_finance_sources.json"
MID = "jp-local-072010"
TERM_ID = "jp-local-072010-executive-2025-12-08"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance) -> list:
    schema = load(ROOT / "schemas" / schema_name)
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )


def test_fukushima_city_identity() -> None:
    municipality = load(CITY / "municipality.json")
    assert municipality["id"] == MID
    assert municipality["official_code"] == "072010"
    assert municipality["name_ja"] == "福島市"
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


def test_fukushima_catalog_shape() -> None:
    catalog = load(CATALOG)
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 10
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "fukushima-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
    validator_text = (ROOT / "scripts/validate_static_export.py").read_text(
        encoding="utf-8"
    )
    assert "fukushima_city_finance_sources.json" in validator_text


def test_fy2026_local_tax_added_and_total_unchanged() -> None:
    records = {r["id"]: r for r in load(CITY / "fiscal_records.json")}
    packets = load(CITY / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 15 and
    # matches the stage-0 inventory (Bill No. 5, 原案可決 on
    # 2026-03-27, 124,500,000 thousand yen), so it is unchanged.
    total = records[f"{MID}-fiscal-2026-total-expenditure"]
    assert total["amount_yen"] == 124_500_000_000
    assert total["stage"] == "initial_budget"

    # The FY2026 local tax was missing and is added. It is verified
    # against the revenue table of the city's official budget
    # overview (資料編「一般会計歳入の状況」, p.47, thousand yen),
    # whose printed total (124,500,000 thousand yen) also equals the
    # sum of its revenue items; Bill No. 5 was passed as proposed
    # (原案可決) on 2026-03-27, so the printed value is the enacted
    # value.
    local_tax = records[f"{MID}-fiscal-2026-local-tax"]
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 42_400_000_000
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["review_status"] == "reviewed"
    assert local_tax["sources"] == [
        "fukushima-budget-2026",
        "fukushima-budget-2026-enactment",
    ]
    assert "原案可決" in local_tax["note"]
    assert validate("fiscal_record.schema.json", local_tax) == []


def test_plan_review_unchanged_from_phase15() -> None:
    plan = load(CITY / "plan_review.json")
    assert {record["id"] for record in plan["records"]} == {
        "fukushima-current-plan-period",
        "fukushima-current-policy-structure",
        "fukushima-plan-period-extension",
        "fukushima-progress-indicator-structure",
        "fukushima-fy2024-settlement-linkage",
    }


def test_mayor_term_and_votes() -> None:
    terms = load(ROOT / "data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == TERM_ID
    assert term["office"] == "mayor"
    assert term["person_name"] == "馬場 雄基"
    # The start is stated directly in the city's inauguration press
    # release (took office on 2025-12-08, the day after the
    # predecessor's officially stated term expiry of 2025-12-07).
    assert term["term_start"] == "2025-12-08"
    assert term["term_end"] == "2029-12-07"
    assert term["election_date"] == "2025-11-16"
    # No manifesto connection at stage 1: the bulletin is located,
    # and transcription plus connection are stage 3 work.
    assert term["manifesto_source_ids"] == []
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load(ROOT / "data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (58,453 votes in the 2025 election per the
    # city election commission's official ballot-count summary, with
    # the candidate totals summing to 105,016 valid votes).
    assert "58,453票" in claims["election_date"]["statement"]
    assert "105,016" in claims["election_date"]["review_note"]
    assert claims["term_start"]["source_ids"] == [
        "fukushima-city-mayor-inauguration-2025",
        "fukushima-city-mayor-election-2025-schedule",
    ]
    # The new expiry's own printed cross-check against the
    # prefectural list is still outstanding.
    assert any("2029年12月7日" in q for q in packet["open_questions"])


def test_bulletin_search_registered_as_located() -> None:
    searches = load(ROOT / "data/entities/executives/manifesto_source_searches.json")
    search = next(s for s in searches if s["executive_term_id"] == TERM_ID)
    assert search["id"] == "manifesto-source-search-fukushima-city-2025"
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [
        "fukushima-city-mayor-election-2025-bulletin"
    ]
    assert search["nonexistence_claim"] is False
    assert validate("manifesto_source_search.schema.json", search) == []

    packets = load(
        ROOT / "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(p for p in packets if p["subject_id"] == search["id"])
    assert packet["review_status"] == "reviewed"
    assert validate("evidence_packet.schema.json", packet) == []


def test_fukushima_web_wiring() -> None:
    executives = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"jp-local-072010": "fukushima-city"' in executives
    catalog = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    assert "fukushima_city_finance_sources.json" in catalog
    assert '"fukushima-city"' in catalog
    quality = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    assert "fukushima-city/fiscal_records.json" in quality
    assert "fukushima-city/settlement_records.json" in quality
    assert '"fukushima-city": "福島市"' in quality
