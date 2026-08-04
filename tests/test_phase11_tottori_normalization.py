from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_tottori.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/31.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_tottori_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_tottori_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_tottori", SCRIPT_PATH)
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
    source = load(SOURCE_PATH)
    summary = next(
        item for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "31"
    )
    assert len(source["records"]) == 91
    assert source["reviewed_target_statement_count"] == 91
    assert source["evidence_packet_count"] == 91
    assert source["landing_audit"]["selected_document_count"] == 2
    assert [item["reviewed_row_count"] for item in source["documents"]] == [4, 87]
    assert summary["reviewed_target_statement_count"] == 91
    assert summary["evidence_packet_count"] == 91
    assert summary["document_count"] == 2
    assert summary["extraction_error_count"] == 0


def test_all_records_validate_and_preserve_source_fields():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(range(1, 92))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 92))
    source_by_id = {item["id"]: item for item in source_records}
    for record in records:
        assert list(validator.iter_errors(record)) == []
        source = source_by_id[record["source_record_id"]]
        note = json.loads(record["indicator_context"]["quality_note"])
        plan = next(
            item for item in record["measurements"] if item["role"] == "plan_current"
        )
        assert plan["value_text"] == source["target_statement_original"]
        assert note["source_document_sha256"] == source["source_document_sha256"]
        assert note["source_location"] == source["source_location"]
        assert note["numeric_tokens_original"] == source["numeric_tokens_original"]
        assert note["period_tokens_original"] == source["period_tokens_original"]
        assert note["comparability"] == source["comparability"]


def test_document_and_version_boundaries_remain_conservative():
    source = load(SOURCE_PATH)
    counts = Counter(item["source_document_title"] for item in source["records"])
    assert sorted(counts.values()) == [4, 87]
    for record in catalog()["records"]:
        assert record["linkage_status"] == "partial"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        by_role = {item["role"]: item for item in record["measurements"]}
        assert by_role["annual_actual"]["status"] == "not_available"
        assert by_role["final_target"]["status"] == "not_available"
        assert "旧戦略" in record["boundary"]
        assert "Society5.0" in record["boundary"]
        assert "政策達成" in record["boundary"]


def test_summary_and_determinism_are_exact():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    titles = Counter(item["source_document_title"] for item in source_records)
    locations = Counter(item["source_location"]["location_kind"] for item in source_records)
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 91,
        "linked_record_count": 0,
        "partial_record_count": 91,
        "not_linked_record_count": 0,
        "indicator_series_count": 91,
        "source_document_count": len(titles),
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 91,
        "policy_achievement_assessment_count": 0,
    }
    assert normalized["document_record_counts"] == dict(sorted(titles.items()))
    assert normalized["source_location_counts"] == dict(sorted(locations.items()))
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
