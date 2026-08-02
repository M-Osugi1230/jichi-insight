from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_tochigi.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/09.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_tochigi_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_tochigi_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_tochigi", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_manifest_and_phase9_counts_reconcile():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "shared_normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()

    source = load(SOURCE_PATH)
    summary = next(item for item in load(SUMMARY_PATH)["records"] if item["prefecture_code"] == "09")
    assert len(source["records"]) == 257
    assert source["reviewed_target_statement_count"] == 257
    assert source["evidence_packet_count"] == 257
    assert summary["reviewed_target_statement_count"] == 257
    assert summary["evidence_packet_count"] == 257
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0


def test_all_records_validate_and_preserve_every_source_field():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(load(RECORD_SCHEMA_PATH), format_checker=FormatChecker())
    assert [item["display_order"] for item in source_records] == list(range(1, 258))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 258))
    assert [item["source_record_id"] for item in records] == [item["id"] for item in source_records]
    assert len({item["id"] for item in records}) == 257

    source_by_id = {item["id"]: item for item in source_records}
    for record in records:
        assert list(validator.iter_errors(record)) == []
        source = source_by_id[record["source_record_id"]]
        note = json.loads(record["indicator_context"]["quality_note"])
        plan = next(item for item in record["measurements"] if item["role"] == "plan_current")
        assert plan["value_text"] == source["target_statement_original"]
        assert plan["components"][0]["unit"] == source["unit_original"]
        for field in (
            "source_document_url", "source_document_sha256", "source_location",
            "numeric_tokens_original", "period_tokens_original", "matched_keywords",
            "keyword_match_kind", "unit_original", "population_scope_original",
            "aggregation_scope", "target_operator", "comparability",
        ):
            assert note[field] == source[field]
        assert record["evidence"]["primary_page"] == source["source_location"]["page"]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        by_role = {item["role"]: item for item in record["measurements"]}
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert by_role["annual_actual"]["status"] == "not_available"
        assert by_role["final_target"]["status"] == "not_available"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "計画履歴" in record["boundary"]


def test_dynamic_counts_and_determinism():
    source_records = load(SOURCE_PATH)["records"]
    normalized = catalog()
    documents = Counter(item["source_document_title"] for item in source_records)
    locations = Counter(item["source_location"]["location_kind"] for item in source_records)
    missing_units = sum(item["unit_original"] is None for item in source_records)
    assert normalized["summary"] == {
        "record_count": 257,
        "linked_record_count": 0,
        "partial_record_count": 257,
        "not_linked_record_count": 0,
        "indicator_series_count": 257,
        "source_document_count": 6,
        "missing_unit_record_count": missing_units,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 257,
        "policy_achievement_assessment_count": 0,
    }
    assert len(documents) == 6
    assert normalized["document_record_counts"] == dict(sorted(documents.items()))
    assert normalized["source_location_counts"] == dict(sorted(locations.items()))
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
