import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/hokkaido_indicator_catalog_zero_carbon.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_zero_carbon_catalog_matches_schema_and_exact_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )

    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 19
    assert catalog["indicator_number_end"] == 29
    assert [
        item["indicator_number"]
        for item in catalog["items"]
    ] == list(range(19, 30))
    assert [
        item["source_page"]
        for item in catalog["items"]
    ] == list(range(1, 12))


def test_zero_carbon_catalog_matches_verified_page_index():
    catalog = load(CATALOG_PATH)
    page_index = load(
        ROOT / "data/catalog/hokkaido_indicator_page_index.json"
    )
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


def test_exact_indicator_names_and_values_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert [
        items[number]["indicator_name_original"]
        for number in range(19, 30)
    ] == [
        "温室効果ガス実質排出量",
        "森林吸収量",
        "再生可能エネルギー導入量（設備容量）",
        "再生可能エネルギー導入量（発電電力量）",
        "再生可能エネルギー熱利用量",
        "バイオマス利活用率",
        "育成複層林の面積",
        "道産木材の利用量",
        "木質バイオマスエネルギー利用量",
        "林業の新規参入者数",
        "林業従事者の通年雇用割合",
    ]

    expected = {
        19: [[5176, 4691, 3788]],
        20: [[986, 755, 850]],
        21: [[417.1, 568.3, 865.7]],
        22: [[11120, 13878, 21516]],
        23: [[15642, 18639, 21540]],
        24: [[91.1, 93.3, 95.4], [80.4, 81.0, 81.4]],
        25: [[772, 803, 854]],
        26: [[445, 480, 502]],
        27: [[160, 179, 200]],
        28: [[134, 160, 160]],
        29: [[71.9, 74.0, 77.0]],
    }
    for number, series_values in expected.items():
        assert [
            [value["value"] for value in series["values"]]
            for series in items[number]["series"]
        ] == series_values


def test_non_monotonic_forest_target_is_not_corrected():
    item = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 20
    )
    values = [
        value["value"]
        for value in item["series"][0]["values"]
    ]

    assert values == [986, 755, 850]
    assert "原文" in item["comparability_note_original"]


def test_biomass_keeps_two_series_and_cross_field_reference():
    item = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 24
    )
    relationship_index = load(
        ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
    )
    relationship = next(
        relation
        for relation in relationship_index["relationships"]
        if relation["indicator_number"] == 24
    )

    assert [series["label"] for series in item["series"]] == [
        "廃棄物系",
        "未利用系",
    ]
    assert item["policy_field_ids"] == [
        relationship["primary_policy_field_id"],
        relationship["additional_policy_field_id"],
    ]


def test_snapshot_and_fiscal_scopes_are_not_mixed():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert items[21]["series"][0]["temporal_scope"] == "snapshot"
    assert items[25]["series"][0]["temporal_scope"] == "snapshot"
    for number in (19, 20, 22, 23, 24, 26, 27, 28, 29):
        assert all(
            series["temporal_scope"] == "fiscal_year"
            for series in items[number]["series"]
        )


def test_zero_carbon_catalog_keeps_actuals_and_evaluations_unlinked():
    catalog = load(CATALOG_PATH)

    assert all(
        item["target_setting_status"] == "set"
        for item in catalog["items"]
    )
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
