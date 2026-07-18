import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data/catalog/miyagi_indicator_source_index.json"
SCHEMA = ROOT / "schemas/miyagi_indicator_source_index.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expand_range(start: int, end: int):
    return list(range(start, end + 1))


def test_miyagi_indicator_source_index_matches_schema():
    index = load(INDEX)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(index)) == []
    assert index["target_group_count"] == 128
    assert index["indicator_series_count"] == 149
    assert index["multi_series_group_count"] == 17
    assert index["additional_series_count"] == 21
    assert index["reviewed_target_group_count"] == 9
    assert index["reviewed_indicator_series_count"] == 9
    assert index["review_status"] == "positions_verified"
    assert index["content_review_status"] == "in_progress"


def test_page_ranges_cover_all_series_without_gaps_or_duplicates():
    index = load(INDEX)
    series_numbers = [
        number
        for page in index["page_ranges"]
        for number in expand_range(
            page["series_number_start"],
            page["series_number_end"],
        )
    ]
    assert series_numbers == list(range(1, 150))
    assert len(series_numbers) == len(set(series_numbers)) == 149
    assert [page["pdf_page_number"] for page in index["page_ranges"]] == [
        56,
        57,
        58,
        59,
        60,
    ]
    assert [page["printed_page_number"] for page in index["page_ranges"]] == [
        55,
        56,
        57,
        58,
        59,
    ]


def test_scope_ranges_cover_target_groups_exactly_once():
    index = load(INDEX)
    target_groups = [
        number
        for scope in index["scope_ranges"]
        for number in expand_range(
            scope["target_group_start"],
            scope["target_group_end"],
        )
    ]
    assert target_groups == list(range(1, 129))
    assert len(target_groups) == len(set(target_groups)) == 128

    pillars = [scope for scope in index["scope_ranges"] if scope["scope_type"] == "pillar"]
    measures = [scope for scope in index["scope_ranges"] if scope["scope_type"] == "measure"]
    assert [scope["scope_number"] for scope in pillars] == [1, 2, 3, 4]
    assert [scope["scope_number"] for scope in measures] == list(range(1, 19))


def test_multi_series_groups_expand_128_groups_to_149_series():
    index = load(INDEX)
    multi = {
        item["target_group_number"]: item["series_count"]
        for item in index["multi_series_groups"]
    }
    expected_multi = {
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
    assert multi == expected_multi

    series_count = sum(multi.get(group, 1) for group in range(1, 129))
    additional_series = sum(count - 1 for count in multi.values())
    assert series_count == index["indicator_series_count"] == 149
    assert additional_series == index["additional_series_count"] == 21


def test_group_66_is_the_only_group_split_across_pdf_pages():
    index = load(INDEX)
    pages_by_group = {}
    for page in index["page_ranges"]:
        for group in expand_range(
            page["target_group_start"],
            page["target_group_end"],
        ):
            pages_by_group.setdefault(group, []).append(page["pdf_page_number"])

    split_groups = {
        group: pages
        for group, pages in pages_by_group.items()
        if len(pages) > 1
    }
    assert split_groups == {66: [57, 58]}
