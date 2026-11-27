"""Issue #1088: Morioka mayor election bulletin, stage-3 full search.

Stage 1 registered the 2023 Morioka mayoral election bulletin as
no_stable_primary_source_found: the city election commission's
current pages carry only the ballot-count results, no Wayback
Machine capture of an official bulletin page or PDF exists, and the
only copy located sits on Seijiyama, a private election-information
site, with no official capture to digest-match against. Stage 3
(2026-11-27) exhausted the remaining routes. The go2senkyo
(Senkyo.com) CDN does host the same-day Morioka City assembly
election bulletin, but no mayoral bulletin PDF could be identified
on that platform either, so no second copy exists to cross-check
the Seijiyama copy against and verification route (3) of
docs/VERIFICATION_CRITERIA.md cannot be satisfied (no URL was
guessed or constructed). The National Diet Library's NDL Search
holds bibliographic records for the Iwate prefectural commission's
"Senkyo no Kiroku" series (held at the Iwate Prefectural Library),
but that series covers prefecture-run elections and records only
results for municipal elections; it does not reproduce mayoral
bulletins, and no bibliographic record of the 2023 Morioka mayoral
bulletin itself could be confirmed. No official publication by the
candidate himself (an official manifesto page) could be identified
either; news summaries of his pledges and his post-inauguration
policy speech are not substitutes for the bulletin. The search
record therefore closes as no_stable_primary_source_found with
nonexistence_claim false, and no promise records are created.
Checking a paper copy held by the commission or a library remains
an offline route outside this search's scope.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-032018"
TERM_ID = "jp-local-032018-executive-2023-09-02"
SEARCH_ID = "manifesto-source-search-morioka-city-2023"
PACKET_ID = "evidence-manifesto-source-search-morioka-city-2023"

CHECKED_SOURCE_IDS = [
    "morioka-city-mayor-election-2023-results",
    "iwate-pref-mayor-term-expiry-list",
    "morioka-city-mayor-election-2023-bulletin-copy",
    "morioka-city-assembly-election-2023-bulletin-go2senkyo",
    "ndl-search-iwate-election-records",
]

NEW_SOURCE_URLS = {
    "morioka-city-assembly-election-2023-bulletin-go2senkyo": (
        "https://prod-cdn.go2senkyo.com/public/senkyo_koho/24229/"
        "20230813盛岡市議会議員選挙.pdf"
    ),
    "ndl-search-iwate-election-records": (
        "https://ndlsearch.ndl.go.jp/books/R100000001-I03112428884"
    ),
}


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
    assert term["person_name"] == "内舘 茂"
    assert term["term_start"] == "2023-09-02"
    assert term["term_end"] == "2027-09-01"
    assert term["election_date"] == "2023-08-13"
    # No verifiable primary source was secured even in stage 3, so
    # the term stays without a manifesto source and no promise or
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
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["checked_source_ids"] == CHECKED_SOURCE_IDS
    assert search["nonexistence_claim"] is False
    assert search["review_status"] == "reviewed"
    assert search["confidence"] == "high"
    # The note records the stage-3 routes that were exhausted: the
    # second-copy cross-check via go2senkyo and the NDL / prefectural
    # library bibliographic route both failed to secure the bulletin.
    assert "段階3" in search["review_note"]
    assert "選挙ドットコム" in search["review_note"]
    assert "NDLサーチ" in search["review_note"]
    assert "存在しないという主張ではない" in search["review_note"]
    assert search["next_actions"]


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
    assert packet["open_questions"]

    catalog = load_json("data/catalog/executive_sources.json")
    source_ids = {record["id"] for record in catalog["records"]}
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids
        assert claim["decision"] == "accepted"
    # A dedicated stage-3 claim covers the two newly checked sources.
    stage3_claims = [
        claim
        for claim in packet["claims"]
        if "morioka-city-assembly-election-2023-bulletin-go2senkyo"
        in claim["source_ids"]
    ]
    assert len(stage3_claims) == 1
    assert stage3_claims[0]["source_ids"] == [
        "morioka-city-assembly-election-2023-bulletin-go2senkyo",
        "ndl-search-iwate-election-records",
    ]


def test_new_sources_are_registered_in_the_catalog() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.70.0"
    assert len(catalog["records"]) == 225
    assert len({record["id"] for record in catalog["records"]}) == 225
    for source_id, url in NEW_SOURCE_URLS.items():
        record = next(r for r in catalog["records"] if r["id"] == source_id)
        assert record["url"] == url
        assert record["municipality_key"] == "morioka-city"
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
