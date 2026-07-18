import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4a.json",
    POLICY / "miyagi_kpi_catalog_measure4b.json",
    POLICY / "miyagi_kpi_catalog_measure5a.json",
    POLICY / "miyagi_kpi_catalog_measure5b.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def groups():
    return [item for path in CATALOGS for item in load(path)["items"]]


def test_schema_sequence_and_scope():
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert all(list(validator.iter_errors(load(path))) == [] for path in CATALOGS)
    items = groups()
    series = [entry for item in items for entry in item["series"]]
    assert [item["target_group_number"] for item in items] == list(range(24, 39))
    assert [entry["series_number"] for entry in series] == list(range(24, 41))
    assert [(item["scope_type"], item["scope_number"]) for item in items] == (
        [("measure", 4)] * 8 + [("measure", 5)] * 7
    )
    assert all(item["source_page"] == 56 for item in items)
    assert all(item["printed_page"] == 55 for item in items)


def test_group_26_keeps_three_series_and_periods():
    item = next(item for item in groups() if item["target_group_number"] == 26)
    assert [entry["series_number"] for entry in item["series"]] == [26, 27, 28]
    assert [[value["value"] for value in entry["values"]] for entry in item["series"]] == [
        [131, 154, 160, None],
        [31, 24, 54, None],
        [33, 69, 100, None],
    ]
    assert [value["period_original"] for value in item["series"][2]["values"][:2]] == [
        "R4",
        "R5",
    ]
    assert "水産業 ）（人）" in item["series"][1]["indicator_name_original"]


def test_original_format_and_missing_unit_are_preserved():
    items = {item["target_group_number"]: item for item in groups()}
    assert items[32]["series"][0]["values"][2]["value_text_original"] == "21400"
    assert items[34]["series"][0]["values"][2]["value_text_original"] == "4126"
    assert items[35]["series"][0]["unit_original"] == "単位記載なし"
    assert [value["period_original"] for value in items[35]["series"][0]["values"][:2]] == [
        "R5",
        "R5",
    ]
