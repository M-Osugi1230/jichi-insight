from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-111007-executive-2025-05-27"
BULLETIN_ID = "saitama-city-mayor-election-2025-bulletin"
RESULTS_ID = "saitama-city-mayor-election-2025-results"

# The Shimizu Hayato panel of the official May 2025 Saitama City
# mayoral election bulletin (two newspaper-format pages, bottom left
# of page 1), transcribed verbatim from the rendered PDF image at
# 300dpi, 450dpi and 600dpi: the twelve bullet items of the frame
# "4つのシンカ", read heading by heading (1 to 4) and in printed
# order inside each heading. The four headings are the names of the
# fields the items belong to, so they are not registered as separate
# records; the headline slogan, the framing statement, the
# track-record frame (three past achievements), the biography and
# the QR codes are not promise records either. No item carries a
# closing full stop in the original, and none is registered with
# one. Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "災害に強い安全で安心できる都市を実現",
    "東日本共創（協奏）都市の創造",
    "日本一の教育文化都市を実現",
    "緑豊かな環境循環都市の構築",
    "国際スポーツ・健康先進都市を実現",
    "全ての世代のしあわせ実感都市を創造",
    "もっと子ども・若者が希望を持てるまち",
    "もっと女性が活躍し、子育てがしやすいまち",
    "もっと障がい者が輝き、暮らしやすいまち",
    "もっと高齢者が生きがいと安心できるまち",
    "DXによる人に優しいスマート都市の推進",
    "絆（みんな）でつくる共創都市を実現",
]

EXPECTED_POLICY_AREAS = [
    "safety_and_disaster_prevention",
    "urban_development_and_tourism",
    "education_and_human_development",
    "environment_and_climate",
    "health_welfare_and_community",
    "health_welfare_and_community",
    "childcare_and_childrearing",
    "childcare_and_childrearing",
    "universal_city_and_inclusion",
    "health_welfare_and_community",
    "fiscal_administrative_reform",
    "health_welfare_and_community",
]

# Nine items are linked to the stage-2 project series of the
# Saitama City Comprehensive Promotion Plan by wording and content
# only (no official mapping exists), so the link confidence is
# capped at low / inferred in the evidence packets. The three
# remaining items (006 across all generations, 009 on disability
# inclusion, 011 on DX) have no corresponding registered series.
EXPECTED_LINKS = {
    "jp-local-111007-executive-2025-05-27-promise-001": [
        "jp-local-111007-project-2024-utility-pole-removal"
    ],
    "jp-local-111007-executive-2025-05-27-promise-002": [
        "jp-local-111007-project-2024-omiya-station-gcs"
    ],
    "jp-local-111007-executive-2025-05-27-promise-003": [
        "jp-local-111007-project-2024-active-learning-promotion",
        "jp-local-111007-project-2024-iwatsuki-ningyo-museum-culture",
    ],
    "jp-local-111007-executive-2025-05-27-promise-004": [
        "jp-local-111007-project-2024-energy-saving-renewables-promotion"
    ],
    "jp-local-111007-executive-2025-05-27-promise-005": [
        "jp-local-111007-project-2024-citizen-health-promotion"
    ],
    "jp-local-111007-executive-2025-05-27-promise-007": [
        "jp-local-111007-project-2024-maternal-child-health-support",
        "jp-local-111007-project-2024-active-learning-promotion",
    ],
    "jp-local-111007-executive-2025-05-27-promise-008": [
        "jp-local-111007-project-2024-maternal-child-health-support"
    ],
    "jp-local-111007-executive-2025-05-27-promise-010": [
        "jp-local-111007-project-2024-care-prevention-promotion"
    ],
    "jp-local-111007-executive-2025-05-27-promise-012": [
        "jp-local-111007-project-2024-community-association-membership"
    ],
}

