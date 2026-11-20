"""Issue #822: Saitama governor promises (cluster 6, stage 3).

The source is the official 2023 Saitama gubernatorial election
bulletin itself, downloaded directly from the election commission's
official result page. Governor Ono's panel (page 1, top) is a poster:
the headline slogan "守り抜く！ 県民の命 暮らし 未来", a left block
"4年間の実績（抜粋）" with seven achievement boxes and a speech
bubble, a right block "これからの政策（抜粋）" with four numbered
policy pillars and two bullet items under each (eight bullets), and
a profile strip along the bottom. The achievements, the slogan and
the profile are not promises. The four numbered pillars are
registered as records of their own: they are not mere headings over
the bullets -- pillar 1 carries the disaster-preparedness element
that no bullet states, and pillar 4 addresses "あらゆる人" beyond
its two bullets -- and the boundary judgement is preserved in the
review's open questions. The eight bullet items follow. No item
states a numeric target, deadline or funding; pillar 3's first
bullet states a "建替検討" (consideration of rebuilding), which is
registered as stated, never as a commitment to rebuild by a date.
The candidate panels are image-only (the PDF text layer holds only
the commission's boilerplate), so the texts were transcribed from
200/300 dpi renderings with collation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-110001-executive-2023-08-31"
BULLETIN_ID = "saitama-pref-governor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-110001-2023"
SEARCH_ID = "manifesto-source-search-saitama-pref-2023"

# The twelve promise items of Governor Ono's panel in the official
# 2023 election bulletin (page 1, top), transcribed verbatim in
# document order: the four numbered pillars of "これからの政策
# （抜粋）", each followed by its two bullet items. The headline
# slogan, the seven achievement boxes of "4年間の実績（抜粋）", the
# speech bubble and the profile are not records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "少子高齢化/災害の頻発・激甚化に対応可能な未来を見据えたまちづくり",
    "埼玉版スーパーシティ・プロジェクトの拡大で、少子高齢化社会に対応するまちづくり",
    "交通の利便性が高い埼玉県をもっと便利に",
    "持続的な発展に向けた戦略的転換",
    "埼玉版SDGs普及と共に環境と経済の両立（エネルギー・レジリエンス強化、サーキュラー・エコノミー推進）",
    "スタートアップ企業と技術を支援し、ニーズと適切にマッチング",
    "DXと行政改革を新たなフェーズへ",
    "県民サービスの向上と働き方改革に努め、DXを前提とした県庁及び地域機関の建替検討",
    "県内事業者のDX支援等を通じた働き方改革、生産性向上の推進",
    "あらゆる人が生き生きと活躍できる居場所と社会を",
    "地域医療の充実、安心と活気にあふれた高齢化社会を実現",
    "子どもたちの居場所や子育て家族を支援するネットワークを拡充",
]

EXPECTED_POLICY_AREAS = [
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "transport_infrastructure",
    "environment_and_climate",
    "environment_and_climate",
    "industry_and_economy",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "industry_and_economy",
    "universal_city_and_inclusion",
    "health_welfare_and_community",
    "childcare_and_childrearing",
]

PROJECT = "jp-local-110001-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [PROJECT.format("livable-community-development")],
    f"{TERM_ID}-promise-002": [PROJECT.format("livable-community-development")],
    f"{TERM_ID}-promise-009": [PROJECT.format("employment-support-environment")],
    f"{TERM_ID}-promise-011": [PROJECT.format("elderly-community-care")],
    f"{TERM_ID}-promise-012": [PROJECT.format("declining-birthrate-measures")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# Promises left unlinked because none of the ten stage-2 series
# covers them (transport, environment-economy balance, startups,
# DX/administrative reform, the office rebuilding study) or because
# the pillar is a framing statement whose concrete bullets are
# registered separately (pillars 2 and 4; pillar 3's first bullet is
# likewise unlinked, its second bullet is linked).
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in (3, 4, 5, 6, 7, 8, 10)
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


def test_all_12_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 13)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-110001"
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
        # The policy block states no numeric target, deadline or
        # funding. The "建替検討" wording is a stated consideration,
        # never supplemented into a deadline or a target.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_slogan_achievements_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    assert "守り抜く" not in " ".join(texts)
    for achievement_line in (
        "飲食店ステッカー",
        "豚熱対応ワクチン",
        "1000億円規模",
        "価格転嫁協定",
        "コピー使用量を半数以下",
        "県庁幹部女性割合を過去最高に",
        "日本一の子ども食堂ネットワーク",
        "日本をリードする埼玉発の施策",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("慶應義塾大学", "参議院議員", "拓殖大学大学院"):
        assert all(profile_line not in text for text in texts)


def test_pillars_carry_their_boundary_notes() -> None:
    items = {record["id"]: record for record in records()}
    # The four numbered pillars are the panel's top-level pledges,
    # registered as records of their own; the notes record both the
    # boundary judgement and, for the rebuilding bullet, that a stated
    # consideration is not a dated commitment.
    for index in (1, 4, 7, 10):
        note = items[f"{TERM_ID}-promise-{index:03d}"]["extraction_note"] or ""
        assert "独立レコード" in note or "政策の柱" in note
    rebuilding = items[f"{TERM_ID}-promise-008"]["extraction_note"] or ""
    assert "建替検討" in rebuilding
    assert "期限の約束ではない" in rebuilding


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
        for project in load_json("data/reviewed/saitama-prefecture/projects.json")
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
    assert review["promise_records_created"] == 12

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 from the Saitama City
    # election commission's official result table (both dates stated
    # day-exact) and the prefectural term-expiry list; it is still
    # never used as an implicit promise deadline.
    assert term["term_start"] == "2023-08-31"
    assert term["term_end"] == "2027-08-30"
