"""Issue #1087: Aomori governor promises (cluster 20, stage 3).

The source is the official 2023 Aomori gubernatorial election
bulletin itself (two pages), published on the prefectural election
commission's current results page and registered in stage 1
(3,285,127 bytes, SHA-256
73caab175758d3ca2bdb76174d1749471b7afe1d33f5d1fe66b98fb6fc86615b).
Governor Miyashita's panel (page 1, middle band) is a poster: the
headline "青森新時代を創る11の柱と90の政策", the candidate's name
with his photo, a prose address and a PROFILE (career history)
column on the left, and eleven numbered pillars in the centre.
Each pillar carries a heading with a bracketed caption and one
prose paragraph of commitments. The headings are topic labels --
they do not complete a commitment sentence on their own, unlike
the Fukushima pillar title statements -- so they are kept in
source_location and each pillar's paragraph is registered as one
record, in the pillars' numbered order (the pillars are printed
right to left, numbers 1-11). The prose has no itemised
sub-structure in the document, so it is not split into sentences.
The headline, the prose address, the PROFILE, the name heading,
the photo and the QR-code pointer to the "90 policies" details
(the details themselves are not printed in the bulletin) are not
promises. The panel has no achievements section, so no
achievement items were excluded. Two paragraphs state a numeric
goal in their own text -- pillar 2 (合計特殊出生率2以上) and
pillar 5 (インバウンドは10年で倍増) -- and those are recorded
verbatim in target; no other paragraph states a numeric target,
a deadline or a funding method (pillar 7's "3年後の国スポ・
障スポ" refers to a scheduled event, not to a deadline for the
item). The candidate panels are image-only (a text extraction of
the whole PDF yields only the commission's printed frame text),
so the texts were transcribed from renderings (full page at
200 dpi, the panel at 400 dpi) with collation. The review and
promotion judgement rests on the owner's 2026-11-15 delegation
to Muse and is not recorded as the owner's own review.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

MUNICIPALITY_ID = "jp-local-020001"
TERM_ID = "jp-local-020001-executive-2023-06-29"
BULLETIN_ID = "aomori-pref-governor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-020001-2023"
SEARCH_ID = "manifesto-source-search-aomori-pref-2023"

# The eleven pillar paragraphs of Governor Miyashita's panel in
# the official 2023 election bulletin (page 1), transcribed
# verbatim in numbered order. The pillar numbers, the headings
# and the bracketed captions are layout / label elements kept in
# source_location; they are not part of the texts. The headline,
# the prose address, the PROFILE, the name heading and the photo
# are not records. Any wording drift against the bulletin must
# fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "社会情勢の変化に応じて事業者・生活者の支援を実施。県庁内に知事を本部長とする緊急対策本部を設置します。スピード感をもった対応を実現。県内生産者にとっても課題の2024年問題について国への提言をまとめます。",
    "少子化の要因を分析し政策を立案実行するため、「青森こども未来県民会議」を設置し、給食費等を含む子育て費用の無償化などを進め、合計特殊出生率2以上に道筋をつける少子化対応政策「青森モデル」を確立します。",
    "県立病院・全県の2次医療機関の費用負担・医療従事者配置について再編・再構築により県内の医療格差を是正します。1次医療機関から3次医療機関までのネットワーク化、オンライン診療の普及により患者負担を軽減します。",
    "八甲田風力発電は白紙撤回を実現します。再エネ推進と自然との共生を図るためのゾーニング条例を制定することにより、風力・太陽光ともに自然保護エリアを定めて禁止区域を明確に定め、促進エリアでは開発を可能とし自然との共生を図ります。",
    "生産者の所得向上のプログラムにより、リンゴ、コメ、野菜、果物、畜産、酪農、林業、水産の全てで豊かさが実感できる「シン・青森農林水産業」を目指し、世界へ発信します。観光客数・消費額を回復させインバウンドは10年で倍増を目指します。",
    "日本海溝等の巨大地震・津波に備え、津波防災タワーの研究・開発を迅速に進め、沿岸市町村で整備推進します。頻発する豪雨災害には、現場を大切に、県と市町村の災害対策本部をデジタル技術で連動させ緊急対応の即応性を高めます。",
    "3年後の国スポ・障スポに向け、競技施設の整備等に万全を期し、選手と指導者の育成を進めるとともに、子供達の夢を制約せず叶う環境づくりを進めます。縄文遺跡群などの世界遺産について世界に発信し、文化財のデジタル化や海外展示も進めます。",
    "ひとり親家庭や貧困家庭などの子どもを地域ぐるみで支援する体制をつくります。経済的理由で夢をあきらめることのないよう高校生、大学生に給付型奨学金を拡充します。海外大学へ挑戦する若者を応援する教育プログラム導入にも取り組みます。",
    "多様性を認め合い、差別のない、あたたかな「あおもり新共生社会」を目指します。障がい者の自立と災害時の支援も充実させます。医療的ケア児とその家族の状況に応じた支援を実施します。高齢者の集いの場を市町村と連携して充実させます。",
    "県民の皆様の身近な課題を解決するため、その最前線に立つ市町村長と連携し日常的に課題を共有し、地域ごとでなく、一つの青森として解決に向かい前進する新しい連携を実現します。知事と40市町村長とをオンラインで常時接続し連携を強化します。",
    "国の補助金・交付金を積極活用し県土の強靭化、高規格道路のネットワーク化、防災減災インフラ整備等の社会資本整備に積極的に取り組みます。経常収支比率、健全化判断比率、県債残高等に常時注視し、安定的県財政で県民経済に貢献します。",
]

EXPECTED_POLICY_AREAS = [
    "industry_and_economy",
    "childcare_and_childrearing",
    "health_welfare_and_community",
    "environment_and_climate",
    "industry_and_economy",
    "safety_and_disaster_prevention",
    "education_and_human_development",
    "education_and_human_development",
    "universal_city_and_inclusion",
    "fiscal_administrative_reform",
    "transport_infrastructure",
]

PROJECT = "jp-local-020001-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [PROJECT.format("industry-competitiveness")],
    f"{TERM_ID}-promise-002": [
        PROJECT.format("childrearing-environment"),
        PROJECT.format("children-youth-support"),
    ],
    f"{TERM_ID}-promise-003": [PROJECT.format("regional-medical-care")],
    f"{TERM_ID}-promise-004": [
        PROJECT.format("renewable-energy-coexistence"),
        PROJECT.format("natural-environment"),
    ],
    f"{TERM_ID}-promise-005": [
        PROJECT.format("agriculture-strength"),
        PROJECT.format("tourism-promotion"),
        PROJECT.format("exports-logistics"),
    ],
    f"{TERM_ID}-promise-006": [
        PROJECT.format("disaster-prevention-crisis"),
        PROJECT.format("safe-land-infrastructure"),
    ],
    f"{TERM_ID}-promise-007": [PROJECT.format("culture-sports")],
    f"{TERM_ID}-promise-008": [
        PROJECT.format("children-youth-support"),
        PROJECT.format("youth-jobs"),
    ],
    f"{TERM_ID}-promise-009": [PROJECT.format("inclusive-society")],
    f"{TERM_ID}-promise-010": [PROJECT.format("community-development")],
    f"{TERM_ID}-promise-011": [
        PROJECT.format("safe-land-infrastructure"),
        PROJECT.format("industry-exchange-infrastructure"),
        PROJECT.format("transport-network"),
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


def test_all_11_pillars_registered_verbatim_in_numbered_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 12)
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
        assert record["source_location"].startswith("選挙公報（全2ページ）・1ページ目")


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_numeric_content_only_where_the_bulletin_states_it() -> None:
    by_id = {record["id"]: record for record in records()}
    # Pillar 2 states its numeric goal in its own text.
    pillar2 = by_id[f"{TERM_ID}-promise-002"]
    assert pillar2["statement_type"] == "specific_commitment"
    assert pillar2["target"] == "合計特殊出生率2以上"
    # Pillar 5 states the inbound-tourism goal in its own text;
    # the paragraph spans two themes, so the record as a whole
    # stays directional.
    pillar5 = by_id[f"{TERM_ID}-promise-005"]
    assert pillar5["statement_type"] == "directional_commitment"
    assert pillar5["target"] == "インバウンドは10年で倍増"
    # Pillar 4 names concrete measures (cancellation of the
    # Hakkoda wind project, a zoning ordinance).
    assert by_id[f"{TERM_ID}-promise-004"]["statement_type"] == "specific_commitment"
    for record in records():
        if record["id"] not in {f"{TERM_ID}-promise-002", f"{TERM_ID}-promise-005"}:
            assert record["target"] is None
        if record["id"] not in {f"{TERM_ID}-promise-002", f"{TERM_ID}-promise-004"}:
            assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        # The term end is never used as an implicit promise deadline.
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["assessability"] == "partially_assessable"
        assert record["controllability"] == "medium"


def test_headline_address_and_profile_were_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    for non_promise_line in (
        # The headline.
        "青森新時代を創る11の柱と90の政策",
        # The prose address.
        "歴史的転換点",
        "お一人おひとりの県民の皆様から選ばれた知事として",
        # The PROFILE (career history).
        "東北大学法学部",
        "むつ市長",
        "国家公務員I種試験",
    ):
        assert all(non_promise_line not in text for text in texts)


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {record["id"] for record in items if record["progress_state"] == "in_progress"}
    assert in_progress == set(EXPECTED_LINKS)
    for record in items:
        assert record["related_project_ids"]


def test_project_links_are_exact_bidirectional_and_capped() -> None:
    items = {record["id"]: record for record in records()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert items[promise_id]["related_project_ids"] == project_ids

    projects = {
        project["id"]: project
        for project in load_json("data/reviewed/aomori-prefecture/projects.json")
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
        # The bulletin provenance (official commission publication
        # on its current page, byte-identical re-acquisition,
        # image-only panels transcribed from renderings) travels
        # with every item.
        assert "選挙公報" in provenance["statement"]
        assert "73caab17" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    assert len(reviews) == 40
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["candidate_name"] == "宮下 宗一郎"
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 11
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
    assert "公約レコード11件を作成した" in search["review_note"]
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
    # official records; it is never used as an implicit promise
    # deadline.
    assert term["term_start"] == "2023-06-29"
    assert term["term_end"] == "2027-06-28"


def test_bulletin_source_record_points_at_the_official_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    # Stage 3 adds no catalog record for Aomori Prefecture (the
    # bulletin was registered at stage 1).  The catalog total itself
    # moved on with the Morioka stage-3 registration, PR #1091; the
    # global version and count pins live in the shared catalog tests.
    aomori_ids = sorted(
        record["id"]
        for record in catalog["records"]
        if record["id"].startswith("aomori-pref-")
    )
    assert aomori_ids == [
        "aomori-pref-election-record-2023",
        "aomori-pref-governor",
        "aomori-pref-governor-election-2023-bulletin",
        "aomori-pref-governor-election-2023-history",
        "aomori-pref-governor-election-2023-record",
        "aomori-pref-governor-election-2023-results",
        "aomori-pref-governor-inauguration-2023",
        "aomori-pref-mayor-term-expiry-list",
    ]
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "aomori-prefecture"
    assert bulletin["organization"] == "青森県選挙管理委員会"
    assert bulletin["url"].endswith("R5_chijisen_kouho.pdf")
    assert bulletin["availability"] == "published"
