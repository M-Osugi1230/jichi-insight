"""Issue #1034: Fukushima governor promises (cluster 16, stage 3).

The source is the official 2026 Fukushima gubernatorial election
bulletin itself (four pages), published on the prefectural
election commission's current candidate-information page and
registered in stage 1 (6,977,745 bytes, SHA-256
50243021adc356bb3bfcd6d64434c8901bf2f627719b6e930f502d7acc947da9).
Governor Uchibori's panel (page 2, middle band) is a poster: the
headline "やさしさ、すこやかさ、おいしさあふれる ふくしまを共に
創り、つなぐ", the vertical slogan "みんなで創る ふくしまの未来。",
a prose resolve statement headed "私の決意", the candidate's name
with his photo, a career-history column (主な略歴), a vertical
theme band ("震災・原子力災害からの復興と人口減少対策への挑戦。"
and "「ふくしまプライド。」で一歩、二歩、前へ！"), and three
pillar boxes (ひと / 暮らし / しごと). Each pillar carries a title
statement plus numbered headings (ひと 1-2, 暮らし 3-4, しごと
5-8), and each heading carries three bullet items (24 in total).
Because each pillar title completes a verb phrase stating the
pillar's goal and each numbered heading states a future goal --
neither is a mere label for the items below -- the thirty-five
records follow the Kyoto pillar-statement / Hyogo numbered-policy
precedent: pillar titles, headings and bullet items are registered
as separate records in the panel's numbered document order (the
printing places the しごと box on the left, but the numbering
1-8 fixes the order ひと -> 暮らし -> しごと; the commission's
audio-reading manuscript, the candidate-submitted text, shows the
same structure). The headline, the slogan, the theme band, the
resolve prose, the career history, the name heading and the photo
are not promises. The panel has no achievements section, so no
achievement items were excluded. None of the thirty-five items
states a numeric target, a deadline or a funding method
("福島2050カーボンニュートラル" is the name of the prefecture's
existing goal framework, not a target stated by the item), so all
thirty-five are directional commitments. The candidate panels are
image-only (a text extraction of the whole PDF yields 486
non-space characters, all of them the commission's printed frame
text), so the texts were transcribed from 200/300/400 dpi
renderings with collation. The review and promotion judgement
rests on the owner's 2026-11-15 delegation to Muse and is not
recorded as the owner's own review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-070009"
TERM_ID = "jp-local-070009-executive-2026-11-12"
BULLETIN_ID = "fukushima-pref-governor-election-2026-bulletin"
REVIEW_ID = "manifesto-review-jp-local-070009-2026"
SEARCH_ID = "manifesto-source-search-fukushima-pref-2026"

# The three pillar title statements, eight numbered headings and
# twenty-four bullet items of Governor Uchibori's panel in the
# official 2026 election bulletin (page 2), transcribed verbatim
# in numbered document order: for each pillar, the title statement
# first, then each heading followed by its bullet items in printed
# order. The bullet markers, the numbers and the pillar ornaments
# are layout elements and are not part of the texts. The headline,
# the slogan, the theme band, the resolve prose, the career
# history, the name heading and the photo are not records. Any
# wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "ひとを大切にするふくしまを創る！",
    "全国に誇れる子育て・教育環境を創る！",
    "出会い・結婚、妊娠・出産の希望をみんなで支える「子育て県」を創ります",
    "「学びの変革」を進め一人一人の子どもの資質・能力を育みます",
    '"ふくしまならでは"を生かした学びで子どもたち一人一人の「誇り」を育みます',
    "誰もがいきいきと暮らし、住みたくなる社会を創る！",
    "誰もが自分らしく生活し人権が守られ個性と能力を発揮できる社会を創ります",
    "安心の医療・福祉で支えスポーツや文化を楽しみ暮らせる健康長寿県を創ります",
    "ふくしまの暮らしを発信し、ご縁を深め新しい人の流れを確かなものとします",
    "安心・快適な暮らしのあるふくしまを創る！",
    "原子力災害からの復興・再生を進める！",
    "避難地域の生業・営農等の再生・再開と経営支援、暮らしの向上に取り組みます",
    "被災の地から希望の地へ向け魅力を更に高め交流や移住・定住を促進します",
    "廃炉・汚染水・処理水等原子力災害の課題には国・東京電力に厳正に対処します",
    "環境にも配慮した安全・安心で活力ある社会を創る！",
    "自然災害、有害鳥獣、新型感染症などから県民の命と暮らし・経済を守ります",
    "環境や地域の特性にも配慮した安心・快適な生活環境の維持・確保を進めます",
    "人口減少、物価高騰、食料安保、AI変革等の情勢変化に対応し県民生活を守ります",
    "働きたいしごとがあるふくしまを創る！",
    "中小企業振興と新産業の創出・集積を進める！",
    "中小企業等の生産・経営基盤の強化やAI活用、働き方の変革を支え魅力を高めます",
    "自動車関連、再エネ、医療、ロボット、航空宇宙等産業の強みを活かします",
    "福島イノベーション・コースト構想を身近な実感につなげ、更にシンカさせます",
    "強くてもうかる農林水産業を創る！",
    "園芸団地等産地の大規模化、風評に負けない農林水産物のブランド化を進めます",
    "高付加価値生産、多様な農業担い手の確保、スマート農業を推進します",
    "農林水産業の多面的機能に着目した取組を推進します",
    "環境と調和。「ふくしまならでは」の観光・交流を進める！",
    "ふくしまSDGs、福島2050カーボンニュートラル、水素社会を推進します",
    "自然や文化、食、サイクリング環境など魅力を生かした観光を国内外に発信します",
    "主に首都圏を対象とした交流拡大・移住・定住・Uターン、副業活動を推進します",
    "地域を結ぶ社会基盤の整備を促進する！",
    "基幹的な道路の整備や地域連携道路、復興を支える道路等の整備を促進します",
    "小名浜港、相馬港、福島空港の利活用を促進します",
    "鉄道や地域の足の利便性向上や利活用、情報通信インフラの整備に取り組みます",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "universal_city_and_inclusion",
    "universal_city_and_inclusion",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "urban_development_and_tourism",
    "environment_and_climate",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "health_welfare_and_community",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "environment_and_climate",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
]

PROJECT = "jp-local-070009-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-002": [
        PROJECT.format("marriage-childbirth-childrearing"),
        PROJECT.format("fukushima-education"),
    ],
    f"{TERM_ID}-promise-003": [PROJECT.format("marriage-childbirth-childrearing")],
    f"{TERM_ID}-promise-004": [PROJECT.format("fukushima-education")],
    f"{TERM_ID}-promise-005": [PROJECT.format("fukushima-education")],
    f"{TERM_ID}-promise-006": [PROJECT.format("inclusive-community-life")],
    f"{TERM_ID}-promise-007": [PROJECT.format("inclusive-community-life")],
    f"{TERM_ID}-promise-008": [
        PROJECT.format("health-longevity"),
        PROJECT.format("medical-care-welfare-system"),
    ],
    f"{TERM_ID}-promise-009": [PROJECT.format("new-inflow-of-people")],
    f"{TERM_ID}-promise-011": [PROJECT.format("reconstruction-and-revitalization")],
    f"{TERM_ID}-promise-012": [PROJECT.format("reconstruction-and-revitalization")],
    f"{TERM_ID}-promise-013": [
        PROJECT.format("reconstruction-and-revitalization"),
        PROJECT.format("new-inflow-of-people"),
    ],
    f"{TERM_ID}-promise-014": [PROJECT.format("reconstruction-and-revitalization")],
    f"{TERM_ID}-promise-015": [PROJECT.format("disaster-resilience-and-safety")],
    f"{TERM_ID}-promise-016": [PROJECT.format("disaster-resilience-and-safety")],
    f"{TERM_ID}-promise-017": [PROJECT.format("environment-coexistence")],
    f"{TERM_ID}-promise-020": [PROJECT.format("regional-industry-development")],
    f"{TERM_ID}-promise-021": [PROJECT.format("regional-industry-development")],
    f"{TERM_ID}-promise-022": [PROJECT.format("regional-industry-development")],
    f"{TERM_ID}-promise-023": [PROJECT.format("innovation-coast-initiative")],
    f"{TERM_ID}-promise-024": [PROJECT.format("profitable-agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-025": [PROJECT.format("profitable-agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-026": [PROJECT.format("profitable-agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-027": [PROJECT.format("profitable-agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-028": [PROJECT.format("tourism-and-exchange")],
    f"{TERM_ID}-promise-029": [
        PROJECT.format("renewable-energy-frontier"),
        PROJECT.format("environment-coexistence"),
    ],
    f"{TERM_ID}-promise-030": [PROJECT.format("tourism-and-exchange")],
    f"{TERM_ID}-promise-031": [
        PROJECT.format("tourism-and-exchange"),
        PROJECT.format("new-inflow-of-people"),
    ],
    f"{TERM_ID}-promise-032": [PROJECT.format("regional-transport-infrastructure")],
    f"{TERM_ID}-promise-033": [PROJECT.format("regional-transport-infrastructure")],
    f"{TERM_ID}-promise-034": [PROJECT.format("regional-transport-infrastructure")],
    f"{TERM_ID}-promise-035": [PROJECT.format("regional-transport-infrastructure")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# The three pillar title statements span their whole pillars and
# one bullet spans several unrelated situational changes, so
# these four stay unlinked -- see the records' extraction notes.
UNLINKED_IDS = {f"{TERM_ID}-promise-{index:03d}" for index in range(1, 36)} - IN_PROGRESS_IDS


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


def test_all_35_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 36)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == MUNICIPALITY_ID
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official printed bulletin itself (the
        # top of the source hierarchy), obtained directly from the
        # prefectural election commission's current official page.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"
        assert record["source_location"].startswith("選挙公報（全4ページ）・2ページ目")


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the thirty-five items states a numeric target, a
    # deadline or a funding method; nothing may be registered
    # for them. "福島2050カーボンニュートラル" names the
    # prefecture's existing goal framework and is not a target
    # stated by the item itself.
    for record in records():
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["assessability"] == "partially_assessable"
    by_id = {record["id"]: record for record in records()}
    # Only the decommissioning item addresses actors outside the
    # prefecture's sole control (the national government and
    # TEPCO), so only it is graded "shared".
    assert by_id[f"{TERM_ID}-promise-014"]["controllability"] == "shared"
    for record in records():
        if record["id"] != f"{TERM_ID}-promise-014":
            assert record["controllability"] == "medium"


def test_slogan_headline_resolve_and_career_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The vertical slogan.
        "みんなで創る",
        # The headline.
        "やさしさ、すこやかさ、おいしさあふれる",
        # The theme band.
        "人口減少対策への挑戦",
        "ふくしまプライド。",
        # The resolve prose.
        "福島県が誕生して150年",
        "私の決意",
        # The career history.
        "東京大学経済学部卒",
        "自治省入省",
        "福島県副知事",
    ):
        assert all(non_promise_line not in text for text in texts)


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
        for project in load_json("data/reviewed/fukushima-prefecture/projects.json")
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
        # The bulletin provenance (official commission publication
        # on its current page, byte-identical re-acquisition,
        # image-only panels transcribed from renderings, structure
        # collated against the audio-reading manuscript) travels
        # with every item.
        assert "選挙公報" in provenance["statement"]
        assert "50243021" in provenance["statement"]
        assert "音声読み上げ" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 38
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "内堀 雅雄"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 35
    # The review rests on the owner's 2026-11-15 delegation to
    # Muse and is not recorded as the owner's own review.
    assert "2026-11-15" in review["review_note"]
    assert "所有者本人のレビューとしては記録しない" in review["review_note"]

    review_packets = load_json("data/entities/executives/manifesto_review_evidence_packets.json")
    review_packet = next(packet for packet in review_packets if packet["subject_id"] == REVIEW_ID)
    assert_valid("schemas/evidence_packet.schema.json", review_packet)
    provenance_claims = {claim["field"] for claim in review_packet["claims"]}
    assert "review_provenance" in provenance_claims
    delegation = next(
        claim for claim in review_packet["claims"] if claim["field"] == "review_provenance"
    )
    assert "2026-11-15" in delegation["statement"]
    assert review_packet["open_questions"]

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    assert len(searches) == 47
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert BULLETIN_ID in search["checked_source_ids"]
    assert search["nonexistence_claim"] is False
    # The stage-1 note deferred extraction to stage 3; the note
    # now records the completed registration instead.
    assert "公約レコード35件を作成した" in search["review_note"]
    assert search["next_actions"]

    search_packets = load_json(
        "data/entities/executives/manifesto_source_search_evidence_packets.json"
    )
    search_packet = next(packet for packet in search_packets if packet["subject_id"] == SEARCH_ID)
    assert_valid("schemas/evidence_packet.schema.json", search_packet)

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term was registered in stage 1 from the commission's
    # official final ballot count; it is never used as an
    # implicit promise deadline.
    assert term["term_start"] == "2026-11-12"
    assert term["term_end"] == "2030-11-11"


def test_bulletin_source_record_points_at_the_official_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.70.0"
    assert len(catalog["records"]) == 225
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "fukushima-prefecture"
    assert bulletin["organization"] == "福島県選挙管理委員会"
    assert bulletin["url"].endswith("766690.pdf")
    assert bulletin["availability"] == "published"
