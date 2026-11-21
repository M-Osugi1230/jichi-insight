from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-221309-executive-2023-05-01"
BULLETIN_ID = "hamamatsu-city-mayor-election-2023-bulletin"

# The Nakano Yusuke panel of the 9 April 2023 Hamamatsu City mayoral
# election bulletin (page 1, upper left): under the catchphrase
# headline and a vision paragraph, three pillars each carry a
# black-bar heading and check-marked items. The pillar headings are
# verb-phrase statements of a future goal ("make ... more
# energetic"), so each heading is registered as one directional
# record (the Kawaguchi City / Chiba City treatment of headings
# that themselves state a goal), and each check item is one record:
# 3 headings + 7 items = 10 records, transcribed verbatim from the
# rendered PDF image at multiple resolutions (the panel is
# image-only, with no text layer; no audio-readable text edition is
# published on the election commission's result page). The
# catchphrase, the vision paragraph, the career profile and the
# website pointer are not promise records, and the panel presents
# no previous-term achievements box (the candidate was a newcomer;
# the profile is a career history). Any wording drift against the
# bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "安心・安全・人をもっと元気に",
    "結婚から出産、子育て、教育への切れ目ない支援",
    "健康長寿で元気に暮らせるまちに",
    "災害に強く安心して住み続けられるまちづくり",
    "産業振興・経済をもっと元気に",
    "ポテンシャルを引き出し、1次、2次、3次産業の更なる成長を促進",
    "ワーク・ライフ・バランスが実現できる環境づくり",
    "地域活性・まちをもっと元気に",
    "地域のにぎわいをつくりだし、交流を活発に",
    "コミュニティの力を引き出す環境整備",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "childcare_and_childrearing",
    "health_welfare_and_community",
    "safety_and_disaster_prevention",
    "industry_and_economy",
    "industry_and_economy",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "health_welfare_and_community",
]

P = "jp-local-221309-project-2025-"
EXPECTED_LINKS = {
    "002": P + "children-youth-healthy-growth",
    "003": P + "inclusive-support-collaboration",
    "004": P + "disaster-survival-community",
    "006": P + "global-market-industry-creation",
    "009": P + "vibrant-city-gathering",
    "010": P + "citizen-partnered-administration",
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
    assert term["person_name"] == "中野 祐介"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2023-04-09"
    # The term start is printed in the city's own list of past
    # mayors (the 30th mayor's term begins 1 May 2023, the day
    # after the 29th mayor's term ended), and the expiry is
    # printed directly in the Shizuoka prefectural election
    # commission's term list (令和9年4月30日).
    assert term["term_start"] == "2023-05-01"
    assert term["term_end"] == "2027-04-30"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert BULLETIN_ID in term["sources"]


def test_all_10_records_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 11)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-221309"
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
    # Every statement is phrased as a direction (a goal-phrased
    # pillar heading or a check-marked item) with no concrete
    # scheme, figure, deadline or funding stated, so all stay
    # directional and the numeric fields stay null instead of
    # being filled in.
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
    # The catchphrase headline, the vision paragraph, the career
    # profile and the website pointer are not commitments, so none
    # of them became a promise record. The panel has no
    # previous-term achievements box (the candidate was a
    # newcomer), so there are no achievement items to exclude.
    fragments = [
        "浜松をもっと元気に!!",
        "地方創生",
        "やらまいか",
        "nakano-yusuke",
        "昭和45年",
        "東京大学",
        "総務省",
        "北海道副知事",
        "53歳",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_limited_to_six_inferred_matches() -> None:
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
    projects = load_json("data/reviewed/hamamatsu-city/projects.json")
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
        if record["id"] == "manifesto-review-jp-local-221309-2023"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 10
    # The treatment of the pillar headings and of the profile is
    # recorded in the review note.
    assert "レコード化した" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "実績" in review["review_note"]


def test_source_search_registered_the_bulletin() -> None:
    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(
        record
        for record in searches
        if record["id"] == "manifesto-source-search-hamamatsu-city-2023"
    )
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False


def test_bulletin_source_record_points_at_the_pdf() -> None:
    catalog = load_json("data/catalog/executive_sources.json")
    bulletin = next(r for r in catalog["records"] if r["id"] == BULLETIN_ID)
    assert bulletin["url"].endswith("07_touitsu_k1.pdf")
    assert bulletin["municipality_key"] == "hamamatsu-city"
