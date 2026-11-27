"""Issue #1089: Aomori City mayoral bulletin, stage 3 full search.

The stage 1 record (Issue #1073) already closed the 2023 Aomori
City mayoral election bulletin as no_stable_primary_source_found
and explicitly deferred the full search to stage 3. This stage
executed that search on 2026-11-27: the city election commission's
current official pages were re-checked directly (the 2023 results
page, updated 2024-12-23, carries only the turnout, the count and
the per-candidate votes -- no bulletin link and no candidate
platforms; the past-results index links no bulletin either), the
prefectural commission's election record was re-confirmed to carry
no reprint of the city mayoral bulletin (the same record series
does reprint the same-day gubernatorial bulletin in its appendix
volume, so the absence is specific to the city part), the Wayback
Machine had already shown no capture of the results page and no
bulletin capture among the city domain's 2023 captures at stage 1
-- the full CDX enumeration attempted at stage 3 was denied from
this environment (HTTP 403) and remains an open item --, the
National Diet Library WARP institutionally collects municipal
websites four times a year but whether its 2023 captures of the
city site include the bulletin could not be determined, and a
general web search including candidate publications and private
election-information sites surfaced no copy of the bulletin.
News reports of candidate questionnaires are not the candidate's
own official publications and are not adopted as a substitute.
Following the Niigata, Okayama and Kumamoto governors' stage 3
precedent, the search record therefore closes as
no_stable_primary_source_found with nonexistence_claim false and
no promise records are created: the bulletin was issued under the
city's bulletin ordinance, so this is not a claim that it does
not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-022012"
TERM_ID = "jp-local-022012-executive-2023-06-04"
SEARCH_ID = "manifesto-source-search-aomori-city-2023"
PACKET_ID = "evidence-manifesto-source-search-aomori-city-2023"

CHECKED_SOURCE_IDS = [
    "aomori-city-mayor-election-2023-results",
    "aomori-pref-election-record-2023",
    "aomori-city-past-election-results",
    "aomori-city-election-bulletin-ordinance",
    "aomori-pref-mayor-term-expiry-list",
]


def load_json(path: str) -> Any:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)


def assert_valid(schema_path: str, instance: Any) -> None:
    validator = Draft202012Validator(
        load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors = list(validator.iter_errors(instance))
    assert errors == [], "; ".join(error.message for error in errors)


def test_term_registers_no_manifesto_source_and_no_promises() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["municipality_id"] == MUNICIPALITY_ID
    assert term["person_name"] == "西 秀記"
    assert term["term_start"] == "2023-06-04"
    assert term["term_end"] == "2027-06-03"
    assert term["election_date"] == "2023-06-04"
    # No verifiable original was secured at stage 3 either, so the
    # term stays without a manifesto source and no promise or
    # review records exist for it.
    assert term["manifesto_source_ids"] == []

    promises = load_json("data/entities/executives/promises.json")
    assert [
        record for record in promises if record["executive_term_id"] == TERM_ID
    ] == []

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert [
        record
        for record in reviews
        if record["executive_term_id"] == TERM_ID
    ] == []


def test_search_record_closes_as_no_stable_primary_source() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    assert len(searches) == 47
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["executive_term_id"] == TERM_ID
    assert search["searched_at"] == "2026-11-27"
    assert search["search_scopes"] == [
        "official_election_result_page",
        "official_site_search",
        "official_document_archive",
        "candidate_publication_search",
        "general_web_search",
    ]
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["checked_source_ids"] == CHECKED_SOURCE_IDS
    assert search["nonexistence_claim"] is False
    assert search["review_status"] == "reviewed"
    assert search["confidence"] == "high"
    # The note records the stage 3 routes that were exhausted,
    # including the two archive limitations, and is explicit that
    # this is not a claim of nonexistence.
    assert "段階3として2026年11月27日に本格探索を実施した" in search["review_note"]
    assert "Wayback Machine" in search["review_note"]
    assert "HTTP 403" in search["review_note"]
    assert "WARP" in search["review_note"]
    assert "存在しないという主張ではない" in search["review_note"]
    assert len(search["next_actions"]) == 5


def test_search_evidence_packet_supports_the_closure() -> None:
    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    assert len(packets) == 47
    packet = next(record for record in packets if record["id"] == PACKET_ID)
    assert_valid("schemas/evidence_packet.schema.json", packet)
    assert packet["subject_type"] == "manifesto_source_search"
    assert packet["subject_id"] == SEARCH_ID
    assert packet["review_status"] == "reviewed"
    # Three stage 1 claims plus the two stage 3 claims.
    assert len(packet["claims"]) == 5
    assert len(packet["open_questions"]) == 3

    catalog = load_json("data/catalog/executive_sources.json")
    source_ids = {record["id"] for record in catalog["records"]}
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids
        assert claim["decision"] == "accepted"
    result_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "result_status"
    )
    assert result_claim["source_ids"] == [
        "aomori-city-mayor-election-2023-results"
    ]
    assert "段階3の本格探索" in (result_claim["review_note"] or "")
    stage3_claims = [
        claim
        for claim in packet["claims"]
        if "段階3" in claim["statement"]
    ]
    assert len(stage3_claims) == 2


def test_catalog_is_unchanged_by_this_closure() -> None:
    # Stage 3 secured no new official document, so -- unlike the
    # Niigata closure -- no source is added to the catalog for
    # Aomori City.  (The catalog total itself moved on with the
    # Morioka stage-3 registration, PR #1091; the global version and
    # count pins live in the shared catalog tests.)
    catalog = load_json("data/catalog/executive_sources.json")
    aomori_city_ids = sorted(
        record["id"]
        for record in catalog["records"]
        if "aomori-city" in record["id"]
    )
    assert aomori_city_ids == [
        "aomori-city-election-bulletin-ordinance",
        "aomori-city-mayor-election-2023-results",
        "aomori-city-past-election-results",
    ]
