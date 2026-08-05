from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_oita.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/44.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_oita_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_oita_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_oita", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_manifest_source_and_summary_reconcile():
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
        if item["prefecture_code"] == "44"
    )
    reviewed_rows = [item["reviewed_row_count"] for item in source["documents"]]
    assert len(source["records"]) == 159
    assert source["reviewed_target_statement_count"] == 159
    assert source["evidence_packet_count"] == 159
    assert len(source["documents"]) == 6
    assert source["landing_audit"]["selected_document_count"] == 6
    assert reviewed_rows == [8, 5, 0, 0, 146, 0]
    assert sum(reviewed_rows) == 159
    assert sum(count == 0 for count in reviewed_rows) == 3
    assert summary["reviewed_target_statement_count"] == 159
    assert summary["evidence_packet_count"] == 159
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0


def test_all_records_validate_and_preserve_source_fields():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 160))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 160))
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    for source, record in zip(source_records, records, strict=True):
        assert list(validator.iter_errors(record)) == []
        note = json.loads(record["indicator_context"]["quality_note"])
        plan = next(
            item for item in record["measurements"] if item["role"] == "plan_current"
        )
        assert plan["value_text"] == source["target_statement_original"]
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


def test_document_and_version_boundaries_remain_explicit():
    source = load(SOURCE_PATH)
    counts = Counter(item["source_document_sha256"] for item in source["records"])
    assert [counts[item["sha256"]] for item in source["documents"]] == [8, 5, 0, 0, 146, 0]
    for record in catalog()["records"]:
        assert "概要1ペーパー8行" in record["boundary"]
        assert "概要版5行" in record["boundary"]
        assert "全体版146行" in record["boundary"]
        assert "3資料の0行状態" in record["boundary"]
        assert "旧プラン2015" in record["boundary"]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        by_role = {item["role"]: item for item in record["measurements"]}
        assert by_role["annual_actual"]["status"] == "not_available"
        assert by_role["final_target"]["status"] == "not_available"


def test_summary_and_determinism_are_exact():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    titles = Counter(item["source_document_title"] for item in source_records)
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 159,
        "linked_record_count": 0,
        "partial_record_count": 159,
        "not_linked_record_count": 0,
        "indicator_series_count": 159,
        "source_document_count": len(titles),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 159,
        "policy_achievement_assessment_count": 0,
    }
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
