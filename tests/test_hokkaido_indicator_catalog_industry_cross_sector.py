import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_industry_cross_sector.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_industry_cross_sector_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )

    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 40
    assert catalog["indicator_number_end"] == 45
    assert [item["indicator_number"] for item in catalog["items"]] == list(
        range(40, 46)
    )
    assert [item["source_page"] for item in catalog["items"]] == list(
        range(1, 7)
    )


def test_industry_cross_sector_catalog_matches_verified_page_index():
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
        for number in range(40, 46)
    ] == [
        "北海道におけるスタートアップの創出・集積数",
        "企業立地件数",
        "就業率（全体）",
        "正規従業員の充足度",
        "産学官の共同研究の件数",
        "輸出額",
    ]
    assert [
        [value["value"] for value in items[40]["series"][0]["values"]],
        [value["value"] for value in items[41]["series"][0]["values"]],
        [value["value"] for value in items[42]["series"][0]["values"]],
        [value["value"] for value in items[43]["series"][0]["values"]],
        [value["value"] for value in items[44]["series"][0]["values"]],
        [value["value"] for value in items[45]["series"][0]["values"]],
    ] == [
        [124, 250, 500],
        [98, 420, 860],
        [57.6, None, None],
        [-41.4, -39.7, -38.0],
        [1712, 1872, 2046],
        [4295, 5395, 6495],
    ]


def test_startup_indicator_uses_cumulative_to_date_scope():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 40
    )

    assert {
        value["aggregation_scope"]
        for value in indicator["series"][0]["values"]
    } == {"cumulative_to_date"}
    assert "累計到達値" in indicator["comparability_note_original"]


def test_company_location_separates_annual_current_from_cumulative_targets():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 41
    )
    values = indicator["series"][0]["values"]

    assert [value["aggregation_scope"] for value in values] == [
        "single_period",
        "multi_year_cumulative",
        "multi_year_cumulative",
    ]
    assert values[1]["period"] == "2023～27年の5年累計"
    assert values[2]["period"] == "2023～32年の10年累計"
    assert "進捗率を計算しない" in indicator["comparability_note_original"]


def test_employment_rate_preserves_non_numeric_conditional_targets():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 42
    )
    values = indicator["series"][0]["values"]

    assert indicator["target_setting_status"] == "set"
    assert [value["status"] for value in values] == [
        "numeric",
        "conditional",
        "conditional",
    ]
    assert [value["value"] for value in values] == [57.6, None, None]
    assert values[1]["value_text_original"] == "各年において前年よりも上昇"
    assert values[2]["value_text_original"] == "各年において前年よりも上昇"
    assert "具体的な数値目標は設定せず" in (
        indicator["target_setting_rationale_original"]
    )


def test_regular_employee_sufficiency_keeps_negative_values():
    indicator = next(
        item
        for item in load(CATALOG_PATH)["items"]
        if item["indicator_number"] == 43
    )
    values = [
        value["value"]
        for value in indicator["series"][0]["values"]
    ]

    assert values == [-41.4, -39.7, -38.0]
    assert all(value < 0 for value in values)
    assert "欠損やエラーではなく" in indicator["comparability_note_original"]


def test_export_indicator_uses_existing_cross_field_relationship():
    catalog = load(CATALOG_PATH)
    indicator = next(
        item
        for item in catalog["items"]
        if item["indicator_number"] == 45
    )
    relationship_index = load(
        ROOT / "data/catalog/hokkaido_indicator_relationship_index.json"
    )
    relationship = next(
        item
        for item in relationship_index["relationships"]
        if item["indicator_number"] == 45
    )

    assert indicator["policy_field_ids"] == [
        relationship["primary_policy_field_id"],
        relationship["additional_policy_field_id"],
    ]
    assert relationship["source_id"] == catalog["source_id"]
    assert relationship["page_number"] == indicator["source_page"]
    assert "重複KPIとして登録しない" in (
        indicator["comparability_note_original"]
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
