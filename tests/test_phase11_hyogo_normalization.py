from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_hyogo.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/28.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_hyogo_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_hyogo_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_hyogo", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


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
    for field in (
        "source_catalog",
        "normalizer",
        "shared_normalizer",
        "record_schema",
    ):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_source_reconcile_to_676():
    source = load(SOURCE_PATH)
    summary = next(
        item
        for item in load(SUMMARY_PATH)["records"]
        if item["prefecture_code"] == "28"
    )
    assert source["name"] == "兵庫県"
    assert source["reviewed_target_statement_count"] == 676
    assert source["evidence_packet_count"] == 676
    assert len(source["records"]) == 676
    assert len(source["documents"]) == 4
    assert summary["reviewed_target_statement_count"] == 676
    assert summary["evidence_packet_count"] == 676
    assert summary["document_count"] == 4
    assert summary["extraction_error_count"] == 0


def test_all_records_validate_and_preserve_source_fields():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert [item["display_order"] for item in source_records] == list(
        range(1, 677)
    )
    assert [item["subject"]["sequence"] for item in records] == list(
        range(1, 677)
    )
    assert [item["source_record_id"] for item in records] == [
        item["id"] for item in source_records
    ]
    assert len({item["id"] for item in records}) == 676
    retained_fields = (
        "source_document_title",
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
    )
    for source, record in zip(source_records, records, strict=True):
        assert list(validator.iter_errors(record)) == []
        note = json.loads(record["indicator_context"]["quality_note"])
        actual = measurements(record)
        assert record["subject"]["name"] == source["indicator_name_original"]
        assert (
            actual["plan_current"]["value_text"]
            == source["target_statement_original"]
        )
        assert (
            record["indicator_context"]["source_page"]
            == source["source_location"]["page"]
        )
        for field in retained_fields:
            assert note[field] == source[field]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        actual = measurements(record)
        assert record["linkage_status"] == "partial"
        assert (
            record["partial_reason"]
            == "structured_actual_and_target_not_reviewed"
        )
        assert actual["annual_actual"]["status"] == "not_available"
        assert actual["final_target"]["status"] == "not_available"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"


def test_dynamic_counts_and_determinism():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    normalized = catalog()
    records = normalized["records"]
    assert normalized["summary"]["record_count"] == 676
    assert normalized["summary"]["partial_record_count"] == 676
    assert normalized["summary"]["source_document_count"] <= 4
    for key, value in manifest["expected_normalization"].items():
        assert normalized["summary"][key] == value
    assert sum(normalized["document_record_counts"].values()) == 676
    assert sum(normalized["source_location_counts"].values()) == 676
    assert normalized["summary"]["missing_unit_record_count"] == sum(
        item["unit_original"] is None for item in source["records"]
    )
    assert len(records) == 676
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
