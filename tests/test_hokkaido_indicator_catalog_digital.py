import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT / "data/entities/policy/hokkaido_indicator_catalog_digital.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_digital_catalog_matches_schema_and_exact_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )

    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 30
    assert catalog["indicator_number_end"] == 32
    assert [item["indicator_number"] for item in catalog["items"]] == [30, 31, 32]
    assert [item["source_page"] for item in catalog["items"]] == [1, 2, 3]


def test_digital_catalog_matches_verified_page_index():
    catalog = load(CATALOG_PATH)
    page_index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    pages = {
        item["indicator_number"]: item
        for item in page_index["records"]
    }

    for item in catalog["items"]:
        page = pages[item["indicator_number"]]
        assert page["source_id"] == catalog["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == catalog["policy_field_id"]
        assert item["policy_field_ids"] == [catalog["policy_field_id"]]


def test_exact_names_values_and_periods_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert [items[number]["indicator_name_original"] for number in (30, 31, 32)] == [
        "データセンター、デジタル関連企業の立地件数",
        "半導体関連企業による製造品出荷額",
        "半導体関連企業の生産活動による道内総生産への影響額",
    ]
    assert [
        value["value"]
        for value in items[30]["series"][0]["values"]
    ] == [28, 105, 260]
    assert [
        value["period"]
        for value in items[30]["series"][0]["values"]
    ] == ["2022年", "2023〜2027年", "2023〜2032年"]
    assert [
        value["value"]
        for value in items[31]["series"][0]["values"]
    ] == [1506, None, 5700]
    assert [
        value["value"]
        for value in items[32]["series"][0]["values"]
    ] == [None, None, 10259]


def test_single_period_and_cumulative_values_are_not_mixed():
    values = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 30
    )["series"][0]["values"]

    assert values[0]["aggregation_scope"] == "single_period"
    assert values[1]["aggregation_scope"] == "multi_year_cumulative"
    assert values[2]["aggregation_scope"] == "multi_year_cumulative"
    assert "単純な達成率" in next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 30
    )["comparability_note_original"]


def test_partial_targets_and_missing_values_remain_null():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert items[31]["target_setting_status"] == "partially_set"
    assert items[32]["target_setting_status"] == "partially_set"

    indicator31_intermediate = items[31]["series"][0]["values"][1]
    indicator32_current = items[32]["series"][0]["values"][0]
    indicator32_intermediate = items[32]["series"][0]["values"][1]

    assert indicator31_intermediate["value"] is None
    assert indicator31_intermediate["status"] == "not_set"
    assert indicator31_intermediate["value_text_original"] == "―"
    assert indicator32_current["value"] is None
    assert indicator32_current["status"] == "not_available"
    assert indicator32_intermediate["value"] is None
    assert indicator32_intermediate["status"] == "not_set"


def test_digital_catalog_keeps_actuals_and_evaluations_unlinked():
    catalog = load(CATALOG_PATH)

    assert all(
        item["actual_linkage_status"] == "not_linked"
        for item in catalog["items"]
    )
    assert all(
        item["evaluation_status"] == "not_assessed"
        for item in catalog["items"]
    )
    assert not any(
        "score" in item or "progress_rate" in item
        for item in catalog["items"]
    )
