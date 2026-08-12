from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part2.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part2_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_project_batch2_advances_coverage_to_six_of_108():
    catalog = load(CATALOG_PATH)
    summary = catalog["summary"]

    assert catalog["official_code"] == "041009"
    assert summary == {
        "prior_reviewed_record_count": 3,
        "batch_reviewed_record_count": 3,
        "cumulative_reviewed_record_count": 6,
        "total_source_project_count": 108,
        "remaining_record_count": 102,
        "complete": False,
    }
    assert [record["sequence_within_batch"] for record in catalog["records"]] == [1, 2, 3]


def test_sendai_challenge_project_batch2_preserves_exact_identity_and_ratings():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}

    coastal = records["coastal_area_revitalization"]
    assert coastal["project_name_ja"] == "海浜エリア活性化事業"
    assert coastal["responsible_bureau_ja"] == "文化観光局・宮城野区・若林区"
    assert coastal["lead_section_ja"] == "若林区 海浜エリア活性化企画室"
    assert coastal["source_pdf_page_index_0_based"] == 9
    assert coastal["source_reported_evaluation"] == "triangle"

    relocation = records["eastern_relocation_site_utilization"]
    assert relocation["project_name_ja"] == "東部地域移転跡地利活用推進事業"
    assert relocation["responsible_bureau_ja"] == "都市整備局"
    assert relocation["lead_section_ja"] == "市街地整備課"
    assert relocation["source_pdf_page_index_0_based"] == 10
    assert relocation["source_reported_evaluation"] == "circle"

    park = records["coastal_park_development"]
    assert park["project_name_ja"] == "海岸公園整備事業"
    assert park["responsible_bureau_ja"] == "建設局"
    assert park["lead_section_ja"] == "公園整備課"
    assert park["source_pdf_page_index_0_based"] == 11
    assert park["source_reported_evaluation"] == "circle"

    assert all(
        record["project_group_ja"] == "杜と水の都プロジェクト"
        for record in records.values()
    )
    assert all(
        record["subsection_ja"] == "海浜エリア活性化"
        for record in records.values()
    )


def test_sendai_challenge_project_batch2_has_one_to_one_page_evidence():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]

    assert len(packets) == len(catalog["records"]) == 3
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }
    assert {packet["evidence_id"] for packet in packets} == {
        record["evidence_id"] for record in catalog["records"]
    }
    assert all(packet["evidence_status"] == "reviewed" for packet in packets)
    assert {packet["source_pdf_page_index_0_based"] for packet in packets} == {9, 10, 11}


def test_sendai_challenge_project_batch2_keeps_source_ratings_bounded():
    catalog = load(CATALOG_PATH)
    ratings = [record["source_reported_evaluation"] for record in catalog["records"]]

    assert ratings.count("triangle") == 1
    assert ratings.count("circle") == 2
    assert "not converted into Jichi Insight scores" in catalog["quality_boundary"]
    assert catalog["summary"]["remaining_record_count"] == 102
    assert all("achievement_score" not in record for record in catalog["records"])


def test_sendai_manifest_records_batch2_without_freezing_later_cumulative_progress():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    batch2 = facts["sendai-challenge-project-records-part2"]
    batches = [
        fact
        for fact in manifest["reviewed_facts"]
        if fact["id"].startswith("sendai-challenge-project-records-part")
    ]
    cumulative_reviewed = sum(fact["value"] for fact in batches)

    assert manifest["status"] == "review_in_progress"
    assert batch2["value"] == 3
    assert batch2["cumulative_value"] == 6
    assert batch2["source_reported_breakdown"] == {"triangle": 1, "circle": 2}
    assert "残り102事業" in batch2["interpretation_boundary"]
    assert cumulative_reviewed >= 6
    assert cumulative_reviewed <= 108
    assert "108/108完了" in manifest["remaining_work"][0]
    assert "成果値・KPI・実績記述" in manifest["remaining_work"][0]
