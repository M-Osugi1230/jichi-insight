import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def all_groups():
    return [group for path in CATALOGS for group in load(path)["items"]]


def test_catalogs_match_schema_and_form_one_sequence():
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    for path in CATALOGS:
        assert list(validator.iter_errors(load(path))) == []

    groups = all_groups()
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 24))
    assert [item["series_number"] for item in series] == list(range(1, 24))
    assert len({group["id"] for group in groups}) == 23
    assert len({item["id"] for item in series}) == 23
    assert all(group["source_page"] == 56 for group in groups)
    assert all(group["printed_page"] == 55 for group in groups)


def test_scope_boundaries_match_verified_source_index():
    groups = all_groups()
    assert [(group["scope_type"], group["scope_number"]) for group in groups] == (
        [("pillar", 1)] * 3
        + [("measure", 1)] * 6
        + [("measure", 2)] * 5
        + [("measure", 3)] * 9
    )
    index = load(ROOT / "data/catalog/miyagi_indicator_source_index.json")
    indexed = {
        number
        for scope in index["scope_ranges"][:4]
        for number in range(scope["target_group_start"], scope["target_group_end"] + 1)
    }
    assert indexed == set(range(1, 24))


def test_all_numeric_values_and_periods_are_preserved():
    expected = {
        1: (-1.12, -1.12, 0.1, 0.1),
        2: (7968, 7968, 8612, 8690),
        3: (2871, 2871, 3107, 3137),
        4: (410, 429, 470, None),
        5: (27276, 27276, 30300, None),
        6: (3463, 3684, 5368, None),
        7: (10283, 19420, 48283, None),
        8: (47669, 47201, 49339, None),
        9: (97, 176, 257, None),
        10: (943, 988, 1104, None),
        11: (51.5, 74.3, 120, None),
        12: (3985, 4527, 6000, None),
        13: (71768, 71508, 90000, None),
        14: (28272, 28555, 29129, None),
        15: (1737, 1924, 2210, None),
        16: (319, 324, 424, None),
        17: (922, 888, 833, None),
        18: (2586, 2661, 2415, None),
        19: (112.4, 97.3, 102, None),
        20: (1145, 1145, 980, None),
        21: (7160, 7491, 7300, None),
        22: (2407, 2472, 2680, None),
        23: (154, 152, 292, None),
    }
    groups = {group["target_group_number"]: group for group in all_groups()}
    for number, values in expected.items():
        assert tuple(
            value["value"] for value in groups[number]["series"][0]["values"]
        ) == values
        assert [
            value["role"] for value in groups[number]["series"][0]["values"]
        ] == ["initial", "current", "midterm_target", "late_target"]


def test_late_targets_are_not_zero_filled():
    groups = {group["target_group_number"]: group for group in all_groups()}
    assert all(groups[number]["target_setting_status"] == "set" for number in range(1, 4))
    assert all(
        groups[number]["target_setting_status"] == "partially_set"
        for number in range(4, 24)
    )
    for number in range(4, 24):
        late = groups[number]["series"][0]["values"][3]
        assert late["status"] == "not_set"
        assert late["value"] is None
        assert late["value_text_original"] == "-"


def test_cumulative_negative_and_declining_targets_are_explicit():
    groups = {group["target_group_number"]: group for group in all_groups()}
    cumulative = {
        number
        for number, group in groups.items()
        if group["series"][0]["aggregation_scope"] == "cumulative_to_date"
    }
    assert cumulative == {4, 5, 7, 9, 23}
    assert groups[1]["series"][0]["values"][0]["value"] == -1.12
    assert groups[1]["series"][0]["values"][1]["value"] == -1.12

    for number in [17, 18, 20, 21]:
        values = groups[number]["series"][0]["values"]
        assert values[2]["value"] < values[1]["value"]
        assert "補正しない" in groups[number]["comparability_note_original"]


def test_review_status_stops_before_actuals_and_evaluation():
    groups = all_groups()
    assert all(group["review_status"] == "reviewed" for group in groups)
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
