from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_hokkaido.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_hokkaido_normalization.json"
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/phase11_hokkaido_normalization.schema.json"
)

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_hokkaido",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records() -> list[tuple[str, dict]]:
    _, records = normalizer.load_source_records(ROOT)
    return records


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def test_hokkaido_normalization_manifest_matches_schema():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path_field in (
        "source_catalog",
        "normalizer",
        "record_schema",
        "regression_test",
    ):
        assert (ROOT / manifest[path_field]).exists()
    assert all((ROOT / path).exists() for path in manifest["source_files"])


def test_all_108_records_match_the_reusable_phase11_schema():
    validator = Draft202012Validator(load(SCHEMA_PATH))
    catalog = normalized_catalog()

    assert len(catalog["records"]) == 108
    for record in catalog["records"]:
        assert list(validator.iter_errors(record)) == []


def test_source_order_ids_and_statuses_are_preserved_without_skips():
    sources = source_records()
    catalog = normalized_catalog()
    normalized = catalog["records"]

    assert [record["indicator_number"] for _, record in sources] == list(
        range(1, 109)
    )
    assert [record["subject"]["sequence"] for record in normalized] == list(
        range(1, 109)
    )
    assert [record["source_record_id"] for record in normalized] == [
        record["id"] for _, record in sources
    ]
    assert len({record["id"] for record in normalized}) == 108

    statuses = Counter(record["linkage_status"] for record in normalized)
    assert statuses == {"linked": 90, "partial": 18}
    assert catalog["summary"] == {
        "record_count": 108,
        "linked_record_count": 90,
        "partial_record_count": 18,
        "not_linked_record_count": 0,
        "policy_achievement_assessment_count": 0,
    }
    assert catalog["summary"] == load(MANIFEST_PATH)["summary"]


def test_every_source_field_is_mapped_or_retained_in_the_normalized_record():
    normalized_by_source_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for source_registry, source in source_records():
        record = normalized_by_source_id[source["id"]]
        subject = record["subject"]
        measurements = {
            measurement["role"]: measurement
            for measurement in record["measurements"]
        }

        assert record["source_registry"] == source_registry
        assert record["linkage_status"] == source["linkage_status"]
        assert record["partial_reason"] == source["partial_reason"]
        assert record["boundary"] == source["boundary"]
        assert record["evaluation_status"] == source["evaluation_status"]
        assert subject == {
            "record_ref": source["indicator_id"],
            "sequence": source["indicator_number"],
            "name": source["indicator_name"],
            "source_name": source["source_indicator_name_text"],
            "definition": source["definition_text"],
            "hierarchy_refs": [
                source["policy_direction_id"],
                *source["policy_field_ids"],
            ],
        }

        assert measurements["plan_current"]["value_text"] == source[
            "plan_current_value_text"
        ]
        assert measurements["plan_current"]["period_text"] == source[
            "plan_current_period_text"
        ]
        assert measurements["intermediate_target"]["value_text"] == source[
            "intermediate_target_text"
        ]
        assert measurements["intermediate_target"]["period_text"] == source[
            "intermediate_target_period_text"
        ]
        assert measurements["final_target"]["value_text"] == source[
            "final_target_text"
        ]
        assert measurements["final_target"]["period_text"] == source[
            "final_target_period_text"
        ]
        assert measurements["annual_actual"] == {
            "role": "annual_actual",
            "status": source["actual_status"],
            "period_text": source["actual_period_text"],
            "value_text": source["actual_value_text"],
            "components": source["actual_components"],
        }

        assert record["evidence"] == {
            "primary_source_number": source["source_number"],
            "primary_page": source["pdf_page"],
            "locations": [
                {
                    "source_number": location["source_number"],
                    "page": location["pdf_page"],
                    "is_reprint": location["is_reprint"],
                }
                for location in source["related_source_locations"]
            ],
        }


def test_partial_records_keep_all_four_original_reason_groups():
    catalog = normalized_catalog()
    partial_records = [
        record
        for record in catalog["records"]
        if record["linkage_status"] == "partial"
    ]
    reasons = Counter(record["partial_reason"] for record in partial_records)

    assert reasons == {
        "target_version_changed": 3,
        "unit_scale_changed_or_requires_conversion": 3,
        "indicator_definition_or_numbering_changed": 10,
        "component_structure_changed": 2,
    }
    assert reasons == load(MANIFEST_PATH)["partial_reason_counts"]
    for record in partial_records:
        actual = next(
            measurement
            for measurement in record["measurements"]
            if measurement["role"] == "annual_actual"
        )
        assert actual["status"] == "not_promoted"
        assert actual["components"] == []
        assert record["partial_reason"] is not None


def test_linked_records_do_not_gain_achievement_or_comparability_claims():
    catalog = normalized_catalog()
    linked_records = [
        record
        for record in catalog["records"]
        if record["linkage_status"] == "linked"
    ]

    assert len(linked_records) == 90
    for record in linked_records:
        assert record["partial_reason"] is None
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "達成・未達は判定しない" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
