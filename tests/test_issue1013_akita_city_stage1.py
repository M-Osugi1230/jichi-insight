"""Issue #1013: Akita cluster stage 1 (Akita City).

Akita City's FY2022-FY2024 ordinary-account settlements were
already registered under the fiscal-detail expansion programme
(Issue #691), so stage 1 covers only the FY2026 initial budget's
local tax (the total was already registered at Phase 15 and matches
Article 1 of the enacted budget book), the registration of Mayor
Numaya Jun's current term, and the manifesto source search (the
2025 election bulletin is extant on the city election commission's
current official page; promise extraction is stage 3).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/reviewed/akita-city"
MID = "jp-local-052019"
TERM_ID = "jp-local-052019-executive-2025-04-12"
SEARCH_ID = "manifesto-source-search-akita-city-2025"


def load_json(relative_path: str | Path):
    path = ROOT / relative_path if isinstance(relative_path, str) else relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def test_akita_city_identity() -> None:
    municipality = load_json(BASE / "municipality.json")

    assert municipality["id"] == MID
    assert municipality["official_code"] == "052019"
    assert municipality["name_ja"] == "秋田市"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"


def test_akita_settlements_were_already_registered() -> None:
    # Stage 1 does not touch the Issue #691 settlements.
    records = load_json(BASE / "settlement_records.json")
    assert len(records) == 51
    assert {record["fiscal_year"] for record in records} == {2022, 2023, 2024}
    packets = load_json(BASE / "settlement_evidence_packets.json")
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in records
    }


def test_akita_fy2026_local_tax_added() -> None:
    records = {r["id"]: r for r in load_json(BASE / "fiscal_records.json")}
    packets = load_json(BASE / "evidence_packets.json")
    assert {p["subject_id"] for p in packets} == set(records)

    # The FY2026 initial-budget total was registered at Phase 15 and
    # matches Article 1 of the budget book exactly, so it is
    # unchanged at stage 1.
    total = records["jp-local-052019-fiscal-2026-total-expenditure"]
    assert total["amount_yen"] == 144_180_000_000

    # The FY2026 local tax was missing and is added. It is verified
    # against Table 1 of the FY2026 budget book itself (Bill No. 2),
    # which the council passed (可決) on 2026-03-17, so the printed
    # bill value is the enacted value. The seven tax items printed
    # in Table 1 sum to the registered total.
    local_tax = records["jp-local-052019-fiscal-2026-local-tax"]
    assert local_tax["stage"] == "initial_budget"
    assert local_tax["metric"] == "local_tax"
    assert local_tax["amount_yen"] == 45_990_931_000
    assert local_tax["sources"] == [
        "akita-city-budget-fy2026",
        "akita-budget-2026-enactment",
    ]
    assert "可決" in local_tax["note"]
    items = [
        21_188_016,  # 市民税
        20_514_891,  # 固定資産税
        930_202,  # 軽自動車税
        2_150_347,  # 市たばこ税
        5_383,  # 鉱産税
        43_908,  # 入湯税
        1_158_184,  # 事業所税
    ]
    assert sum(items) * 1000 == local_tax["amount_yen"]


def test_akita_catalog_shape() -> None:
    catalog = load_json("data/catalog/akita_city_finance_sources.json")
    assert catalog["scope"] == "phase15-core-capital-review"
    assert len(catalog["records"]) == 11
    assert {record["municipality_key"] for record in catalog["records"]} == {
        "akita-city"
    }
    for record in catalog["records"]:
        assert record["url"].startswith("https://")
        assert record["review_status"] == "reviewed"
    validator_text = (ROOT / "scripts/validate_static_export.py").read_text(
        encoding="utf-8"
    )
    assert "akita_city_finance_sources.json" in validator_text


def test_akita_mayor_term_and_votes() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(t for t in terms if t["municipality_id"] == MID)
    assert term["id"] == TERM_ID
    assert term["person_name"] == "沼谷 純"
    # The start follows the Article 259 proviso chain: the 2025
    # election was a term-expiry election held before the previous
    # term expired (2025-04-11, stated in the prefectural election
    # commission's press release).
    assert term["term_start"] == "2025-04-12"
    # The expiry is stated directly in the Akita Prefectural
    # Election Commission's official term-expiry list (as of
    # 2026-06-30).
    assert term["term_end"] == "2029-04-11"
    assert term["election_date"] == "2025-04-06"
    # No manifesto connection at stage 1: the bulletin is located,
    # but promise extraction from it is stage 3.
    assert term["manifesto_source_ids"] == []
    assert len([t for t in terms if t["municipality_id"] == MID]) == 1

    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == term["id"])
    claims = {claim["field"]: claim for claim in packet["claims"]}
    # The vote count has no field on the term record; it is kept in
    # the evidence packet (98,049 votes in the 2025 election per the
    # city election commission's official ballot count).
    assert "98,049票" in claims["election_date"]["statement"]
    assert claims["term_end"]["source_ids"] == [
        "akita-pref-mayor-term-expiry-list"
    ]
    assert packet["open_questions"]


def test_akita_manifesto_search_locates_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(s for s in searches if s["id"] == SEARCH_ID)
    assert search["executive_term_id"] == TERM_ID
    # The bulletin is extant on the city election commission's
    # current official page, so its source is registered now; the
    # promise extraction itself is stage 3, hence follow_up_required.
    assert search["result_status"] == "follow_up_required"
    assert search["manifesto_source_ids_found"] == [
        "akita-city-mayor-election-2025-bulletin"
    ]
    assert search["nonexistence_claim"] is False

    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(p for p in packets if p["subject_id"] == SEARCH_ID)
    assert packet["review_status"] == "reviewed"
    assert packet["open_questions"]


def test_akita_web_wiring() -> None:
    executives = (ROOT / "apps/web/lib/executives.ts").read_text(encoding="utf-8")
    assert '"jp-local-052019": "akita-city"' in executives
    catalog = (ROOT / "apps/web/lib/catalog.ts").read_text(encoding="utf-8")
    assert "akita_city_finance_sources.json" in catalog
    assert '"akita-city"' in catalog
    quality = (ROOT / "apps/web/lib/dataQuality.ts").read_text(encoding="utf-8")
    assert "akita-city/fiscal_records.json" in quality
    assert "akita-city/settlement_records.json" in quality
    assert '"akita-city": "秋田市"' in quality
