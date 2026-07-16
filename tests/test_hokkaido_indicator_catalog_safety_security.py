import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/entities/policy/hokkaido_indicator_catalog_safety_security.json"
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
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (74, 79)
    assert [item["indicator_number"] for item in data["items"]] == list(range(74, 80))
    assert [item["source_page"] for item in data["items"]] == list(range(1, 7))


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


def test_exact_names_values_and_scopes_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert [items[number]["indicator_name_original"] for number in range(74, 80)] == [
        "刑法犯認知件数",
        "重要犯罪の検挙率",
        "消費生活相談の解決割合",
        "人口10万人当たりの人権侵犯事件数",
        "女性（25～34歳）の就業率",
        "感染症指定医療機関病床数",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(74, 80)
    ] == [
        [22232, 22232, None],
        [90.3, 90.3, None],
        [31.4, 34.7, 38.0],
        [7.2, 6.9, 6.9],
        [78.9, 82.5, 82.5],
        [94, 98, 98],
    ]
    assert [
        items[number]["series"][0]["temporal_scope"]
        for number in range(74, 80)
    ] == [
        "calendar_year",
        "calendar_year",
        "fiscal_year",
        "calendar_year",
        "snapshot",
        "snapshot",
    ]


def test_compound_rolling_average_targets_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    crime_values = items[74]["series"][0]["values"]
    arrest_values = items[75]["series"][0]["values"]

    assert crime_values[1]["operator"] == "at_most"
    assert crime_values[1]["value"] == 22232
    assert crime_values[1]["value_text_original"] == (
        "22,232以下かつ過去５年平均値以下"
    )
    assert crime_values[2]["status"] == "conditional"
    assert crime_values[2]["value"] is None
    assert "過去５年平均値以下" in crime_values[2]["value_text_original"]

    assert arrest_values[1]["operator"] == "at_least"
    assert arrest_values[1]["value"] == 90.3
    assert arrest_values[1]["value_text_original"] == (
        "90.3以上かつ過去５年平均値以上"
    )
    assert arrest_values[2]["status"] == "conditional"
    assert arrest_values[2]["value"] is None
    assert "過去５年平均値以上" in arrest_values[2]["value_text_original"]


def test_reference_data_and_distinct_population_scope_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert "29歳以下・65歳以上" in items[76]["comparability_note_original"]
    assert "算出要素" in items[77]["comparability_note_original"]
    assert "指標68" in items[78]["comparability_note_original"]
    assert "年齢範囲と時点が異なる" in items[78]["comparability_note_original"]
    assert "区域・指定医療機関別" in items[79]["comparability_note_original"]
    assert all(len(items[number]["series"]) == 1 for number in range(74, 80))


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
