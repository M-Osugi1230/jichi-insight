import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/entities/policy/hokkaido_indicator_catalog_sme_commerce.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_contract():
    data = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (71, 73)
    assert [item["indicator_number"] for item in data["items"]] == [71, 72, 73]
    assert [item["source_page"] for item in data["items"]] == [1, 2, 3]


def test_page_index_and_values():
    data = load(CATALOG)
    index_path = ROOT / "data/catalog/hokkaido_indicator_page_index.json"
    index = {
        item["indicator_number"]: item
        for item in load(index_path)["records"]
    }
    items = {item["indicator_number"]: item for item in data["items"]}

    for number in (71, 72, 73):
        assert index[number]["source_id"] == data["source_id"]
        assert index[number]["page_number"] == items[number]["source_page"]
        assert index[number]["policy_field_id"] == data["policy_field_id"]

    assert [items[number]["indicator_name_original"] for number in (71, 72, 73)] == [
        "開業率",
        "来街者数が増加している商店街の割合",
        "商店街の営業店舗率",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in (71, 72, 73)
    ] == [
        [3.4, 5.1, 5.9],
        [0.8, 5.2, 9.6],
        [88.5, 88.8, 89.0],
    ]
    assert [
        items[number]["series"][0]["temporal_scope"]
        for number in (71, 72, 73)
    ] == ["fiscal_year", "snapshot", "snapshot"]


def test_reference_boundaries_and_unlinked_status():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    assert "第3位" in items[71]["comparability_note_original"]
    assert "振興局管内別" in items[72]["comparability_note_original"]
    assert "空き店舗が解消されない原因" in items[73]["comparability_note_original"]
    assert all(len(items[number]["series"]) == 1 for number in (71, 72, 73))
    assert all(
        item["actual_linkage_status"] == "not_linked"
        for item in items.values()
    )
    assert all(
        item["evaluation_status"] == "not_assessed"
        for item in items.values()
    )
