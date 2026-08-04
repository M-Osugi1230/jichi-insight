from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_okayama.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/33.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_okayama_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_okayama_normalization.schema.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"


def load_script():
    spec = importlib.util.spec_from_file_location("normalize_phase11_okayama", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_source_and_phase9_summary_reconcile() -> None:
    source = load_json(SOURCE_PATH)
    manifest = load_json(MANIFEST_PATH)
    schema = load_json(MANIFEST_SCHEMA_PATH)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    assert source["reviewed_target_statement_count"] == 343
    assert source["evidence_packet_count"] == 343
    assert manifest["expected_normalization"]["record_count"] == 343
    assert [document["reviewed_row_count"] for document in source["documents"]] == [30, 91, 0, 216, 6]


def test_all_343_records_validate_and_preserve_sequence() -> None:
    source = load_json(SOURCE_PATH)
    catalog = load_script().build_catalog()
    validator = Draft202012Validator(load_json(RECORD_SCHEMA_PATH), format_checker=FormatChecker())
    assert len(catalog["records"]) == 343
    assert [record["display_order"] for record in source["records"]] == list(range(1, 344))
    assert [record["source_record_id"] for record in catalog["records"]] == [
        record["id"] for record in source["records"]
    ]
    for record in catalog["records"]:
        validator.validate(record)


def test_every_source_field_and_evidence_location_are_retained() -> None:
    source = load_json(SOURCE_PATH)
    catalog = load_script().build_catalog()
    for raw, normalized in zip(source["records"], catalog["records"], strict=True):
        note = normalized["quality_note"]
        assert raw["indicator_name_original"] in note
        assert raw["target_statement_original"] in note
        assert raw["source_document_url"] in note
        assert raw["source_document_sha256"] in note
        assert json.dumps(raw["source_location"], ensure_ascii=False, sort_keys=True) in note
        assert raw["numeric_tokens_original"] == normalized["source_numeric_tokens"]
        assert raw["period_tokens_original"] == normalized["source_period_tokens"]


def test_document_layers_and_zero_row_document_remain_explicit() -> None:
    source = load_json(SOURCE_PATH)
    catalog = load_script().build_catalog()
    counts = Counter(record["source_document_url"] for record in source["records"])
    assert sorted(counts.values()) == [6, 30, 91, 216]
    assert sum(document["reviewed_row_count"] == 0 for document in source["documents"]) == 1
    assert catalog["summary"]["record_count"] == 343
    assert "0行状態" in catalog["normalization_boundary"]
    assert "一度だけ正規化" in catalog["normalization_boundary"]


def test_records_remain_partial_unassessed_and_noncomparable() -> None:
    catalog = load_script().build_catalog()
    assert all(record["linkage_status"] == "partial" for record in catalog["records"])
    assert all(record["policy_achievement_assessment_status"] == "not_assessed" for record in catalog["records"])
    assert all(record["ranking_eligibility"] == "excluded_until_comparability_verified" for record in catalog["records"])
    assert all(record["annual_actual"] is None for record in catalog["records"])
    assert all(record["future_target"] is None for record in catalog["records"])


def test_dynamic_counts_and_determinism_are_exact() -> None:
    module = load_script()
    first = module.build_catalog()
    second = module.build_catalog()
    assert first == second
    assert first["summary"] == {
        "record_count": 343,
        "linked_record_count": 0,
        "partial_record_count": 343,
        "not_linked_record_count": 0,
        "indicator_series_count": 343,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 343,
        "policy_achievement_assessment_count": 0,
    }
