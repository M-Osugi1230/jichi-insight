from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"

TERM_ID = "jp-local-232114-executive-2024-02-19"
SEARCH_ID = "manifesto-source-search-toyota-city-2024"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def toyota_term() -> dict[str, Any]:
    terms = load_json("data/entities/executives/executive_terms.json")
    matches = [term for term in terms if term["id"] == TERM_ID]
    assert len(matches) == 1
    return matches[0]


def test_toyota_mayor_term_values_match_official_records() -> None:
    term = toyota_term()

    # Term dates follow the Aichi Prefecture mayors list and the
    # prefectural term-expiry list (expiry 2028-02-18) and the
    # Article 259 proviso counting for a term-expiry election
    # (start is the day after the previous term expired).
    assert term["municipality_id"] == "jp-local-232114"
    assert term["office"] == "mayor"
    assert term["person_name"] == "太田 稔彦"
    assert term["election_date"] == "2024-02-04"
    assert term["term_start"] == "2024-02-19"
    assert term["term_end"] == "2028-02-18"
    assert term["status"] == "current"
    assert term["review_status"] == "reviewed"
    assert term["confidence"] == "high"
    assert term["sources"] == [
        "toyota-city-mayor",
        "toyota-city-mayor-election-2024-schedule",
        "aichi-pref-mayors-term-list-2026",
        "aichi-pref-term-expiry-list-2026",
        "public-offices-election-act",
    ]


def test_toyota_mayor_registers_no_manifesto_source_or_promises() -> None:
    term = toyota_term()

    # The 2024 Toyota mayoral election bulletin is not extant as an
    # official web publication (the city's election pages were removed
    # right after the vote and no archive copy survives), and no
    # verifiable candidate publication was found. The term therefore
    # registers no manifesto source, and no promise records exist for
    # it. This records an unlocated source, not a claim that no
    # manifesto exists.
    assert term["manifesto_source_ids"] == []

    promises = load_json("data/entities/executives/promises.json")
    assert [p for p in promises if p["executive_term_id"] == TERM_ID] == []

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    matches = [s for s in searches if s["id"] == SEARCH_ID]
    assert len(matches) == 1
    search = matches[0]
    assert search["executive_term_id"] == TERM_ID
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["nonexistence_claim"] is False


def test_toyota_mayor_web_wiring_is_lib_layer_only() -> None:
    executives = (WEB / "lib/executives.ts").read_text(encoding="utf-8")
    catalog = (WEB / "lib/catalog.ts").read_text(encoding="utf-8")
    data_quality = (WEB / "lib/dataQuality.ts").read_text(encoding="utf-8")

    assert '"jp-local-232114": "toyota-city"' in executives
    assert '| "toyota-city"' in catalog
    assert '"toyota-city": {' in catalog
    assert 'href: "/municipalities/toyota-city"' in catalog
    assert (WEB / "lib/toyotaCityFinance.ts").exists()
    assert '"toyota-city": toyotaCityFinance.records' in data_quality
    assert '"toyota-city": toyotaCityFinance.evidencePackets' in data_quality
