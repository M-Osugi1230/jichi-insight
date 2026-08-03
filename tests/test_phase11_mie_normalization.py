from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_mie.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/24.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_mie_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_mie_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_mie", SCRIPT_PATH)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)

EXPECTED_DOCUMENT_COUNTS = {
    "プラン（PDF:9.5MB）": 239,
    "参考資料 （PDF:1.6MB）": 324,
    "概要案に対するパブリックコメントの意見と県の考え方（PDF:825KB）": 10,
    "概要案に対する県議会からの申し入れと県の考え方（PDF:788KB）": 11,
}
EXPECTED_ZERO_ROW_DOCUMENTS = {
    "概要版（A3二つ折り PDF1.0MB）",
    "（PDF:2,237KB）",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurements(record: dict) -> dict[str, dict]:
    return {item["role"]: item for item in record["measurements"]}


def test_manifest_matches_schema_and_paths_exist():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "shared_normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_source_reconcile_to_584():
    source = load(SOURCE_PATH)
    summary_entry = next(
        item for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "24"
    )
    assert source["prefecture_code"] == "24"
    assert source["name"] == "三重県"
    assert source["plan_title"] == "みえ元気プラン"
    assert source["plan_period"] == "2022年度～2026年度"
    assert source["reviewed_target_statement_count"] == 584
    assert source["evidence_packet_count"] == 584
    assert len(source["records"]) == 584
    assert summary_entry["reviewed_target_statement_count"] == 584
    assert summary_entry["evidence_packet_count"] == 584
    assert summary_entry["document_count"] == 6
    assert summary_entry["extraction_error_count"] == 0


def test_registered_documents_and_canonical_counts_are_exact():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    reviewed_counts = {item["title"]: item["reviewed_row_count"] for item in source["documents"]}
    canonical_counts = Counter(item["source_document_title"] for item in source["records"])
    zero_rows = {title for title, count in reviewed_counts.items() if count == 0}
    assert dict(sorted(canonical_counts.items())) == EXPECTED_DOCUMENT_COUNTS
    assert zero_rows == EXPECTED_ZERO_ROW_DOCUMENTS
    assert sum(reviewed_counts.values()) == 584
    assert sum(canonical_counts.values()) == 584
    assert manifest["source_document_summary"] == {
        "registered_documents": 6,
        "documents_with_reviewed_candidates": 4,
        "documents_with_canonical_records": 4,
        "documents_without_canonical_records": 2,
        "reviewed_candidate_rows": 584,
        "canonical_records": 584,
        "unique_canonical_source_hashes": 4,
        "pdf_table_row_records": 506,
        "pdf_text_line_records": 78,
    }
    manifest_zero = {
        item["title"] for item in manifest["source_document_inventory"]
        if item["canonical_records"] == 0
    }
    assert manifest_zero == EXPECTED_ZERO_ROW_DOCUMENTS


def test_all_584_records_validate_and_sequences_are_complete():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 585))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 585))
    assert [item["source_record_id"] for item in records] == [item["id"] for item in source_records]
    assert len({item["id"] for item in source_records}) == 584
    assert len({item["evidence_id"] for item in source_records}) == 584
    assert len({item["id"] for item in records}) == 584
    assert all(isinstance(item["source_location"].get("page"), int) for item in source_records)
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_every_reviewed_source_field_is_retained():
    source_by_id = {item["id"]: item for item in load(SOURCE_PATH)["records"]}
    normalized_by_id = {item["source_record_id"]: item for item in catalog()["records"]}
    for source_id, source_record in source_by_id.items():
        record = normalized_by_id[source_id]
        values = measurements(record)
        note = json.loads(record["indicator_context"]["quality_note"])
        page = source_record["source_location"]["page"]
        assert record["subject"]["name"] == source_record["indicator_name_original"]
        assert record["indicator_context"]["source_page"] == page
        assert values["plan_current"]["value_text"] == source_record["target_statement_original"]
        assert values["plan_current"]["components"][0]["unit"] == source_record["unit_original"]
        for field in (
            "source_document_title", "source_document_url", "source_document_sha256",
            "source_location", "numeric_tokens_original", "period_tokens_original",
            "matched_keywords", "keyword_match_kind", "unit_original",
            "population_scope_original", "aggregation_scope", "target_operator",
            "comparability",
        ):
            assert note[field] == source_record[field]
        assert record["evidence"]["primary_page"] == page


def test_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        values = measurements(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        for role in ("annual_actual", "final_target"):
            assert values[role]["status"] == "not_available"
            assert values[role]["components"] == []
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "政策達成" in record["boundary"]


def test_dynamic_counts_locations_units_hashes_and_determinism():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    locations = Counter(item["source_location"]["location_kind"] for item in source_records)
    missing_units = sum(item["unit_original"] is None for item in source_records)
    hashes = {item["source_document_sha256"] for item in source_records}
    assert normalized["summary"] == {
        "record_count": 584,
        "linked_record_count": 0,
        "partial_record_count": 584,
        "not_linked_record_count": 0,
        "indicator_series_count": 584,
        "source_document_count": 4,
        "missing_unit_record_count": 36,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 584,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == EXPECTED_DOCUMENT_COUNTS
    assert dict(sorted(locations.items())) == {"pdf_table_row": 506, "pdf_text_line": 78}
    assert normalized["source_location_counts"] == {"pdf_table_row": 506, "pdf_text_line": 78}
    assert missing_units == 36
    assert len(hashes) == 4
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
