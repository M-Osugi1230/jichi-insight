"""Issue #921: Hiroshima governor promises (cluster 11, stage 3).

The source is the official 2025 Hiroshima gubernatorial election
bulletin itself, published on the prefectural election
commission's official site (the "令和7年執行 広島県知事選挙" page,
posted 2025-11-10). The bulletin is a single page holding the
three candidates' panels; Governor Yokota's panel is the top
band. It is a poster: the slogan "実りある広島新時代へ。" with a
QR code at the top, her name in large vertical type with the
shoulder title "無所属・広島県知事候補・前広島県副知事" and her
photograph on the right, five policy items in a 3x2 grid -- each
a heading that itself states a future goal plus bullet items
(2, 2, 2, 2 and 1 bullets respectively, nine in total) -- and a
profile box (career history) at the lower right. Because each
heading states a goal rather than merely naming a field, the
fourteen records follow the Hyogo / Hamamatsu precedent:
headings and bullet items are registered as separate records in
document order (heading first, then its bullets). The panel has
no achievements section presenting past results as items; the
profile is a career history, not a set of achievement claims, so
no achievement items were excluded and none were registered. The
slogan, the QR code, the shoulder title, the photograph and the
profile are not promises either. None of the fourteen items
states a numeric target, a deadline or a funding method, so all
fourteen are directional commitments with no target registered.
The candidate panels are image-only (a text extraction of the
whole PDF yields zero non-space characters), so the texts were
transcribed from 200/300 dpi renderings and collated across
resolutions. No candidate-submitted audio-readable data
publication could be confirmed on the commission's election page
or in search, so no text-layer collation was available; the
search record does not claim the data does not exist.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-340006-executive-2025-11-29"
BULLETIN_ID = "hiroshima-pref-governor-election-2025-bulletin"
REVIEW_ID = "manifesto-review-jp-local-340006-2025"
SEARCH_ID = "manifesto-source-search-hiroshima-pref-2025"

# The five headings and nine bullet items of Governor Yokota's
# panel in the official 2025 election bulletin (single page, top
# band), transcribed verbatim in document order: each item's
# heading first, then its bullet items in printed order. The
# bullet markers themselves are layout symbols and are not part
# of the texts. The slogan, the QR code, the shoulder title, the
# photograph and the profile are not records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "農林水産業の生産力を強化し、次の世代に残していく",
    "農業生産を拡大し、地産地消の学校給食や、食育・食体験、観光活用の増大へ",
    "気温上昇や大雨など気象変動対策の強化",
    "若者や女性が住みたくなる地域づくり",
    "特に若者・女性が住みたい、働きたいと思う地域づくり、職場づくり（職場の魅力向上、産業誘致、活躍する姿の発信等）",
    "コンサートの広島飛ばしの解消、文化・アート・祭り・エンターテイメントによる魅力向上・関係人口の増加",
    "防災・減災対策、危機管理の強化",
    "すべての県民の命とくらし、雇用を守り抜くための対策を強化",
    "既存する老朽化した施設の改修補強を含めたインフラ整備、デジタル技術等も活用した災害情報の迅速な共有や避難指示体制の強化",
    "地域の宝を活かした、創造性や文化・歴史を感じられる観光振興",
    "海山島川、産業の歴史など各地域の資源、物語、食を、デジタル技術の力や官民共創により磨き、つなげて、人を惹きつける地域をつくる（観光資源の磨き上げ）",
    "ふるさと納税の活用（体験型など）",
    "核兵器廃絶、恒久平和に向けた取り組みの前進",
    "「国際平和拠点ひろしま構想」に基づき、国際社会に被爆の実相を伝え、多様な主体と連携し、核兵器廃絶のプロセスや平和構築を推進",
]

EXPECTED_POLICY_AREAS = [
    "industry_and_economy",
    "industry_and_economy",
    "environment_and_climate",
    "universal_city_and_inclusion",
    "universal_city_and_inclusion",
    "urban_development_and_tourism",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "international_engagement",
    "international_engagement",
]

PROJECT = "jp-local-340006-project-2025-{}"
EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [PROJECT.format("agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-002": [PROJECT.format("agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-003": [PROJECT.format("agriculture-forestry-fisheries")],
    f"{TERM_ID}-promise-004": [
        PROJECT.format("work-style-reform-diverse-participation")
    ],
    f"{TERM_ID}-promise-005": [
        PROJECT.format("work-style-reform-diverse-participation"),
        PROJECT.format("industrial-innovation"),
    ],
    f"{TERM_ID}-promise-007": [PROJECT.format("disaster-prevention-mitigation")],
    f"{TERM_ID}-promise-008": [PROJECT.format("disaster-prevention-mitigation")],
    f"{TERM_ID}-promise-009": [PROJECT.format("disaster-prevention-mitigation")],
}
IN_PROGRESS_IDS = set(EXPECTED_LINKS)
# The culture / related-population item, the three tourism-block
# items and the two peace items have no corresponding series
# among the ten stage-2 policy domains -- see the records'
# extraction notes.
UNLINKED_IDS = {
    f"{TERM_ID}-promise-006",
    f"{TERM_ID}-promise-010",
    f"{TERM_ID}-promise-011",
    f"{TERM_ID}-promise-012",
    f"{TERM_ID}-promise-013",
    f"{TERM_ID}-promise-014",
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


def test_all_14_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 15)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-340006"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from the
        # prefectural election commission's official site, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_numeric_content_was_invented() -> None:
    # None of the fourteen items states a numeric target, a
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


def test_slogan_profile_and_title_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    for non_promise_line in (
        # The slogan headline.
        "実りある広島新時代へ",
        # The shoulder title.
        "無所属・広島県知事候補",
        "前広島県副知事",
        # The profile (career history).
        "呉市生まれ",
        "東京大学法学部卒業",
        "農林水産省入省",
        "富山県副知事",
        "内閣官房内閣審議官",
        "広島県副知事（同年9月辞職）",
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
        for project in load_json("data/reviewed/hiroshima-prefecture/projects.json")
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
        # The bulletin provenance (official document, official
        # commission hosting, image-based panel transcribed from
        # renderings, no audio-readable data publication confirmed)
        # travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "音声読み上げ対応データ" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert set(provenance["source_ids"]) == {BULLETIN_ID}
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["statement_boundary"] == "mixed"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 14

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
    # The term was registered in stage 1: the start follows the
    # term-expiry election construction and the expiry is stated
    # verbatim in the commission's official term list; it is never
    # used as an implicit promise deadline.
    assert term["term_start"] == "2025-11-29"
    assert term["term_end"] == "2029-11-28"


def test_bulletin_source_record_points_at_the_official_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    assert catalog["version"] == "0.66.0"
    assert len(catalog["records"]) == 195
    assert len(catalog["records"]) == 195
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["municipality_key"] == "hiroshima-prefecture"
    assert bulletin["organization"] == "広島県選挙管理委員会"
    assert bulletin["url"].endswith("645830.pdf")
    assert bulletin["availability"] == "published"
