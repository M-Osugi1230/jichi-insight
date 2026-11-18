from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-400009-executive-2025-04-14"
BULLETIN_ID = "fukuoka-pref-governor-election-2025-bulletin"
REVIEW_ID = "manifesto-review-jp-local-400009-2025"

# The nine numbered items of "これからの未来を見据え 3つの挑戦" in
# Governor Hattori's panel of the official 2025 election bulletin
# (page 1, lower half), transcribed verbatim in document order:
# challenge 1 items 1-3, challenge 2 items 1-3, challenge 3 items 1-3.
# The challenge headings themselves are not records (kept as the
# policy_area grouping and in source_location), and the panel's
# "主な実績" achievements, profile and party endorsements are not
# promises. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "「こども」の教育環境を充実",
    "「若者」の挑戦を応援",
    "「女性・高齢者」をはじめ「すべての人」の活躍を応援",
    "県経済の原動力「中小企業」を応援",
    "成長の起爆剤となる「スタートアップ」の育成",
    "基幹産業「農林水産業」を稼ぐ産業へ",
    "人の命・健康を守る「ワンヘルス」の取組みを推進",
    "「子育て世帯」の応援及び「生活困難者」を支援",
    "「防災・減災」対策の強化",
]

EXPECTED_POLICY_AREAS = [
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "health_welfare_and_safety",
    "health_welfare_and_safety",
    "health_welfare_and_safety",
]

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-001",
    f"{TERM_ID}-promise-002",
    f"{TERM_ID}-promise-003",
    f"{TERM_ID}-promise-004",
    f"{TERM_ID}-promise-007",
    f"{TERM_ID}-promise-008",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        "jp-local-400009-project-2025-mirai-kodomo-challenge",
    ],
    f"{TERM_ID}-promise-002": [
        "jp-local-400009-project-2025-youth-international-exchange",
        "jp-local-400009-project-2025-technology-talent",
    ],
    f"{TERM_ID}-promise-003": [
        "jp-local-400009-project-2025-work-style-improvement",
        "jp-local-400009-project-2025-single-parent-employment-support",
    ],
    f"{TERM_ID}-promise-004": [
        "jp-local-400009-project-2025-work-style-improvement",
    ],
    f"{TERM_ID}-promise-007": [
        "jp-local-400009-project-2025-infectious-disease-prevention",
    ],
    f"{TERM_ID}-promise-008": [
        "jp-local-400009-project-2025-single-parent-employment-support",
        "jp-local-400009-project-2025-male-childcare-leave",
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


def test_all_9_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 10)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-400009"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["statement_type"] == "directional_commitment"
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_challenge_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_target_was_invented_from_the_text() -> None:
    items = records()
    for record in items:
        # The bulletin panel states no numeric target, deadline or
        # funding for these items. The concrete measures reported for
        # the 2025-03-03 policy announcement (gym air-conditioning,
        # new crop varieties, the One Health Center) come from news
        # summaries and are not supplemented into the records.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_achievements_were_not_registered_as_promises() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    # The same panel's "主な実績" (first-term achievements) uses similar
    # wording; none of those achievement lines may appear as promises.
    for achievement in (
        "学校教育を充実",
        "中小企業を振興",
        "ワンヘルスを推進",
        "若者のチャレンジを応援",
        "新型コロナから県民を守る",
    ):
        assert achievement not in texts


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {
        record["id"] for record in items if record["progress_state"] == "in_progress"
    }
    assert in_progress == IN_PROGRESS_IDS
    for record in items:
        if record["id"] not in IN_PROGRESS_IDS:
            # Unassessed is never converted into "not started" or a score.
            assert record["progress_state"] == "not_assessable"
            assert record["related_project_ids"] == []
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
        for project in load_json("data/reviewed/fukuoka-prefecture/projects.json")
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
        progress_claim = claims["progress_state"]
        assert progress_claim["decision"] == "needs_review"


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
        # The bulletin provenance (official document, hosted copy,
        # image-based panel) travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 9

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-fukuoka-pref-2025"
    )
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term end is registered from the prefecture's official
    # term-expiry list; it is still never used as an implicit promise
    # deadline.
    assert term["term_end"] == "2029-04-10"
