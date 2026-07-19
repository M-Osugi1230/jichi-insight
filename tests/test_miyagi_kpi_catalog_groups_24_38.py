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


def groups():
    return [group for path in CATALOGS for group in load(path)["items"]]


def test_measure4_and_5_schema_sequences_and_values():
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    for path in CATALOGS:
        assert list(validator.iter_errors(load(path))) == []
    reviewed = groups()
    series = [item for group in reviewed for item in group["series"]]
    assert [group["target_group_number"] for group in reviewed] == list(range(24, 39))
    assert [item["series_number"] for item in series] == list(range(24, 41))
    assert [item["series_number"] for item in reviewed[2]["series"]] == [26, 27, 28]
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
    for item in series:
        assert tuple(value["value"] for value in item["values"]) == expected[item["series_number"]]
        assert item["values"][3]["status"] == "not_set"


def test_measure4_linked_and_measure5_unlinked():
    reviewed = groups()
    by_number = {group["target_group_number"]: group for group in reviewed}
    assert all(by_number[number]["actual_linkage_status"] == "linked" for number in range(24, 32))
    assert all(by_number[number]["actual_linkage_status"] == "not_linked" for number in range(32, 39))
    assert all(group["evaluation_status"] == "not_assessed" for group in reviewed)
