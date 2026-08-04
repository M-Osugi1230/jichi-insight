from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_gifu.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/21.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_gifu_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_gifu_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_gifu", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_manifest_source_and_phase9_summary_reconcile():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(manifest)) == []
    for field in (
        "source_catalog",
        "normalizer",
        "shared_normalizer",
        "record_schema",
    ):
        assert (ROOT / manifest[field]).exists()

    source = load(SOURCE_PATH)
    summary = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "21"
    )
    assert len(source["records"]) == 1500
    assert source["reviewed_target_statement_count"] == 1500
    assert source["evidence_packet_count"] == 1500
    assert len(source["documents"]) == 6
    assert source["landing_audit"]["selected_document_count"] == 6
    assert sum(item["reviewed_row_count"] for item in source["documents"]) == 1500
    assert summary["reviewed_target_statement_count"] == 1500
    assert summary["evidence_packet_count"] == 1500
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0
    assert manifest["document_boundary"] == {
        "registered_document_count": 6,
        "canonical_record_count": 1500,
    }


def test_all_1500_records_validate_and_preserve_sequence():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 1501))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 1501))
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in records}) == 1500
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_every_source_field_and_evidence_location_are_retained():
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


def test_document_registry_and_record_usage_are_consistent():
    source = load(SOURCE_PATH)
    registered_hashes = {item["sha256"] for item in source["documents"]}
    used_hashes = {item["source_document_sha256"] for item in source["records"]}
    nonzero_hashes = {
        item["sha256"]
        for item in source["documents"]
        if item["reviewed_row_count"] > 0
    }
    assert len(registered_hashes) == 6
    assert used_hashes == nonzero_hashes
    assert used_hashes <= registered_hashes
    assert catalog()["sources"][0]["document_count"] == 6


def test_hierarchy_evaluation_and_series_boundaries_are_preserved():
    for record in catalog()["records"]:
        assert "戦略、政策・施策、KPI、実施計画、事業評価、年次進捗" in record["boundary"]
        assert "現況値、基準値、目標値、単年度実績、累計、参考値、全国値" in record["boundary"]
        assert "予算・決算・事業費" in record["boundary"]
        by_role = {item["role"]: item for item in record["measurements"]}
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert by_role["annual_actual"]["status"] == "not_available"
        assert by_role["final_target"]["status"] == "not_available"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_dynamic_document_location_and_unit_counts_are_exact():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    used_titles = Counter(item["source_document_title"] for item in source_records)
    locations = Counter(
        item["source_location"]["location_kind"] for item in source_records
    )
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 1500,
        "linked_record_count": 0,
        "partial_record_count": 1500,
        "not_linked_record_count": 0,
        "indicator_series_count": 1500,
        "source_document_count": len(used_titles),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1500,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(used_titles.items()))
    assert normalized["source_location_counts"] == dict(sorted(locations.items()))


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
