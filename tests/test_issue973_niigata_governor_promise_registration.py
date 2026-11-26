"""Issue #973: Niigata governor promises (cluster 13, stage 3).

The 2026 Niigata gubernatorial election bulletin could not be
secured as a verifiable primary source, so -- following the
Toyota City and Sakai City precedent -- no promise records are
created for Governor Hanazumi's term. The search was repeated on
2026-11-23 across every official route: the prefectural election
commission's results page still shows its "election record"
section as "in preparation" (the 2022 record PDF was published
about nineteen months after that election), the election-period
special site and the ballot-count site are both offline with no
Wayback Machine captures, the National Diet Library WARP holds
no copy of the special site, Niigata City's commission page
states the bulletin was distributed on paper only (newspaper
inserts, door-to-door delivery and copies kept at public
offices; the braille/audio edition was mailed on request), and
the prefectural gazette extra of 2026-05-14 (commission notice
No. 55, the lottery for the bulletin's placement order) proves
the bulletin was issued without printing its text. News reports
of the candidate's policy announcements are not the candidate's
own official publications and are not adopted as a substitute.
The search record therefore closes as
no_stable_primary_source_found with nonexistence_claim false:
it does not claim the bulletin or the promises do not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-150002"
TERM_ID = "jp-local-150002-executive-2026-06-10"
SEARCH_ID = "manifesto-source-search-niigata-pref-2026"
PACKET_ID = "evidence-manifesto-source-search-niigata-pref-2026"

CHECKED_SOURCE_IDS = [
    "niigata-pref-governor-election-2026-results",
    "niigata-pref-governor-election-list",
    "niigata-pref-gazette-2026-05-14-extra",
    "niigata-city-governor-election-2026-overview",
    "niigata-pref-governor-term-list",
    "niigata-pref-governor",
]

NEW_SOURCE_URLS = {
    "niigata-pref-governor-election-list": (
        "https://www.pref.niigata.lg.jp/site/senkyo/1200589259767.html"
    ),
    "niigata-pref-gazette-2026-05-14-extra": (
        "https://kenpo.pref.niigata.lg.jp/bn/R08_05/0514_g1/g1_20260514.pdf"
    ),
    "niigata-city-governor-election-2026-overview": (
        "https://www.city.niigata.lg.jp/shisei/senkyo/oshirase/"
        "kentiji_senkyo/r8kenchiji_senkyo.html"
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
    assert term["person_name"] == "花角 英世"
    assert term["term_start"] == "2026-06-10"
    assert term["term_end"] == "2030-06-09"
    assert term["election_date"] == "2026-05-31"
    # No primary source was secured, so the term stays without a
    # manifesto source and no promise or review records exist.
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
    assert len(searches) == 41
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["executive_term_id"] == TERM_ID
    assert search["searched_at"] == "2026-11-23"
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert search["checked_source_ids"] == CHECKED_SOURCE_IDS
    assert search["nonexistence_claim"] is False
    assert search["review_status"] == "reviewed"
    assert search["confidence"] == "high"
    # The note records the concrete routes that were exhausted and
    # keeps the door open: the commission's election record is
    # still in preparation.
    assert "作成中です" in search["review_note"]
    assert "選挙の記録" in search["review_note"]
    assert "存在しないという主張ではない" in search["review_note"]
    assert search["next_actions"]


def test_search_evidence_packet_supports_the_closure() -> None:
    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    assert len(packets) == 41
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
    result_claim = next(
        claim for claim in packet["claims"] if claim["field"] == "result_status"
    )
    assert result_claim["source_ids"] == ["niigata-pref-gazette-2026-05-14-extra"]


def test_new_sources_are_registered_in_the_catalog() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.65.0"
    assert len(catalog["records"]) == 191
    assert len(catalog["records"]) == 191
    for source_id, url in NEW_SOURCE_URLS.items():
        record = next(r for r in catalog["records"] if r["id"] == source_id)
        assert record["url"] == url
        assert record["availability"] == "published"
        assert record["review_status"] == "reviewed"
