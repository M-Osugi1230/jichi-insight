"""Issue #938: Kyoto City mayor promises (cluster 12, stage 3).

The source is the official 2024 Kyoto City mayoral election
bulletin itself, which is still published on the city election
commission's current official site (the "過去の選挙公報" page
"令和6年2月4日執行京都市長選挙 選挙公報", posted 30 April 2024).
The PDF was downloaded again from that page on 2026-11-23 and
its SHA-256 matches the stage-0 download of 2026-11-22
(82c263c3015f312b74398cda52fa8217c9d0e6a2c6bae533ee9145385121c5,
1,730,228 bytes, 2 pages, five candidates, matching the city's
official results). Mayor Matsui's panel (page 1, lower left) is
a poster: the headline "突き抜ける『世界都市京都』をつくる" and
the slogan band "古きをいつくしみ、新しき世を切り拓く" above
his profile box (career history: born in Kyoto in 1960, Rakusei
junior/senior high school, University of Tokyo, MITI official,
two terms in the House of Councillors, Deputy Chief Cabinet
Secretary, Keio University professor), the vertical label
"松井こうじの市政改革5つの柱" over five pillars whose bulleted
items are the pledges (市民第一主義で人々から選ばれるまち京都
～子育て・教育環境の充実～ = 8 items, 突き抜ける魅力のある
文化首都・京都 = 10 items, 文化首都を支えるつよい経済の復活
京都を日本のシリコンバレーに = 7 items, すべての人に「居場所」
と「出番」のある京都 = 3 items, 全国に先駆ける京都型共生社会
モデルの形成 = 5 items), a disaster-prevention band
"いのちとくらしを守る防災・減災対策" (5 items) and an
endorsers' row. Each bullet stands as a policy statement on its
own, so the 38 records follow the Chiba City / Sendai /
Hiroshima City precedent of one record per item, registered in
the panel's visual reading order (the two left-column pillars,
the three right-column pillars, then the disaster band). The
pillar headings are topic labels, not verb-phrase commitments,
so they are kept in the source locations rather than
registered (the Hamamatsu precedent registered headings only
because they were verb phrases). The headline, the slogan, the
profile and the endorsers are framing or career history, not
promises; the panel presents no past achievements as pledges,
so zero records were excluded as achievements (the profile is
career presentation, not an achievement list). Two disaster
band items consist of a lead line plus detail lines and are
registered as single records carrying the full text. None of
the 38 items states a numeric target, a deadline or a funding
method, so all 38 are directional commitments with no target
registered. The bulletin is entirely image-based (a text
extraction of the whole PDF yields no characters), so the
texts were transcribed from 200/300 dpi renderings and
collated across resolutions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-261009-executive-2024-02-25"
BULLETIN_ID = "kyoto-city-mayor-election-2024-bulletin"
REVIEW_ID = "manifesto-review-jp-local-261009-2024"
SEARCH_ID = "manifesto-source-search-kyoto-city-2024"
BULLETIN_SHA256 = "82c263c3015f312b74398cda52fa8217c9d0e6a2c6bae533ee9145385121c5"

# The 38 bulleted items of Mayor Matsui's panel in the official
# 2024 election bulletin (page 1), transcribed verbatim in the
# panel's reading order. The headline, the slogan, the profile
# box and the endorsers' row are not records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "保育料の軽減",
    "子ども医療費の無償化",
    "全員制中学校給食を早期開始",
    "児童館やこども食堂のような「第三の居場所」を充実",
    "オンライン学習・教育データ活用など、デジタル教育の充実",
    "小中学校の普通教室、学校体育館の空調整備を計画的に推進",
    "教員不足の解消",
    "子育て世帯の定住を促進",
    "文化首都・京都にふさわしい「大京都圏」創出",
    "国際的音楽祭など音楽文化都市・京都の魅力向上",
    "国立文化財修理センターの市内への早期設置実現",
    "宿泊税を引き上げ、観光課題対策を強化",
    "観光ハイシーズンの休日に市民以外の方のマイカーでの市内乗り入れを抑制・制限",
    "市バス・市営地下鉄の市民優先価格",
    "バスの生活路線の混雑緩和",
    "京都駅の施設改善・機能強化による混雑緩和を国・事業者と連携して実現",
    "「市民の足」地域公共交通の維持・発展",
    "ごみのポイ捨て（不法投棄）の規制強化",
    "日本中、世界中の多彩な才能の移住・交流によるイノベーション、新産業の創出",
    "都市計画の見直しと連動した企業立地支援",
    "大学発ベンチャー・スタートアップの創出を加速",
    "複数住民票構想を研究し、国に提案",
    "学生の京都での就職・定着促進",
    "地域企業・中小企業の相談・支援体制を充実し経営基盤強化",
    "安心安全な市民生活、都市機能を支えるインフラ整備",
    "地域ぐるみで安心安全な生活を支える",
    "地域ぐるみで重層的な支援体制を構築",
    "市内の周辺部における都市計画規制を再考",
    "京都の文化・暮らしの脱炭素化",
    "人と自然の共生",
    "自然体験学習、文化体験学習の充実",
    "誰もが生きやすい多様性・包摂性のある共生社会",
    "高齢などでごみ出しが困難な方への支援を充実",
    (
        "安心安全な避難所環境の整備 "
        "プライバシーや更衣・授乳スペースを確保する間仕切りテント "
        "衛生的な段ボールベッド、災害用マンホールトイレなど"
    ),
    (
        "災害用備蓄物資の充実 "
        "食料・飲料水や毛布等の備蓄の確保に加え、"
        "水が不要な液体ミルク・ペーパー歯磨き、蓄電池など品目拡充"
    ),
    "水道管の耐震化を更に推進",
    "避難ルート、支援車両の通行確保のため、計画的な道路整備、橋りょうの耐震補強",
    "まちの匠の知恵を活かし、木造住宅や京町家の耐震化・防火改修を促進",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "education_and_human_development",
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "childcare_and_childrearing",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "environment_and_climate",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "transport_infrastructure",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "urban_development_and_tourism",
    "environment_and_climate",
    "environment_and_climate",
    "education_and_human_development",
    "universal_city_and_inclusion",
    "health_welfare_and_community",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
]

_PROJECT = "jp-local-261009-project-2025-"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-004": [_PROJECT + "civic-life-community"],
    f"{TERM_ID}-promise-010": [_PROJECT + "culture"],
    f"{TERM_ID}-promise-011": [_PROJECT + "culture"],
    f"{TERM_ID}-promise-012": [_PROJECT + "tourism"],
    f"{TERM_ID}-promise-018": [_PROJECT + "environment"],
    f"{TERM_ID}-promise-019": [_PROJECT + "industry-commerce"],
    f"{TERM_ID}-promise-020": [_PROJECT + "industry-commerce"],
    f"{TERM_ID}-promise-021": [_PROJECT + "universities"],
    f"{TERM_ID}-promise-023": [_PROJECT + "universities"],
    f"{TERM_ID}-promise-024": [_PROJECT + "industry-commerce"],
    f"{TERM_ID}-promise-026": [_PROJECT + "civic-life-community"],
    f"{TERM_ID}-promise-027": [_PROJECT + "civic-life-community"],
    f"{TERM_ID}-promise-029": [_PROJECT + "environment"],
    f"{TERM_ID}-promise-030": [_PROJECT + "environment"],
    f"{TERM_ID}-promise-031": [_PROJECT + "environment"],
    f"{TERM_ID}-promise-032": [_PROJECT + "human-rights-gender-equality"],
    f"{TERM_ID}-promise-033": [_PROJECT + "environment"],
    f"{TERM_ID}-promise-034": [_PROJECT + "civic-life-safety"],
    f"{TERM_ID}-promise-035": [_PROJECT + "civic-life-safety"],
    f"{TERM_ID}-promise-036": [_PROJECT + "civic-life-safety"],
    f"{TERM_ID}-promise-037": [_PROJECT + "civic-life-safety"],
    f"{TERM_ID}-promise-038": [_PROJECT + "civic-life-safety"],
}
# The remaining sixteen items have no stage-2 policy whose
# subject matches them (the ten registered policies carry no
# childcare, school-education, transport, metropolitan-area,
# migration-system or urban-planning policy), so they stay
# unlinked -- see the records' extraction notes.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}"
    for index in (1, 2, 3, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 22, 25, 28)
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


def test_all_38_items_registered_verbatim_in_panel_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 39)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-261009"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself
        # (the top of the source hierarchy), still live on the
        # election commission's current official site, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the 38 items states a numeric target, a deadline
    # or a funding method; nothing may be registered for them.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_framing_profile_and_endorsers_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The headline and the slogan (framing statements).
        "世界都市京都",
        "古きをいつくしみ",
        # The profile box (the candidate's career history).
        "1960年4月",
        "通商産業省",
        "内閣官房副長官",
        "慶應義塾大学",
        # The endorsers' row.
        "よろしくお願いします",
        "西脇隆俊",
        "門川大作",
        # The pillar headings are topic labels, kept in the
        # source locations, not registered as records.
        "市民第一主義で人々から選ばれるまち京都",
        "突き抜ける魅力のある文化首都・京都",
        "文化首都を支えるつよい経済の復活",
        "すべての人に「居場所」と「出番」のある京都",
        "全国に先駆ける京都型共生社会モデルの形成",
        "いのちとくらしを守る防災・減災対策",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    # No official evaluation tied to these promises themselves
    # has been published, so nothing is scored: every item
    # stays not_assessable, linked or not.
    for record in records():
        assert record["progress_state"] == "not_assessable"


def test_project_links_are_exact_bidirectional_and_capped() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids
    for record in items.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []

    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/kyoto-city/projects.json")
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
        # The bulletin provenance (official document, still live
        # on the current official site, re-downloaded and matched
        # by SHA-256 against the stage-0 copy, image-based panel
        # transcribed from renderings) travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert BULLETIN_SHA256 in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_bulletin_source_record_points_at_the_live_official_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.60.0"
    assert len(catalog["records"]) == 172
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "kyoto-city"
    assert bulletin["organization"].startswith("京都市選挙管理委員会")
    # The bulletin is still live on the election commission's
    # current official site; the registered URL is that live
    # PDF, and the notes record the re-download and the
    # SHA-256 match with the stage-0 copy.
    assert bulletin["url"] == (
        "https://www.city.kyoto.lg.jp/senkyo/cmsfiles/contents/"
        "0000326/326065/kouhou.pdf"
    )
    assert BULLETIN_SHA256 in bulletin["notes"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 38

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert BULLETIN_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]
    assert term["term_start"] == "2024-02-25"
    assert term["term_end"] == "2028-02-24"
