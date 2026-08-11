from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_project_source_index_has_exact_official_document_spine():
    index = load(INDEX_PATH)
    fields = index["machizukuri_field_sources"]
    chapter3 = index["chapter3_sources"]

    assert index["official_code"] == "011002"
    assert index["status"] == "source_documents_indexed_project_review_in_progress"
    assert [record["sequence"] for record in fields] == list(range(1, 9))
    assert [(record["field_id"], record["field_ja"]) for record in fields] == [
        ("children_youth", "子ども・若者"),
        ("daily_life", "生活・暮らし"),
        ("community", "地域"),
        ("safety_security", "安全・安心"),
        ("economy", "経済"),
        ("sports_culture", "スポーツ・文化"),
        ("environment", "環境"),
        ("urban_space", "都市空間"),
    ]
    assert [record["sequence"] for record in chapter3] == [1, 2]
    assert [record["source_id"] for record in chapter3] == [
        "administrative_operations",
        "fiscal_operations",
    ]


def test_sapporo_project_source_index_uses_unique_official_sapporo_urls():
    index = load(INDEX_PATH)
    records = index["machizukuri_field_sources"] + index["chapter3_sources"]
    urls = [record["url"] for record in records]

    assert len(urls) == 10
    assert len(set(urls)) == 10
    assert all(url.startswith("https://www.city.sapporo.jp/chosei/documents/") for url in urls)
    assert all(
        record["source_identification_status"] == "official_link_verified"
        for record in records
    )


def test_sapporo_project_source_index_preserves_known_and_pending_page_counts():
    index = load(INDEX_PATH)
    fields = {record["field_id"]: record for record in index["machizukuri_field_sources"]}
    chapter3 = {record["source_id"]: record for record in index["chapter3_sources"]}

    assert fields["children_youth"]["page_count"] == 16
    assert fields["daily_life"]["page_count"] == 13
    assert fields["community"]["page_count"] is None
    assert fields["safety_security"]["page_count"] == 10
    assert fields["economy"]["page_count"] is None
    assert fields["sports_culture"]["page_count"] == 9
    assert fields["environment"]["page_count"] is None
    assert fields["urban_space"]["page_count"] == 12
    assert chapter3["administrative_operations"]["page_count"] == 29
    assert chapter3["fiscal_operations"]["page_count"] is None


def test_sapporo_safety_source_records_first_reviewed_project_batch():
    index = load(INDEX_PATH)
    safety = next(
        record
        for record in index["machizukuri_field_sources"]
        if record["field_id"] == "safety_security"
    )

    assert safety["content_review_status"] == "record_review_in_progress"
    assert safety["reviewed_project_record_count"] == 4
    assert safety["reviewed_page_labels"] == [80]
    assert safety["record_catalog_path"] == (
        "data/catalog/sapporo_action_plan_safety_security_projects_part1.json"
    )
    assert safety["evidence_path"] == (
        "data/evidence/sapporo_action_plan_safety_security_projects_part1_evidence.json"
    )


def test_sapporo_project_source_index_does_not_invent_project_allocation():
    index = load(INDEX_PATH)
    records = index["machizukuri_field_sources"] + index["chapter3_sources"]
    summary = index["summary"]
    aggregate = index["plan_level_aggregate"]

    assert aggregate["planned_project_count"] == 599
    assert aggregate["planned_project_cost_yen"] == 1_785_400_000_000
    assert aggregate["allocation_status"] == "not_allocated_to_source_documents"
    assert summary["total_identified_document_count"] == 10
    assert summary["total_action_plan_project_count"] == 599
    assert summary["per_document_project_counts_reviewed"] == 0
    assert summary["individual_project_records_reviewed"] == 4
    assert summary["project_count_allocation_status"] == "not_allocated_to_documents"
    assert summary["chapter3_denominator_membership_review_status"] == "pending"
    assert all("project_count" not in record for record in records)
    assert all(
        record["project_denominator_membership_status"] == "pending_record_level_review"
        for record in index["chapter3_sources"]
    )


def test_sapporo_project_source_index_keeps_review_boundary_explicit():
    index = load(INDEX_PATH)
    boundary = index["quality_boundary"]

    assert "does not allocate the 599-project denominator" in boundary
    assert "complete safety/security project count" in boundary
    assert "infer project counts from page counts" in boundary
    assert "assume Chapter 3 denominator membership" in boundary
    assert "unseen project rows" in boundary


def test_sapporo_manifest_records_document_index_without_city_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    assert manifest["status"] == "review_in_progress"
    source_index = facts["action-plan-project-source-index"]
    assert source_index["value"] == 10
    assert source_index["registry_path"] == (
        "data/catalog/sapporo_action_plan_project_source_index.json"
    )
    assert "599事業" in source_index["interpretation_boundary"]
    project_batch = facts["action-plan-safety-security-project-records-part1"]
    assert project_batch["value"] == 4
    assert project_batch["source_page_label"] == 80
    assert "4事業" in project_batch["interpretation_boundary"]
    assert any("資料10本" in item and "4事業" in item for item in manifest["remaining_work"])
