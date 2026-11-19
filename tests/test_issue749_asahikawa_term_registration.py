from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-012041-executive-2025-09-26"
SEARCH_ID = "manifesto-source-search-asahikawa-city-2025"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def asahikawa_term() -> dict[str, Any]:
    terms = load_json("data/entities/executives/executive_terms.json")
    matches = [term for term in terms if term["id"] == TERM_ID]
    assert len(matches) == 1
    return matches[0]


def test_asahikawa_mayor_term_values_match_official_records() -> None:
    term = asahikawa_term()

    # Term dates follow the statutory chain: the city election
    # commission's official press-release document states the previous
    # term expired on 2025-09-25, the 2025 election was a term-expiry
    # election held on 2025-09-07, so Article 259's proviso starts the
    # new term on 2025-09-26 and the four-year term (Local Autonomy
    # Act Article 140) ends on 2029-09-25.
    assert term["municipality_id"] == "jp-local-012041"
    assert term["office"] == "mayor"
    assert term["person_name"] == "今津 寛介"
    assert term["election_date"] == "2025-09-07"
    assert term["term_start"] == "2025-09-26"
    assert term["term_end"] == "2029-09-25"
    assert term["status"] == "current"
    assert term["review_status"] == "reviewed"
    assert term["confidence"] == "high"
    assert term["sources"] == [
        "asahikawa-city-mayor-profile",
        "asahikawa-city-mayor-election-2025-schedule",
        "asahikawa-city-mayor-election-2025-results",
        "public-offices-election-act",
    ]


def test_asahikawa_mayor_registers_no_manifesto_source_or_promises() -> None:
    term = asahikawa_term()

    # The 2025 Asahikawa mayoral election bulletin has no official web
    # publication (the city's election pages carry only the schedule
    # and the results, and no bulletin copy survives in the Wayback
    # Machine's archive of the election section), and no verifiable
    # candidate publication was found. The term therefore registers no
    # manifesto source, and no promise records exist for it. This
    # records an unlocated source, not a claim that no manifesto
    # exists: the paper bulletin itself was printed and distributed.
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


def test_asahikawa_mayor_vote_count_is_officially_published() -> None:
    # Unlike the Toyota City precedent (whose election pages were
    # removed), Asahikawa City still publishes the official results:
    # the evidence packet records the winning vote count from the
    # city's own results page. The term record itself has no vote
    # field, so the count lives only in the evidence packet.
    packets = load_json("data/entities/executives/evidence_packets.json")
    matches = [p for p in packets if p["subject_id"] == TERM_ID]
    assert len(matches) == 1
    election_claims = [
        claim for claim in matches[0]["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    assert "78,884" in election_claims[0]["statement"]
    assert "asahikawa-city-mayor-election-2025-results" in (
        election_claims[0]["source_ids"]
    )
