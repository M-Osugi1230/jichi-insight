"""Issue #842: Chiba governor promises (cluster 7, stage 3).

The source is the official 2025 Chiba gubernatorial election
bulletin itself, downloaded directly from the election commission's
official result page. Governor Kumagai's panel (page 1, middle) is a
poster: the headline slogan "県民を守り、支え、そして飛躍する千葉
へ", a right block headed "県民の命とくらしを守る" with an
introductory paragraph and a "4年の主な成果" box listing five
first-term achievements, a left/centre block "県政ビジョン 次の4年
に向けて" with eight numbered policy pillars and their diamond
bullets (3+2+3+3+2+1+1+2 = 17 bullets), a strip pointing to the
candidate's official homepage, and a profile strip. The
achievements, the slogan, the introduction and the profile are not
promises. The eight numbered pillars are registered as records of
their own: they are not mere headings over the bullets -- pillar 1
also covers crime prevention, which no bullet states, and pillar
4's heading states the Narita Airport industrial-hub ambition --
and the boundary judgement is preserved in the review's open
questions. Pillar 4's heading also references a first-term
achievement (the record business-attraction count); the heading is
registered for its forward-looking statement, never for the
achievement mention. The only numeric target in the panel is the
"洋式化100%" for prefectural school toilets, registered as the
record's target. The candidate panels are image-only (a text
extraction of the PDF yields two non-space characters), so the
texts were transcribed from 150/300 dpi renderings with collation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-120006-executive-2025-04-05"
BULLETIN_ID = "chiba-pref-governor-election-2025-bulletin"
REVIEW_ID = "manifesto-review-jp-local-120006-2025"
SEARCH_ID = "manifesto-source-search-chiba-pref-2025"

# The twenty-five promise items of Governor Kumagai's panel in the
# official 2025 election bulletin (page 1, middle), transcribed
# verbatim in document order: the eight numbered pillars of "県政
# ビジョン 次の4年に向けて", each followed by its diamond bullets.
# The headline slogan, the introduction, the five achievements of
# "4年の主な成果", the homepage strip and the profile are not
# records. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "災害や犯罪等から県民を守る",
    "水道や下水道の更新・耐震化、河川の整備、無電柱化などを推進し、「防災県・千葉」を確立",
    "女性・障害者・高齢者などに配慮した災害時の支援",
    "闇バイト、トクリュウ対策など、防犯対策を大幅に強化",
    "超高齢化時代に対応した医療・福祉の充実",
    "住み慣れた場所で安心して医療・介護が受けられる千葉県づくり",
    "県立保健医療大学の充実など、千葉県の医療を支える医療・福祉人材の育成を強化",
    "子育て世代の知事として子育て支援・教育の充実",
    "保育・学童保育の環境整備と質の向上を進め、子育て世帯を支援",
    "県立学校のトイレ改修・洋式化100%、避難所となる体育館へのエアコン設置を推進",
    "いじめ・不登校への対策強化。教員の負担軽減をさらに進める",
    "過去最高の企業誘致数のその先へ。成田空港を核とした産業拠点を",
    "将来の県経済を支えるエリアを各地に創出し、さらなる企業誘致・投資の呼び込みを図る",
    "成田空港を核とした、アジアと競う産業拠点づくりと住環境整備で広域を活性化",
    "中小企業への支援を強化し、賃上げが持続的に行える環境を整備",
    "半島性を克服する交通インフラの充実",
    "渋滞緩和や災害時の支援のため、県内各地を結ぶ道路ネットワークを整備",
    "市町村と連携し、地域に必要なバス路線を維持",
    "農業・漁業の振興",
    "一次産業に従事する方々の所得向上、担い手確保、有機農業の推進",
    "多様性を尊重する千葉県へ",
    "男女共同参画、障害者施策の充実など、多様な人々が活躍できる千葉県へ",
    "現実主義で行政の縦割りを超え、効率的で筋肉質の行政組織へ",
    "現場主義を貫くとともに、県民や若者との対話を拡大し、身近な県政の実現へ",
    "行財政改革とデジタル化をさらに進め、県民の利便性を向上",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "industry_and_economy",
    "industry_and_economy",
    "universal_city_and_inclusion",
    "universal_city_and_inclusion",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
]

PROJECT = "jp-local-120006-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        PROJECT.format("disaster-response-strengthening"),
        PROJECT.format("disaster-resilient-community-development"),
    ],
    f"{TERM_ID}-promise-002": [
        PROJECT.format("disaster-resilient-community-development")
    ],
    f"{TERM_ID}-promise-003": [PROJECT.format("disaster-response-strengthening")],
    f"{TERM_ID}-promise-005": [PROJECT.format("growing-medical-demand")],
    f"{TERM_ID}-promise-006": [PROJECT.format("growing-medical-demand")],
    f"{TERM_ID}-promise-008": [PROJECT.format("childrearing-environment")],
    f"{TERM_ID}-promise-009": [PROJECT.format("childrearing-environment")],
    f"{TERM_ID}-promise-012": [
        PROJECT.format("new-industry-and-business-attraction")
    ],
    f"{TERM_ID}-promise-013": [
        PROJECT.format("new-industry-and-business-attraction")
    ],
    f"{TERM_ID}-promise-014": [
        PROJECT.format("new-industry-and-business-attraction")
    ],
    f"{TERM_ID}-promise-015": [PROJECT.format("core-industry-promotion")],
    f"{TERM_ID}-promise-021": [PROJECT.format("diversity-inclusive-society")],
    f"{TERM_ID}-promise-022": [PROJECT.format("diversity-inclusive-society")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# Promises left unlinked because none of the ten stage-2 series
# covers them (crime prevention, medical/welfare workforce
# development, school facilities, bullying and non-attendance,
# transport infrastructure, agriculture and fisheries,
# administrative reform) -- see each record's extraction note.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-{index:03d}"
    for index in (4, 7, 10, 11, 16, 17, 18, 19, 20, 23, 24, 25)
}
PILLAR_IDS = {
    f"{TERM_ID}-promise-{index:03d}" for index in (1, 5, 8, 12, 16, 19, 21, 23)
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


def test_all_25_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 26)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-120006"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
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


def test_only_the_stated_numeric_target_was_registered() -> None:
    items = {record["id"]: record for record in records()}
    toilet = items[f"{TERM_ID}-promise-010"]
    # The panel's only numeric target is the 100% western-style
    # conversion of prefectural school toilets; it is registered as
    # stated, and the record is the panel's only specific commitment.
    assert toilet["statement_type"] == "specific_commitment"
    assert toilet["target"] == "県立学校のトイレの洋式化100%"
    for record in items.values():
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        if record["id"] != f"{TERM_ID}-promise-010":
            assert record["statement_type"] == "directional_commitment"
            assert record["target"] is None


def test_slogan_achievements_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    assert "飛躍する千葉へ" not in " ".join(texts)
    assert "県民の命とくらしを守る" not in " ".join(texts)
    for achievement_line in (
        "対策本部を設置",
        "企業立地件数を記録",
        "物価高騰対策のための補正予算を編成し",
        "教育予算を1.5倍",
        "54市町村すべてを訪問",
    ):
        assert all(achievement_line not in text for text in texts)
    for profile_line in ("早稲田大学政治経済学部", "NTTコミュニケーションズ", "1978年2月18日"):
        assert all(profile_line not in text for text in texts)


def test_pillars_carry_their_boundary_notes() -> None:
    items = {record["id"]: record for record in records()}
    # The eight numbered pillars are the panel's top-level pledges,
    # registered as records of their own; the notes record the
    # boundary judgement.
    for promise_id in PILLAR_IDS:
        note = items[promise_id]["extraction_note"] or ""
        assert "独立レコード" in note
    # Pillar 4's heading references a first-term achievement; the
    # note records that the achievement mention itself was not
    # registered as a promise.
    pillar4 = items[f"{TERM_ID}-promise-012"]["extraction_note"] or ""
    assert "過去最高の企業誘致数" in pillar4
    assert "実績の言及そのものは公約化していない" in pillar4


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
        for project in load_json("data/reviewed/chiba-prefecture/projects.json")
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
    assert review["promise_records_created"] == 25

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 from the election
    # commission's statement that the previous term expired on
    # 2025-04-04 (Article 259 construction) and the Kashiwa City
    # commission's day-exact term-expiry list; it is still never used
    # as an implicit promise deadline.
    assert term["term_start"] == "2025-04-05"
    assert term["term_end"] == "2029-04-04"
