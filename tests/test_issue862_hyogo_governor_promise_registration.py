"""Issue #862: Hyogo governor promises (cluster 8, stage 3).

The source is the official 2024 Hyogo gubernatorial election
bulletin itself, preserved on the Kobe City election commission's
official page (the same document the prefectural commission issued).
Governor Saito's panel (page 3, top) is a poster: a top strip
stating that four policies were set as pillars based on the previous
promises and three years of work, the headline slogan "兵庫の躍動を
止めない！" with a counter for the previous term's promises
(171 of 173 items achieved or in progress), a left grey box headed
"既得権益やしがらみから脱し県民本位の県政へ" with four
check-marked items and, beneath it, a bar chart of the fiscal fund
balance at the end of FY2023 (over 12.7 billion yen), the "4つの
政策" block with four numbered policies and their bullet items
(4+3+3+4 = 14 bullets), and a profile strip with a QR code. The
grey box's check-marked items sit directly above the fund-balance
chart (actual past values) and read together with it as a display
of the first term's actions and record, so -- like the achievements
boxes of earlier clusters -- they are not registered as promises;
the boundary judgement is preserved in the review's open questions.
The slogan, the previous-term counter, the chart and the profile
are not promises either. The four numbered policies are registered
as records of their own: they are the panel's stated pillars, not
mere headings over the bullets, and the boundary judgement is
preserved in the review's open questions. Two bullets state numeric
targets -- "毎年100人" for the high-school challenge study-abroad
programme and "200億円規模" for the fiscal fund -- and both are
registered as targets with specific commitments. The "約1,500億円"
in the hidden-debt bullet is the stated scale of the problem (a
premise), not a target, and is not registered as one. Each policy's
last bullet ends with "等" in print; the character is transcribed
as printed. The candidate panels are image-only (a text extraction
of the whole PDF yields 2,180 non-space characters, all of them the
commission's printed frame text; no text is extracted from the
candidate panels), so the texts were transcribed from 100/300 dpi
renderings with collation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-280003-executive-2024-11-17"
BULLETIN_ID = "hyogo-pref-governor-election-2024-bulletin"
REVIEW_ID = "manifesto-review-jp-local-280003-2024"
SEARCH_ID = "manifesto-source-search-hyogo-pref-2024"

# The eighteen promise items of Governor Saito's panel in the
# official 2024 election bulletin (page 3, top), transcribed
# verbatim in document order: the four numbered policies of
# "4つの政策", each followed by its bullet items. The headline
# slogan, the previous-term promise counter, the left grey box
# (four check-marked first-term items and the fiscal fund chart),
# the QR code strip and the profile are not records. Any wording
# drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "未来を担う若者が輝く兵庫",
    "兵庫県立大学の授業料等無償化",
    "兵庫県立高校の環境整備",
    "毎年100人高校生のチャレンジ留学",
    "不妊治療支援特化条例の制定 等",
    "誰もが活躍できる兵庫",
    "フィールドパビリオンによる国際交流",
    "女性経営者等への子育てサポートの充実",
    "有機農業推進条例の制定 等",
    "安全安心に暮らせる兵庫",
    "特殊詐欺被害対策課の創設",
    "阪神淡路大震災30年をふまえた災害対応力の強化",
    "AIカメラを活用した客引き防止対策 等",
    "県政改革等が進む兵庫",
    "コンパクトな県庁舎再整備",
    "県の貯金（財政基金）を200億円規模に",
    "約1,500億円の隠れ借金問題への対処",
    "海外事務所の更なる見直し 等",
]

EXPECTED_POLICY_AREAS = [
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "international_engagement",
    "childcare_and_childrearing",
    "industry_and_economy",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
]

PROJECT = "jp-local-280003-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        PROJECT.format("next-generation-education"),
        PROJECT.format("educational-environment"),
    ],
    f"{TERM_ID}-promise-002": [PROJECT.format("next-generation-education")],
    f"{TERM_ID}-promise-003": [PROJECT.format("educational-environment")],
    f"{TERM_ID}-promise-004": [PROJECT.format("next-generation-education")],
    f"{TERM_ID}-promise-005": [PROJECT.format("marriage-support")],
    f"{TERM_ID}-promise-009": [PROJECT.format("local-industry-development")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# Promises left unlinked because none of the ten stage-2 series
# covers them (international exchange through the field pavilion,
# childcare support for business owners, crime prevention and
# disaster response, prefectural administrative and fiscal reform)
# -- see each record's extraction note.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}"
    for index in (6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18)
}
PILLAR_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in (1, 6, 10, 14)
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


def test_all_18_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 19)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-280003"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from a public
        # election commission's official site, so the record-level
        # grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_only_the_stated_numeric_targets_were_registered() -> None:
    items = {record["id"]: record for record in records()}
    study_abroad = items[f"{TERM_ID}-promise-004"]
    # "毎年100人" is a stated numeric target and is registered as
    # stated; the record is a specific commitment.
    assert study_abroad["statement_type"] == "specific_commitment"
    assert study_abroad["target"] == "毎年100人の高校生のチャレンジ留学"
    fund = items[f"{TERM_ID}-promise-016"]
    # "200億円規模" for the fiscal fund is the panel's other stated
    # numeric target.
    assert fund["statement_type"] == "specific_commitment"
    assert fund["target"] == "県の貯金（財政基金）を200億円規模に"
    hidden_debt = items[f"{TERM_ID}-promise-017"]
    # "約1,500億円" states the scale of the problem to be dealt
    # with (a premise), not an achievement target.
    assert hidden_debt["statement_type"] == "directional_commitment"
    assert hidden_debt["target"] is None
    for record in items.values():
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        if record["id"] not in {f"{TERM_ID}-promise-004", f"{TERM_ID}-promise-016"}:
            assert record["statement_type"] == "directional_commitment"
            assert record["target"] is None


def test_slogan_achievements_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    assert "躍動を止めない" not in " ".join(texts)
    # The left grey box's four check-marked items are presented with
    # the fiscal fund chart as the first term's actions and record.
    for achievement_line in (
        "自分の給料等を見直し",
        "ハコモノの見直し",
        "制度の見直し",
        "見える化の徹底",
        "171項目",
        "127億円",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("須磨区", "愛光学園", "東京大学経済学部", "総務省"):
        assert all(profile_line not in text for text in texts)


def test_pillars_carry_their_boundary_notes() -> None:
    items = {record["id"]: record for record in records()}
    # The four numbered policies are the panel's top-level pledges,
    # registered as records of their own; the notes record the
    # boundary judgement.
    for promise_id in PILLAR_IDS:
        note = items[promise_id]["extraction_note"] or ""
        assert "独立レコード" in note
    # The fund promise's note records that the charted FY2023-end
    # balance in the panel is a first-term record display and was
    # not registered as the promise's baseline.
    fund = items[f"{TERM_ID}-promise-016"]["extraction_note"] or ""
    assert "127億円超は1期目の実績表示" in fund
    assert "baseline には登録していない" in fund


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
        for project in load_json("data/reviewed/hyogo-prefecture/projects.json")
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
        # commission hosting, image-based panel) travels with every
        # item.
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
    assert review["promise_records_created"] == 18

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 as a vacancy-election
    # construction: the governor lost office on 2024-09-30 after a
    # unanimous no-confidence motion, so under the main text of
    # Article 259 the term runs four years from the election day
    # itself; it is never used as an implicit promise deadline.
    assert term["term_start"] == "2024-11-17"
    assert term["term_end"] == "2028-11-16"
