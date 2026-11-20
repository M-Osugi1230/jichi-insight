from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-141003-executive-2026-10-18"
BULLETIN_ID = "yokohama-city-mayor-election-2026-bulletin"

# The Harasawa Atsumi panel of the official October 2026 Yokohama
# mayoral vacancy-election bulletin (single newspaper-format page,
# middle left), transcribed verbatim from the rendered PDF image at
# 300dpi and 450dpi: the twelve items of the frame
# "横浜の未来をつくる12の政策", read down the left column (items
# 1-6) and then down the right column (items 7-12); the frame itself
# carries no numbering. Item 11 has no closing full stop in the
# original and is registered without one. The headline, the slogan,
# the catchphrase, the endorsing parties' band and the biography are
# not promise records. Any wording drift against the bulletin must
# fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "災害に強く、危機管理に優れた横浜をつくります。",
    "必要な人に、必要な支援が届く福祉を実現します。",
    "18区それぞれの個性を生かし、地域の活力を高めます。",
    "GREEN×EXPO 2027を契機に横浜の未来を切り拓きます。",
    "横浜を観光客が訪れるだけでなく楽しみ、過ごす「滞在型観光」の拠点にします。",
    "公正・適正な官民連携で、民間の力を最大限に生かします。",
    "道路・橋・上下水道など、暮らしを支えるインフラを守ります。",
    "子育て支援をさらに充実させ、子どもを安心して育てられる横浜をつくります。",
    "財政基盤を強化し、将来世代に責任を持つ市政を実現します。",
    "企業を呼び込み、横浜に働く場所と新たな雇用を生み出します。",
    "横浜の持つ豊富な基盤を活かし、横浜を世界に誇るエンタメ一大拠点にします",
    "市職員に笑顔を取り戻し、一丸となって市民のために働く市役所をつくります。",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "fiscal_administrative_reform",
    "transport_infrastructure",
    "childcare_and_childrearing",
    "fiscal_administrative_reform",
    "industry_and_economy",
    "urban_development_and_tourism",
    "fiscal_administrative_reform",
]

# Three items are linked to the stage-2 measure groups of the
# Yokohama City Medium-Term Plan 2026-2029 by wording and content
# only (no official mapping exists), so the link confidence is
# capped at low / inferred in the evidence packets.
EXPECTED_LINKS = {
    "jp-local-141003-executive-2026-10-18-promise-001": [
        "jp-local-141003-project-2026-earthquake-disaster-prevention"
    ],
    "jp-local-141003-executive-2026-10-18-promise-005": [
        "jp-local-141003-project-2026-tourism-mice"
    ],
    "jp-local-141003-executive-2026-10-18-promise-008": [
        "jp-local-141003-project-2026-childcare-support"
    ],
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
    assert term["person_name"] == "原澤 敦美"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2026-10-18"
    # Vacancy election: the previous mayor resigned on 2026-09-07, so
    # under the main text of Article 259 of the Public Offices
    # Election Act the term starts on the election day itself.
    assert term["term_start"] == "2026-10-18"
    # Four years from the start under Article 140 of the Local
    # Autonomy Act: the day before the fourth anniversary. The
    # Kanagawa election commission's term-expiry list still shows the
    # predecessor's expiry in its current edition (2026-08-03), so the
    # stated cross-check is pending the list's next update and is
    # recorded as an open question in the term's evidence packet.
    assert term["term_end"] == "2030-10-17"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_vote_count_was_collated_in_the_official_results_book() -> None:
    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == TERM_ID)
    election_claims = [
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    # 552,207 votes for Harasawa Atsumi, collated directly in the
    # city election commission's official results book PDF (final
    # candidate vote table), not from press coverage.
    assert "552,207" in election_claims[0]["statement"]
    assert "yokohama-city-mayor-election-2026-results" in (
        election_claims[0]["source_ids"]
    )
    # The pending term-expiry-list cross-check stays visible.
    assert any("任期満了一覧" in q for q in packet["open_questions"])


def test_all_12_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 13)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-141003"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution_is_all_directional() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    # Every item is a directional commitment without a numeric
    # target, deadline or funding statement; "18区" states the
    # city's ward count and "GREEN×EXPO 2027" is an event name, so
    # neither was promoted into a target or a deadline.
    for record in items:
        assert record["statement_type"] == "directional_commitment"
        assert record["assessability"] == "partially_assessable"
        assert record["controllability"] == "medium"
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["progress_state"] == "not_assessable"


def test_non_promise_panel_parts_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The headline, the catchphrase, the slogan, the endorsing
    # parties' band and the biography are not commitments by the
    # candidate, so none of their wording became a promise record.
    # The candidate was a newcomer, so the panel carries no
    # track-record block either.
    fragments = [
        "あなたの笑顔のために",
        "もっと前へ",
        "守る。育てる。支える",
        "自民党",
        "弁護士",
        "1967",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_capped_at_inferred() -> None:
    items = records()
    for record in items:
        assert record["related_project_ids"] == EXPECTED_LINKS.get(record["id"], [])

    projects = load_json("data/reviewed/yokohama-city/projects.json")
    by_id = {record["id"]: record for record in projects}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        for project_id in project_ids:
            assert by_id[project_id]["related_promise_ids"] == [promise_id]

    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        packet = packets[promise_id]
        link_claims = [
            claim
            for claim in packet["claims"]
            if claim["field"] == "related_project_ids"
        ]
        assert len(link_claims) == 1
        # Wording-based links are never asserted as established:
        # they stay at needs_review with the low / inferred cap.
        assert link_claims[0]["decision"] == "needs_review"
        assert "low" in link_claims[0]["review_note"]


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
        if record["id"] == "manifesto-review-jp-local-141003-2026"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 12
    # The reading order (left column, then right column) and the
    # exclusion of the headline, slogan, endorsement band and
    # biography are recorded in the review note.
    assert "左列" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "プロフィール" in review["review_note"]
