from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-112038-executive-2026-02-09"
BULLETIN_ID = "kawaguchi-city-mayor-election-2026-bulletin"

# The Okamura Yuriko panel of the 1 February 2026 Kawaguchi mayoral
# election bulletin (bulletin page (3), lower half): six basic
# policies, each a heading plus bullet items closed by the
# enumeration mark "、他". The registration takes each heading as one
# directional record and each bullet item as one record, in policy
# order (policy 1 to 6, heading first): 6 headings + 20 items = 26
# records, transcribed verbatim from the rendered PDF image at
# multiple resolutions. The headline slogan, the framework subtitle,
# the biography, the motto line and the pointer to the candidate's
# website are not promise records. Any wording drift against the
# bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "人づくりなくして国づくりなし 子育て、教育に力を入れるまちへ",
    "学校のトイレ環境の整備推進",
    "小学校体育館のエアコン整備促進",
    "学校図書室の充実",
    "妊婦タクシー利用助成制度の創設",
    "市民の声や繋がりを大切にするまちへ",
    "市長との意見交換会の実施",
    "町会・自治会活動の充実、負担軽減対策",
    "臨機応変な公民館運営と公民館活動の活性化",
    "安心して暮らし続けられるまちへ",
    "外国人政策の推進（全庁あげた生活ルールの徹底、国への要望強化）",
    "地域防災力の強化・活動支援",
    "障がい者の親なき後支援の推進",
    "認知症対策の充実",
    "地域経済の活性化による活気のあるまちへ",
    "アスリートを応援しスポーツでまちを活性化",
    "グリーンセンターの再整備",
    "文化や歴史を活かした賑わいづくり",
    "真に選ばれるまちへ",
    "上野東京ライン停車に関する総事業費の再確認、再検討",
    "公共インフラ総点検の実施",
    "高齢者の移動手段の確保",
    "働きやすく信頼できる市役所があるまちへ",
    "職員との積極的な意見交換",
    "財政の健全化",
    "公正で公平な入札・契約制度の確立",
]

EXPECTED_POLICY_AREAS = [
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "education_and_human_development",
    "childcare_and_childrearing",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "education_and_human_development",
    "health_welfare_and_safety",
    "universal_city_and_inclusion",
    "safety_and_disaster_prevention",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "transport_infrastructure",
    "transport_infrastructure",
    "transport_infrastructure",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
]

EXPECTED_STATEMENT_TYPES = [
    "directional_commitment",
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
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
    "directional_commitment",
]

EXPECTED_LINKS = {
    "005": "jp-local-112038-project-2026-child-wellbeing-support",
    "007": "jp-local-112038-project-2026-multi-stakeholder-collaboration",
    "008": "jp-local-112038-project-2026-mutual-respect-community",
    "009": "jp-local-112038-project-2026-lifelong-learning-sports",
    "011": "jp-local-112038-project-2026-mutual-respect-community",
    "012": "jp-local-112038-project-2026-disaster-resilient-safe-city",
    "014": "jp-local-112038-project-2026-elderly-healthy-active-life",
    "016": "jp-local-112038-project-2026-lifelong-learning-sports",
    "017": "jp-local-112038-project-2026-water-and-greenery",
    "018": "jp-local-112038-project-2026-economic-activity-employment",
    "020": "jp-local-112038-project-2026-planned-urban-development",
    "021": "jp-local-112038-project-2026-planned-urban-development",
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
    assert term["person_name"] == "岡村 ゆり子"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2026-02-01"
    # Both dates are stated day-exact in the city's official
    # public-relations magazine (March 2026 issue, page 2): she took
    # office on 9 February 2026 and the term runs until 8 February
    # 2030. The start also follows the Article 259 proviso chain,
    # anchored by the previous term's expiry (2026-02-08) stated in
    # the election commission's 2025-05-16 press release.
    assert term["term_start"] == "2026-02-09"
    assert term["term_end"] == "2030-02-08"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_26_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 27)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-112038"
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
    # Only the five specific commitments carry a target. The panel
    # states no baseline, no day-level deadline and no funding for
    # any item.
    for index, record in enumerate(items, start=1):
        if index in (5, 7, 17, 20, 21):
            assert record["target"] is not None
        else:
            assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_non_promise_elements_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The headline slogan, the framework subtitle, the motto line,
    # the biography and the pointer to the candidate's website are
    # not commitments for the term, so none of them became a promise
    # record. The enumeration mark "、他" closing each item list is
    # an omission symbol, not part of any item's wording.
    fragments = [
        "変えるなら今",
        "川口を輝かせる",
        "意志を貫き",
        "yurikookamura",
        "2015年5月",
        "、他",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_limited_to_twelve_inferred_matches() -> None:
    items = {record["id"]: record for record in records()}
    for suffix, project_id in EXPECTED_LINKS.items():
        record = items[f"{TERM_ID}-promise-{suffix}"]
        assert record["related_project_ids"] == [project_id]
    for record in items.values():
        suffix = record["id"].rsplit("-", 1)[1]
        if suffix not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []
        # The mayor took office in February 2026 and no official
        # progress reporting on the promises exists, so every record
        # stays not_assessable (the Yokohama first-term model, not
        # the incumbent Kawasaki model).
        assert record["progress_state"] == "not_assessable"


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
        if record["id"] == "manifesto-review-jp-local-112038-2026"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 26
    # The numbering convention and the elements that were not
    # itemised are recorded in the review note.
    assert "見出し" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]


def test_source_search_registered_the_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-kawaguchi-city-2026"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False


def test_bulletin_source_record_points_at_the_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["url"].endswith("sichouyou.pdf")
    assert bulletin["municipality_key"] == "kawaguchi-city"
