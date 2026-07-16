import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_infrastructure.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_schema_sequence_and_pages():
    data = load(CATALOG)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (92, 98)
    assert [item["indicator_number"] for item in data["items"]] == list(range(92, 99))
    assert [item["source_page"] for item in data["items"]] == list(range(1, 8))


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    index = {
        item["indicator_number"]: item
        for item in load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")[
            "records"
        ]
    }
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_values_series_and_periods_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in (92, 93, 94, 96, 97, 98)
    ] == [
        [51.6, 92.9, 100],
        [44.6, 76.8, 100],
        [620, 712, 712],
        [6298, 14000, 24000],
        [95.5, 97.8, 99.0],
        [23261, 25110, 27000],
    ]
    assert [series["label"] for series in items[95]["series"]] == ["バス", "トラック"]
    assert [[value["value"] for value in series["values"]] for series in items[95]["series"]] == [
        [9.1, 29.5, 50.0],
        [28.5, 39.3, 50.0],
    ]
    assert items[96]["series"][0]["temporal_scope"] == "fiscal_year"
    assert items[95]["series"][0]["temporal_scope"] == "calendar_year"
    assert items[97]["series"][0]["values"][2]["period"] == "2031年"


def test_quality_boundaries_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert "地域別" in items[92]["comparability_note_original"]
    assert "地域別" in items[93]["comparability_note_original"]
    assert "主要産業別" in items[94]["comparability_note_original"]
    assert "過去の実績データはなく" in items[95]["comparability_note_original"]
    assert "新千歳空港" in items[96]["comparability_note_original"]
    assert "2031年" in items[97]["comparability_note_original"]
    assert "採用状況" in items[98]["comparability_note_original"]


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
