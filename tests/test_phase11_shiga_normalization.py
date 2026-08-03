from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_shiga.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/25.json"
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_shiga_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_shiga_normalization.schema.json"

spec = importlib.util.spec_from_file_location("normalize_phase11_shiga", SCRIPT_PATH)
assert spec is not None and spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)

EXPECTED_CANONICAL_BY_HASH = {
    "6df41da2eb2b7e2d625bd22367f1fbe8f8d50e40029a98c8a66b17aa4849b9b9": 504,
    "6235ee656ecb13c59bd1337c53ca3919ee56f1f172185e45ab1a11ef75b3d143": 452,
    "a7288906c86f9224aeb7c0eaa3a3cf801a0ad4a78acc76fb311ed94c170717aa": 461,
    "cbc7c8731791426a8fdad160bf6c99f7d4a1ab70e977232feb27f97c7e15db20": 42,
    "4645a759d4eda3216b9002bbfa335572b9d8f5daf19b1b4f9292c8147102bfce": 41,
}
EXPECTED_CANDIDATE_BY_HASH = {
    "6df41da2eb2b7e2d625bd22367f1fbe8f8d50e40029a98c8a66b17aa4849b9b9": 504,
    "6235ee656ecb13c59bd1337c53ca3919ee56f1f172185e45ab1a11ef75b3d143": 603,
    "a7288906c86f9224aeb7c0eaa3a3cf801a0ad4a78acc76fb311ed94c170717aa": 611,
    "cbc7c8731791426a8fdad160bf6c99f7d4a1ab70e977232feb27f97c7e15db20": 42,
    "4645a759d4eda3216b9002bbfa335572b9d8f5daf19b1b4f9292c8147102bfce": 584,
    "96cec938a3d48ed316852aa26e3e7130b4ceafc30f90432d25dc9f76f61761e0": 322,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurements(record: dict) -> dict[str, dict]:
    return {item["role"]: item for item in record["measurements"]}


def test_manifest_matches_schema_and_paths_exist():
    manifest = load(MANIFEST_PATH)
    validator = Draft202012Validator(load(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "shared_normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_phase9_summary_and_source_reconcile_to_1500():
    source = load(SOURCE_PATH)
    summary = next(item for item in load(SUMMARY_PATH)["records"] if item["prefecture_code"] == "25")
    assert source["name"] == "滋賀県"
    assert source["reviewed_target_statement_count"] == 1500
    assert source["evidence_packet_count"] == 1500
    assert len(source["records"]) == 1500
    assert summary["reviewed_target_statement_count"] == 1500
    assert summary["document_count"] == 6
    assert summary["extraction_error_count"] == 0


def test_candidate_and_canonical_document_counts_are_not_conflated():
    source = load(SOURCE_PATH)
    manifest = load(MANIFEST_PATH)
    candidates = {item["sha256"]: item["reviewed_row_count"] for item in source["documents"]}
    canonical = Counter(item["source_document_sha256"] for item in source["records"])
    inventory_candidates = {item["sha256"]: item["reviewed_candidate_rows"] for item in manifest["source_document_inventory"]}
    inventory_canonical = {item["sha256"]: item["canonical_records"] for item in manifest["source_document_inventory"] if item["canonical_records"]}
    assert candidates == EXPECTED_CANDIDATE_BY_HASH
    assert dict(canonical) == EXPECTED_CANONICAL_BY_HASH
    assert inventory_candidates == EXPECTED_CANDIDATE_BY_HASH
    assert inventory_canonical == EXPECTED_CANONICAL_BY_HASH
    assert sum(candidates.values()) == 2666
    assert sum(canonical.values()) == 1500


def test_all_records_validate_and_preserve_sequence_and_source_fields():
    source_records = load(SOURCE_PATH)["records"]
    records = catalog()["records"]
    validator = Draft202012Validator(load(RECORD_SCHEMA_PATH), format_checker=FormatChecker())
    assert [item["display_order"] for item in source_records] == list(range(1, 1501))
    assert [item["subject"]["sequence"] for item in records] == list(range(1, 1501))
    assert [item["source_record_id"] for item in records] == [item["id"] for item in source_records]
    assert len({item["id"] for item in records}) == 1500
    for source, record in zip(source_records, records, strict=True):
        assert list(validator.iter_errors(record)) == []
        note = json.loads(record["indicator_context"]["quality_note"])
        actual = measurements(record)
        assert record["subject"]["name"] == source["indicator_name_original"]
        assert actual["plan_current"]["value_text"] == source["target_statement_original"]
        assert record["indicator_context"]["source_page"] == source["source_location"]["page"]
        for field in ("source_document_title", "source_document_url", "source_document_sha256", "source_location", "numeric_tokens_original", "period_tokens_original", "matched_keywords", "keyword_match_kind", "unit_original", "population_scope_original", "aggregation_scope", "target_operator", "comparability"):
            assert note[field] == source[field]


def test_all_records_remain_partial_unassessed_and_noncomparable():
    for record in catalog()["records"]:
        actual = measurements(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == "structured_actual_and_target_not_reviewed"
        assert actual["annual_actual"]["status"] == "not_available"
        assert actual["final_target"]["status"] == "not_available"
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "候補行" in record["boundary"]


def test_dynamic_counts_and_zero_record_document_are_exact():
    source = load(SOURCE_PATH)
    records = source["records"]
    normalized = catalog()
    manifest = load(MANIFEST_PATH)
    assert normalized["summary"] == manifest["expected_normalization"]
    assert Counter(item["source_location"]["location_kind"] for item in records) == {"pdf_table_row": 1399, "pdf_text_line": 101}
    assert sum(item["unit_original"] is None for item in records) == 272
    assert len({item["source_document_sha256"] for item in records}) == 5
    unused = [item for item in manifest["source_document_inventory"] if item["canonical_records"] == 0]
    assert len(unused) == 1
    assert unused[0]["reviewed_candidate_rows"] == 322


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
