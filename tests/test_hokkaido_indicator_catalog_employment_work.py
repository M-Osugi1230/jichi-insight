import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_employment_work.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_employment_work_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 66
    assert catalog["indicator_number_end"] == 70
    assert [item["indicator_number"] for item in catalog["items"]] == list(
        range(66, 71)
    )
    assert [item["source_page"] for item in catalog["items"]] == list(
        range(1, 6)
    )


def test_catalog_matches_verified_page_index():
    catalog = load(CATALOG_PATH)
    index = load(ROOT / "data/catalog/hokkaido_indicator_page_index.json")
    pages = {item["indicator_number"]: item for item in index["records"]}
    for item in catalog["items"]:
        page = pages[item["indicator_number"]]
        assert page["source_id"] == catalog["source_id"]
        assert page["page_number"] == item["source_page"]
        assert page["policy_field_id"] == catalog["policy_field_id"]


def test_exact_names_values_and_periods_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert [items[number]["indicator_name_original"] for number in range(66, 71)] == [
        "若者（25～29歳）の就業率",
        "高齢者（65歳以上）の就業率",
        "女性の就業率",
        "障がいのある人の実雇用率（民間企業）",
        "年間総労働時間（フルタイム労働者）",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(66, 71)
    ] == [
        [85.8, 87.2, 88.6],
        [23.3, 25.4, 27.4],
        [49.2, 50.4, 51.6],
        [2.58, None, None],
        [1954, 1928, 1923],
    ]
    assert [
        [value["period"] for value in items[number]["series"][0]["values"]]
        for number in range(66, 71)
    ] == [
        ["2023年", "2028年", "2033年"],
        ["2023年", "2028年", "2033年"],
        ["2023年", "2028年", "2033年"],
        ["2023年", "2028年", "2033年"],
        ["2022年", "2027年", "2032年"],
    ]


def test_reference_breakdowns_are_excluded_from_kpi_series():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    for number in (66, 67, 68):
        assert len(items[number]["series"]) == 1
        assert "参考内訳" in items[number]["comparability_note_original"]
    assert "男性89.7％、女性81.8％" in items[66]["comparability_note_original"]
    assert "男性32.8％、女性16.5％" in items[67]["comparability_note_original"]
    assert "年齢階層別" in items[68]["comparability_note_original"]


def test_legal_employment_rate_targets_remain_conditional():
    item = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 69
    )
    values = item["series"][0]["values"]
    assert values[0]["value"] == 2.58
    assert values[0]["status"] == "numeric"
    assert [value["status"] for value in values[1:]] == ["conditional", "conditional"]
    assert [value["value"] for value in values[1:]] == [None, None]
    assert [value["value_text_original"] for value in values[1:]] == [
        "法定雇用率以上",
        "法定雇用率以上",
    ]


def test_working_hours_and_temporal_scopes_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    for number in (66, 67, 68, 70):
        assert items[number]["series"][0]["temporal_scope"] == "calendar_year"
    assert items[69]["series"][0]["temporal_scope"] == "snapshot"
    hours = items[70]["series"][0]
    assert hours["unit_original"] == "時間"
    assert [value["value"] for value in hours["values"]] == [1954, 1928, 1923]
    assert "全国との過去推移" in items[70]["comparability_note_original"]


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    catalog = load(CATALOG_PATH)
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert not any("score" in item or "progress_rate" in item for item in catalog["items"])
