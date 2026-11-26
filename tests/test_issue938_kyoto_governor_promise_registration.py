"""Issue #938: Kyoto governor promises (cluster 12, stage 3).

The source is the candidate-submitted election-bulletin
manuscript that the Kyoto Prefectural Election Commission
publishes on its official candidate-information page ("京都府
知事選挙・京都府議会議員補欠選挙 候補者情報（選挙公報）（音声
読み上げ用）", updated 2026-03-28). The PDF is the manuscript
sheet itself ("京都府知事選挙公報掲載文原稿用紙（電子データ
入稿用）", one page, 1,903,102 bytes, SHA-256
ae07590608f2e5b6083e3fb022f1a6c0fd40cc2cfaf80044ddd148d73f69b360):
the whole page is Governor Nishiwaki's panel. It is a poster:
the slogan "わくわくする京都" with three pillar ovals （安心・
はぐくみ・輝き） at the top, each pillar carrying an overall
statement plus headings and bullet items (headings 3/3/4, ten
in total; bullets 4/5/7, sixteen in total), a band heading
"基盤整備 地域や暮らしを支える基盤づくり" with a profile
(career history) and a supporters box below, the candidate's
name in large vertical type with the shoulder title "京都府
知事" on the right edge, and an empty photo frame (the sheet
is the manuscript, so the frame holds only an instruction).
Because each overall statement completes a sentence stating
the pillar's goal and each heading states a future goal as a
verb phrase -- neither is a mere label for the items below --
the twenty-nine records follow the Hyogo numbered-policy /
Hiroshima heading precedent: overall statements, headings and
bullet items are registered as separate records in document
order. The band heading has no items under it and states no
goal sentence, so it is not a record. The panel has no
achievements section presenting past results as items (the
governor is an incumbent seeking a third term, but the profile
is a career history, not a set of achievement claims), so no
achievement items were excluded and none were registered. The
slogan, the pillar names, the band heading, the profile, the
supporters box, the QR code, the shoulder title and the photo
frame are not promises either. None of the twenty-nine items
states a numeric target, a deadline or a funding method, so
all twenty-nine are directional commitments. The manuscript
carries a text layer, so the texts were transcribed visually
from 200/300 dpi renderings and collated against the extracted
text layer for every item (full agreement). No combined
printed-bulletin (image) PDF publication could be confirmed
on the commission's election information page or in search;
the search record does not claim it does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-260002"
TERM_ID = "jp-local-260002-executive-2026-04-16"
BULLETIN_ID = "kyoto-pref-governor-election-2026-bulletin"
REVIEW_ID = "manifesto-review-jp-local-260002-2026"
SEARCH_ID = "manifesto-source-search-kyoto-pref-2026"

# The three overall statements, ten headings and sixteen bullet
# items of Governor Nishiwaki's panel in the official 2026
# election bulletin manuscript (single page), transcribed
# verbatim in document order: for each pillar, the overall
# statement first, then each heading followed by its bullet
# items in printed order. The bullet markers and the pillar
# ovals are layout elements and are not part of the texts. The
# slogan, the band heading, the profile, the supporters box,
# the QR code, the shoulder title and the photo frame are not
# records. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "あらゆる危機に備え、住み慣れた地域で、これからも暮らし続けることができる、府民の皆様が「安心できる京都」を目指します",
    "府民生活や事業活動を守る",
    "府民を災害・犯罪から守る",
    "全国トップレベルの危機管理体制の構築",
    "地域の治安向上と防犯力の強化",
    "健やかに暮らせる社会を創る",
    "新たな地域包括ケア体制の構築",
    "地域で支え合う社会の実現",
    "子どもからお年寄りまで、誰もが役割を持って活躍できるよう、府民の皆様が「はぐくまれる京都」を目指します",
    "若者・現役世代に選ばれる京都づくり",
    "「子育て環境日本一・京都」の深化",
    "京都に住まい、働く希望を支援",
    "結婚・出産の願いを社会全体で後押しする",
    "次世代に引き継ぐ価値をはぐくむ",
    "世界に羽ばたき、京都の未来を拓く「人財」を育成する",
    "京都の豊かな自然環境を未来につなぐ",
    "外国人との共生社会を推進",
    "連綿と受け継がれてきた多彩な魅力にあふれる「輝く京都」を目指します",
    "世界に輝く京都産業の創造",
    "中小企業の経営基盤づくり",
    "京都産業創造プロジェクトの展開",
    "豊かな恵みをもたらす農林水産業の活性化",
    "文化が息づく京都を磨く",
    "唯一無二の魅力を国内外に発信",
    "京都文化を未来につなぐ",
    "地域に活力を生み出す交流・連携の推進",
    "結びつきから生まれる賑わいと価値づくり",
    "サステナブル北京都構想の推進",
    "エリア構想の推進",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "industry_and_economy",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "universal_city_and_inclusion",
    "childcare_and_childrearing",
    "universal_city_and_inclusion",
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "environment_and_climate",
    "universal_city_and_inclusion",
    "urban_development_and_tourism",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "city_image_and_public_relations",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
]

PROJECT = "jp-local-260002-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-006": [PROJECT.format("health-medical-longevity")],
    f"{TERM_ID}-promise-007": [PROJECT.format("care-welfare")],
    f"{TERM_ID}-promise-008": [PROJECT.format("community-bonds")],
    f"{TERM_ID}-promise-009": [PROJECT.format("all-genders-participation")],
    f"{TERM_ID}-promise-010": [PROJECT.format("hopeful-childrearing")],
    f"{TERM_ID}-promise-011": [PROJECT.format("hopeful-childrearing")],
    f"{TERM_ID}-promise-013": [PROJECT.format("hopeful-childrearing")],
    f"{TERM_ID}-promise-014": [PROJECT.format("dream-education")],
    f"{TERM_ID}-promise-015": [PROJECT.format("dream-education")],
    f"{TERM_ID}-promise-017": [PROJECT.format("foreign-residents-vibrant")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# The remaining nineteen items have no corresponding series
# among the ten stage-2 field policies (which cover welfare and
# daily-life fields only; industry, disaster prevention,
# culture, environment and regional-promotion series are not
# among them), and the two pillar overall statements span their
# whole pillars -- see the records' extraction notes.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in range(1, 30)
} - IN_PROGRESS_IDS


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


def test_all_29_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 30)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == MUNICIPALITY_ID
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the candidate-submitted bulletin manuscript
        # itself (the top of the source hierarchy), obtained directly
        # from the prefectural election commission's official page,
        # so the record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["source_location"].startswith(
            "選挙公報（候補者提出原稿・全1ページ）"
        )


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the twenty-nine items states a numeric target, a
    # deadline or a funding method; nothing may be registered
    # for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["assessability"] == "partially_assessable"
        assert record["controllability"] == "medium"


def test_slogan_profile_and_band_heading_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The slogan headline.
        "わくわくする京都",
        # The band heading and its subtitle.
        "地域や暮らしを支える基盤づくり",
        # The profile (career history).
        "洛星高等学校卒業",
        "東京大学法学部卒業",
        "建設省採用",
        "復興庁事務次官",
        "第51代京都府知事",
        # The supporters box.
        "私たちも応援しています",
    ):
        assert all(non_promise_line not in text for text in texts)


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
        for project in load_json("data/reviewed/kyoto-prefecture/projects.json")
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
        # The bulletin provenance (candidate-submitted manuscript
        # itself, official commission hosting, audio-readable data
        # carrying a text layer collated against the renderings)
        # travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "音声読み上げ" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "西脇 隆俊"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 29

    review_packets = load_json(
        "data/entities/executives/manifesto_review_evidence_packets.json"
    )
    review_packet = next(
        packet for packet in review_packets if packet["subject_id"] == REVIEW_ID
    )
    assert_valid("schemas/evidence_packet.schema.json", review_packet)
    assert review_packet["open_questions"]

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert BULLETIN_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False

    search_packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    search_packet = next(
        packet for packet in search_packets if packet["subject_id"] == SEARCH_ID
    )
    assert_valid("schemas/evidence_packet.schema.json", search_packet)

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1: the start is the day
    # after the previous term's expiry in the commission's
    # official term list and the expiry is stated verbatim in
    # the same list; it is never used as an implicit promise
    # deadline.
    assert term["term_start"] == "2026-04-16"
    assert term["term_end"] == "2030-04-15"


def test_bulletin_source_record_points_at_the_official_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.62.0"
    assert len(catalog["records"]) == 178
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "kyoto-prefecture"
    assert bulletin["organization"] == "京都府選挙管理委員会"
    assert bulletin["url"].endswith("r8tijiniwakitakatoshi.pdf")
    assert bulletin["availability"] == "published"
