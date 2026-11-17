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
BULLETIN_ID = "fukuoka-city-mayor-election-2022-bulletin"
GO2_ID = "fukuoka-city-mayor-manifesto-2022-go2senkyo-archive"

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
    # The follow-up read the archived blog itself: it holds no manifesto
    # post, so the record must state that the blog is not the source of
    # the manifesto text and must point at the article archive instead.
    assert "公約原文の出典とはならない" in archive["notes"]
    assert GO2_ID in archive["notes"]


def test_manifesto_text_sources_are_registered_with_honest_grading() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    by_id = {record["id"]: record for record in catalog["records"]}

    go2 = by_id[GO2_ID]
    assert go2["url"] == (
        "https://web.archive.org/web/20221116023507/"
        "https://go2senkyo.com/articles/2022/11/16/73290.html"
    )
    assert go2["availability"] == "published"
    # The full text reached the registry through a contemporaneous
    # third-party quotation of the candidate homepage, not through an
    # archived copy of the homepage itself; the grading must say so.
    assert go2["confidence"] == "medium"
    assert "引用" in go2["notes"]
    assert "存在せず" in go2["notes"]

    bulletin = by_id[BULLETIN_ID]
    assert bulletin["source_kind"] == "document"
    assert bulletin["confidence"] == "high"
    # The bulletin carries the six headings only; the record must not
    # pretend the paragraph text came from it.
    assert "掲載されていない" in bulletin["notes"]


def test_search_records_the_text_as_secured() -> None:
    search = fukuoka_search()
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["searched_at"] == "2026-11-17"
    # The full text was secured through the archived article quotation,
    # cross-checked against the official election bulletin, so the
    # search now reports the sources as registered.
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID, GO2_ID]
    assert set(search["checked_source_ids"]) <= source_ids()
    for expected in (SITE_ID, ARCHIVE_ID, BULLETIN_ID, GO2_ID):
        assert expected in search["checked_source_ids"]
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
    # The earlier archive-access failure was resolved by the follow-up
    # read, and the text acquisition is recorded as its own claim.
    access_claims = [
        claim for claim in packet["claims"] if claim["field"] == "archive_access"
    ]
    assert len(access_claims) == 1
    assert access_claims[0]["decision"] == "accepted"
    text_claims = [
        claim for claim in packet["claims"] if claim["field"] == "manifesto_text"
    ]
    assert len(text_claims) == 1
    assert text_claims[0]["decision"] == "accepted"


def test_term_lists_the_registered_manifesto_sources() -> None:
    # The term lists manifesto sources once the text has been extracted
    # and segmentation-reviewed (manifesto-review-jp-local-401307-2022).
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(term for term in terms if term["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID, GO2_ID]

    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        review
        for review in reviews
        if review["id"] == "manifesto-review-jp-local-401307-2022"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == GO2_ID
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 6
    # The review keeps the provenance caveat: the text is a quotation,
    # so confidence stays at medium rather than high.
    assert review["confidence"] == "medium"
