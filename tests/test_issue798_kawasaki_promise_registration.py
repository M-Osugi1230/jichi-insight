from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-141305-executive-2025-11-19"
BULLETIN_ID = "kawasaki-city-mayor-election-2025-bulletin"

# The Fukuda Norihiko panel of the 26 October 2025 Kawasaki mayoral
# election bulletin, as reprinted in Chapter 8 (3) of the city
# election commission's official election record (record page 90,
# lower left): twelve policy boxes in a two-column grid plus the
# "special city" block below the grid, transcribed verbatim from the
# rendered PDF image at multiple resolutions. Numbering follows the
# documented convention: left column top to bottom (001-006), right
# column top to bottom (007-012), then the special-city block (013).
# The headline slogan, the biography, the pointer to the candidate's
# website and the campaign-method statement are not promise records.
# Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "来年9月から小児医療費助成18歳まで拡大、負担金ゼロに",
    "「卓越スクール（高専）」の設立を企業との共創で目指す",
    "朝、始業前の学校内で安心の居場所をスタート",
    "要介護度の改善全国の2倍を達成!さらなる高みへ",
    "再エネの地産地消ごみ発電、家庭&学校発電",
    "「市内の住み替え支援」と「子育て支援住宅」を推進",
    "デマンド交通や自動運転の活用で市民の足を守る",
    "学校体育館の冷房設置とマンホールトイレで災害にも強く",
    "プラスチックの100%市内リサイクルを実現",
    "徒歩圏内で完結する安心の“ケア付き地域”へ",
    "等々力の再整備でスポーツ・健康、みどりの聖地に",
    "川崎臨海部が次の100年を創る新産業の拠点に",
    "「特別市」の実現に全力を尽くします！",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "health_welfare_and_community",
    "environment_and_climate",
    "childcare_and_childrearing",
    "transport_infrastructure",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "health_welfare_and_community",
    "urban_development_and_tourism",
    "industry_and_economy",
    "fiscal_administrative_reform",
]

EXPECTED_STATEMENT_TYPES = [
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
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
    assert term["person_name"] == "福田 紀彦"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2025-10-26"
    # The start follows the Article 259 proviso chain: the previous
    # term's expiry (2025-11-18) is stated in the election
    # commission's schedule announcement for this term-expiry
    # election, and the incumbent served until that expiry.
    assert term["term_start"] == "2025-11-19"
    # The expiry is stated directly in the city election commission's
    # official list of terms of public offices (2029-11-18).
    assert term["term_end"] == "2029-11-18"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_13_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 14)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-141305"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (as
        # reprinted in the official election record), so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    # Only the two items that state a concrete content carry a target:
    # the child medical subsidy expansion (item 001) and the 100%
    # in-city plastic recycling (item 009). The "2x" figure in item
    # 004 belongs to the candidate's track-record claim, not to a
    # target, so it is not registered as one.
    for index, record in enumerate(items, start=1):
        if index in (1, 9):
            assert record["target"] is not None
        else:
            assert record["target"] is None
        # The panel states no day-level deadline and no funding for
        # any item ("next September" in item 001 is month-level and
        # is recorded in the extraction note, not as a date).
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_non_promise_elements_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The headline slogan, the biography, the pointer to more detail
    # on the website and the campaign-method statement (no loud
    # campaign cars) are not commitments for the term, so none of
    # them became a promise record.
    for fragment in ["実行する", "ご覧ください", "選挙カー", "プロフィール"]:
        assert not any(fragment in text for text in texts)


def test_project_links_are_limited_to_two_inferred_matches() -> None:
    items = {record["id"]: record for record in records()}
    renewable = items[f"{TERM_ID}-promise-005"]
    disaster = items[f"{TERM_ID}-promise-008"]
    # The renewable-energy project itself describes local production
    # and consumption of surplus solar power from homes and schools,
    # and the community disaster-prevention project covers shelter
    # environment improvement (school gymnasiums are designated
    # shelters, and manhole toilets are shelter equipment). Both
    # links are inferred from wording and content, not from an
    # official mapping, and their packets cap the confidence at
    # low / inferred.
    assert renewable["related_project_ids"] == [
        "jp-local-141305-project-2026-renewable-energy-promotion"
    ]
    assert disaster["related_project_ids"] == [
        "jp-local-141305-project-2026-community-disaster-prevention"
    ]
    assert renewable["progress_state"] == "in_progress"
    assert disaster["progress_state"] == "in_progress"
    for record in items.values():
        if record["id"] not in (renewable["id"], disaster["id"]):
            assert record["related_project_ids"] == []
            assert record["progress_state"] == "not_assessable"


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
        # The reprint provenance is stated, not hidden: the bulletin
        # survives as a reprint in the official election record.
        assert "再録" in provenance["statement"]
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_mixed_track_record_box_is_flagged() -> None:
    packet = packets_by_subject()[f"{TERM_ID}-promise-004"]
    boundary = next(
        claim for claim in packet["claims"] if claim["field"] == "statement_boundary"
    )
    # The first half of the box is the candidate's own track-record
    # claim and the second half a forward-looking direction; the
    # packet records that mixture explicitly.
    assert "実績" in boundary["statement"]
    assert "未検証" in boundary["statement"]


def test_manifesto_review_records_the_segmentation() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        record
        for record in reviews
        if record["id"] == "manifesto-review-jp-local-141305-2025"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 13
    # The numbering convention and the elements that were not
    # itemised are recorded in the review note.
    assert "左列" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "再録" in review["review_note"]


def test_source_search_registered_the_reprint() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-kawasaki-city-2025"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    assert "再録" in search["review_note"]
