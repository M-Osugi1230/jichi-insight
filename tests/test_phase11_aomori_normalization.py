from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_aomori.py"
SOURCE_PATH = ROOT / "data/reviewed/phase9/02.json"
RECORD_SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_aomori_normalization.json"
MANIFEST_SCHEMA_PATH = ROOT / "schemas/phase11_aomori_normalization.schema.json"

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_aomori",
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


def test_aomori_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for field in ("source_catalog", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_aomori_record_matches_shared_phase11_schema():
    validator = Draft202012Validator(
        load(RECORD_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = catalog()["records"]

    assert len(records) == 1
    assert list(validator.iter_errors(records[0])) == []


def test_reviewed_source_record_is_retained_without_reinterpretation():
    source = load(SOURCE_PATH)
    source_record = source["records"][0]
    record = catalog()["records"][0]
    measurements = measurement_by_role(record)
    note = json.loads(record["indicator_context"]["quality_note"])

    assert source["reviewed_target_statement_count"] == 1
    assert record["source_record_id"] == source_record["id"]
    assert record["subject"]["name"] == source_record[
        "indicator_name_original"
    ]
    assert record["subject"]["definition"] == source_record[
        "plan_history_boundary"
    ]
    assert measurements["plan_current"]["value_text"] == source_record[
        "target_statement_original"
    ]
    assert measurements["plan_current"]["period_text"] == (
        " / ".join(source_record["period_tokens_original"])
    )
    assert measurements["plan_current"]["components"][0][
        "value_text"
    ] == source_record["target_statement_original"]
    assert note["numeric_tokens_original"] == source_record[
        "numeric_tokens_original"
    ]
    assert note["period_tokens_original"] == source_record[
        "period_tokens_original"
    ]
    assert note["comparability"] == source_record["comparability"]
    assert note["maximum_depth"] == "reviewed_observation_statement"


def test_observation_statement_is_not_promoted_to_actual_or_future_target():
    record = catalog()["records"][0]
    measurements = measurement_by_role(record)

    assert record["linkage_status"] == "partial"
    assert record["partial_reason"] == (
        "annual_actual_and_future_target_not_reviewed"
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


def test_source_page_hash_and_history_boundary_are_preserved():
    source = load(SOURCE_PATH)
    source_record = source["records"][0]
    record = catalog()["records"][0]
    note = json.loads(record["indicator_context"]["quality_note"])

    assert record["evidence"]["primary_page"] == 2
    assert record["evidence"]["locations"] == [
        {"source_number": 1, "page": 2, "is_reprint": False}
    ]
    assert note["source_document_sha256"] == source_record[
        "source_document_sha256"
    ]
    assert note["source_row"] == source_record["source_location"]["row"]
    assert "旧計画KPI" in record["boundary"]
    assert "政策点検結果" in record["boundary"]


def test_summary_and_non_assessment_boundary_are_exact():
    normalized = catalog()
    record = normalized["records"][0]

    assert normalized["summary"] == {
        "record_count": 1,
        "linked_record_count": 0,
        "partial_record_count": 1,
        "not_linked_record_count": 0,
        "indicator_series_count": 1,
        "annual_actual_available_count": 0,
        "future_target_available_count": 0,
        "reviewed_maximum_depth_record_count": 1,
        "policy_achievement_assessment_count": 0,
    }
    assert record["evaluation_status"] == "not_assessed"
    assert record["comparability_status"] == "excluded_until_verified"


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
