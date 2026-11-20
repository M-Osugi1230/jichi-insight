"""Issue #798: Kanagawa governor promises (cluster 5, stage 3).

The source is the official 2023 Kanagawa gubernatorial election
bulletin itself, downloaded directly from the election commission's
official page. Governor Kuroiwa's panel (page 1, middle) is a poster:
the headline "県民目線のデジタル行政で やさしい社会を実現！", a box
"黒岩県政4期目〔3つの実現!!〕" with three top-level pledges, a
"黒岩流県政 = 5つのチカラ" grid presenting the candidate's governing
style and track record, the centre column "黒岩祐治 4期目の新たな挑戦"
with five policy fields and six bullet items each (thirty items), and
a right column with the third-term achievements (including the UN
"The Healthy Ageing 50" selection) and a career profile. The three
"3つの実現" pledges are registered as records of their own: they are
not summaries of the bullet items but the panel's top-level pledges
with content of their own (the boundary judgement is preserved in
the review's open questions). The thirty bullet items follow. The
headline slogan, the "5つのチカラ" grid, the achievements and the
profile are not promises. No item states a numeric target, deadline
or funding; the "ゼロ" phrasings are stated end-states without a
deadline or measurement method, so no target is supplemented.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-140007-executive-2023-04-23"
BULLETIN_ID = "kanagawa-pref-governor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-140007-2023"
SEARCH_ID = "manifesto-source-search-kanagawa-pref-2023"

# The thirty-three promise items of Governor Kuroiwa's panel in the
# official 2023 election bulletin (page 1, middle), transcribed
# verbatim in document order: the three "3つの実現" pledges first,
# then the five policy fields of "4期目の新たな挑戦" with six bullet
# items each. The headline slogan, the "5つのチカラ" grid, the
# achievements and the career profile are not records. Any wording
# drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "デジタル革命（DX）推進（申請ゼロ・窓口行くことゼロ）",
    "県民目線・障害当事者目線で共生社会を実現",
    "万全の危機管理対応能力で想定外の被害ゼロを実現",
    "「子育てパーソナルサポート」で子育てをデジタル支援",
    "ネットかけこみ寺で、いじめ対策",
    "生活困窮・虐待の子ども対策",
    "医療的ケア児・リトルベビーへの徹底支援",
    "基金創設で少子化対策の充実・強化",
    "パパママ目線で子育て環境の充実",
    "デジタル防災で水害時逃げ遅れゼロ",
    "AI技術で道路の消えかけ白線ゼロ",
    "サイバー攻撃へのセキュリティ対策強化",
    "防犯カメラの設置促進",
    "大規模災害時のトイレ対策プロジェクト",
    "水防災戦略で水害対策強化",
    "中小企業等に必要なデジタル人材の育成",
    "特区発ロボット・デジタルで産業基盤強化",
    "宇宙関連産業クラスターの形成強化",
    "ポストコロナのインバウンド観光強化",
    "脱炭素社会を強力推進",
    "市町村と連携し移住・定住促進",
    "当事者目線の障害福祉の実現",
    "筋電義手の最先県を目指す",
    "ジェンダー主流化の推進",
    "合唱・芸術の力で、いのち輝く100歳時代",
    "メタバースで、ひきこもりのデジタル支援",
    "犬猫殺処分ゼロ継続で、ペットのいのちも輝く神奈川",
    "デジタル活用で全県民の未病改善推進",
    "認知症・未病改善プロジェクト全県展開",
    "介護を科学する神奈川モデル",
    "医療・看護・介護の人材確保",
    "新たな感染症への万全の備え",
    "ヘルスケア・ニューフロンティア政策の更なる推進",
]

EXPECTED_POLICY_AREAS = [
    "fiscal_administrative_reform",
    "universal_city_and_inclusion",
    "safety_and_disaster_prevention",
    "childcare_and_childrearing",
    "education_and_human_development",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "safety_and_disaster_prevention",
    "transport_infrastructure",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "environment_and_climate",
    "urban_development_and_tourism",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_safety",
    "health_welfare_and_community",
]

PROJECT = "jp-local-140007-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-002": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-003": [PROJECT.format("crisis-management")],
    f"{TERM_ID}-promise-004": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-005": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-006": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-007": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-008": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-009": [PROJECT.format("children-and-youth")],
    f"{TERM_ID}-promise-010": [PROJECT.format("crisis-management")],
    f"{TERM_ID}-promise-011": [PROJECT.format("urban-infrastructure")],
    f"{TERM_ID}-promise-013": [PROJECT.format("everyday-life-safety")],
    f"{TERM_ID}-promise-014": [PROJECT.format("crisis-management")],
    f"{TERM_ID}-promise-015": [PROJECT.format("crisis-management")],
    f"{TERM_ID}-promise-016": [PROJECT.format("economy-and-employment")],
    f"{TERM_ID}-promise-017": [PROJECT.format("economy-and-employment")],
    f"{TERM_ID}-promise-018": [PROJECT.format("economy-and-employment")],
    f"{TERM_ID}-promise-022": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-023": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-024": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-025": [PROJECT.format("mebyo-health-longevity")],
    f"{TERM_ID}-promise-026": [PROJECT.format("livelihood-support")],
    f"{TERM_ID}-promise-028": [PROJECT.format("mebyo-health-longevity")],
    f"{TERM_ID}-promise-029": [PROJECT.format("mebyo-health-longevity")],
    f"{TERM_ID}-promise-030": [PROJECT.format("mebyo-health-longevity")],
    f"{TERM_ID}-promise-031": [PROJECT.format("mebyo-health-longevity")],
    f"{TERM_ID}-promise-032": [PROJECT.format("crisis-management")],
    f"{TERM_ID}-promise-033": [PROJECT.format("mebyo-health-longevity")],
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


def test_all_33_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 34)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-140007"
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
        # deadline or funding. The "ゼロ" phrasings (申請ゼロ,
        # 逃げ遅れゼロ, 被害ゼロ, 消えかけ白線ゼロ, 殺処分ゼロ継続)
        # are stated end-states without a deadline or measurement
        # method in the bulletin, and are never supplemented into the
        # structured fields.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_headline_achievements_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    assert "やさしい社会を実現！" not in texts
    assert "県民目線のデジタル行政で" not in texts
    for style_line in ("徹底力", "発信力", "決断力", "先進力", "突破力"):
        assert all(style_line not in text for text in texts)
    for achievement_line in (
        "世界の50人に選ばれる",
        "The Healthy Ageing 50",
        "コロナ対策で国をリード",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("早稲田大学", "昭和29年生まれ", "フジテレビジョン"):
        assert all(profile_line not in text for text in texts)


def test_headline_pledges_carry_their_boundary_notes() -> None:
    items = {record["id"]: record for record in records()}
    # The three "3つの実現" pledges are the panel's top-level pledges,
    # registered as records of their own; the notes record both the
    # end-state wording (never promoted into target) and the thematic
    # overlap with the bullet groups.
    assert "target には登録していない" in items[f"{TERM_ID}-promise-001"]["extraction_note"]
    assert "二重計上には当たらない" in (
        items[f"{TERM_ID}-promise-002"]["extraction_note"] or ""
    ) or "最上位の公約" in (items[f"{TERM_ID}-promise-002"]["extraction_note"] or "")
    assert "ゼロ継続" in (items[f"{TERM_ID}-promise-027"]["extraction_note"] or "") or (
        "継続の公約" in (items[f"{TERM_ID}-promise-027"]["extraction_note"] or "")
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
        for project in load_json("data/reviewed/kanagawa-prefecture/projects.json")
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
    assert review["promise_records_created"] == 33

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term end is registered from the official term-expiry list in
    # stage 1; it is still never used as an implicit promise deadline.
    assert term["term_end"] == "2027-04-22"
