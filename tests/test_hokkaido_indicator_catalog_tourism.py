import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data/entities/policy/hokkaido_indicator_catalog_tourism.json"
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_tourism_indicator_catalog_matches_schema():
    catalog = load(CATALOG_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    assert list(validator.iter_errors(catalog)) == []


def test_tourism_catalog_covers_exact_indicator_sequence_and_pages():
    catalog = load(CATALOG_PATH)
    items = catalog["items"]

    assert catalog["indicator_number_start"] == 13
    assert catalog["indicator_number_end"] == 18
    assert len(items) == 6
    assert [item["indicator_number"] for item in items] == list(range(13, 19))
    assert [item["source_page"] for item in items] == list(range(1, 7))


def test_tourism_catalog_matches_verified_source_page_index():
    catalog = load(CATALOG_PATH)
    page_index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    pages_by_number = {
        record["indicator_number"]: record for record in page_index["records"]
    }

    for item in catalog["items"]:
        page = pages_by_number[item["indicator_number"]]
        assert page["source_id"] == catalog["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == catalog["policy_field_id"]
        assert catalog["policy_field_id"] in item["policy_field_ids"]


def test_exact_tourism_indicator_names_are_preserved():
    items = load(CATALOG_PATH)["items"]
    assert [item["indicator_name_original"] for item in items] == [
        "観光入込客数",
        "１人当たり観光消費額",
        "ＡＴガイド資格保持者数",
        "道内空港の利用者数",
        "クルーズ船の寄港回数",
        "国際会議等の開催件数",
    ]


def test_multi_series_and_exact_values_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG_PATH)["items"]}

    assert [series["label"] for series in items[13]["series"]] == [
        "道内客",
        "道外客",
        "外国人",
    ]
    assert [[value["value"] for value in series["values"]] for series in items[13]["series"]] == [
        [3756, 4880, 4880],
        [404, 700, 700],
        [69, 244, 244],
    ]

    assert [series["label"] for series in items[14]["series"]] == [
        "道内客",
        "道外客",
        "外国人",
    ]
    assert [[value["value"] for value in series["values"]] for series in items[14]["series"]] == [
        [12972, 15000, 15000],
        [81182, 88000, 88000],
        [None, 210000, 210000],
    ]

    assert [series["label"] for series in items[16]["series"]] == [
        "国内線",
        "国際線",
    ]
    assert [[value["value"] for value in series["values"]] for series in items[16]["series"]] == [
        [2189, 2671, 2671],
        [93, 410, 410],
    ]


def test_lower_bound_targets_keep_the_official_above_condition():
    items = {item["indicator_number"]: item for item in load(CATALOG_PATH)["items"]}

    bounded_final_values = [
        value
        for number in (13, 14, 15, 16)
        for series in items[number]["series"]
        for value in series["values"]
        if value["role"] == "final_target"
    ]
    assert len(bounded_final_values) == 9
    assert all(value["operator"] == "at_least" for value in bounded_final_values)
    assert all("以上" in value["value_text_original"] for value in bounded_final_values)


def test_missing_current_values_are_null_not_zero():
    items = {item["indicator_number"]: item for item in load(CATALOG_PATH)["items"]}

    foreign_current = items[14]["series"][2]["values"][0]
    guide_current = items[15]["series"][0]["values"][0]

    assert foreign_current["value"] is None
    assert foreign_current["status"] == "not_available"
    assert foreign_current["value_text_original"] == "―"
    assert guide_current["value"] is None
    assert guide_current["status"] == "not_available"
    assert guide_current["value_text_original"] == "-"


def test_cross_field_indicators_match_the_relationship_index():
    items = {item["indicator_number"]: item for item in load(CATALOG_PATH)["items"]}
    relationships = load(
        ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
    )["relationships"]
    relationships_by_number = {
        relationship["indicator_number"]: relationship
        for relationship in relationships
    }

    for indicator_number in (16, 17):
        relationship = relationships_by_number[indicator_number]
        assert items[indicator_number]["policy_field_ids"] == [
            relationship["primary_policy_field_id"],
            relationship["additional_policy_field_id"],
        ]


def test_temporal_scopes_and_simple_targets_are_preserved():
    items = {item["indicator_number"]: item for item in load(CATALOG_PATH)["items"]}

    assert all(series["temporal_scope"] == "fiscal_year" for series in items[13]["series"])
    assert all(series["temporal_scope"] == "fiscal_year" for series in items[14]["series"])
    assert items[15]["series"][0]["temporal_scope"] == "snapshot"
    assert all(series["temporal_scope"] == "fiscal_year" for series in items[16]["series"])
    assert items[17]["series"][0]["temporal_scope"] == "calendar_year"
    assert items[18]["series"][0]["temporal_scope"] == "calendar_year"
    assert [value["value"] for value in items[17]["series"][0]["values"]] == [121, 160, 200]
    assert [value["value"] for value in items[18]["series"][0]["values"]] == [23, 145, 155]


def test_tourism_catalog_keeps_actuals_and_evaluation_unlinked():
    catalog = load(CATALOG_PATH)
    assert catalog["review_status"] == "reviewed"
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert not any("score" in item for item in catalog["items"])
    assert not any("progress_rate" in item for item in catalog["items"])
