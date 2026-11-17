from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "jp-local-401005-executive-2023-02-20"
MANIFESTO_ID = "kitakyushu-mayor-candidate-2023-manifesto-v13-archive"

# The 34 small items of the "7つの基本政策", transcribed verbatim from the
# archived policy PDF (v13, snapshot of 2023-01-11), pp. 12-13, in document
# order. Any wording drift against the primary text must fail here.
EXPECTED_ORIGINAL_TEXTS: list[str] = [
    "「行政コストの削減」への市長報酬1割カット、議員報酬見直し要請、公共施設運営・維持見直し（進捗管理）",
    "「官民財政再建チーム」を結成し、民間目線で財政運営の見直し",
    "データ分析（EBPM）、マーケティングによる事業・予算見直し",
    "既得権化している契約方式・補助金の見直し、不当要求の撲滅",
    "デジタル決済など行政手続き簡素化、LINEの市民参加型通報システム、「縦割り・お役所対応」の解消",
    "「いつでも待機児童ゼロ」へ、保育所送迎ステーション事業の試行、町ぐるみで保育士を守り育てる仕組み",
    "子育てサポート施設（産前産後ケア・病児保育）の増設、女性のヘルスケア継続支援システム",
    "「子育てバリアフリー計画」による子ども連れ施設、遊び場、ケア環境、\"本気の体験ができる場所\"等の整備、地域で子どもを育てる「子ども憲章」の制定",
    "放課後活動の充実など学校施設を活用した「遊び・学び」の活動支援、不登校対策、給食の質と量の向上、教員の負担軽減",
    "運動と食、家庭医機能・認知症予防で「健康で長生き」を実現",
    "地域や在宅での看護機能の発揮・充実、介護職のイメージ・地位の向上、口腔ケア推進、薬局機能の強化支援",
    "高齢者の在宅生活を全面サポート（バス・モノレールの充実、住まいのセーフティネット、在宅医療環境、孤立対策）",
    "ジェンダー格差是正、シングルマザー、ヤングケアラーの支援",
    "地域・コミュニティ活動の支援（自治会加入促進、負担軽減）",
    "市民センターの機能強化・多目的利用化",
    "「空き家問題」の対策強化（売却・改修・活用を官民タッグで）",
    "地域資源を活かしたまちづくり（小倉・黒崎の再開発加速、若松の観光地化、国家戦略特区規制緩和、民間投資の促進等）",
    "若者が集う「eスポーツ拠点」の整備、サブカルの振興",
    "「英語教育特区」「英語特化型小中一貫校」の創設",
    "若年世代の移住・定住政策の抜本的強化（伴走型の起業支援、最先端の理工系教育、ベッドタウン化戦略）",
    "農山村のマルチ活用（稼ぐ農業、住宅、観光、教育等）推進",
    "ギラヴァンツJ1昇格目指した経営支援強化、北九州市民球場の整備支援など「スポーツ都市戦略」を策定",
    "空港・港湾を最大限活用したアジアをリードする物流拠点化",
    "洋上風力・潮流発電など再生可能エネルギー施設の整備・拠点化",
    "充実した都市インフラ・災害の少なさを強みに国内外企業の積極的誘致・投資促進、中小企業経営支援、後継者確保・海外展開支援",
    "技術、デザイン、経営を学ぶ環境、企業マッチング、資金とカルチャーが集う「ものづくり起業地帯」の創造",
    "野心的な次世代産業（IT・宇宙・半導体）の誘致・育成に着手",
    "北九州市立大学への支援強化",
    "災害時の避難体制の強化、シェルター整備の検討",
    "半グレ対策、暴力団対策の徹底推進、AI防犯の試行",
    "浸水・治水対策のインフラ整備促進",
    "通学路の安全対策強化、ヒヤリハットマップ、防犯カメラを増設",
    "民間マーケティング手法を活用した広報戦略",
    "「挑戦する取組み」で明るいニュースを全国展開、国内や世界への市長トップセールス"
]

PILLAR_COUNTS = {
    "fiscal_administrative_reform": 5,
    "childcare_and_childrearing": 4,
    "health_welfare_and_community": 7,
    "urban_development_and_tourism": 6,
    "industry_and_economy": 6,
    "safety_and_disaster_prevention": 4,
    "city_image_and_public_relations": 2,
}

IN_PROGRESS_IDS = {
    f"{TERM_ID}-promise-005",
    f"{TERM_ID}-promise-013",
    f"{TERM_ID}-promise-020",
    f"{TERM_ID}-promise-029",
    f"{TERM_ID}-promise-033",
    f"{TERM_ID}-promise-034",
}

