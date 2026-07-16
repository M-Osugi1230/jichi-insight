import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/catalog/miyagi_indicator_source_index.json"
INDEX_SCHEMA = ROOT / "schemas/miyagi_indicator_source_index.schema.json"
COMPOSITE = ROOT / "data/catalog/miyagi_indicator_composite_targets.json"
COMPOSITE_SCHEMA = (
    ROOT / "schemas/miyagi_indicator_composite_targets.schema.json"
)
INVENTORY = ROOT / "data/catalog/miyagi_policy_source_inventory.json"
HIERARCHY = ROOT / "data/entities/policy/miyagi_policy_hierarchy.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_indicator_indexes_match_schemas():
    checker = FormatChecker()
    index_validator = Draft202012Validator(
        load(INDEX_SCHEMA),
        format_checker=checker,
    )
    composite_validator = Draft202012Validator(
        load(COMPOSITE_SCHEMA),
        format_checker=checker,
    )
    assert list(index_validator.iter_errors(load(INDEX))) == []
    assert list(composite_validator.iter_errors(load(COMPOSITE))) == []


def test_source_and_document_boundaries_match_reviewed_inventory():
    index = load(INDEX)
    sources = {
        source["id"]: source
        for source in load(INVENTORY)["sources"]
    }
    source = sources[index["source_id"]]

    assert source["id"] == "miyagi-source-implementation-middle-2026-pdf"
    assert source["url"] == index["source_document_url"]
    assert source["page_count"] == 61
    assert index["document_page_start"] == 56
    assert index["document_page_end"] == 60
    assert index["table_title_original"] == "目標指標一覧表"


def test_unique_targets_and_display_rows_are_not_confused():
    index = load(INDEX)
    composite = load(COMPOSITE)

    assert index["target_number_start"] == 1
    assert index["target_number_end"] == 128
    assert index["unique_target_count"] == 128
    assert index["display_row_count"] == 149
    assert index["composite_target_count"] == 17
    assert index["additional_series_row_count"] == 21
    assert composite["target_count"] == 17
    assert composite["additional_series_row_count"] == 21
    assert index["unique_target_count"] + 21 == index["display_row_count"]
    assert "149行を149個の独立KPIへ水増ししない" in index["counting_boundary"]


def test_page_segments_cover_rows_without_gaps():
    segments = load(INDEX)["page_segments"]
    assert [item["document_page"] for item in segments] == [56, 57, 58, 59, 60]
    assert [item["row_number_start"] for item in segments] == [1, 41, 82, 86, 124]
    assert [item["row_number_end"] for item in segments] == [40, 81, 85, 123, 149]
    assert [item["target_number_start"] for item in segments] == [1, 39, 66, 69, 105]
    assert [item["target_number_end"] for item in segments] == [38, 66, 68, 104, 128]
    assert "系列1" in segments[1]["boundary_note"]
    assert "系列2" in segments[2]["boundary_note"]


def test_sections_cover_four_directions_and_eighteen_measures():
    index = load(INDEX)
    hierarchy = load(HIERARCHY)
    sections = index["sections"]
    direction_sections = [
        item for item in sections if item["section_type"] == "direction"
    ]
    measure_sections = [
        item for item in sections if item["section_type"] == "measure"
    ]
    direction_ids = {
        direction["id"] for direction in hierarchy["directions"]
    }
    measure_ids = {
        measure["id"]
        for direction in hierarchy["directions"]
        for policy in direction["policies"]
        for measure in policy["measures"]
    }

    assert len(sections) == 22
    assert len(direction_sections) == 4
    assert len(measure_sections) == 18
    assert {item["hierarchy_id"] for item in direction_sections} == direction_ids
    assert {item["hierarchy_id"] for item in measure_sections} == measure_ids
    assert [item["section_number"] for item in direction_sections] == [1, 2, 3, 4]
    assert [item["section_number"] for item in measure_sections] == list(
        range(1, 19)
    )


def test_section_target_and_row_ranges_are_contiguous():
    sections = load(INDEX)["sections"]
    assert [item["target_number_start"] for item in sections] == [
        1,
        4,
        10,
        15,
        24,
        32,
        39,
        41,
        46,
        53,
        63,
        69,
        72,
        81,
        85,
        94,
        101,
        105,
        107,
        114,
        120,
        126,
    ]
    assert [item["target_number_end"] for item in sections] == [
        3,
        9,
        14,
        23,
        31,
        38,
        40,
        45,
        52,
        62,
        68,
        71,
        80,
        84,
        93,
        100,
        104,
        106,
        113,
        119,
        125,
        128,
    ]
    assert sections[0]["row_number_start"] == 1
    assert sections[-1]["row_number_end"] == 149
    for previous, current in zip(sections, sections[1:]):
        assert current["target_number_start"] == previous["target_number_end"] + 1
        assert current["row_number_start"] == previous["row_number_end"] + 1


def test_composite_targets_explain_all_additional_rows():
    composite = load(COMPOSITE)
    records = composite["records"]
    expected = {
        26: 3,
        40: 2,
        42: 2,
        49: 2,
        54: 2,
        55: 2,
        58: 3,
        59: 2,
        60: 2,
        62: 4,
        63: 2,
        66: 2,
        67: 2,
        71: 2,
        81: 2,
        116: 2,
        125: 2,
    }
    assert {item["target_number"]: item["series_row_count"] for item in records} == expected
    assert len(records) == composite["target_count"] == 17
    extra_rows = sum(item["series_row_count"] - 1 for item in records)
    assert extra_rows == composite["additional_series_row_count"] == 21
    assert "独立KPIへ分割せず" in composite["counting_boundary"]


def test_index_is_reviewed_but_kpi_bodies_are_not_implied():
    index = load(INDEX)
    composite = load(COMPOSITE)
    assert index["index_status"] == "position_ranges_reviewed"
    assert index["review_status"] == "reviewed"
    assert index["confidence"] == "high"
    assert composite["review_status"] == "reviewed"
    assert composite["confidence"] == "high"
