"""Issue #772: Osaka governor promises (cluster 4, stage 3).

The source is the official bulletin of the February 2026 Osaka
gubernatorial re-election (a resignation-triggered election), downloaded
directly from the prefectural election commission's official page.
Governor Yoshimura's panel (the top band of the single large-format
sheet) is a poster that mixes an achievements presentation with the
outlook: an opening statement, a left banner, a "維新には実績がある"
block (an Expo arrow unit, three achievement boxes and a
self-sacrifice-reform strip), a "維新には展望がある" block (two
headings with five triangle-marked items), a large slogan headline, a
logo, a photo and a career profile.

Seven records are created: the opening statement's metropolitan-plan
commitment, the Expo arrow unit (whose lead clause states future
growth and whose second bullet states the super-city acceleration),
and the five outlook items. The remaining achievement units are not
promises as presented and are not registered; their verbatim texts
are preserved in the manifesto review evidence packet. The term is
the one registered in stage 1 (2023-04-09 to 2027-04-08): the 2026
re-election does not start a new term, and the term end is never used
as a promise deadline. The 2023 bulletin is also reachable from the
official site (confirmed in the stage-0 inventory) but is not the
registered source; that fact is recorded in the evidence packets.

The stage-2 priority projects live on their own branch (PR #769), so
the reverse links from projects.json cannot be asserted here; only
the promise-side links are pinned.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-270008-executive-2023-04-09"
BULLETIN_ID = "osaka-pref-governor-election-2026-bulletin"
REVIEW_ID = "manifesto-review-jp-local-270008-2026"
SEARCH_ID = "manifesto-source-search-osaka-pref-2026"

# The seven registered units of Governor Yoshimura's panel, in
# document order: the opening statement, the Expo arrow unit of the
# achievements block, the three items under "日本の経済成長を
# 大阪がけん引！" and the two items under "首都機能をバックアップ！".
# Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "副首都にふさわしい都構想を実現することこそ、大阪の成長、そして日本の成長に不可欠だと考えています。",
    "「大阪・関西万博」を起点に大阪は大きく成長します。運営費は最大で約370億円の黒字見込み。"
    "経済波及効果約3.6兆円（経済産業省）。AIやビッグデータなど先端技術を活用した"
    "未来都市「大阪スーパーシティ構想」が加速",
    "地方分権をさらに促進させ、経済基盤を強化",
    "規制緩和による事業の高度化・生産性向上",
    "人材育成・確保や子育て環境整備を進める拠点へ",
    "災害等の発生時に首都中枢機能を代替できるよう、首都機能の一部を移転",
    "東京一極集中から段階的に多極型の日本社会へ移行",
]

EXPECTED_POLICY_AREAS = [
    "fiscal_administrative_reform",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "education_and_human_development",
    "safety_and_disaster_prevention",
    "fiscal_administrative_reform",
]

EXPECTED_STATEMENT_TYPES = [
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "vision",
]

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-002": [
        "jp-local-270008-project-2026-cutting-edge-technology-implementation"
    ],
    f"{TERM_ID}-promise-005": ["jp-local-270008-project-2026-growth-industry-talent"],
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


def test_all_7_units_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 8)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-270008"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from the
        # prefecture's official site, so the record-level grading is
        # high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_statement_type_and_policy_area_distribution() -> None:
    items = records()
    assert [record["statement_type"] for record in items] == EXPECTED_STATEMENT_TYPES
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_target_was_invented_from_the_text() -> None:
    items = records()
    for record in items:
        # No promise unit states a numeric target, deadline or funding.
        # The figures in the achievements block (最大770万円以上 of
        # burden reduction, 1.5兆円以上 of debt reduction) present the
        # party's record, and the Expo figures inside record 002
        # (約370億円の黒字見込み, 約3.6兆円の経済波及効果) are factual
        # presentations about the completed Expo; none of them is
        # supplemented into the structured fields.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_achievement_units_slogan_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    # The slogan headline and the banner are not records (the banner's
    # commitment is registered through the opening statement instead).
    assert "府市一体で大阪を日本のエンジンに！" not in texts
    assert "副首都・大阪 「都構想」へ挑戦" not in texts
    assert all("One Osaka" not in text for text in texts)
    # The achievement boxes and the self-sacrifice strip are presented
    # as the party's record and are not registered as promises.
    for achievement_line in (
        "教育・子育て負担の軽減",
        "介護保険料を下げ",
        "1.5兆円以上削減",
        "109人▶79人",
        "議員報酬3割カット継続中",
        "知事退職金制度の廃止",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("昭和50年", "司法試験合格", "大阪市長当選"):
        assert all(profile_line not in text for text in texts)


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


def test_project_links_are_capped_at_inferred() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids
    for record in items.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []

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
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 7
    # The borderline calls travel with the review: the achievements
    # block is excluded, with the two continuing/future-leaning units
    # named explicitly.
    assert "健活10プロジェクト" in review["review_note"]
    assert "3割カット継続中" in review["review_note"]

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False
    # The 2023 bulletin is reachable but deliberately not the
    # registered source; the choice is recorded, not hidden.
    assert "2023年" in search["review_note"]

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term is the 2023-started term registered in stage 1; the
    # 2026 re-election created no second term and its end is never
    # used as an implicit promise deadline.
    assert term["term_start"] == "2023-04-09"
    assert term["term_end"] == "2027-04-08"
    osaka_terms = [t for t in terms if t["municipality_id"] == "jp-local-270008"]
    assert len(osaka_terms) == 1


def test_bulletin_source_record_points_at_the_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    # The catalog has since grown: the Kanagawa cluster's stage 3
    # (Issue #798) appended the Kanagawa bulletin record, the
    # Yokohama City records and the five Kawasaki City records,
    # bringing the combined catalog to version 0.22.0 / 71 records;
    # the Saitama cluster's stage 1 (Issue #815) then appended the
    # four Saitama Prefecture governor records, bringing it to
    # version 0.23.0 / 75 records; the Saitama cluster's stage 3
    # (Issue #822) then appended the Saitama bulletin record, the
    # five Kawaguchi City records and the three Saitama City mayor
    # records, bringing it to version 0.26.0 / 84 records; the Chiba
    # cluster's stage 1 (Issue #835) then appended the four Chiba
    # Prefecture governor records, bringing it to version 0.27.0 /
    # 88 records; the Chiba cluster's stage 3 (Issue #842) then
    # appended the Chiba Prefecture bulletin record and the five
    # Chiba City mayor records, bringing it to
    # version 0.28.0 / 94 records; the Hyogo cluster's stage 1
    # (Issue #854) then appended the two Hyogo Prefecture governor
    # records, bringing it to version 0.29.0 / 96 records; the
    # Hyogo cluster's stage 3 (Issue #862) then appended the
    # Hyogo Prefecture bulletin record and the four Kobe City
    # mayor records, bringing it to
    # version 0.31.0 / 101 records; the Miyagi cluster's stage 1
    # (Issue #874) then appended the three Miyagi Prefecture governor
    # records and the four Sendai City mayor records, bringing it to
    # version 0.33.0 / 108 records; the Miyagi cluster's stage 3
    # (Issue #881) then appended the Miyagi Prefecture bulletin
    # record and its audio-readable data record and the Sendai City
    # mayor bulletin record, bringing it to
    # version 0.35.0 / 111 records; the Shizuoka cluster's stage 1
    # (Issue #891) then appended the three Shizuoka Prefecture
    # governor records, the four Hamamatsu City mayor records and
    # the three Shizuoka City mayor records across parallel stage-1
    # branches, bringing the combined catalog to
    # version 0.38.0 / 121 records; the Shizuoka cluster's stage 3
    # (Issue #900) then appended the Shizuoka Prefecture bulletin
    # record, the Hamamatsu City mayor election bulletin record
    # and the Shizuoka City bulletin record across parallel
    # stage-3 branches, bringing the combined catalog to
    # version 0.41.0 / 124 records; the Hiroshima cluster's stage 1
    # (Issue #915) then appended the three Hiroshima Prefecture
    # governor records and the three Hiroshima City mayor records
    # across parallel stage-1 branches, bringing the combined
    # catalog to version 0.43.0 / 130 records; the Hiroshima
    # cluster's stage 3 (Issue #921) then appended the Hiroshima
    # Prefecture governor election bulletin record and the
    # Hiroshima City mayor election bulletin record across
    # parallel branches, bringing the combined
    # catalog to version 0.45.0 / 132 records; the Kyoto cluster's
    # stage 1 (Issue #932) then appended the three Kyoto City mayor
    # records and the five Kyoto Prefecture governor records,
    # bringing the combined catalog to version 0.47.0 / 140 records;
    # stage 3 (Issue #938) then appended the Kyoto Prefecture
    # governor election bulletin manuscript record and the Kyoto
    # City mayor election bulletin record, bringing the combined
    # catalog to version 0.49.0 / 142 records; the Niigata cluster's
    # stage 1 (Issue #952) then appended the three Niigata City
    # mayor records and the Okayama cluster's stage 1 (Issue #954)
    # appended the five Okayama Prefecture governor records,
    # bringing the combined catalog to version 0.51.0 / 150 records.
    assert catalog["version"] == "0.51.0"
    assert len(catalog["records"]) == 150
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["url"].endswith("chijisenkyokoho.pdf")
    assert bulletin["municipality_key"] == "osaka-prefecture"
