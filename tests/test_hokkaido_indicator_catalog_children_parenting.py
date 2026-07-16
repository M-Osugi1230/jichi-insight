import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_children_parenting.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_children_parenting_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )

    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 46
    assert catalog["indicator_number_end"] == 52
    assert [item["indicator_number"] for item in catalog["items"]] == list(
        range(46, 53)
    )
    assert [item["source_page"] for item in catalog["items"]] == list(
        range(1, 8)
    )


def test_children_parenting_catalog_matches_verified_page_index():
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
        assert catalog["policy_field_id"] in item["policy_field_ids"]


def test_exact_names_and_values_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert [
        items[number]["indicator_name_original"]
        for number in range(46, 53)
    ] == [
        "合計特殊出生率",
        "総合周産期母子医療センターの整備圏域数",
        "地域周産期母子医療センターの整備圏域数",
        "保育所入所待機児童数",
        "育児休業取得率",
        "小児二次救急医療体制の確保された圏域数",
        "里親等委託率",
    ]
    assert [
        [value["value"] for value in items[46]["series"][0]["values"]],
        [value["value"] for value in items[47]["series"][0]["values"]],
        [value["value"] for value in items[48]["series"][0]["values"]],
        [value["value"] for value in items[49]["series"][0]["values"]],
        [
            [value["value"] for value in series["values"]]
            for series in items[50]["series"]
        ],
        [value["value"] for value in items[51]["series"][0]["values"]],
        [value["value"] for value in items[52]["series"][0]["values"]],
    ] == [
        [1.12, None, None],
        [4, 6, 6],
        [21, 21, 21],
        [62, 0, 0],
        [[29.4, 71.0, 85.0], [83.5, 90.0, 90.0]],
        [20, 21, 21],
        [36.1, None, None],
    ]


def test_fertility_rate_preserves_national_benchmark_targets():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 46
    )
    values = indicator["series"][0]["values"]

    assert [value["status"] for value in values] == [
        "numeric",
        "conditional",
        "conditional",
    ]
    assert [value["value_text_original"] for value in values[1:]] == [
        "全国値",
        "全国値",
    ]
    assert all(value["value"] is None for value in values[1:])
    assert "固定数値へ変換せず" in indicator["comparability_note_original"]


def test_waiting_children_zero_targets_are_explicit_numeric_values():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 49
    )
    values = indicator["series"][0]["values"]

    assert [value["value"] for value in values] == [62, 0, 0]
    assert all(value["status"] == "numeric" for value in values)
    assert values[1]["value_text_original"] == "0"
    assert values[2]["value_text_original"] == "0"
    assert "明示されたゼロ目標" in indicator["comparability_note_original"]


def test_parental_leave_keeps_sex_series_and_cross_field_reference():
    catalog = load(CATALOG_PATH)
    indicator = next(
        item
        for item in catalog["items"]
        if item["indicator_number"] == 50
    )
    relationship_index = load(
        ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
    )
    relationship = next(
        item
        for item in relationship_index["relationships"]
        if item["indicator_number"] == 50
    )

    assert [series["label"] for series in indicator["series"]] == [
        "男性",
        "女性",
    ]
    assert indicator["policy_field_ids"] == [
        relationship["primary_policy_field_id"],
        relationship["additional_policy_field_id"],
    ]
    assert relationship["source_id"] == catalog["source_id"]
    assert relationship["page_number"] == indicator["source_page"]
    assert "男女を別系列" in indicator["comparability_note_original"]


def test_foster_care_rate_preserves_relative_increase_targets():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 52
    )
    values = indicator["series"][0]["values"]

    assert [value["status"] for value in values] == [
        "numeric",
        "conditional",
        "conditional",
    ]
    assert [value["value_text_original"] for value in values[1:]] == [
        "現状より増加",
        "現状より増加",
    ]
    assert all(value["value"] is None for value in values[1:])


def test_snapshot_and_other_scopes_are_not_mixed():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    for number in (47, 48, 49, 51, 52):
        assert items[number]["series"][0]["temporal_scope"] == "snapshot"
    assert items[46]["series"][0]["temporal_scope"] == "calendar_year"
    assert all(
        series["temporal_scope"] == "other"
        for series in items[50]["series"]
    )


def test_catalog_keeps_actuals_and_evaluations_unlinked():
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
