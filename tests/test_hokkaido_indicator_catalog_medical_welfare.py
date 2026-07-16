import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT
    / "data/entities/policy/"
    "hokkaido_indicator_catalog_medical_welfare.json"
)
SCHEMA_PATH = ROOT / "schemas/hokkaido_indicator_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_medical_welfare_catalog_matches_schema_and_sequence():
    catalog = load(CATALOG_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    assert catalog["indicator_number_start"] == 61
    assert catalog["indicator_number_end"] == 65
    assert [item["indicator_number"] for item in catalog["items"]] == list(
        range(61, 66)
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


def test_exact_names_and_values_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert [items[number]["indicator_name_original"] for number in range(61, 66)] == [
        "医師少数区域数",
        "看護職員就業者数が全国平均値以上の圏域数",
        "北海道福祉人材センターの支援による介護職への就業者数",
        "特定健康診査受診率",
        "特定保健指導実施率",
    ]
    assert [
        [value["value"] for value in items[number]["series"][0]["values"]]
        for number in range(61, 66)
    ] == [
        [11, 0, 0],
        [16, 21, 21],
        [234, 234, 263],
        [45.7, 70.0, 70.0],
        [42.4, 60.0, 60.0],
    ]


def test_explicit_zero_is_numeric_and_reference_series_are_excluded():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    doctor_values = items[61]["series"][0]["values"]
    assert [value["value"] for value in doctor_values] == [11, 0, 0]
    assert all(value["status"] == "numeric" for value in doctor_values)
    assert "解消目標" in items[61]["comparability_note_original"]
    assert len(items[62]["series"]) == 1
    assert "参考内訳" in items[62]["comparability_note_original"]
    assert len(items[63]["series"]) == 1
    assert "有効求人倍率" in items[63]["comparability_note_original"]


def test_temporal_scopes_and_delayed_publication_are_preserved():
    items = {
        item["indicator_number"]: item
        for item in load(CATALOG_PATH)["items"]
    }
    assert items[61]["series"][0]["temporal_scope"] == "snapshot"
    assert items[62]["series"][0]["temporal_scope"] == "snapshot"
    for number in (63, 64, 65):
        assert items[number]["series"][0]["temporal_scope"] == "fiscal_year"
    assert items[64]["series"][0]["values"][0]["period"] == "2021年"
    assert items[65]["series"][0]["values"][0]["period"] == "2021年"
    assert "2年前" in items[64]["comparability_note_original"]
    assert "2年前" in items[65]["comparability_note_original"]


def test_catalog_keeps_actuals_and_evaluations_unlinked():
    catalog = load(CATALOG_PATH)
    assert all(item["actual_linkage_status"] == "not_linked" for item in catalog["items"])
    assert all(item["evaluation_status"] == "not_assessed" for item in catalog["items"])
    assert not any("score" in item or "progress_rate" in item for item in catalog["items"])
