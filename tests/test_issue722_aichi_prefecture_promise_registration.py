"""Issue #722: Aichi Prefecture governor promises (cluster 2, stage 3).

The source is the official 2023 Aichi gubernatorial election bulletin
itself, downloaded directly from the prefectural election commission's
official page. Governor Ohmura's panel (page 1, upper half) is a poster:
a catchphrase, the slogan "人が輝くあいち", ten star-marked policy items
and a career profile. The ten star items are the promise units; the
catchphrase, slogan, profile and illustrations are not promises. Items
with detail text are transcribed as heading + detail text in one record.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-230006-executive-2023-02-15"
BULLETIN_ID = "aichi-pref-governor-election-2023-bulletin"
REVIEW_ID = "manifesto-review-jp-local-230006-2023"
SEARCH_ID = "manifesto-source-search-aichi-pref-2023"

# The ten star-marked items of Governor Ohmura's panel in the official
# 2023 election bulletin (page 1, upper half), transcribed verbatim in
# document order: the two boxed slogans on the first star line, the
# three items with detail text, then the five right-column headings.
# The catchphrase ("日本一元気な愛知をつくり 日本の未来をつくる！"),
# the slogan ("人が輝くあいち") and the career profile are not records.
# Any wording drift against the bulletin must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "ジブリパークの魅力発信",
    "新型コロナウイルス感染症を克服!!",
    (
        "「リニア大交流圏」の形成 〜首都圏・中京圏で5千万人のメガ・リージョンを！"
        "リニア中央新幹線。名古屋駅スーパーターミナル化。高速道路・鉄道ネットワーク。"
        "中部国際空港の2本目滑走路。港湾国際競争力強化。住みやすさ日本一あいちの発信。"
    ),
    (
        "「産業首都あいち」〜国際イノベーション都市へ "
        "国際展示場「Aichi Sky Expo」、国際的なMICE誘致、新たな産業展示会の創出。"
        "スタートアップ・エコシステム「STATION Ai」整備（24年）、世界一の集積・"
        "自動車産業のイノベーション。自動運転、FCV次世代自動車の世界一の拠点化"
        "（開発・生産・普及）。アジアNo.1航空宇宙産業の発展。産業用・サービス"
        "ロボットの社会実装。健康長寿（あいちデジタルヘルスプロジェクト）。"
        "環境、エネルギー、中小企業の振興。商店街の振興（集客力・販売力向上、"
        "コミュニティ機能強化、大型店の地域貢献活動等）。金融・政策減税の強化。"
        "中部最大の農業県・愛知の力をパワーアップ。農林水産業の振興。"
    ),
    (
        "「すべての人が輝くあいち」〜子ども、若者、女性、高齢者、障害のある人など、"
        "全ての人が活躍 教育立県あいち、人財創造あいち。中高一貫校。少人数学級。"
        "魅力ある高校づくり。定時制・通信制リニューアル。夜間中学。特別支援学校。"
        "女性の活躍促進。子ども・子育て支援。医療の充実。健康長寿。認知症医療の強化。"
        "障害者福祉・支援、ノーマライゼーション推進。産業人材育成。"
        "「技能五輪・アビリンピック」。働き方改革、ワーク・ライフ・バランス。"
        "人権施策の推進。"
    ),
    "観光あいち・魅力発信、文化芸術都市、スポーツ王国あいち",
    "あいちのグローバル展開",
    "安全・安心なあいち",
    "環境首都あいち",
    "地方分権・行財政改革、東三河の振興",
]

EXPECTED_POLICY_AREAS = [
    "urban_development_and_tourism",
    "health_welfare_and_safety",
    "transport_infrastructure",
    "industry_and_economy",
    "education_and_human_development",
    "urban_development_and_tourism",
    "international_engagement",
    "safety_and_disaster_prevention",
    "environment_and_climate",
    "fiscal_administrative_reform",
]

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-001",
    f"{TERM_ID}-promise-002",
    f"{TERM_ID}-promise-003",
    f"{TERM_ID}-promise-004",
    f"{TERM_ID}-promise-005",
    f"{TERM_ID}-promise-009",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-001": [
        "jp-local-230006-project-2025-ghibli-park-promotion",
    ],
    f"{TERM_ID}-promise-002": [
        "jp-local-230006-project-2025-infectious-disease-control",
    ],
    f"{TERM_ID}-promise-003": [
        "jp-local-230006-project-2025-transport-measures",
    ],
    f"{TERM_ID}-promise-004": [
        "jp-local-230006-project-2025-station-ai-project",
        "jp-local-230006-project-2025-aichi-sky-expo-management",
    ],
    f"{TERM_ID}-promise-005": [
        "jp-local-230006-project-2025-high-school-education-promotion",
        "jp-local-230006-project-2025-gender-equality-promotion",
        "jp-local-230006-project-2025-child-rearing-support",
        "jp-local-230006-project-2025-worker-welfare-promotion",
    ],
    f"{TERM_ID}-promise-009": [
        "jp-local-230006-project-2025-global-warming-countermeasures",
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


def test_all_10_items_registered_verbatim_in_document_order() -> None:
    items = records()
    assert [record["original_text"] for record in items] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in items] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 11)
    ]
    for record in items:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-230006"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [BULLETIN_ID]
        assert record["statement_type"] == "directional_commitment"
        assert record["plain_summary"]
        # The source is the official election bulletin itself (the top
        # of the source hierarchy), obtained directly from the
        # prefecture's official site, so the record-level grading is
        # high.
        assert record["confidence"] == "high"
        assert record["review_status"] == "reviewed"


def test_policy_area_distribution() -> None:
    items = records()
    assert [record["policy_area"] for record in items] == EXPECTED_POLICY_AREAS


def test_no_target_was_invented_from_the_text() -> None:
    items = records()
    for record in items:
        # The panel states no numeric target, deadline or funding for
        # these items. "5千万人" describes the population scale of the
        # two metropolitan regions, and "（24年）" is the scheduled
        # completion noted for STATION Ai inside the text; neither is
        # supplemented into the structured fields.
        assert record["target"] is None
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_catchphrase_slogan_and_profile_were_not_registered() -> None:
    items = records()
    texts = [record["original_text"] for record in items]
    # The panel's catchphrase, the slogan on its own, and the career
    # profile lines are not promises and may not appear as records.
    assert "日本一元気な愛知をつくり 日本の未来をつくる！" not in texts
    assert "人が輝くあいち" not in texts
    for profile_line in (
        "愛知県碧南市生まれ",
        "衆議院議員初当選",
        "経済産業大臣政務官",
        "愛知県知事3選",
    ):
        assert all(profile_line not in text for text in texts)


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
        for project in load_json("data/reviewed/aichi-prefecture/projects.json")
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
        # The bulletin provenance (official document, direct official
        # hosting, image-based panel) travels with every item.
        assert "選挙公報" in provenance["statement"]
        assert "high" in provenance["statement"]
        assert packet["open_questions"]


def test_review_search_and_term_reflect_the_registration() -> None:
    reviews = load_json("data/entities/executives/manifesto_reviews.json")
    review = next(record for record in reviews if record["id"] == REVIEW_ID)
    assert_valid("schemas/manifesto_review.schema.json", review)
    assert review["source_id"] == BULLETIN_ID
    assert review["review_scope"] == "candidate_panel"
    assert review["segmentation_status"] == "segmented"
    assert review["promise_records_created"] == 10

    searches = load_json("data/entities/executives/manifesto_source_searches.json")
    search = next(record for record in searches if record["id"] == SEARCH_ID)
    assert_valid("schemas/manifesto_source_search.schema.json", search)
    assert search["result_status"] == "source_registered"
    assert search["manifesto_source_ids_found"] == [BULLETIN_ID]
    assert search["nonexistence_claim"] is False

    terms = load_json("data/entities/executives/executive_terms.json")
    term = next(record for record in terms if record["id"] == TERM_ID)
    assert term["manifesto_source_ids"] == [BULLETIN_ID]
    # The term end is registered from the election commission's
    # official announcement; it is still never used as an implicit
    # promise deadline.
    assert term["term_end"] == "2027-02-14"
