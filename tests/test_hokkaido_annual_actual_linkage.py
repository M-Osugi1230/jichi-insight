import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
POLICY = ROOT / "data/entities/policy"
INDEX_PATH = CATALOG / "hokkaido_annual_actual_linkage.json"
INDEX_SCHEMA = ROOT / "schemas/hokkaido_annual_actual_linkage.schema.json"
PART_SCHEMA = ROOT / "schemas/hokkaido_annual_actual_linkage_part.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    index = load(INDEX_PATH)
    parts = [load(CATALOG / name) for name in index["part_files"]]
    return index, parts, [record for part in parts for record in part["records"]]


def catalog_ids():
    ids = []
    for path in sorted(POLICY.glob("hokkaido_indicator_catalog_*.json")):
        ids.extend(item["id"] for item in load(path)["items"])
    return ids


def test_index_and_parts_match_schema():
    index_validator = Draft202012Validator(
        load(INDEX_SCHEMA), format_checker=FormatChecker()
    )
    part_validator = Draft202012Validator(
        load(PART_SCHEMA), format_checker=FormatChecker()
    )
    index, parts, _ = records()

    assert list(index_validator.iter_errors(index)) == []
    assert len(parts) == 2
    assert all(list(part_validator.iter_errors(part)) == [] for part in parts)
    assert [(part["record_number_from"], part["record_number_to"]) for part in parts] == [
        (1, 54),
        (55, 108),
    ]


def test_all_108_official_indicator_numbers_are_covered_once():
    index, _, items = records()
    numbers = [item["indicator_number"] for item in items]
    ids = [item["indicator_id"] for item in items]

    assert index["indicator_count"] == 108
    assert index["series_count"] == 126
    assert numbers == list(range(1, 109))
    assert len(ids) == len(set(ids)) == 108
    assert ids == catalog_ids()


def test_reviewed_classification_remains_conservative():
    index, _, items = records()
    statuses = Counter(item["linkage_status"] for item in items)
    reasons = Counter(
        item["partial_reason"]
        for item in items
        if item["linkage_status"] == "partial"
    )

    assert statuses == {"linked": 93, "partial": 15}
    assert index["summary"] == {
        "linked_record_count": 93,
        "partial_record_count": 15,
        "not_linked_record_count": 0,
    }
    assert reasons == {
        "target_version_changed": 3,
        "indicator_definition_or_numbering_changed": 10,
        "component_structure_changed": 2,
    }
    assert index["evaluation_status"] == "not_assessed"


def test_partial_indicator_numbers_are_explicit_and_not_promoted():
    _, _, items = records()
    partial = {
        item["indicator_number"]: item["partial_reason"]
        for item in items
        if item["linkage_status"] == "partial"
    }

    assert set(partial) == {6, 10, 21, *range(31, 40), 65, 107, 108}
    for item in items:
        assert item["evaluation_status"] == "not_assessed"
        assert item["related_source_locations"]
        if item["linkage_status"] == "partial":
            assert item["actual_status"] == "not_promoted"
            assert item["actual_components"] == []
            assert "接続しない" in item["boundary"]
        else:
            assert item["partial_reason"] is None
            assert "達成・未達は判定しない" in item["boundary"]


def test_reprinted_rows_keep_one_primary_source_and_all_locations():
    _, _, items = records()
    by_number = {item["indicator_number"]: item for item in items}

    for number in (16, 17, 24, 45, 50):
        item = by_number[number]
        assert len(item["related_source_locations"]) == 2
        assert sum(location["is_reprint"] for location in item["related_source_locations"]) == 1
        assert not next(
            location["is_reprint"]
            for location in item["related_source_locations"]
            if location["source_number"] == item["source_number"]
            and location["pdf_page"] == item["pdf_page"]
        )


def test_linked_actuals_preserve_raw_values_periods_and_components():
    _, _, items = records()
    by_number = {item["indicator_number"]: item for item in items}

    assert by_number[4]["actual_value_text"] == "1,479"
    assert by_number[4]["actual_period_text"] == "r4 （2022）"
    assert by_number[4]["actual_components"] == [
        {
            "label": None,
            "unit": "万円",
            "value_text": "1,479",
            "value": 1479,
            "value_status": "numeric",
        }
    ]
    assert by_number[51]["actual_status"] == "not_available"
    assert by_number[51]["actual_value_text"] == ""
    assert by_number[54]["actual_status"] == "available"
    assert len(by_number[54]["actual_components"]) == 4
