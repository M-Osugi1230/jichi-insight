import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_manufacturing_growth.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manufacturing_growth_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )

    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 33
    assert catalog["indicator_number_end"] == 39
    assert [
        item["indicator_number"]
        for item in catalog["items"]
    ] == list(range(33, 40))
    assert [
        item["source_page"]
        for item in catalog["items"]
    ] == list(range(1, 8))


def test_manufacturing_growth_catalog_matches_verified_page_index():
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
        assert item["policy_field_ids"] == [catalog["policy_field_id"]]


def test_exact_indicator_names_and_values_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert [
        items[number]["indicator_name_original"]
        for number in range(33, 40)
    ] == [
        "製造業の従業者１人当たり付加価値額",
        "製造業の付加価値額",
        "宇宙産業関連の企業・団体数",
        "ヘルスケア関連産業の市場規模",
        "健康経営優良法人認定数",
        "食品工業の付加価値額",
        "省エネルギー・新エネルギー関連機器製造・関連サービス事業所売上高",
    ]

    expected_values = {
        33: [[1234, 1350, 1430]],
        34: [[20268, 20763, 22033]],
        35: [[57, 90, 115]],
        36: [[1256, 1430, 1700]],
        37: [[8, 10, 10], [8, 16, 16]],
        38: [[7303, 7700, 8100]],
        39: [[1740, 1547, 1705]],
    }
    for number, expected in expected_values.items():
        assert [
            [value["value"] for value in series["values"]]
            for series in items[number]["series"]
        ] == expected


def test_health_management_indicator_keeps_two_series():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 37
    )

    assert [series["label"] for series in indicator["series"]] == [
        "大規模法人部門（ホワイト500）",
        "中小規模法人部門（ブライト500）",
    ]
    assert all(
        series["temporal_scope"] == "snapshot"
        for series in indicator["series"]
    )


def test_indicator_38_is_not_inferred_to_be_indicator_9():
    manufacturing_indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 38
    )
    food_catalog = load(
        ROOT / "data/entities/policy/hokkaido_indicator_catalog_food.json"
    )
    food_indicator = next(
        item
        for item in food_catalog["items"]
        if item["indicator_number"] == 9
    )

    assert manufacturing_indicator["indicator_name_original"] == (
        food_indicator["indicator_name_original"]
    )
    assert manufacturing_indicator["id"] != food_indicator["id"]
    assert manufacturing_indicator["source_page"] == 6
    assert food_indicator["source_page"] == 9
    assert manufacturing_indicator["policy_field_ids"] != (
        food_indicator["policy_field_ids"]
    )
    assert "推測で統合しない" in (
        manufacturing_indicator["comparability_note_original"]
    )


def test_indicator_39_non_monotonic_target_is_not_corrected():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 39
    )
    values = [
        value["value"]
        for value in indicator["series"][0]["values"]
    ]

    assert values == [1740, 1547, 1705]
    assert "非単調" in indicator["comparability_note_original"]


def test_temporal_scopes_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }

    assert items[35]["series"][0]["temporal_scope"] == "snapshot"
    assert all(
        series["temporal_scope"] == "snapshot"
        for series in items[37]["series"]
    )
    for number in (33, 34, 36, 38, 39):
        assert all(
            series["temporal_scope"] == "calendar_year"
            for series in items[number]["series"]
        )


def test_catalog_keeps_actuals_and_evaluations_unlinked():
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
