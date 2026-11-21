from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-041009-executive-2025-08-22"
BULLETIN_ID = "sendai-city-mayor-election-2025-bulletin"

# The Kori Kazuko panel of the 3 August 2025 Sendai City mayoral
# election bulletin (page 2, upper panel): under the heading
# "priority policies", four circle-marked items are the only
# forward-looking statements. Three state concrete outcomes (a
# city top-up on the childbirth lump sum, zero childcare fees
# from the second child, zero medical costs up to age 18) and are
# registered as specific commitments; the fourth states a
# direction (attracting and cultivating large anime/game events)
# and stays directional. The slogan, the career profile and the
# QR-code pointer are not promise records, and the panel's
# "four years of achievements" box presents the previous term's
# record, so none of its four items became a promise either. The
# bulletin itself is no longer on the city's site (the election-
# period URL now returns 404); the registration was transcribed
# from the rendered images of the archived copy of the city's
# official URL, cross-checked at multiple resolutions (the panel
# is image-only apart from the masthead and footnotes). Any
# wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "出産育児一時金50万円に仙台市独自の上乗せ助成",
    "第二子以降の保育料負担ゼロ",
    "18歳まで医療費ゼロ、子育てに安心を",
    "アニメ・ゲームの聖地に！大型イベントを仙台に誘致・育成",
]

EXPECTED_STATEMENT_TYPES = [
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "urban_development_and_tourism",
]

EXPECTED_TARGETS: list[str | None] = [
    "出産育児一時金50万円への仙台市独自の上乗せ助成",
    "第二子以降の保育料負担ゼロ",
    "18歳まで医療費ゼロ",
    None,
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


def records() -> list[dict[str, Any]]:
    return [
        record
        for record in load_json("data/entities/executives/promises.json")
        if record["executive_term_id"] == TERM_ID
    ]


def packets_by_subject() -> dict[str, dict[str, Any]]:
    packets = load_json("data/entities/executives/promise_evidence_packets.json")
    return {
        packet["subject_id"]: packet
        for packet in packets
        if packet["subject_id"].startswith(TERM_ID)
    }


def test_term_is_registered_with_official_dates() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert_valid("schemas/executive_term.schema.json", term)
    assert term["person_name"] == "郡 和子"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2025-08-03"
    # The term was registered at stage 1 (Issue #874): the start
    # is stated on the city's official list of past mayors and the
    # expiry is stated directly in the Miyagi prefectural election
    # commission's term-expiry list, so no open cross-check
    # remains for Sendai.
    assert term["term_start"] == "2025-08-22"
    assert term["term_end"] == "2029-08-21"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_all_4_records_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 5)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-041009"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so
        # the record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution() -> None:
    items = records()
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["target"] for record in items] == EXPECTED_TARGETS
    for record in items:
        # No start date or funding is stated in the bulletin, so
        # those fields stay null instead of being filled in.
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        # No official progress reporting keyed to the promises
        # exists, so every record stays not_assessable.
        assert record["progress_state"] == "not_assessable"
    for record in items[:3]:
        assert record["assessability"] == "assessable"
        assert record["controllability"] == "high"
    # Event attraction depends on outside organisers, so the
    # directional record is only partially assessable.
    assert items[3]["assessability"] == "partially_assessable"
    assert items[3]["controllability"] == "medium"


def test_non_promise_elements_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The slogan is a catchphrase, the profile is a career record,
    # and the "four years of achievements" box presents the
    # previous term's record, so none of them became a promise
    # record. (The achievements box's event-attraction headline is
    # similar to promise 004's wording, but 004 comes from the
    # forward-looking priority-policies list.)
    fragments = [
        "笑顔あふれ",
        "世界から選ばれる",
        "待機児童ゼロ」の達成",
        "エアコン設置完了",
        "大型観光イベントの誘致・育成",
        "コロナ禍を乗り越え",
        "東北放送",
        "衆議院議員選挙で初当選",
        "全国市長会副会長",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_no_project_links() -> None:
    # None of the Stage 2 series is the promised scheme itself,
    # so no promise is linked and the reverse links stay empty.
    for record in records():
        assert record["related_project_ids"] == []
    projects = load_json("data/reviewed/sendai-city/projects.json")
    for project in projects:
        assert project["related_promise_ids"] == []


def test_every_promise_has_one_packet_with_provenance() -> None:
    items = records()
    packets = packets_by_subject()
    assert set(packets) == {record["id"] for record in items}
    for record in items:
        packet = packets[record["id"]]
        assert_valid("schemas/evidence_packet.schema.json", packet)
        fields = [claim["field"] for claim in packet["claims"]]
        assert "original_text" in fields
        provenance = next(
            claim for claim in packet["claims"] if claim["field"] == "source_provenance"
        )
        # The bulletin is the official document itself; the live
        # page has been removed, so the archived copy of the
        # city's official URL is the carrier, and the grading
        # stays high.
        assert "選挙公報" in provenance["statement"]
        assert "Wayback" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_manifesto_review_records_the_segmentation() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        record
        for record in reviews
        if record["id"] == "manifesto-review-jp-local-041009-2025"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 4
    # The treatment of the slogan and of the achievements box is
    # recorded in the review note.
    assert "レコード化せず" in review["review_note"]
    assert "公約化しなかった" in review["review_note"]
    assert "実績" in review["review_note"]


def test_source_search_registered_the_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-sendai-city-2025"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    # The search records that the live bulletin page is gone and
    # that the archived copy of the official URL was used.
    assert "404" in search["review_note"]
    assert "Wayback" in search["review_note"]


def test_bulletin_source_record_points_at_the_archived_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    # The catalog URL is the Wayback Machine capture of the
    # bulletin PDF that the city published at its official URL
    # during the election period.
    assert bulletin["url"].startswith("https://web.archive.org/web/20250731061328/")
    assert bulletin["url"].endswith("senkyokouhou_sityou.pdf")
    assert bulletin["municipality_key"] == "sendai-city"
    assert bulletin["organization"].startswith("仙台市選挙管理委員会")
