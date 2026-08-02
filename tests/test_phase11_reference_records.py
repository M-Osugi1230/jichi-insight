from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = ROOT / "data/catalog/phase11_reference_records.json"
REFERENCE_SCHEMA_PATH = ROOT / "schemas/phase11_reference_records.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase11_execution_queue.json"
QUEUE_SCHEMA_PATH = ROOT / "schemas/phase11_execution_queue.schema.json"
ALL_CODES = {f"{value:02d}" for value in range(1, 48)}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase11_reference_records_match_schema():
    validator = Draft202012Validator(
        load(REFERENCE_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REFERENCE_PATH))) == []


def test_phase11_execution_queue_matches_schema():
    validator = Draft202012Validator(
        load(QUEUE_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_reference_records_resolve_to_reviewed_source_records():
    catalog = load(REFERENCE_PATH)

    for reference in catalog["records"]:
        registry_path = ROOT / reference["source_registry"]
        assert registry_path.exists()
        registry = load(registry_path)
        records = registry.get("records", [])
        resolved_ids = {
            record.get("id") or record.get("target_id")
            for record in records
        }
        assert reference["source_record_id"] in resolved_ids
        assert all((ROOT / path).exists() for path in reference["evidence_paths"])


def test_reference_layers_are_unique_and_linked_values_remain_separate():
    catalog = load(REFERENCE_PATH)

    for reference in catalog["records"]:
        layers = reference["layers"]
        layer_names = [layer["layer"] for layer in layers]
        assert len(layer_names) == len(set(layer_names))
        assert all(
            layer["record_ref"] is not None
            for layer in layers
            if layer["status"] == "linked"
        )
        assert reference["evaluation_status"] == "not_assessed"
        assert reference["comparability_status"] == "excluded_until_verified"

    miyagi = next(
        item
        for item in catalog["records"]
        if item["prefecture_code"] == "04"
    )
    layers = {layer["layer"]: layer for layer in miyagi["layers"]}
    assert layers["budget"]["period"] == "令和8年度"
    assert layers["settlement"]["period"] == "令和6年度"
    assert layers["budget"]["value_text"] != layers["settlement"]["value_text"]


def test_execution_waves_partition_all_prefectures_once():
    queue = load(QUEUE_PATH)
    wave_codes = [
        code
        for wave in queue["waves"]
        for code in wave["prefecture_codes"]
    ]

    assert set(wave_codes) == ALL_CODES
    assert len(wave_codes) == len(set(wave_codes)) == 47

    reference_codes = {
        record["prefecture_code"]
        for record in load(REFERENCE_PATH)["records"]
    }
    assert reference_codes == set(queue["waves"][0]["prefecture_codes"])


def test_phase11_does_not_claim_achievement_or_comparability():
    catalog = load(REFERENCE_PATH)

    assert catalog["summary"]["policy_achievement_assessment_count"] == 0
    assert all(record["linkage_status"] == "linked" for record in catalog["records"])
    assert "does not imply policy achievement" in catalog["record_level_definition"]