EXPECTED_LINKS = {
    f"{TERM_ID}-promise-005": [
        "jp-local-401005-project-2024-sumaraku-ward-office",
        "jp-local-401005-project-2024-information-dissemination",
    ],
    f"{TERM_ID}-promise-013": [
        "jp-local-401005-project-2024-women-perspective-policy",
    ],
    f"{TERM_ID}-promise-020": [
        "jp-local-401005-project-2024-shin-jidai-youth-challenge",
    ],
    f"{TERM_ID}-promise-029": [
        "jp-local-401005-project-2024-community-shelter-operation",
        "jp-local-401005-project-2024-disaster-stockpile",
    ],
    f"{TERM_ID}-promise-033": [
        "jp-local-401005-project-2024-city-promotion",
        "jp-local-401005-project-2024-information-dissemination",
    ],
    f"{TERM_ID}-promise-034": [
        "jp-local-401005-project-2024-city-promotion",
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


def promises() -> list[dict[str, Any]]:
    # Scoped to this term: the registry also holds other terms' records.
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


def test_all_34_items_registered_verbatim_in_document_order() -> None:
    records = promises()
    assert [record["original_text"] for record in records] == EXPECTED_ORIGINAL_TEXTS
    assert [record["id"] for record in records] == [
        f"{TERM_ID}-promise-{index:03d}" for index in range(1, 35)
    ]
    for record in records:
        assert_valid("schemas/promise.schema.json", record)
        assert record["municipality_id"] == "jp-local-401005"
        assert record["executive_term_id"] == TERM_ID
        assert record["sources"] == [MANIFESTO_ID]
        assert record["plain_summary"]
        assert "政策PDF" in record["source_location"]


def test_pillar_distribution_and_statement_types() -> None:
    records = promises()
    counts: dict[str, int] = {}
    for record in records:
        counts[record["policy_area"]] = counts.get(record["policy_area"], 0) + 1
    assert counts == PILLAR_COUNTS
    types = [record["statement_type"] for record in records]
    assert types.count("specific_commitment") == 8
    assert types.count("directional_commitment") == 26
    # No pillar heading or contextual statement became a promise record.
    assert "vision" not in types
    assert "supporting_context" not in types


def test_quality_dimensions_record_text_facts_only() -> None:
    records = {record["id"]: record for record in promises()}
    # Numeric targets are recorded only where the manifesto text states
    # them: the mayoral salary cut (item 1) and zero waiting children
    # (item 6). The Giravanz J1 promotion is the club's aim, not a target.
    assert records[f"{TERM_ID}-promise-001"]["target"] == "市長報酬1割カット"
    assert records[f"{TERM_ID}-promise-006"]["target"] == "いつでも待機児童ゼロ"
    for record in records.values():
        if record["id"] not in {
            f"{TERM_ID}-promise-001",
            f"{TERM_ID}-promise-006",
        }:
            assert record["target"] is None
        # Nothing was supplemented from outside the text: no baselines, no
        # deadlines (the term end is never an implicit deadline), no
        # funding statements, and no change explanations.
        assert record["baseline"] is None
        assert record["deadline"] is None
        assert record["funding_statement"] is None
        assert record["change_explanation"] is None


def test_progress_states_are_evidence_gated() -> None:
    records = promises()
    in_progress = {
        record["id"] for record in records if record["progress_state"] == "in_progress"
    }
    assert in_progress == IN_PROGRESS_IDS
    for record in records:
        if record["id"] not in IN_PROGRESS_IDS:
            # Unassessed is never converted into "not started" or a score.
            assert record["progress_state"] == "not_assessable"
        else:
            assert record["related_project_ids"]


def test_project_links_are_exact_and_capped_at_inferred() -> None:
    records = {record["id"]: record for record in promises()}
    for promise_id, project_ids in EXPECTED_LINKS.items():
        assert records[promise_id]["related_project_ids"] == project_ids
    for record in records.values():
        if record["id"] not in EXPECTED_LINKS:
            assert record["related_project_ids"] == []
    packets = packets_by_subject()
    for promise_id in EXPECTED_LINKS:
        claims = {claim["field"]: claim for claim in packets[promise_id]["claims"]}
        link_claim = claims["related_project_ids"]
        assert link_claim["decision"] == "needs_review"
        assert "low / inferred" in link_claim["review_note"]
        progress_claim = claims["progress_state"]
        assert progress_claim["decision"] == "needs_review"


def test_every_promise_has_one_packet_with_version_caveat() -> None:
    records = promises()
    packets = packets_by_subject()
    assert set(packets) == {record["id"] for record in records}
    for record in records:
        packet = packets[record["id"]]
        assert_valid("schemas/evidence_packet.schema.json", packet)
        fields = [claim["field"] for claim in packet["claims"]]
        assert "original_text" in fields
        version = next(
            claim for claim in packet["claims"] if claim["field"] == "source_version"
        )
        # The v13 basis and the unverified V15 diff travel with every item.
        assert "V15" in version["statement"]
        assert "最終版とは扱わない" in version["statement"]
        assert packet["open_questions"]
