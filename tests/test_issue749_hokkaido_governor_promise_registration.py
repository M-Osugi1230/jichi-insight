"""Issue #749: Hokkaido governor promises (cluster 3, stage 3).

The source is the official 2023 Hokkaido gubernatorial election
bulletin itself, downloaded directly from the election commission's
official page. Governor Suzuki's panel (page 1, upper half) is a
poster: the heading "鈴木直道の主な基本政策" with three pillars and
fifteen bullet-marked policy items, a "3つのキーワード" circle
diagram (seven circles) restating the same policies, a first-term
achievements column, a career profile, a slogan and a resolve text.
The fifteen bullet items are the promise units; the circles are not
separately recorded (their texts are preserved in the corresponding
records' extraction notes), and the achievements, profile, slogan
and resolve text are not promises. No item states a numeric target,
deadline or funding in the policy part of the panel.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-010006-executive-2023-04-23"
BULLETIN_ID = "hokkaido-pref-governor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-010006-2023"
SEARCH_ID = "manifesto-source-search-hokkaido-pref-2023"

# The fifteen bullet items of Governor Suzuki's panel in the official
# 2023 election bulletin (page 1, upper half), transcribed verbatim in
# document order: pillar "地域とともにすすめる" (2), pillar
# "北海道の未来をつくる" (6), pillar "道民の暮らしをまもる" (7).
# The heading, the slogan ("暮らしをまもり、未来をつくる"), the
# resolve text, the first-term achievements and the career profile
# are not records. Any wording drift against the bulletin must fail
# here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "「ほっかいどう応援団会議」の発展",
    "チャレンジする道庁づくり",
    "ゼロカーボン北海道の推進",
    "DX・デジタル化の推進",
    "食と観光",
    "アイヌ文化振興",
    "教育・人材育成強化",
    "北方領土問題の解決に向けた取り組み",
    "経済活性化",
    "子ども・女性支援の強化",
    "医療・福祉の充実",
    "感染症対策・防災",
    "農林水産業の持続的発展",
    "交通・物流政策の推進",
    "食料安全保障をリード",
]

EXPECTED_POLICY_AREAS = [
    "industry_and_economy",
    "fiscal_administrative_reform",
    "environment_and_climate",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "education_and_human_development",
    "international_engagement",
    "industry_and_economy",
    "childcare_and_childrearing",
    "health_welfare_and_community",
    "safety_and_disaster_prevention",
    "industry_and_economy",
    "transport_infrastructure",
    "industry_and_economy",
]

PROJECT = "jp-local-010006-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [PROJECT.format("regional-revitalization")],
    f"{TERM_ID}-promise-003": [PROJECT.format("global-warming-countermeasures")],
    f"{TERM_ID}-promise-004": [PROJECT.format("digital-company-clustering")],
    f"{TERM_ID}-promise-005": [PROJECT.format("visitor-attraction")],
    f"{TERM_ID}-promise-007": [PROJECT.format("competency-education")],
    f"{TERM_ID}-promise-010": [PROJECT.format("marriage-childbirth-support")],
    f"{TERM_ID}-promise-011": [PROJECT.format("regional-healthcare")],
    f"{TERM_ID}-promise-013": [PROJECT.format("agricultural-rural-infrastructure")],
    f"{TERM_ID}-promise-015": [PROJECT.format("agricultural-rural-infrastructure")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)


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


def test_all_15_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 16)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-010006"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["statement_type"] == "directional_commitment"
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from the
        # prefecture's official site, so the record-level grading is
        # high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_target_was_invented_from_the_text() -> None:
    items = records()
    for record in items:
        # The policy part of the panel states no numeric target,
        # deadline or funding. The figures in the left column
        # (1376億円 of emergency economic measures, the 1500億円
        # food-export target already achieved, the 5兆円 investment
        # outlook) describe the first term's record, not promises,
        # and are never supplemented into the structured fields.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_heading_slogan_achievements_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    assert "暮らしをまもり、未来をつくる" not in texts
    assert "直向きに、北海道を前へ。" not in texts
    for achievement_line in (
        "ふるさと納税3年連続日本一達成",
        "首都圏からの本社機能移転増加数全国1位",
        "半導体工場の誘致に成功",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("夕張市長", "法政大学法学部", "昭和56年生まれ"):
        assert all(profile_line not in text for text in texts)


def test_keyword_circles_are_preserved_in_extraction_notes() -> None:
    items = {record["id"]: record for record in records()}
    # The seven keyword circles restate the same policy package as a
    # diagram; they are not separate records, but their texts travel
    # with the corresponding bullet records.
    assert "ほっかいどう応援団 第二章" in items[f"{TERM_ID}-promise-001"]["extraction_note"]
    assert "次世代半導体、データセンターなど" in items[f"{TERM_ID}-promise-004"]["extraction_note"]
    assert (
        "アドベンチャートラベルでアジアをリード"
        in items[f"{TERM_ID}-promise-005"]["extraction_note"]
    )
    assert "輸入依存穀物の国産化" in items[f"{TERM_ID}-promise-015"]["extraction_note"]
    for record in items.values():
        assert "二重計上を避けるため" in (record["extraction_note"] or "") or (
            "3つのキーワード" not in (record["extraction_note"] or "")
        )


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {record["id"] for record in items if record["progress_state"] == "in_progress"}
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
        for project in load_json("data/reviewed/hokkaido-prefecture/projects.json")
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
        # The bulletin provenance (official document, direct official
        # hosting, image-based panel) travels with every item.
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
    assert review["promise_records_created"] == 15

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term end is registered from the statutory chain documented
    # in stage 1; it is still never used as an implicit promise
    # deadline.
    assert term["term_end"] == "2027-04-22"
