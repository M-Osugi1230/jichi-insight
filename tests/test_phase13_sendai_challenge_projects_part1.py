from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part1.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part1_evidence.json"
SOURCE_PATH = ROOT / "data/catalog/sendai_phase13_sources.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_project_batch_reviews_exactly_three_of_108_projects():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]

    assert catalog["official_code"] == "041009"
    assert catalog["reporting_fiscal_year"] == 2024
    assert catalog["status"] == "reviewed_core_evaluation_batch"
    assert summary == {
        "total_source_project_count": 108,
        "reviewed_record_count": 3,
        "remaining_record_count": 105,
        "complete": False,
    }
    assert [record["sequence_within_batch"] for record in records] == [1, 2, 3]
    assert len({record["id"] for record in records}) == 3


def test_sendai_challenge_project_batch_preserves_exact_identity_and_source_rating():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    city_hall = records["new_city_hall_development"]
    assert city_hall["project_name_ja"] == "新本庁舎整備事業"
    assert city_hall["responsible_bureau_ja"] == "財政局"
    assert city_hall["lead_section_ja"] == "本庁舎整備室"
    assert city_hall["source_pdf_page_index_0_based"] == 6

    nishi = records["nishi_park_redevelopment"]
    assert nishi["project_name_ja"] == "西公園再整備事業"
    assert nishi["responsible_bureau_ja"] == "建設局"
    assert nishi["lead_section_ja"] == "公園整備課"
    assert nishi["source_pdf_page_index_0_based"] == 7

    kotodai = records["kotodai_park_surroundings_redevelopment"]
    assert kotodai["project_name_ja"] == "勾当台公園及び周辺再整備事業"
    assert kotodai["responsible_bureau_ja"] == "建設局"
    assert kotodai["lead_section_ja"] == "公園整備課"
    assert kotodai["source_pdf_page_index_0_based"] == 7

    assert all(
        record["project_group_ja"] == "杜と水の都プロジェクト"
        for record in records.values()
    )
    assert all(
        record["subsection_ja"] == "勾当台・定禅寺通エリア活性化"
        for record in records.values()
    )
    assert all(
        record["source_reported_evaluation"] == "circle"
        for record in records.values()
    )
    assert all(
        record["review_status"] == "reviewed_core_evaluation"
        for record in records.values()
    )


def test_sendai_challenge_project_rating_scale_remains_municipality_reported():
    catalog = load(CATALOG_PATH)

    assert catalog["source_reported_rating_scale"] == {
        "double_circle": "予定を上回る成果が出ている",
        "circle": "予定どおり進んでいる",
        "triangle": "一部にやや遅れが出ている",
        "cross": "遅れている",
    }
    assert "source-reported self-evaluation" in catalog["quality_boundary"]
    assert "not converted into a Jichi Insight achievement score" in catalog[
        "quality_boundary"
    ]
    assert all("achievement_score" not in record for record in catalog["records"])


def test_sendai_challenge_project_batch_has_one_to_one_evidence():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    records = catalog["records"]
    packets = evidence["evidence_packets"]

    assert evidence["source"]["page_count"] == 126
    assert evidence["source"]["review_method"] == "record_level_pdf_review"
    assert len(packets) == len(records) == 3
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in records
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in records
    }
    assert all(packet["evidence_status"] == "reviewed" for packet in packets)
    assert all(
        "independent achievement judgment" in packet["boundary"]
        for packet in packets
    )


def test_sendai_challenge_project_source_and_manifest_stay_partial():
    sources = {record["id"]: record for record in load(SOURCE_PATH)["records"]}
    source = sources["sendai-city-challenge-project-self-evaluation-2024-report"]
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    batch = facts["sendai-challenge-project-records-part1"]

    assert source["page_count"] == 126
    assert source["review_status"] == "partial_record_review_in_progress"
    assert batch["value"] == 3
    assert batch["review_status"] == "reviewed_core_evaluation"
    assert "残り105事業" in batch["interpretation_boundary"]
    assert manifest["status"] == "review_in_progress"
    assert "3事業を個票レビュー済み" in manifest["remaining_work"][0]
