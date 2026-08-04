from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_nara.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/29.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_nara_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_nara_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_nara", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_manifest_and_phase9_source_reconcile():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "shared_normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()

    source = load(SOURCE_PATH)
    summary = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "29"
    )
    assert len(source["records"]) == 59
    assert source["reviewed_target_statement_count"] == 59
    assert source["evidence_packet_count"] == 59
    assert len(source["documents"]) == 1
    assert source["documents"][0]["reviewed_row_count"] == 59
    assert source["landing_audit"]["landing_status_code"] == 200
    assert source["landing_audit"]["landing_content_type"] == "application/pdf"
    assert summary["reviewed_target_statement_count"] == 59
    assert summary["evidence_packet_count"] == 59
    assert summary["document_count"] == 1
    assert summary["extraction_error_count"] == 0


def test_all_59_records_validate_and_preserve_order():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 60))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 60))
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in records}) == 59
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_source_fields_and_locations_are_retained_exactly():
    source_by_id = {item["id"]: item for item in load(SOURCE_PATH)["records"]}
    normalized_by_id = {
        item["source_record_id"]: item for item in catalog()["records"]
    }
    for source_id, source in source_by_id.items():
        record = normalized_by_id[source_id]
        note = json.loads(record["indicator_context"]["quality_note"])
        plan = next(
            item for item in record["measurements"] if item["role"] == "plan_current"
        )
        assert plan["value_text"] == source["target_statement_original"]
        assert plan["components"][0]["unit"] == source["unit_original"]
        for field in (
            "source_document_url",
            "source_document_sha256",
            "source_location",
            "numeric_tokens_original",
            "period_tokens_original",
            "matched_keywords",
            "keyword_match_kind",
            "unit_original",
            "population_scope_original",
            "aggregation_scope",
            "target_operator",
            "comparability",
        ):
            assert note[field] == source[field]
        assert record["evidence"]["primary_page"] == source["source_location"]["page"]


def test_policy_table_boundaries_remain_conservative():
    records = catalog()["records"]
    for record in records:
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        by_role = {item["role"]: item for item in record["measurements"]}
        assert by_role["annual_actual"]["status"] == "not_available"
        assert by_role["final_target"]["status"] == "not_available"
        assert "基準値" in record["boundary"]
        assert "全国平均" in record["boundary"]
        assert "政策達成" in record["boundary"]


def test_summary_is_exact_and_normalization_is_deterministic():
    normalized = catalog()
    source_records = load(SOURCE_PATH)["records"]
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 59,
        "linked_record_count": 0,
        "partial_record_count": 59,
        "not_linked_record_count": 0,
        "indicator_series_count": 59,
        "source_document_count": 1,
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 59,
        "policy_achievement_assessment_count": 0,
    }
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