EXPECTED_REVERSE_LINKS = {
    "jp-local-111007-project-2024-community-association-membership": [
        "jp-local-111007-executive-2025-05-27-promise-012"
    ],
    "jp-local-111007-project-2024-energy-saving-renewables-promotion": [
        "jp-local-111007-executive-2025-05-27-promise-004"
    ],
    "jp-local-111007-project-2024-citizen-health-promotion": [
        "jp-local-111007-executive-2025-05-27-promise-005"
    ],
    "jp-local-111007-project-2024-active-learning-promotion": [
        "jp-local-111007-executive-2025-05-27-promise-003",
        "jp-local-111007-executive-2025-05-27-promise-007",
    ],
    "jp-local-111007-project-2024-traffic-safety-facilities": [],
    "jp-local-111007-project-2024-care-prevention-promotion": [
        "jp-local-111007-executive-2025-05-27-promise-010"
    ],
    "jp-local-111007-project-2024-maternal-child-health-support": [
        "jp-local-111007-executive-2025-05-27-promise-007",
        "jp-local-111007-executive-2025-05-27-promise-008",
    ],
    "jp-local-111007-project-2024-iwatsuki-ningyo-museum-culture": [
        "jp-local-111007-executive-2025-05-27-promise-003"
    ],
    "jp-local-111007-project-2024-omiya-station-gcs": [
        "jp-local-111007-executive-2025-05-27-promise-002"
    ],
    "jp-local-111007-project-2024-utility-pole-removal": [
        "jp-local-111007-executive-2025-05-27-promise-001"
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


def test_term_is_registered_with_official_dates() -> None:
    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert_valid("schemas/executive_term.schema.json", term)
    assert term["person_name"] == "清水 勇人"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2025-05-25"
    # Both endpoints are stated day-exact in the title of the city
    # election commission's official ballot-count table ("当選人の
    # 任期：令和7年5月27日～令和11年5月26日"), so no statutory
    # construction was needed or applied.
    assert term["term_start"] == "2025-05-27"
    assert term["term_end"] == "2029-05-26"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    assert term["sources"] == [RESULTS_ID, BULLETIN_ID]


def test_results_table_was_collated_directly() -> None:
    packets = load_json("data/entities/executives/evidence_packets.json")
    packet = next(p for p in packets if p["subject_id"] == TERM_ID)
    election_claims = [
        claim for claim in packet["claims"] if claim["field"] == "election_date"
    ]
    assert len(election_claims) == 1
    # 177,217 votes for Shimizu Hayato, collated directly in the
    # city election commission's official ballot-count table PDF,
    # not from press coverage.
    assert "177,217" in election_claims[0]["statement"]
    assert RESULTS_ID in election_claims[0]["source_ids"]
    for field in ("term_start", "term_end"):
        claims = [claim for claim in packet["claims"] if claim["field"] == field]
        assert len(claims) == 1
        assert claims[0]["decision"] == "accepted"
        assert claims[0]["source_ids"] == [RESULTS_ID]
    # The cross-check against the prefectural term-expiry list was
    # completed on 2026-11-22: the list (as of 2025-12-18) states
    # 2029-05-26 for the Saitama City mayor, matching the record,
    # so it is recorded in the term_end claim and no longer open.
    term_end_claims = [
        claim for claim in packet["claims"] if claim["field"] == "term_end"
    ]
    assert "任期満了日一覧" in term_end_claims[0]["statement"]
    assert "照合済み" in term_end_claims[0]["review_note"]
    assert not any("未照合" in q for q in packet["open_questions"])


def test_all_12_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 13)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-111007"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution_is_all_directional() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    # Every item is a directional commitment without a numeric
    # target, deadline or funding statement; the figures in the
    # panel's track-record frame (87.2%, 53.1% and the like) are
    # presented achievements, not targets of these items.
    for record in items:
        assert record["statement_type"] == "directional_commitment"
        assert record["assessability"] == "partially_assessable"
        assert record["controllability"] == "medium"
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
        assert record["progress_state"] == "not_assessable"


def test_non_promise_panel_parts_are_not_registered() -> None:
    texts = [record["original_text"] for record in records()]
    # The headline slogan, the framing statement, the track-record
    # frame's three presented achievements and the biography are not
    # commitments, so none of their wording became a promise record.
    # The four frame headings are field names for the items below
    # them, so they were not double-registered either.
    fragments = [
        "もっとシンカ",
        "市民とともに実現した",
        "幸福度",
        "87.2",
        "水道管路耐震化率",
        "松下政経塾",
        "推進します",
        "安全で強靱な都市へのシンカ",
        "誇りあふれる都市へのシンカ",
        "しあわせ実感都市へのシンカ",
        "絆で支えあう都市へのシンカ",
    ]
    for fragment in fragments:
        assert not any(fragment in text for text in texts)


def test_project_links_are_capped_at_inferred() -> None:
    items = records()
    for record in items:
        assert record["related_project_ids"] == EXPECTED_LINKS.get(record["id"], [])

    projects = load_json("data/reviewed/saitama-city/projects.json")
    by_id = {record["id"]: record for record in projects}
    assert set(by_id) == set(EXPECTED_REVERSE_LINKS)
    for project_id, promise_ids in EXPECTED_REVERSE_LINKS.items():
        assert by_id[project_id]["related_promise_ids"] == promise_ids

    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        packet = packets[promise_id]
        link_claims = [
            claim
            for claim in packet["claims"]
            if claim["field"] == "related_project_ids"
        ]
        assert len(link_claims) == 1
        # Wording-based links are never asserted as established:
        # they stay at needs_review with the low / inferred cap.
        assert link_claims[0]["decision"] == "needs_review"
        assert "low" in link_claims[0]["review_note"]


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
        # The official-bulletin provenance and the high grading travel
        # with every item.
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_manifesto_review_records_the_segmentation() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(
        record
        for record in reviews
        if record["id"] == "manifesto-review-jp-local-111007-2025"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 12
    # The reading order (headings 1 to 4, printed order inside each
    # heading) and the exclusion of the headings themselves, the
    # framing statement, the track-record frame and the biography
    # are recorded in the review note.
    assert "4つのシンカ" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
    assert "実績" in review["review_note"]
    assert "経歴" in review["review_note"]
