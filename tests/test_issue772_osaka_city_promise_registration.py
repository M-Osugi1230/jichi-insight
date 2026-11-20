from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-271004-executive-2026-02-09"
BULLETIN_ID = "osaka-city-mayor-election-2026-bulletin"

# The Yokoyama Hideyuki panel of the official February 2026 Osaka
# mayoral snap-election bulletin (page 1, middle right), transcribed
# verbatim from the rendered PDF image: the five items of the outlook
# frame "維新には展望がある" (two boxes: three items under "日本の
# 経済成長を大阪がけん引！", two under "首都機能をバックアップ！"),
# in document order. The headline, the slogan, the box titles, the
# biography and the three track-record items of the "維新には実績が
# ある" frame are not promise records. Any wording drift against the
# bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "地方分権をさらに促進させ、経済基盤を強化",
    "規制緩和による事業の高度化・生産性向上",
    "人材育成・確保や子育て環境整備を進める拠点へ",
    "災害等の発生時に首都中枢機能を代替できるよう、首都機能の一部を移転",
    "東京一極集中から段階的に多極型の日本社会へ移行",
]

EXPECTED_POLICY_AREAS = [
    "industry_and_economy",
    "industry_and_economy",
    "education_and_human_development",
    "safety_and_disaster_prevention",
    "urban_development_and_tourism",
]

EXPECTED_STATEMENT_TYPES = [
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "vision",
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
    assert term["person_name"] == "横山 英幸"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2026-02-08"
    # The start is stated directly in the city's official list of past
    # mayors ("令和8年2月9日～" for the 22nd mayor's current term).
    assert term["term_start"] == "2026-02-09"
    # The expiry is stated directly in the city election commission's
    # list of upcoming elections. This is a residual term: the mayor
    # resigned and was re-elected in a snap election, and the term was
    # not reset, so the end is the 2023 cycle's expiry (2027-04-08),
    # not the start plus four years.
    assert term["term_end"] == "2027-04-08"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_5_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 6)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-271004"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution_and_vision_boundary() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    # The four directional items stay partially assessable; the fifth
    # item states a transformation of Japanese society as a whole, so
    # it is a vision and is not assessable.
    for record in items[:4]:
        assert record["assessability"] == "partially_assessable"
    vision = items[4]
    assert vision["assessability"] == "not_assessable"
    assert vision["controllability"] == "not_assessable"


def test_no_targets_or_deadlines_were_supplemented() -> None:
    items = records()
    for record in items:
        # The panel states no numeric target, deadline or funding for
        # any item, so nothing was filled in.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_track_record_frame_is_not_registered_as_promises() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    # The "維新には実績がある" frame presents the party's track
    # record (Expo surplus outlook, childcare burden reduction, seat
    # cuts and the mayoral retirement allowance), not commitments for
    # the coming term, so none of it became a promise record; the same
    # applies to the headline and the slogan.
    for fragment in ["370億円", "770万円", "退職金", "都構想", "エンジン"]:
        assert not any(fragment in text for text in texts)


def test_no_project_links_are_asserted() -> None:
    items = records()
    # Stage 2 registered the Future City Creation Strategy measures,
    # but no official mapping between the bulletin items and those
    # measures exists, so no link is asserted and every progress
    # state stays not_assessable.
    for record in items:
        assert record["related_project_ids"] == []
        assert record["progress_state"] == "not_assessable"

    projects = load_json("data/reviewed/osaka-city/projects.json")
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
        # The official-bulletin provenance and the high grading travel
        # with every item.
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_manifesto_review_records_the_segmentation() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        record
        for record in reviews
        if record["id"] == "manifesto-review-jp-local-271004-2026"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 5
    # The track-record frame was deliberately not itemised, and the
    # headline, slogan and biography were not itemised either.
    assert "実績" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "プロフィール" in review["review_note"]
