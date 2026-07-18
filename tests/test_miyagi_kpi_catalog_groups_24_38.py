import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def all_groups():
    return [group for path in CATALOGS for group in load(path)["items"]]


def all_series():
    return [series for group in all_groups() for series in group["series"]]


def test_catalogs_match_schema_and_exact_ranges():
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    measure4, measure5 = [load(path) for path in CATALOGS]

    assert list(validator.iter_errors(measure4)) == []
    assert list(validator.iter_errors(measure5)) == []
    assert (
        measure4["target_group_start"],
        measure4["target_group_end"],
        measure4["series_number_start"],
        measure4["series_number_end"],
    ) == (24, 31, 24, 33)
    assert (
        measure5["target_group_start"],
        measure5["target_group_end"],
        measure5["series_number_start"],
        measure5["series_number_end"],
    ) == (32, 38, 34, 40)


def test_groups_24_to_38_and_series_24_to_40_are_contiguous():
    groups = all_groups()
    series = all_series()

    assert [group["target_group_number"] for group in groups] == list(range(24, 39))
    assert [item["series_number"] for item in series] == list(range(24, 41))
    assert len(groups) == 15
    assert len(series) == 17
    assert all(group["source_page"] == 56 for group in groups)
    assert all(group["printed_page"] == 55 for group in groups)
    assert all(group["scope_type"] == "measure" for group in groups)
    assert [group["scope_number"] for group in groups[:8]] == [4] * 8
    assert [group["scope_number"] for group in groups[8:]] == [5] * 7


def test_group_26_preserves_three_primary_industry_series():
    group = next(item for item in all_groups() if item["target_group_number"] == 26)
    assert [series["series_number"] for series in group["series"]] == [26, 27, 28]
    assert [series["indicator_name_original"] for series in group["series"]] == [
        "第一次産業における新規就業者数（農業）（人）",
        "第一次産業における新規就業者数（水産業）（人）",
        "第一次産業における新規就業者数（林業）（人）",
    ]
    assert [series["values"][1]["value"] for series in group["series"]] == [154, 24, 69]
    assert [series["values"][2]["value"] for series in group["series"]] == [160, 54, 100]
    assert "3系列" in group["comparability_note_original"]


def test_revised_current_values_and_targets_are_preserved():
    series = {item["series_number"]: item for item in all_series()}
    assert [value["value"] for value in series[24]["values"]] == [60.4, 61.1, 61.4, None]
    assert [value["value"] for value in series[25]["values"]] == [35.8, 35.5, 36.0, None]
    assert [value["value"] for value in series[31]["values"]] == [66, 67, 77, None]
    assert [value["value"] for value in series[33]["values"]] == [5732, 5452, 4900, None]
    assert [value["value"] for value in series[38]["values"]] == [355, 377.8, 405, None]
    assert [value["value"] for value in series[39]["values"]] == [37, 51.9, 55, None]
    assert [value["value"] for value in series[40]["values"]] == [3942, 3988, 4379, None]


def test_lower_targets_missing_unit_and_original_number_format_are_not_normalized():
    groups = {group["target_group_number"]: group for group in all_groups()}
    series = {item["series_number"]: item for item in all_series()}

    assert series[29]["values"][2]["value"] < series[29]["values"][1]["value"]
    assert series[33]["values"][2]["value"] < series[33]["values"][1]["value"]
    assert series[34]["values"][2]["value"] < series[34]["values"][1]["value"]
    assert all(groups[number]["comparability_note_original"] for number in (27, 31, 32))

    assert series[34]["values"][2]["value_text_original"] == "21400"
    assert series[36]["values"][2]["value_text_original"] == "4126"
    assert series[37]["indicator_name_original"] == "耕地利用率"
    assert series[37]["unit_original"] == "記載なし"
    assert "単位を推測で補完しない" in groups[35]["comparability_note_original"]


def test_late_targets_remain_unset_and_no_actuals_or_evaluations_are_inferred():
    groups = all_groups()
    for group in groups:
        assert group["target_setting_status"] == "partially_set"
        assert group["actual_linkage_status"] == "not_linked"
        assert group["evaluation_status"] == "not_assessed"
        for series in group["series"]:
            late_target = series["values"][-1]
            assert late_target == {
                "role": "late_target",
                "period_original": "R12",
                "period_year": 2030,
                "value": None,
                "status": "not_set",
                "value_text_original": "-",
            }
