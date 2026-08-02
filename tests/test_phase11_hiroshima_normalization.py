from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/normalize_phase11_hiroshima.py"
SCHEMA_PATH = ROOT / "schemas/phase11_record_linkage.schema.json"
MANIFEST_PATH = ROOT / "data/catalog/phase11_hiroshima_normalization.json"
MANIFEST_SCHEMA_PATH = (
    ROOT / "schemas/phase11_hiroshima_normalization.schema.json"
)
SOURCE_MANIFEST_PATH = (
    ROOT / "data/catalog/hiroshima_revised_vision_indicator_review_manifest.json"
)

spec = importlib.util.spec_from_file_location(
    "normalize_phase11_hiroshima",
    SCRIPT_PATH,
)
assert spec is not None
assert spec.loader is not None
normalizer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalizer)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_records() -> list[tuple[str, dict]]:
    return normalizer.load_records(ROOT)


def normalized_catalog() -> dict:
    return normalizer.build_catalog(ROOT)


def measurement_by_role(record: dict) -> dict[str, dict]:
    return {
        measurement["role"]: measurement
        for measurement in record["measurements"]
    }


def is_pending(record: dict) -> bool:
    return normalizer.is_missing_current(record["current"])


def test_hiroshima_manifest_matches_schema_and_paths_exist():
    validator = Draft202012Validator(
        load(MANIFEST_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    manifest = load(MANIFEST_PATH)

    assert list(validator.iter_errors(manifest)) == []
    for path in manifest["source_catalogs"]:
        assert (ROOT / path).exists()
    for field in ("source_review_manifest", "normalizer", "record_schema"):
        assert (ROOT / manifest[field]).exists()


def test_all_62_records_match_the_shared_phase11_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    records = normalized_catalog()["records"]

    assert len(records) == 62
    for record in records:
        assert list(validator.iter_errors(record)) == []


def test_three_parts_form_one_complete_sequence_without_skips():
    source = source_records()
    records = normalized_catalog()["records"]
    source_ids = [record["id"] for _, record in source]

    assert len(source) == 62
    assert source_ids == [
        f"hiroshima-vision-indicator-{number:03d}"
        for number in range(1, 63)
    ]
    assert [record["source_record_id"] for record in records] == source_ids
    assert [record["subject"]["sequence"] for record in records] == list(
        range(1, 63)
    )
    assert len({record["id"] for record in records}) == 62
    assert len({record["source_record_id"] for record in records}) == 62


def test_every_source_field_is_retained_exactly():
    source_by_id = {
        record["id"]: (source_registry, record)
        for source_registry, record in source_records()
    }
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    for source_id, (source_registry, source) in source_by_id.items():
        record = normalized_by_id[source_id]
        measurements = measurement_by_role(record)
        context_note = json.loads(record["indicator_context"]["quality_note"])
        pending = is_pending(source)

        assert record["source_registry"] == source_registry
        assert record["subject"] == {
            "record_ref": source["id"],
            "sequence": int(source["id"].rsplit("-", 1)[1]),
            "name": source["name"],
            "source_name": source["name"],
            "definition": source["change"],
            "hierarchy_refs": [f"hiroshima-policy-area-{source['area']}"],
        }
        assert record["indicator_context"]["policy_direction_code"] == source[
            "area"
        ]
        assert record["indicator_context"]["policy_direction_name"] == source[
            "area"
        ]
        assert record["indicator_context"]["source_page"] == source["page"]
        assert record["indicator_context"]["target_revision_status"] == source[
            "change"
        ]
        assert record["indicator_context"]["linked_current_series_count"] == (
            0 if pending else 1
        )
        assert record["indicator_context"]["target_series_count"] == 1
        assert record["indicator_context"]["review_status"] == source["review"]
        assert context_note == {
            "evidence_id": source["evidence_id"],
            "change": source["change"],
            "source_original": source["source"],
            "target_period": source["target_period"],
            "raw_values_are_not_split": True,
        }

        assert measurements["plan_current"]["value_text"] == source["baseline"]
        assert measurements["annual_actual"]["value_text"] == source["current"]
        assert measurements["final_target"]["value_text"] == source["target"]
        assert measurements["final_target"]["period_text"] == source[
            "target_period"
        ]
        assert record["evidence"] == {
            "primary_source_number": 1,
            "primary_page": source["page"],
            "locations": [
                {
                    "source_number": 1,
                    "page": source["page"],
                    "is_reprint": False,
                }
            ],
        }


def test_raw_compound_values_are_not_split_or_rewritten():
    source_by_id = {
        record["id"]: record for _, record in source_records()
    }
    normalized_by_id = {
        record["source_record_id"]: record
        for record in normalized_catalog()["records"]
    }

    special_ids = {
        "hiroshima-vision-indicator-002",
        "hiroshima-vision-indicator-005",
        "hiroshima-vision-indicator-010",
        "hiroshima-vision-indicator-026",
        "hiroshima-vision-indicator-027",
        "hiroshima-vision-indicator-039",
        "hiroshima-vision-indicator-042",
        "hiroshima-vision-indicator-049",
    }
    for source_id in special_ids:
        source = source_by_id[source_id]
        measurements = measurement_by_role(normalized_by_id[source_id])
        assert measurements["plan_current"]["components"][0]["value_text"] == (
            source["baseline"]
        )
        assert measurements["annual_actual"]["components"][0]["value_text"] == (
            source["current"]
        )
        assert measurements["final_target"]["components"][0]["value_text"] == (
            source["target"]
        )
        assert all(
            len(measurement["components"]) == 1
            for measurement in measurements.values()
        )


def test_status_counts_match_review_manifest_and_pending_measurements():
    source = [record for _, record in source_records()]
    review_manifest = load(SOURCE_MANIFEST_PATH)
    catalog = normalized_catalog()
    statuses = Counter(
        record["linkage_status"] for record in catalog["records"]
    )
    pending_ids = {
        record["id"] for record in source if is_pending(record)
    }

    assert pending_ids == {
        "hiroshima-vision-indicator-006",
        "hiroshima-vision-indicator-007",
        "hiroshima-vision-indicator-008",
    }
    assert statuses == Counter({"linked": 59, "partial": 3})
    assert catalog["summary"]["record_count"] == 62
    assert catalog["summary"]["linked_record_count"] == 59
    assert catalog["summary"]["partial_record_count"] == 3
    assert catalog["summary"]["not_linked_record_count"] == 0
    assert catalog["summary"]["policy_area_count"] == 17
    assert catalog["summary"]["pending_measurement_record_count"] == 3
    assert review_manifest["reviewed_indicator_count"] == 62
    assert review_manifest[
        "indicators_with_numeric_or_qualitative_current_value_count"
    ] == 59
    assert review_manifest["pending_measurement_indicator_count"] == 3


def test_partial_records_keep_raw_missing_and_future_survey_text():
    source_by_id = {
        record["id"]: record for _, record in source_records()
    }
    partial_records = [
        record
        for record in normalized_catalog()["records"]
        if record["linkage_status"] == "partial"
    ]

    assert len(partial_records) == 3
    for record in partial_records:
        source = source_by_id[record["source_record_id"]]
        actual = measurement_by_role(record)["annual_actual"]
        assert record["partial_reason"] == "pending_measurement"
        assert actual["status"] == "not_available"
        assert actual["value_text"] == source["current"]
        assert actual["components"][0]["value"] is None
        assert actual["components"][0]["value_status"] == "missing"
        assert "Partial" in record["boundary"]


def test_qualitative_target_and_change_states_are_preserved():
    source = [record for _, record in source_records()]
    catalog = normalized_catalog()
    normalized_by_id = {
        record["source_record_id"]: record for record in catalog["records"]
    }
    qualitative = normalized_by_id["hiroshima-vision-indicator-042"]

    assert measurement_by_role(qualitative)["final_target"]["value_text"] == (
        "多国間枠組みに核兵器国を含む全ての国が参加"
    )
    assert catalog["summary"]["qualitative_target_record_count"] == 1
    assert catalog["summary"]["change_counts"] == dict(
        sorted(Counter(record["change"] for record in source).items())
    )


def test_no_record_gains_assessment_or_comparison_eligibility():
    for record in normalized_catalog()["records"]:
        assert record["evaluation_status"] == "not_assessed"
        assert record["comparability_status"] == "excluded_until_verified"
        assert "政策達成" in record["boundary"]


def test_normalization_is_deterministic():
    assert normalizer.build_catalog(ROOT) == normalizer.build_catalog(ROOT)
