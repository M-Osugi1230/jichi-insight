import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
NEW_CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
]
ALL_CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
    *NEW_CATALOGS,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def groups(paths=NEW_CATALOGS):
    return [group for path in paths for group in load(path)["items"]]


def test_new_catalogs_match_schema_and_exact_sequences():
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    for path in NEW_CATALOGS:
        assert list(validator.iter_errors(load(path))) == []

    reviewed = groups()
    series = [item for group in reviewed for item in group["series"]]
    assert [group["target_group_number"] for group in reviewed] == list(range(24, 39))
    assert [item["series_number"] for item in series] == list(range(24, 41))
    assert len({group["id"] for group in reviewed}) == 15
    assert len({item["id"] for item in series}) == 17
    assert all(group["source_page"] == 56 for group in reviewed)
    assert all(group["printed_page"] == 55 for group in reviewed)


def test_measure_boundaries_and_multi_series_group_are_preserved():
    reviewed = groups()
    assert [(group["scope_type"], group["scope_number"]) for group in reviewed] == (
        [("measure", 4)] * 8 + [("measure", 5)] * 7
    )
    group26 = next(group for group in reviewed if group["target_group_number"] == 26)
    assert [series["series_number"] for series in group26["series"]] == [26, 27, 28]
    assert [series["indicator_name_original"] for series in group26["series"]] == [
        "第一次産業における新規就業者数（農業）（人）",
        "第一次産業における新規就業者数（水産業）（人）",
        "第一次産業における新規就業者数（林業）（人）",
    ]
    assert "単一値へ圧縮しない" in group26["comparability_note_original"]


def test_official_values_are_preserved_by_series_number():
    expected = {
        24: (60.4, 61.1, 61.4, None),
        25: (35.8, 35.5, 36.0, None),
        26: (131, 154, 160, None),
        27: (31, 24, 54, None),
        28: (33, 69, 100, None),
        29: (9.4, 10.0, 8.8, None),
        30: (11.3, 11.2, 13.3, None),
        31: (66, 67, 77, None),
        32: (3.2, 3.2, 3.6, None),
        33: (5732, 5452, 4900, None),
        34: (21200, 21500, 21400, None),
        35: (16.4, 16.8, 17.3, None),
        36: (3930, 4085, 4126, None),
        37: (90, 90, 90, None),
        38: (355, 377.8, 405, None),
        39: (37, 51.9, 55, None),
        40: (3942, 3988, 4379, None),
    }
    series_by_number = {
        series["series_number"]: series
        for group in groups()
        for series in group["series"]
    }
    assert set(series_by_number) == set(expected)
    for number, values in expected.items():
        assert tuple(value["value"] for value in series_by_number[number]["values"]) == values
        assert [value["role"] for value in series_by_number[number]["values"]] == [
            "initial",
            "current",
            "midterm_target",
            "late_target",
        ]


def test_missing_late_targets_and_declining_targets_are_not_inferred():
    reviewed = groups()
    assert all(group["target_setting_status"] == "partially_set" for group in reviewed)
    assert all(
        series["aggregation_scope"] == "single_period"
        for group in reviewed
        for series in group["series"]
    )
    for group in reviewed:
        for series in group["series"]:
            late = series["values"][3]
            assert late == {
                "role": "late_target",
                "period_original": "R12",
                "period_year": 2030,
                "value": None,
                "status": "not_set",
                "value_text_original": "-",
            }

    by_group = {group["target_group_number"]: group for group in reviewed}
    for number in [27, 31, 32]:
        values = by_group[number]["series"][0]["values"]
        assert values[2]["value"] < values[1]["value"]
        assert "推測せず" in by_group[number]["comparability_note_original"]


def test_farmland_unit_is_explicitly_cross_checked_and_evaluation_stays_unlinked():
    reviewed = groups()
    group35 = next(group for group in reviewed if group["target_group_number"] == 35)
    assert group35["series"][0]["indicator_name_original"] == "耕地利用率"
    assert group35["series"][0]["unit_original"] == "%"
    assert "第3期みやぎ食と農の県民条例基本計画" in group35["comparability_note_original"]
    assert all(group["actual_linkage_status"] == "not_linked" for group in reviewed)
    assert all(group["evaluation_status"] == "not_assessed" for group in reviewed)


def test_all_reviewed_batches_form_38_groups_and_40_series():
    reviewed = groups(ALL_CATALOGS)
    series = [item for group in reviewed for item in group["series"]]
    assert [group["target_group_number"] for group in reviewed] == list(range(1, 39))
    assert [item["series_number"] for item in series] == list(range(1, 41))
