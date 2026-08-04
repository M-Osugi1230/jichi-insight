from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_nagasaki.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/42.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_nagasaki_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_nagasaki_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_nagasaki", SCRIPT_PATH)
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
        if item["prefecture_code"] == "42"
    )
    candidate_rows = [item["reviewed_row_count"] for item in source["documents"]]
    assert len(source["records"]) == 673
    assert source["reviewed_target_statement_count"] == 673
    assert source["evidence_packet_count"] == 673
    assert len(source["documents"]) == 6
    assert source["landing_audit"]["selected_document_count"] == 7
    assert candidate_rows == [157, 103, 61, 64, 166, 137]
    assert sum(candidate_rows) == 688
    assert sum(candidate_rows) - len(source["records"]) == 15
    assert summary["reviewed_target_statement_count"] == 673
    assert summary["evidence_packet_count"] == 673
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0


def test_all_records_validate_and_preserve_source_fields():
    source = load(SOURCE_PATH)
    source_records = source["records"]
    records = catalog()["records"]
    document_hashes = {item["sha256"] for item in source["documents"]}
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 674))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 674))
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert {item["source_document_sha256"] for item in source_records} <= document_hashes
    for source_record, record in zip(source_records, records, strict=True):
        assert list(validator.iter_errors(record)) == []
        note = json.loads(record["indicator_context"]["quality_note"])
        plan = next(
            item for item in record["measurements"] if item["role"] == "plan_current"
        )
        assert plan["value_text"] == source_record["target_statement_original"]
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


def test_candidate_and_canonical_boundaries_remain_explicit():
    for record in catalog()["records"]:
        assert "合計688件" in record["boundary"]
        assert "canonical673件" in record["boundary"]
        assert "15件を水増ししない" in record["boundary"]
        assert "施策評価" in record["boundary"]
        assert "事業評価" in record["boundary"]
        assert "次期総合計画" in record["boundary"]


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
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 673,
        "linked_record_count": 0,
        "partial_record_count": 673,
        "not_linked_record_count": 0,
        "indicator_series_count": 673,
        "source_document_count": len(
            {item["source_document_title"] for item in source_records}
        ),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 673,
        "policy_achievement_assessment_count": 0,
    }
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
