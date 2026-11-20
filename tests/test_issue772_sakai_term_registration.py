from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-271403-executive-2023-06-09"
SEARCH_ID = "manifesto-source-search-sakai-city-2023"


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def sakai_term() -> dict[str, Any]:
    terms = load_json("data/entities/executives/executive_terms.json")
    matches = [term for term in terms if term["id"] == TERM_ID]
    assert len(matches) == 1
    return matches[0]


def test_sakai_mayor_term_values_match_official_records() -> None:
    term = sakai_term()

    # The term end is stated directly in the city election
    # commission's official election-schedule page (expiry
    # 2027-06-08). The start follows the statutory chain: the
    # commission's own minutes state the previous term expired on
    # 2023-06-08, the 2023 election was a term-expiry election held
    # on 2023-06-04, so Article 259's proviso starts the new term
    # on 2023-06-09 and the four-year term (Local Autonomy Act
    # Article 140) ends on 2027-06-08, agreeing with the stated
    # expiry.
    assert term["municipality_id"] == "jp-local-271403"
    assert term["office"] == "mayor"
    assert term["person_name"] == "永藤 英機"
    assert term["election_date"] == "2023-06-04"
    assert term["term_start"] == "2023-06-09"
    assert term["term_end"] == "2027-06-08"
    assert term["status"] == "current"
    assert term["review_status"] == "reviewed"
    assert term["confidence"] == "high"
    assert term["sources"] == [
        "sakai-city-mayor-profile",
        "sakai-city-election-schedule",
        "sakai-city-mayor-election-2023-results",
        "sakai-city-election-commission-minutes-2023-13",
        "public-offices-election-act",
    ]


def test_sakai_mayor_registers_no_manifesto_source_or_promises() -> None:
    term = sakai_term()

    # The 2023 Sakai mayoral election bulletin has no official web
    # publication (the city's election pages carry only the schedule
    # and the results, and no bulletin copy survives in the Wayback
    # Machine's archive of the election data section), and no
    # verifiable candidate publication was found: the candidate's
    # official site policy page still carries his 2015 prefectural
    # assembly-era content. The term therefore registers no
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


def test_sakai_mayor_vote_count_is_officially_published() -> None:
    # Sakai City still publishes the official results: the evidence
    # packet records the winning vote count from the city's own
    # ballot-count results PDF. The term record itself has no vote
    # field, so the count lives only in the evidence packet.
    packets = load_json("data/entities/executives/evidence_packets.json")
    matches = [p for p in packets if p["subject_id"] == TERM_ID]
    assert len(matches) == 1
    election_claims = [
        claim for claim in matches[0]["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    assert "139,295" in election_claims[0]["statement"]
    assert "sakai-city-mayor-election-2023-results" in (
        election_claims[0]["source_ids"]
    )
