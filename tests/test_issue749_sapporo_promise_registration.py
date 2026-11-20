from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-011002-executive-2023-05-02"
BULLETIN_ID = "sapporo-city-mayor-election-2023-bulletin"

# The Akimoto Katsuhiro panel of the official 2023 Sapporo mayoral
# election bulletin (page 1, upper right), transcribed verbatim from the
# rendered PDF image: the thirteen bullet items of the policy frame
# "6つの道標" (six pillars), in document order (pillar 1 items 1-2,
# pillar 2 items 1-2, pillar 3 items 1-3, pillar 4 items 1-2, pillar 5
# items 1-2, pillar 6 items 1-2). The headline, the pillar titles and
# the biography profile are not promise records. Any wording drift
# against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "迅速に救急医療を提供できる仕組みをつくります。",
    "福祉に関する困りごとの相談を受け付ける「（仮称）福祉ワンストップ窓口」を新設します。",
    "大雪にも強い街をつくります。",
    "企業家等と市長が直接意見交換を行い、民間の発想を具体的な行政運営に反映させる新たな仕組みをつくります。",
    "子ども医療費や保育料の無料化の対象をさらに拡大します。",
    "学校給食費への公費負担をさらに拡大します。",
    "ひとり親家庭に対する医療費の支援を拡大します。",
    "「（仮称）共生社会推進条例」を新たに制定します。",
    "道内で作られる再生可能エネルギーを利用するなど、北海道全体のゼロカーボンの実現に貢献します。",
    "民間企業のアイデアを受け付ける市役所窓口を新設します。",
    "経済界・労働界と協力して雇用環境の改善に取り組みます。",
    "大通公園エリア及び創成川東エリアのリニューアルを進めます。",
    "札幌ドーム周辺を「スポーツ交流拠点」として整備します。",
]

EXPECTED_POLICY_AREAS = [
    "health_welfare_and_community",
    "health_welfare_and_community",
    "safety_and_disaster_prevention",
    "fiscal_administrative_reform",
    "childcare_and_childrearing",
    "education_and_human_development",
    "health_welfare_and_community",
    "universal_city_and_inclusion",
    "environment_and_climate",
    "fiscal_administrative_reform",
    "industry_and_economy",
    "urban_development_and_tourism",
    "urban_development_and_tourism",
]

EXPECTED_STATEMENT_TYPES = [
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "specific_commitment",
    "directional_commitment",
    "specific_commitment",
    "directional_commitment",
    "specific_commitment",
    "specific_commitment",
]

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-008",
    f"{TERM_ID}-promise-009",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-008": [
        "jp-local-011002-project-2026-multicultural-coexistence-promotion",
    ],
    f"{TERM_ID}-promise-009": [
        "jp-local-011002-project-2026-gx-investment-promotion",
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
    assert term["person_name"] == "秋元 克広"
    assert term["office"] == "mayor"
    assert term["election_date"] == "2023-04-09"
    # Term-expiry election: Article 259's proviso counts the term from
    # the day after the previous term expired. The profile states the
    # first term began on May 2 and records the 2019 and 2023
    # re-elections; no four years were added to the election date.
    assert term["term_start"] == "2023-05-02"
    # The expiry date is the one stated in the Hokkaido Election
    # Commission's official term-expiry list, not a derived value.
    assert term["term_end"] == "2027-05-01"
    assert term["manifesto_source_ids"] == [BULLETIN_ID]


def test_all_13_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == (
        EXPECTED_ORIGINAL_TEXTS
    )
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 14)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-011002"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["plain_summary"]
        # The source is the official election bulletin itself, so the
        # record-level grading is high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_distribution_and_directional_boundary() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS
    assert [record["statement_type"] for record in items] == (
        EXPECTED_STATEMENT_TYPES
    )
    # The panel carries no vision-only bullet: the slogan "安心と、希望。"
    # is the headline and was not itemised, so every record stays
    # assessable in principle.
    for record in items:
        assert record["assessability"] == "assessable"


def test_no_targets_or_deadlines_were_supplemented() -> None:
    items = records()
    for record in items:
        # The panel states no numeric target for any item, so every
        # target stays null; the frame's "2023-2026" period label is
        # not a per-promise deadline and was not recorded as one.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_childcare_fee_expansion_is_not_linked_to_plan_projects() -> None:
    items = {record["id"]: record for record in records()}
    fee = items[f"{TERM_ID}-promise-005"]
    # Expanding free childcare/medical coverage is a different measure
    # from the registered Action Plan projects (the future-creation
    # plan promotion project is a plan vehicle, not the fee measure),
    # so no link is asserted.
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
        for project in load_json("data/reviewed/sapporo-city/projects.json")
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
        if record["id"] == "manifesto-review-jp-local-011002-2023"
    )
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 13
    # The headline, the pillar titles and the biography were
    # deliberately not itemised.
    assert "プロフィール" in review["review_note"]
    assert "レコード化しなかった" in review["review_note"]
