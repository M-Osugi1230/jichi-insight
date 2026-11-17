from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-401307-executive-2022-12-07"
SEARCH_ID = "manifesto-source-search-fukuoka-city-2022"
SITE_ID = "fukuoka-city-mayor-candidate-official-site"
ARCHIVE_ID = "fukuoka-city-mayor-candidate-2022-blog-archive"

CATALOG_PATHS = [
    "data/catalog/official_sources.json",
    "data/catalog/fukuoka_finance_sources.json",
    "data/catalog/fukuoka_city_finance_sources.json",
    "data/catalog/kitakyushu_finance_sources.json",
    "data/catalog/kitakyushu_project_sources.json",
    "data/catalog/fukuoka_assembly_sources.json",
    "data/catalog/executive_sources.json",
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


def source_ids() -> set[str]:
    return {
        source["id"]
        for path in CATALOG_PATHS
        for source in load_json(path)["records"]
    }


def fukuoka_search() -> dict[str, Any]:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    return next(
        search for search in searches if search["executive_term_id"] == TERM_ID
    )


def test_candidate_sources_are_registered_without_overstating() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert_valid("schemas/source_catalog.schema.json", catalog)
    by_id = {record["id"]: record for record in catalog["records"]}

    site = by_id[SITE_ID]
    assert site["url"] == "https://www.takashima-soichiro.com/"
    assert site["availability"] == "published"
    # The current policy page is a post-election policy presentation, not
    # the 2022 election manifesto; the record must say so and must note
    # that this domain has no election-period Wayback snapshot.
    assert "原文ではない" in site["notes"]
    assert "選挙期間中" in site["notes"]

    archive = by_id[ARCHIVE_ID]
    assert archive["url"] == (
        "https://web.archive.org/web/20221011231540/https://lineblog.me/takashima/"
    )
    assert archive["availability"] == "published"
    # The archive record must not pretend the manifesto text was verified:
    # it records that the snapshot exists but its text is not yet extracted.
    assert "未実施" in archive["notes"]
    assert "まだ作成していない" in archive["notes"]


def test_followup_search_keeps_the_registration_gate_closed() -> None:
    search = fukuoka_search()
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["searched_at"] == "2026-11-17"
    # The follow-up located the candidate's current site and confirmed
    # archived copies of the election-era blog, but the manifesto's
    # primary text is still not secured, so the status must not move.
    assert search["result_status"] == "no_stable_primary_source_found"
    assert search["manifesto_source_ids_found"] == []
    assert set(search["checked_source_ids"]) <= source_ids()
    assert SITE_ID in search["checked_source_ids"]
    assert ARCHIVE_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False
    assert search["next_actions"]

    packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    packet = next(
        packet for packet in packets if packet["subject_id"] == SEARCH_ID
    )
    assert_valid("schemas/evidence_packet.schema.json", packet)
    assert packet["open_questions"]
    for claim in packet["claims"]:
        assert set(claim["source_ids"]) <= source_ids()
    # The archive access failure must stay visible as an unresolved claim.
    access_claims = [
        claim for claim in packet["claims"] if claim["field"] == "archive_access"
    ]
    assert len(access_claims) == 1
    assert access_claims[0]["decision"] == "needs_review"


def test_term_manifesto_sources_stay_empty_until_text_is_verified() -> None:
    # The term lists manifesto sources only once the primary text has
    # been extracted and segmentation-reviewed. For Fukuoka City neither
    # the election bulletin nor the candidate manifesto has reached that
    # stage, so the list stays empty.
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(term for term in terms if term["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == []


def test_no_promise_records_exist_for_the_fukuoka_city_term() -> None:
    # Promise records must not be created from news quotes, third-party
    # summaries, or the post-election policy page. Until the archived
    # primary text is extracted and checked, the registry holds no
    # records for this term.
    promises = load_json("data/entities/executives/promises.json")
    packets = load_json("data/entities/executives/promise_evidence_packets.json")
    assert [
        promise
        for promise in promises
        if promise["executive_term_id"] == TERM_ID
    ] == []
    fukuoka_promise_ids = {
        promise["id"]
        for promise in promises
        if promise["executive_term_id"] == TERM_ID
    }
    assert [
        packet
        for packet in packets
        if packet["subject_id"] in fukuoka_promise_ids
    ] == []
