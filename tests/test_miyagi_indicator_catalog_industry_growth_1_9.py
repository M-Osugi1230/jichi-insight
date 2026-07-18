import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_indicator_catalog_industry_growth_1_9.json"
SCHEMA = ROOT / "schemas/miyagi_indicator_catalog.schema.json"
INDEX = ROOT / "data/catalog/miyagi_indicator_source_index.json"
HIERARCHY = POLICY / "miyagi_policy_hierarchy.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_catalog_schema_sequence_scope_and_source_page():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    assert (
        catalog["target_group_number_start"],
        catalog["target_group_number_end"],
    ) == (1, 9)
    assert (
        catalog["indicator_series_number_start"],
        catalog["indicator_series_number_end"],
    ) == (1, 9)
    assert [item["target_group_number"] for item in catalog["items"]] == list(
        range(1, 10)
    )
    assert [
        item["series"][0]["series_number"] for item in catalog["items"]
    ] == list(range(1, 10))
    assert all(item["source_pdf_page"] == 56 for item in catalog["items"])
    assert all(item["source_printed_page"] == 55 for item in catalog["items"])

    assert [item["scope_type"] for item in catalog["items"][:3]] == [
        "pillar",
        "pillar",
        "pillar",
    ]
    assert all(
        item["scope_id"] == "policy-direction-miyagi-industry-growth"
        for item in catalog["items"][:3]
    )
    assert all(
        item["scope_id"] == "policy-measure-miyagi-1"
        for item in catalog["items"][3:]
    )


def test_catalog_matches_verified_index_and_hierarchy():
    catalog = load(CATALOG)
    index = load(INDEX)
    hierarchy = load(HIERARCHY)

    page = index["page_ranges"][0]
    assert page["pdf_page_number"] == 56
    assert page["printed_page_number"] == 55
    assert page["target_group_start"] <= catalog["target_group_number_start"]
    assert page["target_group_end"] >= catalog["target_group_number_end"]
    assert page["series_number_start"] <= catalog["indicator_series_number_start"]
    assert page["series_number_end"] >= catalog["indicator_series_number_end"]

    direction = hierarchy["directions"][0]
    measure = direction["policies"][0]["measures"][0]
    assert direction["id"] == catalog["policy_direction_id"]
    assert measure["id"] == "policy-measure-miyagi-1"
    assert hierarchy["kpi_linkage_status"] == "positions_indexed"


def test_initial_current_and_target_values_are_preserved():
    items = {
        item["target_group_number"]: item
        for item in load(CATALOG)["items"]
    }
    assert [
        value["role"] for value in items[1]["series"][0]["values"]
    ] == ["initial", "current", "intermediate_target", "final_target"]
    assert [
        value["value"] for value in items[1]["series"][0]["values"]
    ] == [-1.12, -1.12, 0.1, 0.1]
    assert [
        value["value"] for value in items[2]["series"][0]["values"]
    ] == [7968, 7968, 8612, 8690]
    assert [
        value["value"] for value in items[3]["series"][0]["values"]
    ] == [2871, 2871, 3107, 3137]
    assert [
        value["value"] for value in items[8]["series"][0]["values"]
    ] == [47669, 47201, 49339, None]


def test_hyphen_targets_and_cumulative_values_keep_quality_boundaries():
    items = {
        item["target_group_number"]: item
        for item in load(CATALOG)["items"]
    }
    for number in range(4, 10):
        item = items[number]
        final_target = item["series"][0]["values"][-1]
        assert item["target_setting_status"] == "partially_set"
        assert final_target["role"] == "final_target"
        assert final_target["period_original"] == "令和12年度"
        assert final_target["value"] is None
        assert final_target["status"] == "not_set"
        assert final_target["value_text_original"] == "-"

    cumulative_groups = {4, 5, 7, 9}
    assert {
        number
        for number, item in items.items()
        if item["series"][0]["aggregation_scope"] == "cumulative_to_date"
    } == cumulative_groups
    assert all(
        item["actual_linkage_status"] == "not_linked"
        and item["evaluation_status"] == "not_assessed"
        for item in items.values()
    )
