"""Issue #900: Shizuoka governor promises (cluster 10, stage 3).

The source is the official 2024 Shizuoka gubernatorial election
bulletin itself, published on the prefectural election commission's
official site (www_dr.pref.shizuoka.jp). Governor Suzuki's panel
(page 1, middle band) is a poster: the manifesto heading
"鈴木やすともマニフェスト「やります！」" above nine items in a
3x3 grid, each a heading (a field name) plus one body sentence,
with a calligraphic "やります！" on every item; a speech-bubble
line to the left of the heading; a left-hand achievements panel
listing seven numbered items from his four terms (sixteen years)
as Mayor of Hamamatsu City, with a vertical note that what was
possible in Hamamatsu can be applied and developed in Shizuoka
Prefecture; his profile and a LINE QR-code box at the bottom; and
the closing banner "「オール静岡」で幸福度日本一の静岡県をめざします！".
Because each heading is a field name that does not stand as a
pledge on its own, the nine records follow the Fukuoka City /
Miyagi precedent of heading-plus-body records (the heading and
the body joined by a newline); the boundary judgement is
preserved in the review's open questions. The seven achievements
are presented as his record as Mayor of Hamamatsu City and are
not promises, so they were not registered. The speech-bubble
line, the profile, the QR-code guidance and the closing banner
(a slogan) are not promises either. None of the nine items
states a numeric target, a deadline or a funding method, so all
nine are directional commitments with no target registered. The
candidate panels are image-only (a text extraction of the whole
PDF yields zero non-space characters, so no text is extracted
from the candidate panels), so the texts were transcribed from
200/300 dpi renderings and collated across resolutions. Unlike
Miyagi, no candidate-submitted audio-readable data publication
could be confirmed for the 21st election (the 20th election of
2021 has an official "候補者情報（音声読み上げ用）" page), so no
text-layer collation was available; the search record does not
claim the data does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-220001-executive-2024-05-26"
BULLETIN_ID = "shizuoka-pref-governor-election-2024-bulletin"
REVIEW_ID = "manifesto-review-jp-local-220001-2024"
SEARCH_ID = "manifesto-source-search-shizuoka-pref-2024"

# The nine manifesto items of Governor Suzuki's panel in the
# official 2024 election bulletin (page 1, middle band),
# transcribed verbatim in document order as heading-plus-body
# records. The heading line, the speech-bubble line, the seven
# Hamamatsu achievements, the profile, the QR-code guidance and
# the closing banner are not records. Any wording drift against
# the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "リニア\n大井川の水資源確保と南アルプスの自然環境の保全の両立を図りながら推進をします。",
    "産業\n伊豆・東部・中部・西部、それぞれの強みを活かした産業を育みます！",
    "子育て支援・教育\n将来の宝を全力で支えていきます！",
    "健康\nいつまでも健康で心豊かに暮らせる社会をつくります！",
    "防災\nこれまでの震災・風水害を教訓に、命を守る施策を強化します！",
    "環境\n将来世代にツケを残さないよう責任を果たします！",
    "観光・移住\n静岡県の魅力を存分に磨き、人を呼び込みます！",
    "多文化共生\n違いを認め合い、高め合える社会を構築します！",
    "行財政改革\n経営の観点を注ぎ込み、持続可能な静岡県をつくります！",
]

EXPECTED_POLICY_AREAS = [
    "transport_infrastructure",
    "industry_and_economy",
    "childcare_and_childrearing",
    "health_welfare_and_community",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "urban_development_and_tourism",
    "universal_city_and_inclusion",
    "fiscal_administrative_reform",
]

PROJECT = "jp-local-220001-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-002": [
        PROJECT.format("innovation-next-generation-industry"),
        PROJECT.format("sme-competitiveness-growth"),
    ],
    f"{TERM_ID}-promise-003": [PROJECT.format("child-centered-society")],
    f"{TERM_ID}-promise-004": [PROJECT.format("medical-care-health-longevity")],
    f"{TERM_ID}-promise-005": [PROJECT.format("disaster-prevention-mitigation")],
    f"{TERM_ID}-promise-006": [
        PROJECT.format("decarbonized-society"),
        PROJECT.format("circular-society"),
    ],
    f"{TERM_ID}-promise-007": [PROJECT.format("tourism-promotion")],
    f"{TERM_ID}-promise-008": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-009": [PROJECT.format("administrative-fiscal-reform")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# The Linear item is left unlinked because none of the ten
# stage-2 policy-pillar series covers the Linear / transport
# infrastructure theme -- see the record's extraction note.
UNLINKED_IDS = {f"{TERM_ID}-promise-001"}


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


def test_all_9_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 10)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-220001"
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


def test_no_numeric_content_was_invented() -> None:
    # None of the nine items states a numeric target, a deadline
    # or a funding method; nothing may be registered for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_achievements_slogan_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The closing banner (slogan).
        "幸福度日本一",
        # The speech-bubble line.
        "やれます",
        # The seven Hamamatsu City achievements (past record).
        "5,632億円",
        "4,317億円",
        "30人学級",
        "FSC森林認証",
        "343社",
        "154億円",
        "浜松市長在任中",
        # The profile and the QR-code guidance.
        "松下政経塾",
        "お読み取り下さい",
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
        for project in load_json("data/reviewed/shizuoka-prefecture/projects.json")
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
        # commission hosting, image-based panel transcribed from
        # renderings, no audio-readable data publication confirmed)
        # travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "音声読み上げ対応データ" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 9

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert BULLETIN_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 as a vacancy-election
    # construction: under the main text of Article 259 of the
    # Public Offices Election Act the term runs from the election
    # day itself for four years, and the expiry is also stated
    # verbatim on the commission's official term page; it is never
    # used as an implicit promise deadline.
    assert term["term_start"] == "2024-05-26"
    assert term["term_end"] == "2028-05-25"
