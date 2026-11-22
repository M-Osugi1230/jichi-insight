"""Issue #900: Shizuoka City mayor promises (cluster 10, stage 3).

The source is the official 2023 Shizuoka City mayoral election
bulletin itself. During the election period the bulletin PDF was
published on the city's official site (000973077.pdf, linked from
the city's election page as the mayoral election bulletin), but
the current site carries no path to it and the URL returns 404,
so the registered copy is the Wayback Machine capture of the
city's official URL (29 March 2023); the captures of 27 March,
29 March and 9 April 2023 (election day) share one Wayback digest
and the downloaded files share one SHA-256, so the archived copy
is the bulletin as published. Mayor Nanba's panel (page 1) is a
poster: the headline "市政の変革で『難しい』を『できる』に変えます！"
above three numbered items, each a heading plus a body sentence
(1 現場主義, 2 開かれたわかりやすい市政, 3 信頼と共創の市政), his
profile box (career history: Shizuoka Prefecture vice-governor,
MLIT official and similar posts) below, and his photograph, name
and the slogan "現場主義" set vertically at the right. Because
each heading does not stand as a pledge on its own, the three
records follow the Fukuoka City / Miyagi / Shizuoka Prefecture
precedent of heading-plus-body records (the heading and the body
joined by a newline); the boundary judgement is preserved in the
review's open questions. The headline is a slogan-like framing
statement for the three items as a whole and is not a record;
the profile is the candidate's career history, not a promise,
and the panel carries no numbered achievements list. None of
the three items states a numeric target, a deadline or a funding
method, so all three are directional commitments with no target
registered. The bulletin is entirely image-based (a text
extraction of the whole PDF yields zero characters), so the
texts were transcribed from 200/300 dpi renderings and collated
across resolutions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-221007-executive-2023-04-13"
BULLETIN_ID = "shizuoka-city-mayor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-221007-2023"
SEARCH_ID = "manifesto-source-search-shizuoka-city-2023"

# The three numbered items of Mayor Nanba's panel in the official
# 2023 election bulletin (page 1), transcribed verbatim in
# document order as heading-plus-body records. The headline, the
# profile box and the vertical name/slogan are not records. Any
# wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "現場主義\n一つひとつの現場の現実を直視し、課題の解決方法をとことん考え抜き、実行し、結果を出します。",
    "開かれたわかりやすい市政\nデータや政策決定根拠を社会にわかりやすく公開し、対話することで、それならいいね！と共感を得て進める市政にします。",
    "信頼と共創の市政\n市民と市政が相互信頼のもと「社会の大きな力がつながる」×「世界の大きな知が集まりつながる」×「市政が下支えし伴走する」ことで、みんなで一緒に「安心感がある温かい社会」を共働、共創する市政にします。",
]

EXPECTED_POLICY_AREAS = [
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
]

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-003": [
        "jp-local-221007-project-2026-citizen-activity-support"
    ],
}
# The field-first principle and the open-government principle are
# statements about how the administration itself works; none of
# the ten stage-2 measure series takes them as its subject, so
# they stay unlinked -- see the records' extraction notes.
UNLINKED_IDS = {f"{TERM_ID}-promise-001", f"{TERM_ID}-promise-002"}


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


def test_all_3_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 4)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-221007"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the
        # top of the source hierarchy); the registered copy is the
        # archived copy of the city's official election-period URL,
        # digest-matched across three captures, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the three items states a numeric target, a deadline
    # or a funding method; nothing may be registered for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_headline_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The headline (slogan-like framing for the whole panel).
        "市政の変革で",
        "変えます",
        # The profile box (the candidate's career history).
        "昭和31年生まれ",
        "静岡県副知事",
        "国土交通省",
        "博士（工学）",
        "難波喬司プロフィール",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    # No official evaluation of the linked measure has been
    # published, so nothing is scored: every item stays
    # not_assessable, linked or not.
    for record in records():
        assert record["progress_state"] == "not_assessable"


def test_project_links_are_exact_bidirectional_and_capped() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids
    for record in items.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []

    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/shizuoka-city/projects.json")
    }
    for promise_id, project_ids in EXPECTED_LINKS.items():
        for project_id in project_ids:
            assert promise_id in projects[project_id]["related_promise_ids"]
    linked_promise_ids = {
        promise_id
        for project in projects.values()
        for promise_id in project["related_promise_ids"]
    }
    assert linked_promise_ids == set(EXPECTED_LINKS)

    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        claims = {claim["field"]: claim for claim in packets[promise_id]["claims"]}
        link_claim = claims["related_project_ids"]
        assert link_claim["decision"] == "needs_review"
        assert "low / inferred" in link_claim["review_note"]


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
        # The bulletin provenance (official document, the city's
        # official URL deleted from the current site, the archived
        # copy digest-matched across captures, image-based panel
        # transcribed from renderings) travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "Wayback" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_bulletin_source_record_points_at_the_archived_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.50.0"
    assert len(catalog["records"]) == 147
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "shizuoka-city"
    assert bulletin["organization"].startswith("静岡市選挙管理委員会")
    # The live official URL is deleted (404); the registered URL is
    # the Wayback capture of that same official URL, and the notes
    # record the digest match across the three election-period
    # captures.
    assert bulletin["url"] == (
        "https://web.archive.org/web/20230329084240/"
        "https://www.city.shizuoka.lg.jp/000973077.pdf"
    )
    assert "ダイジェスト" in bulletin["notes"]
    assert "DZNM3S4ZQGC4UR55TI2F6I42C2TCR6HQ" in bulletin["notes"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 3

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
    assert BULLETIN_ID in term["sources"]
    assert term["term_start"] == "2023-04-13"
    assert term["term_end"] == "2027-04-12"
