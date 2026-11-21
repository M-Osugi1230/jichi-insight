from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-281000-executive-2025-11-20"
BULLETIN_ID = "kobe-city-mayor-election-2025-bulletin"

# The Hisamoto Kizo panel of the 26 October 2025 Kobe City mayoral
# election bulletin (the single bulletin page, lower right): under
# the band heading "my priority measures", five numbered pillars
# each carry a black-bar heading (a title label), a lead sentence
# stating the pillar's direction, and circle-marked items. The
# registration takes each pillar's lead sentence as one directional
# record and each circle item as one record: 5 leads + 23 items =
# 28 records, transcribed verbatim from the rendered PDF image at
# multiple resolutions (the panel is image-only, with no text
# layer). The pillar headings themselves are title labels, not
# statements, so they are kept in source_location and in the
# segmentation review instead of becoming records (the Fukuoka
# Prefecture / Kitakyushu City treatment of pillar headings). The
# catchphrases, the career profile and the QR-code pointers are not
# promise records, and the panel presents no previous-term
# achievements box. Any wording drift against the bulletin must
# fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "幾多の経験と想像力を駆使し、あらゆる危機に備え、市民の「日常」を守る",
    "防災DX",
    "防犯カメラ・街灯増設",
    "サイバー攻撃対策",
    "こうべ木陰プロジェクト",
    "「子育て」も「仕事」も両立でき、誰もがいきいきと暮らせるまちをつくる",
    "高校生通学定期券無料化の充実",
    "「まちなか自習室」",
    "無料コワーキングスペースの拡充",
    "きめ細かく多様な支援",
    "世界とつながる「新たな国際都市」として圏域経済を牽引する",
    "空港ターミナル強化",
    "海外ビジネス展開の促進",
    "スパコン・量子コンピューター活用",
    "都心の再生",
    "質の高い観光促進",
    "自然と暮らしが調和する「豊かなライフスタイル」を実現する",
    "多様な住宅供給",
    "マンション管理の適正化",
    "「市内居住」「職住近接」推進",
    "スポンジ化対策",
    "「森の未来都市神戸」",
    "多様な主体との協働により「先駆的」な行政運営を徹底的に進める",
    "地域貢献活動促進",
    "AI活用・現場力強化",
    "行政機能強化",
    "特別市法制化に向けた活動への貢献",
    "近隣市町との広域連携",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "childcare_and_childrearing",
    "education_and_human_development",
    "education_and_human_development",
    "industry_and_economy",
    "health_welfare_and_community",
    "industry_and_economy",
    "transport_infrastructure",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "environment_and_climate",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "environment_and_climate",
    "fiscal_administrative_reform",
    "health_welfare_and_community",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
]

P = "jp-local-281000-project-2026-"
EXPECTED_LINKS = {
    "005": P + "connected-distinctive-townscape",
    "006": P + "childrearing-work-balance",
    "007": P + "childrearing-work-balance",
    "008": P + "childrearing-work-balance",
    "009": P + "childrearing-work-balance",
    "010": P + "healthy-secure-living",
    "011": P + "metropolitan-economic-growth",
    "012": P + "global-talent-development",
    "013": P + "metropolitan-economic-growth",
    "014": P + "metropolitan-economic-growth",
    "015": P + "downtown-experience-and-business",
    "016": P + "international-city-appeal",
    "017": P + "nature-for-next-generation",
    "018": P + "connected-distinctive-townscape",
    "019": P + "existing-urban-area-renewal",
    "020": P + "existing-urban-area-renewal",
    "021": P + "existing-urban-area-renewal",
    "022": P + "nature-for-next-generation",
    "023": P + "inclusive-challenge-society",
    "024": P + "inclusive-challenge-society",
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
    assert term["person_name"] == "久元 喜造"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2025-10-26"
    # The city audit commissioners' official report (神監2第59号)
    # states the mayoral term expired on 19 November 2021, fixing
    # the four-year cycle of a 20 November start and a 19 November
    # expiry; the 2025 election was a term-expiry election, so the
    # Article 259 proviso gives the 20 November 2025 start. The
    # cross-check against the prefectural election commission's
    # own term-expiry list is still outstanding (open question).
    assert term["term_start"] == "2025-11-20"
    assert term["term_end"] == "2029-11-19"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_28_records_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 29)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-281000"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so
        # the record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    # Every statement is phrased as a direction (a lead sentence or
    # a noun-phrase item) with no concrete scheme, figure, deadline
    # or funding stated, so all stay directional and the numeric
    # fields stay null instead of being filled in.
    for record in items:
        assert record["statement_type"] == "directional_commitment"
        assert record["baseline"] is None
        assert record["target"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["assessability"] == "partially_assessable"


def test_non_promise_elements_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The pillar headings are title labels, not statements, and the
    # catchphrases and the career profile are not commitments
    # either, so none of them became a promise record. The panel
    # has no previous-term achievements box.
    fragments = [
        "強靭で力強いまち",
        "人間らしいあたたかいまち",
        "グローバル社会に羽ばたくまち",
        "海と山を感じる美しいまち",
        "対話と参加が進むまち",
        "ブレることなく",
        "ひたすら神戸のために",
        "1954年",
        "自治省",
        "総務省",
        "副市長",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_limited_to_twenty_inferred_matches() -> None:
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
    projects = load_json("data/reviewed/kobe-city/projects.json")
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
        if record["id"] == "manifesto-review-jp-local-281000-2025"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 28
    # The treatment of the pillar headings and of the profile is
    # recorded in the review note.
    assert "レコード化せず" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "実績" in review["review_note"]


def test_source_search_registered_the_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-kobe-city-2025"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False


def test_bulletin_source_record_points_at_the_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["url"].endswith("senkyokouhoushityousen.pdf")
    assert bulletin["municipality_key"] == "kobe-city"
    audit = next(
        r
        for r in catalog["records"]
        if r["id"] == "kobe-city-mayor-term-audit-report-2022"
    )
    assert audit["url"].endswith(
        "r4_sumakusenkyokouhounokansahoukokutobessi.pdf"
    )
    assert audit["category"] == "audit"
