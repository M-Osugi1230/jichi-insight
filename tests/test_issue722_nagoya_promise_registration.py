from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-231002-executive-2024-11-24"
BULLETIN_ID = "nagoya-city-mayor-election-2024-bulletin"

# The Hirosawa Ichiro panel of the official 2024 Nagoya mayoral election
# bulletin (page 1, lower left), transcribed verbatim from the rendered
# PDF image: the four highlighted boxes, the two remuneration band lines,
# and the eleven bullet items, in document order. The headline and the
# biography profile are not promise records. Any wording drift against
# the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "市民税減税\n5%→10%",
    "敬老パス\n値下げ",
    "保育料\n0歳児から無償化",
    "名古屋城\n木造本物復元",
    "市長報酬を2,800万円から800万円 退職金廃止",
    "市議報酬も800万円を貫き地方議員の家業化を無くす!",
    "日本一の福祉と医療",
    "子ども、子育て世帯を徹底的に応援",
    "1人の子どもも死なせないナゴヤ",
    "日本最強の防災体制の構築",
    "行政のデジタル化（DX化）の推進",
    "公園に大人や高齢者向け運動機能強化",
    "東山線の昼間時間帯増発",
    "ホームレス対策",
    "新堀川上流の緑地化検討",
    "東山動物園でコアラを抱っこ",
    "コモドドラゴンを増やし繁殖可能に",
]

EXPECTED_POLICY_AREAS = [
    "fiscal_administrative_reform",
    "health_welfare_and_community",
    "childcare_and_childrearing",
    "urban_development_and_tourism",
    "fiscal_administrative_reform",
    "fiscal_administrative_reform",
    "health_welfare_and_community",
    "childcare_and_childrearing",
    "health_welfare_and_safety",
    "safety_and_disaster_prevention",
    "fiscal_administrative_reform",
    "health_welfare_and_community",
    "transport_infrastructure",
    "health_welfare_and_community",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
]

EXPECTED_STATEMENT_TYPES = [
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "vision",
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
]

# Only the four items whose panel text states a measurable aim carry a
# target; every other numeric-looking absence stays null.
EXPECTED_TARGETS = {
    f"{TERM_ID}-promise-001": "市民税減税 5%→10%",
    f"{TERM_ID}-promise-003": "0歳児からの保育料無償化",
    f"{TERM_ID}-promise-005": "市長報酬800万円・退職金廃止",
    f"{TERM_ID}-promise-006": "市議報酬800万円",
}

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-008",
    f"{TERM_ID}-promise-010",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-008": [
        "jp-local-231002-project-2025-childcare-waitlist-countermeasures",
        "jp-local-231002-project-2025-area-support-nursery-schools",
        "jp-local-231002-project-2025-kodomo-sumairu-housing-project",
    ],
    f"{TERM_ID}-promise-010": [
        "jp-local-231002-project-2025-seismic-breaker-installation",
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
    assert term["person_name"] == "広沢 一郎"
    assert term["office"] == "mayor"
    # Vacancy election: Article 259 counts the term from election day.
    assert term["election_date"] == "2024-11-24"
    assert term["term_start"] == "2024-11-24"
    # The expiry date is the one stated in Aichi Prefecture's official
    # mayors list, not a derived value.
    assert term["term_end"] == "2028-11-23"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_17_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 18)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-231002"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution_and_vision_boundary() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    vision = items[6]
    assert vision["id"] == f"{TERM_ID}-promise-007"
    # A superlative slogan without a specific measure is a vision and is
    # never given a progress judgement.
    assert vision["assessability"] == "not_assessable"
    assert vision["progress_state"] == "not_assessable"


def test_only_stated_targets_were_recorded() -> None:
    items = records()
    for record in items:
        assert record["target"] == EXPECTED_TARGETS.get(record["id"])
        # Nothing was supplemented from outside the text: no baselines,
        # no deadlines (the term end is never an implicit deadline), no
        # funding statements, and no change explanations.
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
    packets = packets_by_subject()
    for promise_id in EXPECTED_TARGETS:
        target_claims = [
            claim
            for claim in packets[promise_id]["claims"]
            if claim["field"] == "target"
        ]
        assert len(target_claims) == 1
        assert target_claims[0]["decision"] == "accepted"


def test_childcare_fee_abolition_is_not_linked_to_waitlist_projects() -> None:
    items = {record["id"]: record for record in records()}
    fee = items[f"{TERM_ID}-promise-003"]
    # Free childcare fees are a different measure from the registered
    # waitlist-countermeasure projects, so no link is asserted.
    assert fee["related_project_ids"] == []
    assert fee["progress_state"] == "not_assessable"


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {
        record["id"] for record in items if record["progress_state"] == "in_progress"
    }
    assert in_progress == IN_PROGRESS_IDS
    for record in items:
        if record["id"] not in IN_PROGRESS_IDS:
            assert record["progress_state"] == "not_assessable"
            assert record["related_project_ids"] == []
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
        for project in load_json("data/reviewed/nagoya-city/projects.json")
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
        if record["id"] == "manifesto-review-jp-local-231002-2024"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 17
    # The headline and the biography were deliberately not itemised.
    assert "プロフィール" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
