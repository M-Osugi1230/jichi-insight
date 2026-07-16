import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/entities/policy/hokkaido_indicator_catalog_sme_commerce.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def test_catalog_contract():
    data = load(CATALOG)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (71, 73)
    assert [x["indicator_number"] for x in data["items"]] == [71, 72, 73]
    assert [x["source_page"] for x in data["items"]] == [1, 2, 3]

def test_page_index_and_values():
    data = load(CATALOG)
    index = {x["indicator_number"]: x for x in load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")["records"]}
    items = {x["indicator_number"]: x for x in data["items"]}
    for number in (71, 72, 73):
        assert index[number]["source_id"] == data["source_id"]
        assert index[number]["page_number"] == items[number]["source_page"]
        assert index[number]["policy_field_id"] == data["policy_field_id"]
    assert [items[n]["indicator_name_original"] for n in (71, 72, 73)] == ["開業率", "来街者数が増加している商店街の割合", "商店街の営業店舗率"]
    assert [[v["value"] for v in items[n]["series"][0]["values"]] for n in (71, 72, 73)] == [[3.4, 5.1, 5.9], [0.8, 5.2, 9.6], [88.5, 88.8, 89.0]]
    assert [items[n]["series"][0]["temporal_scope"] for n in (71, 72, 73)] == ["fiscal_year", "snapshot", "snapshot"]

def test_reference_boundaries_and_unlinked_status():
    items = {x["indicator_number"]: x for x in load(CATALOG)["items"]}
    assert "第3位" in items[71]["comparability_note_original"]
    assert "振興局管内別" in items[72]["comparability_note_original"]
    assert "空き店舗が解消されない原因" in items[73]["comparability_note_original"]
    assert all(len(items[n]["series"]) == 1 for n in (71, 72, 73))
    assert all(x["actual_linkage_status"] == "not_linked" for x in items.values())
    assert all(x["evaluation_status"] == "not_assessed" for x in items.values())
