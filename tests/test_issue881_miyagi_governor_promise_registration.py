"""Issue #881: Miyagi governor promises (cluster 9, stage 3).

The source is the official 2025 Miyagi gubernatorial election
bulletin itself, published on the prefectural election commission's
official election page. Governor Murai's panel (page 1, lower half)
is a poster: the headline slogan "さらなる成長戦略を実行します！"
above four policies, each a heading (a noun phrase) plus one body
paragraph, a closing note "＊これらの政策はほんの一例です。", a
left block promoting the candidate's YouTube presence ("AIむらい
YouTubeライブ", two QR codes and a note that the photograph is an
AI-generated image), and the candidate's name written vertically.
Because each heading is a noun phrase that does not stand as a
pledge on its own, the four records follow the Fukuoka City
precedent of heading-plus-body records (the heading and the body
joined by a newline); the boundary judgement is preserved in the
review's open questions. The slogan, the closing note, the YouTube
promotion and the QR codes are not promises. The panel carries no
display of the previous term's record or progress, so no
achievements had to be separated out. Two policies state numeric
content: "県内総生産10兆円" (registered as the target of the
semiconductor policy) and "1万人～1.5万人を収容" (registered as
the target of the arena policy, whose "民間の資金を活用して" is
also registered as its funding statement). The hospital policy's
"次の4年間で" is a stated period, not a date, so no deadline is
registered (the term end is never used as an implicit promise
deadline). The candidate panels are image-only (a text extraction
of the whole PDF yields 837 non-space characters, all of them the
commission's printed frame text; no text is extracted from the
candidate panels), so the texts were transcribed from 100/300 dpi
renderings and collated, item by item, against the text layer of
the candidate-submitted audio-readable data PDF that the
commission publishes for screen readers; the only differences are
line breaks and the asterisk glyph.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-040002-executive-2025-11-21"
BULLETIN_ID = "miyagi-pref-governor-election-2025-bulletin"
AUDIO_ID = "miyagi-pref-governor-election-2025-bulletin-audio-data"
REVIEW_ID = "manifesto-review-jp-local-040002-2025"
SEARCH_ID = "manifesto-source-search-miyagi-pref-2025"

# The four policy items of Governor Murai's panel in the official
# 2025 election bulletin (page 1, lower half), transcribed verbatim
# in document order as heading-plus-body records. The headline
# slogan, the closing note, the YouTube promotion block, the QR
# codes and the photograph note are not records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    (
        "最先端技術を生かしたDXの推進\n"
        "誰でもAIなどのデジタル技術を活用できるようにして、生活や仕事を効率化し、"
        "人口が減少する中でも活力に満ちた県土を実現します。デジタル身分証アプリを活用し、"
        "県民の皆さんと意思疎通をはかり、大規模災害時には多くの命を救います。"
    ),
    (
        "世界的半導体企業の誘致\n"
        "県内総生産10兆円を目指し、新たなマザー工場になる世界的半導体企業の誘致を実現します。"
    ),
    (
        "若者が集える場所の確保\n"
        "1万人～1.5万人を収容できるローコストアリーナを民間の資金を活用してつくります（東北初）。"
    ),
    (
        "病院再編の完結\n"
        "次の4年間で仙台赤十字病院＋県立がんセンターの新病院を名取市に建設します。"
        "富谷市にできる東北医科薬科大学の新病院を確実に支援し、精神医療センターを名取市内で建設します。"
        "次期宮城県地域医療構想の策定に仙台市の委員を加え、仙台市の意見をしっかり伺います。"
    ),
]

EXPECTED_POLICY_AREAS = [
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "health_welfare_and_community",
]

PROJECT = "jp-local-040002-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-002": [PROJECT.format("academia-industry-new-industry")],
    f"{TERM_ID}-promise-004": [PROJECT.format("health-medical-care-sustainability")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# Promises left unlinked because none of the ten stage-2 series
# covers them (no digital/DX series and no sports-facility series
# was selected) -- see each record's extraction note.
UNLINKED_IDS = {f"{TERM_ID}-promise-001", f"{TERM_ID}-promise-003"}


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


def test_all_4_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 5)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-040002"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from the
        # prefectural election commission's official site, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_only_the_stated_numeric_content_was_registered() -> None:
    items = {record["id"]: record for record in records()}
    dx = items[f"{TERM_ID}-promise-001"]
    assert dx["statement_type"] == "directional_commitment"
    assert dx["target"] is None
    assert dx["funding_statement"] is None
    semiconductor = items[f"{TERM_ID}-promise-002"]
    # "県内総生産10兆円" is a stated numeric target and is
    # registered as stated; the record is a specific commitment.
    assert semiconductor["statement_type"] == "specific_commitment"
    assert semiconductor["target"] == "県内総生産10兆円"
    arena = items[f"{TERM_ID}-promise-003"]
    # "1万人～1.5万人を収容" states the scale of the facility to be
    # built, and "民間の資金を活用して" states the funding method;
    # both are registered as stated.
    assert arena["statement_type"] == "specific_commitment"
    assert arena["target"] == "1万人～1.5万人を収容できるローコストアリーナ"
    assert arena["funding_statement"] == "民間の資金を活用してつくります"
    hospital = items[f"{TERM_ID}-promise-004"]
    assert hospital["statement_type"] == "specific_commitment"
    assert hospital["target"] is None
    for record in items.values():
        assert record["baseline"] is None
        # "次の4年間で" is a stated period, not a date; the term end
        # is never used as an implicit promise deadline either.
        assert record["deadline"] is None
        assert record["change_explanation"] is None


def test_slogan_note_and_promotion_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        "さらなる成長戦略を実行します",
        "ほんの一例",
        "AIむらい",
        "YouTube",
        "AIが生成した画像",
        "398-9436",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {record["id"] for record in items if record["progress_state"] == "in_progress"}
    assert in_progress == IN_PROGRESS_IDS
    for record in items:
        if record["id"] not in IN_PROGRESS_IDS:
            # Unassessed is never converted into "not started" or a score.
            assert record["progress_state"] == "not_assessable"
            assert record["related_project_ids"] == []
            assert record["id"] in UNLINKED_IDS
        else:
            assert record["related_project_ids"]


def test_project_links_are_exact_bidirectional_and_capped() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids
    for record in items.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []

    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/miyagi-prefecture/projects.json")
    }
    for promise_id, project_ids in EXPECTED_LINKS.items():
        for project_id in project_ids:
            assert promise_id in projects[project_id]["related_promise_ids"]
    linked_promise_ids = {
        promise_id for project in projects.values() for promise_id in project["related_promise_ids"]
    }
    assert linked_promise_ids == set(EXPECTED_LINKS)

    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        claims = {claim["field"]: claim for claim in packets[promise_id]["claims"]}
        link_claim = claims["related_project_ids"]
        assert link_claim["decision"] == "needs_review"
        assert "low / inferred" in link_claim["review_note"]
        progress_claim = claims["progress_state"]
        assert progress_claim["decision"] == "needs_review"


def test_unlinked_promises_state_the_reason() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id in UNLINKED_IDS:
        note = items[promise_id]["extraction_note"] or ""
        assert "事業接続は行っていない" in note
        packet = packets_by_subject()[promise_id]
        assert packet["open_questions"]


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
        # The bulletin provenance (official document, official
        # commission hosting, image-based panel collated against the
        # audio-readable data) travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "音声読み上げ対応データ" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID, AUDIO_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 4

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert AUDIO_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 as a term-expiry-election
    # construction: the prefectural election commission's official
    # election page states the previous term expired on 2025-11-20,
    # so under the proviso of Article 259 the new term runs from
    # the following day for four years; it is never used as an
    # implicit promise deadline.
    assert term["term_start"] == "2025-11-21"
    assert term["term_end"] == "2029-11-20"
