from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_iwate.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/03.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_iwate_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_iwate_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_iwate",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def test_iwate_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_all_208_records_match_shared_phase11_schema():
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = catalog()["records"]

    assert len(records) == 208
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_source_sequence_and_ids_are_complete_without_skips():
    source = load(SOURCE_PATH)
    records = catalog()["records"]

    assert source["reviewed_target_statement_count"] == 208
    assert source["evidence_packet_count"] == 208
    assert [record["display_order"] for record in source["records"]] == list(
        range(1, 209)
    )
    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 209)
    )
    assert [record["source_record_id"] for record in records] == [
        source_record["id"] for source_record in source["records"]
    ]
    assert len({record["id"] for record in records}) == 208
    assert len({record["source_record_id"] for record in records}) == 208


def test_every_reviewed_field_is_retained_exactly():
    source = load(SOURCE_PATH)
    source_by_id = {record["id"]: record for record in source["records"]}
    normalized_by_id = {
        record["source_record_id"]: record for record in catalog()["records"]
    }

    for source_id, source_record in source_by_id.items():
        record = normalized_by_id[source_id]
        measurements = measurement_by_role(record)
        note = json.loads(record["indicator_context"]["quality_note"])

        assert record["subject"]["name"] == source_record[
            "indicator_name_original"
        ]
        assert record["subject"]["definition"] == source_record[
            "plan_history_boundary"
        ]
        assert record["indicator_context"]["source_page"] == source_record[
            "source_location"
        ]["page"]
        assert record["indicator_context"]["policy_direction_name"] == (
            source_record["source_document_title"]
        )
        assert measurements["plan_current"]["value_text"] == source_record[
            "target_statement_original"
        ]
        assert measurements["plan_current"]["period_text"] == (
            " / ".join(source_record["period_tokens_original"])
        )
        assert measurements["plan_current"]["components"][0][
            "value_text"
        ] == source_record["target_statement_original"]
        assert note["evidence_id"] == source_record["evidence_id"]
        assert note["source_document_url"] == source_record[
            "source_document_url"
        ]
        assert note["source_document_sha256"] == source_record[
            "source_document_sha256"
        ]
        assert note["source_row"] == source_record["source_location"]["row"]
        assert note["numeric_tokens_original"] == source_record[
            "numeric_tokens_original"
        ]
        assert note["period_tokens_original"] == source_record[
            "period_tokens_original"
        ]
        assert note["matched_keywords"] == source_record["matched_keywords"]
        assert note["comparability"] == source_record["comparability"]


def test_no_raw_line_is_promoted_to_structured_actual_or_target():
    for record in catalog()["records"]:
        measurements = measurement_by_role(record)
        assert record["linkage_status"] == "partial"
        assert record["partial_reason"] == (
            "structured_actual_and_target_not_reviewed"
        )
        assert measurements["annual_actual"] == {
            "role": "annual_actual",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert measurements["final_target"] == {
            "role": "final_target",
            "status": "not_available",
            "period_text": "",
            "value_text": "",
            "components": [],
            "evidence": {"source_number": None, "page": None},
        }
        assert record["indicator_context"]["linked_current_series_count"] == 0
        assert record["indicator_context"]["target_series_count"] == 0


def test_all_six_source_documents_remain_separate():
    source = load(SOURCE_PATH)
    normalized = catalog()
    source_counts = Counter(
        record["source_document_title"] for record in source["records"]
    )

    assert len(source["documents"]) == 6
    assert len(source_counts) == 6
    assert sum(source_counts.values()) == 208
    assert normalized["summary"]["source_document_count"] == 6
    assert normalized["document_record_counts"] == dict(
        sorted(source_counts.items())
    )
    for record in normalized["records"]:
        assert len(record["subject"]["hierarchy_refs"]) == 2
        assert record["subject"]["hierarchy_refs"][0] == (
            "iwate-current-action-plan-2023-2026"
        )


def test_summary_and_non_assessment_boundaries_are_exact():
    normalized = catalog()

    assert normalized["summary"] == {
        "record_count": 208,
        "linked_record_count": 0,
        "partial_record_count": 208,
        "not_linked_record_count": 0,
        "indicator_series_count": 208,
        "source_document_count": 6,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 208,
        "policy_achievement_assessment_count": 0,
    }
    for record in normalized["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "6地域振興圏" not in record["boundary"]
        assert "4地域振興圏" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
