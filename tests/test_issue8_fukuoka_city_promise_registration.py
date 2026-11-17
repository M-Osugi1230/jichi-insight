from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-401307-executive-2022-12-07"
GO2_ID = "fukuoka-city-mayor-manifesto-2022-go2senkyo-archive"
BULLETIN_ID = "fukuoka-city-mayor-election-2022-bulletin"

# The six pillars of "一緒に福岡の未来へ種をまこう", transcribed verbatim
# (heading, then the single paragraph) from the archived 2022-11-16
# article quotation of the candidate homepage, in document order.
# Any wording drift against that text must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "子育てしやすく、こどもの個性や才能を伸ばせるまちへ\n"
    "こどもの医療費をひと月最大で500円までとする「ふくおか安心ワンコイン」などを"
    "進めてきましたが、今後は、多子世帯の負担軽減、困難を抱えるこどもの支援、"
    "生きる力を身につける場づくりなどを進め、次代を担うこどもが生き生きと育つ、"
    "日本の少子化対策のロールモデル都市となることを目指します。",
    "未来の福岡に向けた交通環境づくり\n"
    "強みである博多駅、博多港、福岡空港の近接性をいかし、市内主要拠点や"
    "自然豊かな観光資源などへのアクセス強化に向けた交通ネットワークの検討に"
    "取り組みます。また、生活交通の確保や最寄り駅・バス停までの利便性の高い"
    "交通環境づくりを進めます。",
    "経済復活「とりもどせ元気！」\n"
    "ポストコロナ。さあ、ここからは経済を回すときです。厳しい状況にある商店街・"
    "中小企業を応援するとともに、スタートアップ支援や国際金融機能の誘致を"
    "進めます。また、世界水泳福岡大会を成功させ、観光振興やMICE誘致に繋げます。"
    "同時に、水素活用をはじめとする脱炭素化を推進し、地球環境を守りながら、"
    "持続可能な経済成長を目指します。",
    "誰もが安心して暮らせる、ユニバーサル都市\n"
    "インクルーシブな遊び場づくりや街なかへのベンチの設置、多様性が認められる"
    "社会づくりなど、「ユニバーサル都市・福岡」を推進します。高齢者の社会参加や"
    "健康増進、認知症にやさしいまちづくりなど、人生100年時代を見据えた取組みを"
    "進めます。",
    "エリアごとの個性を活かしたまちづくり\n"
    "最新のオフィスビルへ建替えが進む天神や博多では、緑や水辺、アートを活かした"
    "空間づくりを行います。また、豊かな自然を楽しめる環境づくり、農山漁村地域の"
    "活性化など、地域の多彩な個性を伸ばします。",
    "感染症に強く、地域が絆で結ばれた安全で快適なまちへ\n"
    "市民病院の機能強化や大学との連携等により感染症対策の拠点都市づくりを"
    "進めます。区役所の機能強化や地域活動の支援、一人一花運動など、"
    "地域コミュニティづくりを推進します。災害から市民の命と安全、財産を守り、"
    "犯罪や事故が発生しにくい住環境づくりに取り組みます。",
]

EXPECTED_POLICY_AREAS = [
    "childcare_and_childrearing",
    "transport_infrastructure",
    "industry_and_economy",
    "universal_city_and_inclusion",
    "urban_development_and_tourism",
    "safety_and_disaster_prevention",
]

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-001",
    f"{TERM_ID}-promise-003",
    f"{TERM_ID}-promise-004",
    f"{TERM_ID}-promise-005",
    f"{TERM_ID}-promise-006",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        "jp-local-401307-project-2025-child-rights-voice-support",
        "jp-local-401307-project-2025-community-childrearing-support",
    ],
    f"{TERM_ID}-promise-003": [
        "jp-local-401307-project-2025-sme-management-base-strengthening",
        "jp-local-401307-project-2025-food-universal-hospitality",
    ],
    f"{TERM_ID}-promise-004": [
        "jp-local-401307-project-2025-universal-city-promotion",
    ],
    f"{TERM_ID}-promise-005": [
        "jp-local-401307-project-2025-downtown-redevelopment-promotion",
        "jp-local-401307-project-2025-waterfront-redevelopment",
    ],
    f"{TERM_ID}-promise-006": [
        "jp-local-401307-project-2025-fukuoka-points",
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


def test_all_6_pillars_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 7)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-401307"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [GO2_ID, BULLETIN_ID]
        assert record["statement_type"] == "directional_commitment"
        assert record["plain_summary"]
        # The text arrived through a contemporaneous quotation of the
        # candidate homepage, not the homepage's own archived copy, so
        # the record-level grading stays at medium.
        assert record["confidence"] == "medium"
        assert record["review_status"] == "reviewed"


def test_pillar_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_target_was_invented_from_the_text() -> None:
    items = records()
    for record in items:
        # The only numeric-looking element, the 500-yen child medical
        # fee cap in pillar 1, is phrased as an existing measure being
        # continued ("進めてきました"), so it is not a new target.
        assert record["target"] is None
        # Nothing was supplemented from outside the text: no baselines,
        # no deadlines (the term end is never an implicit deadline), no
        # funding statements, and no change explanations.
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None
    first = items[0]
    assert "ひと月最大で500円" in first["original_text"]
    target_claims = [
        claim
        for claim in packets_by_subject()[first["id"]]["claims"]
        if claim["field"] == "target"
    ]
    assert len(target_claims) == 1
    assert "継続言及" in target_claims[0]["statement"]


def test_progress_states_are_evidence_gated() -> None:
    items = records()
    in_progress = {
        record["id"] for record in items if record["progress_state"] == "in_progress"
    }
    assert in_progress == IN_PROGRESS_IDS
    for record in items:
        if record["id"] not in IN_PROGRESS_IDS:
            # Unassessed is never converted into "not started" or a score.
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
        for project in load_json("data/reviewed/fukuoka-city/projects.json")
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


def test_every_promise_has_one_packet_with_provenance_caveat() -> None:
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
        # The quotation-based provenance and the medium grading travel
        # with every item.
        assert "引用" in provenance["statement"]
        assert "medium" in provenance["statement"]
        assert packet["open_questions"]
