from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-121002-executive-2025-03-21"
BULLETIN_ID = "chiba-city-mayor-election-2025-bulletin"

# The Kamiya Shunichi panel of the 16 March 2025 Chiba City mayoral
# election bulletin (bulletin page (1), lower half): under the
# heading "10 visions for the future, 15 promises", VISION 01-05
# each carry a heading plus three circle-marked items (the 15 items
# are the candidate's own "15 promises"), and a separate vertical
# box for the 900th anniversary of Chiba's founding carries a lead
# sentence plus four bullet items. The registration takes the 15
# items as the core, each VISION heading as one directional record
# (the Kawaguchi heading precedent), and the anniversary box's lead
# and items as five more records: 25 records, transcribed verbatim
# from the rendered PDF image at multiple resolutions. The
# "2021-2024 achievements" box (four items presented as the record
# of the previous term), the slogan, the endorsers, the profile and
# the QR-code pointers are not promise records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "職住近接が可能で、子育てと仕事が両立できる・千葉市に",
    "3歳未満児の保育料の減免を年齢や所得制限なしで実施",
    "病児・病後児保育の受け皿拡大",
    "市内企業の事業継続支援と企業立地の推進",
    "こどもの権利が守られ、確かな学力が身に付き、若者に支援が届く・千葉市に",
    "市立学校の体育館へのエアコン設置",
    "不登校児童生徒の支援充実と「学びの多様化学校」の開校準備",
    "こどもの発達に関する相談・支援の拠点整備",
    "都市機能の中に緑と水辺が感じられる・千葉市に",
    "都市公園・河川空間のリニューアルと身近な公園の快適化",
    "広域道路ネットワークの整備検討と市内道路のミッシングリンクの解消",
    "市内路線バスの維持・復便等地域の移動手段の確保",
    "高齢者も障害のある人も、地域で長く住み続けられる・千葉市に",
    "帯状疱疹ワクチン接種に助成",
    "救急医療と診療科を強化した「幕張海浜病院」の開院",
    "手話言語普及・コミュニケーション条例の制定",
    "迅速な初動と避難所が強じんな防災都市・千葉市に",
    "下水道施設の確実な定期点検と下水管の耐震化",
    "新たな高潮・地震被害想定に基づく避難計画策定",
    "防災備蓄倉庫、分散備蓄倉庫の増設と更新",
    "愛着と誇りを育み「地域のちから」を高めます",
    "千葉開府900年記念事業",
    "郷土博物館のリニューアルオープン",
    "千葉国際芸術祭2025「ちから ひらく」開催",
    "町内自治会の担い手確保を支援し、地域の支え合いの仕組みを再構築",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "industry_and_economy",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "childcare_and_childrearing",
    "environment_and_climate",
    "environment_and_climate",
    "transport_infrastructure",
    "transport_infrastructure",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "city_image_and_public_relations",
    "city_image_and_public_relations",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "health_welfare_and_community",
]

EXPECTED_STATEMENT_TYPES = [
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
]

P = "jp-local-121002-project-2026-"
EXPECTED_LINKS = {
    "002": P + "childbearing-and-childrearing",
    "003": P + "childbearing-and-childrearing",
    "004": P + "local-industry",
    "008": P + "childbearing-and-childrearing",
    "010": P + "greenery-and-waterside",
    "011": P + "sustainable-attractive-city",
    "012": P + "sustainable-attractive-city",
    "014": P + "healthy-living",
    "015": P + "healthy-living",
    "016": P + "diversity-and-participation",
    "018": P + "disaster-resilient-infrastructure",
    "019": P + "collaborative-disaster-preparedness",
    "020": P + "collaborative-disaster-preparedness",
    "022": P + "culture-and-arts",
    "023": P + "culture-and-arts",
    "024": P + "culture-and-arts",
    "025": P + "diversity-and-participation",
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


def test_term_is_registered_with_official_dates() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert_valid("schemas/executive_term.schema.json", term)
    assert term["person_name"] == "神谷 俊一"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2025-03-16"
    # The prefecture's official list of municipal mayors (as of
    # 31 December 2025) states the current term's inauguration date
    # day-exact (21 March 2025, his second term) and the expiry
    # (20 March 2029); the city's election schedule page states the
    # same expiry. The start also follows the Article 259 proviso
    # chain from the previous term's expiry (20 March 2025).
    assert term["term_start"] == "2025-03-21"
    assert term["term_end"] == "2029-03-20"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_25_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 26)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-121002"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    # The panel states no baseline, no target figure, no day-level
    # deadline and no funding for any item, so all stay null instead
    # of being filled in.
    for record in items:
        assert record["baseline"] is None
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_non_promise_elements_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The four "2021-2024 achievements" items are presented as the
    # record of the previous term, not as promises, and the slogan,
    # the endorsers and the profile are not commitments either, so
    # none of them became a promise record.
    fragments = [
        "マンホールトイレ",
        "高校生まで拡大",
        "洋式化を完了",
        "京葉線",
        "地域をまもり",
        "熊谷",
        "1973年",
        "旧自治省",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_limited_to_seventeen_inferred_matches() -> None:
    items = {record["id"]: record for record in records()}
    for suffix, project_id in EXPECTED_LINKS.items():
        record = items[f"{TERM_ID}-promise-{suffix}"]
        assert record["related_project_ids"] == [project_id]
    for record in items.values():
        suffix = record["id"].rsplit("-", 1)[1]
        if suffix not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []
        # No official progress reporting keyed to the promises
        # exists, so every record stays not_assessable.
        assert record["progress_state"] == "not_assessable"
    # Reverse links on the Stage 2 project records mirror the
    # forward links exactly.
    projects = load_json("data/reviewed/chiba-city/projects.json")
    expected_reverse: dict[str, list[str]] = {}
    for suffix, project_id in EXPECTED_LINKS.items():
        expected_reverse.setdefault(project_id, []).append(
            f"{TERM_ID}-promise-{suffix}"
        )
    for project in projects:
        assert project["related_promise_ids"] == expected_reverse.get(
            project["id"], []
        )


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
        # The bulletin is the official document itself, reachable as
        # a standalone PDF from the city's election-result page.
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]
        if record["related_project_ids"]:
            link_claim = next(
                claim
                for claim in packet["claims"]
                if claim["field"] == "related_project_ids"
            )
            # Inferred links are capped at low / inferred and stay
            # under review until an official mapping is published.
            assert link_claim["decision"] == "needs_review"
            assert "low" in link_claim["review_note"]


def test_manifesto_review_records_the_segmentation() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        record
        for record in reviews
        if record["id"] == "manifesto-review-jp-local-121002-2025"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 25
    # The treatment of the achievements box and of the headings is
    # recorded in the review note.
    assert "実績" in review["review_note"]
    assert "公約化しなかった" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]


def test_source_search_registered_the_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-chiba-city-2025"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False


def test_bulletin_source_record_points_at_the_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    # The file name suggests the governor's bulletin, but the
    # document itself is the mayoral bulletin, as the review
    # verified from the rendered pages.
    assert bulletin["url"].endswith("r7shiji_senkyokouhou2.pdf")
    assert bulletin["municipality_key"] == "chiba-city"
