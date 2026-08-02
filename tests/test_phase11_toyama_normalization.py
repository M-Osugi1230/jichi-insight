from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_toyama.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/16.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = (
    ROOT / "schemas/phase11_record_linkage_source_location.schema.json"
)
MANIFEST_PATH = ROOT / "data/catalog/phase11_toyama_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_toyama_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_toyama", SCRIPT_PATH
)
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
    for field in ("source_catalog", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()

    source = load(SOURCE_PATH)
    summary = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "16"
    )
    assert len(source["records"]) == 1
    assert source["reviewed_target_statement_count"] == 1
    assert source["evidence_packet_count"] == 1
    assert len(source["documents"]) == 1
    assert source["documents"][0]["content_type"] == "text/html"
    assert source["documents"][0]["reviewed_row_count"] == 1
    assert source["landing_audit"]["selected_document_count"] == 1
    assert summary["reviewed_target_statement_count"] == 1
    assert summary["evidence_packet_count"] == 1
    assert summary["document_count"] == 1
    assert summary["extraction_error_count"] == 0


def test_single_record_validates_against_locator_aware_schema():
    record = catalog()["records"][0]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(record)) == []
    assert record["id"] == "phase11-record-toyama-0001"
    assert record["prefecture_code"] == "16"
    assert record["source_record_id"] == "phase9-16-target-0001"


def test_html_row_is_never_converted_to_a_fake_page():
    source_location = {
        "location_kind": "html_text_line",
        "row": 79,
    }
    source = load(SOURCE_PATH)["records"][0]
    record = catalog()["records"][0]
    plan = next(
        item for item in record["measurements"] if item["role"] == "plan_current"
    )
    assert source["source_location"] == source_location
    assert record["indicator_context"]["source_page"] is None
    assert record["indicator_context"]["source_location"] == source_location
    assert plan["evidence"] == {
        "source_number": 1,
        "page": None,
        "source_location": source_location,
    }
    assert record["evidence"]["primary_page"] is None
    assert record["evidence"]["primary_location"] == source_location
    assert record["evidence"]["locations"] == [
        {
            "source_number": 1,
            "page": None,
            "source_location": source_location,
            "is_reprint": False,
        }
    ]
    assert catalog()["source_location_counts"] == {"html_text_line": 1}


def test_every_source_field_is_retained_in_quality_note():
    source = load(SOURCE_PATH)
    source_record = source["records"][0]
    record = catalog()["records"][0]
    note = json.loads(record["indicator_context"]["quality_note"])
    plan = next(
        item for item in record["measurements"] if item["role"] == "plan_current"
    )
    assert plan["value_text"] == source_record["target_statement_original"]
    assert plan["components"][0]["unit"] == source_record["unit_original"]
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
        assert note[field] == source_record[field]


def test_indicator_creation_explanation_is_not_promoted_to_kpi_value():
    source = load(SOURCE_PATH)["records"][0]
    record = catalog()["records"][0]
    assert "県独自の指標を策定" in source["target_statement_original"]
    assert source["period_tokens_original"] == ["令和4年", "令和5年"]
    assert source["population_scope_original"] == "県民"
    assert record["linkage_status"] == "partial"
    assert record["partial_reason"] == "html_explanation_not_structured_indicator_value"
    by_role = {item["role"]: item for item in record["measurements"]}
    assert by_role["annual_actual"]["status"] == "not_available"
    assert by_role["final_target"]["status"] == "not_available"
    assert record["evaluation_status"] == "not_assessed"
    assert record["comparability_status"] == "excluded_until_verified"
    assert "12政策分野" in record["boundary"]
    assert "100政策評価" in record["boundary"]
    assert "初回政策評価は未公表" in record["boundary"]


def test_summary_and_determinism_are_exact():
    normalized = catalog()
    assert normalized["record_schema"] == (
        "schemas/phase11_record_linkage_source_location.schema.json"
    )
    assert normalized["sources"][0]["document_count"] == 1
    assert normalized["summary"] == {
        "record_count": 1,
        "linked_record_count": 0,
        "partial_record_count": 1,
        "not_linked_record_count": 0,
        "indicator_series_count": 1,
        "source_document_count": 1,
        "missing_unit_record_count": 0,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1,
        "policy_achievement_assessment_count": 0,
    }
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
