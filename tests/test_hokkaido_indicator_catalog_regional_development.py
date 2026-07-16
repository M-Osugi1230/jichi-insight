import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "hokkaido_indicator_catalog_regional_development.json"
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
    assert (data["indicator_number_start"], data["indicator_number_end"]) == (80, 83)
    assert [item["indicator_number"] for item in data["items"]] == [80, 81, 82, 83]
    assert [item["source_page"] for item in data["items"]] == [1, 2, 3, 4]


def test_catalog_matches_verified_page_index():
    data = load(CATALOG)
    index_path = ROOT / "data/catalog/hokkaido_indicator_page_index.json"
    index = {
        item["indicator_number"]: item
        for item in load(index_path)["records"]
    }
    for item in data["items"]:
        page = index[item["indicator_number"]]
        assert page["source_id"] == data["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == data["policy_field_id"]


def test_exact_names_values_and_scopes_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    assert [items[number]["indicator_name_original"] for number in range(80, 84)] == [
        "人口の社会増減数",
        "地域おこし協力隊員数",
        "北海道への移住相談件数",
        "北方領土返還要求署名数",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(80, 84)
    ] == [
        [4021, 0, None],
        [943, 1300, 1600],
        [15540, 18690, 21840],
        [9332, 9782, 10232],
    ]
    assert [
        items[number]["series"][0]["temporal_scope"]
        for number in range(80, 84)
    ] == ["calendar_year", "fiscal_year", "fiscal_year", "fiscal_year"]


def test_social_increase_target_remains_conditional():
    item = next(
        item
        for item in load(CATALOG)["items"]
        if item["indicator_number"] == 80
    )
    values = item["series"][0]["values"]
    assert values[0]["value"] == 4021
    assert values[1]["value"] == 0
    assert values[2]["status"] == "conditional"
    assert values[2]["value"] is None
    assert values[2]["value_text_original"] == "社会増"


def test_signature_total_is_cumulative_and_reference_breakdowns_are_excluded():
    items = {item["indicator_number"]: item for item in load(CATALOG)["items"]}
    signature_values = items[83]["series"][0]["values"]
    assert all(
        value["aggregation_scope"] == "cumulative_to_date"
        for value in signature_values
    )
    assert items[83]["series"][0]["unit_original"] == "万人"
    assert "単年度署名数" in items[83]["comparability_note_original"]
    assert "日本人・外国人" in items[80]["comparability_note_original"]
    assert "振興局別・自治体別" in items[81]["comparability_note_original"]
    assert "北海道窓口と市町村窓口" in items[82]["comparability_note_original"]


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    items = load(CATALOG)["items"]
    assert all(item["actual_linkage_status"] == "not_linked" for item in items)
    assert all(item["evaluation_status"] == "not_assessed" for item in items)
