import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_nature_environment.json"
SCHEMA = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_schema_sequence_and_pages():
    data = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(data)) == []
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (
        99,
        102,
    )
    assert [item["indicator_number"] for item in data["items"]] == [
        99,
        100,
        101,
        102,
    ]
    assert [item["source_page"] for item in data["items"]] == [1, 2, 3, 4]


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    page_index = load(
        ROOT / "data/catalog/hokkaido_indicator_page_index.json"
    )["records"]
    index = {item["indicator_number"]: item for item in page_index}
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_exact_values_periods_and_series_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    values = [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in (99, 100, 102)
    ]
    assert values == [
        [100, 100, 100],
        [90.8, 100, 100],
        [105.0, 82.0, 82.0],
    ]
    assert [
        value["period"]
        for value in items[99]["series"][0]["values"]
    ] == ["2021年", "2026年", "2031年"]
    assert [
        value["period"]
        for value in items[102]["series"][0]["values"]
    ] == ["2020年", "2025年", "2030年"]
    assert [series["label"] for series in items[101]["series"]] == [
        "東部",
        "北部",
        "中部",
    ]
    assert [
        series["values"][0]["value"] for series in items[101]["series"]
    ] == [137, 121, 107]


def test_deer_range_targets_remain_conditional():
    item = next(
        item
        for item in load(CATALOG)["items"]
        if item["indicator_number"] == 101
    )
    east, north, central = item["series"]
    assert [value["value_text_original"] for value in east["values"][1:]] == [
        "37.5～50",
        "37.5～50",
    ]
    assert [value["status"] for value in east["values"][1:]] == [
        "conditional",
        "conditional",
    ]
    assert north["values"][1]["value"] == 83
    assert central["values"][1]["value"] == 83
    assert north["values"][2]["value_text_original"] == "25～50"
    assert central["values"][2]["value_text_original"] == "25～50"
    assert north["values"][2]["value"] is None
    assert central["values"][2]["value"] is None


def test_reference_breakdowns_and_publication_lags_are_separated():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG)["items"]
    }
    air_note = items[99]["comparability_note_original"]
    substances = ["二酸化硫黄", "二酸化窒素", "浮遊粒子状物質"]
    assert all(name in air_note for name in substances)
    assert "河川、湖沼、海域" in items[100]["comparability_note_original"]
    assert "捕獲目標・捕獲実績" in items[101]["comparability_note_original"]
    assert "一般廃棄物・産業廃棄物" in items[102]["comparability_note_original"]
    assert all(
        item["actual_linkage_status"] == "not_linked"
        for item in items.values()
    )
    assert all(
        item["evaluation_status"] == "not_assessed"
        for item in items.values()
    )
