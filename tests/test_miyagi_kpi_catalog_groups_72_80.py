import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure10.json"
EVIDENCE = POLICY / "miyagi_kpi_measure10_evidence_packets.json"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
ALL_CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
    POLICY / "miyagi_kpi_catalog_pillar2.json",
    POLICY / "miyagi_kpi_catalog_measure6.json",
    POLICY / "miyagi_kpi_catalog_measure7.json",
    POLICY / "miyagi_kpi_catalog_measure8.json",
    POLICY / "miyagi_kpi_catalog_measure9.json",
    POLICY / "miyagi_kpi_catalog_pillar3.json",
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure10_catalog_matches_schema_and_exact_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []

    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(72, 81))
    assert [item["series_number"] for item in series] == list(range(90, 99))
    assert all(group["scope_type"] == "measure" for group in groups)
    assert all(group["scope_number"] == 10 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)
    assert all(group["printed_page"] == 58 for group in groups)


def test_official_values_are_preserved():
    expected = {
        90: (7602, 7602, 8430, None),
        91: (68026, 67759, 71000, None),
        92: (2.29, 2.39, 2.70, None),
        93: (43, 50, 60, None),
        94: (276, 276, 363, None),
        95: (806, 961, 1330, None),
        96: (491, 492, 500, None),
        97: (16, 16, 30, None),
        98: (16586, 16586, 20000, None),
    }
    series = {
        item["series_number"]: item
        for group in load(CATALOG)["items"]
        for item in group["series"]
    }
    assert set(series) == set(expected)
    for number, values in expected.items():
        assert tuple(value["value"] for value in series[number]["values"]) == values
        assert series[number]["values"][3]["status"] == "not_set"
        assert series[number]["values"][3]["value_text_original"] == "-"

    assert series[92]["values"][2]["value_text_original"] == "2.70"
    assert series[95]["values"][2]["value_text_original"] == "1330"


def test_cumulative_and_same_period_boundaries_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert {
        number
        for number, group in groups.items()
        if group["series"][0]["aggregation_scope"] == "cumulative_to_date"
    } == {72, 76, 77}

    for number in [72, 76]:
        values = groups[number]["series"][0]["values"]
        assert values[0]["period_original"] == values[1]["period_original"] == "R6"

    for number in [79, 80]:
        values = groups[number]["series"][0]["values"]
        assert values[0]["period_original"] == values[1]["period_original"] == "R5"

    assert "半角括弧" in groups[76]["comparability_note_original"]
    assert "原文表記は1330" in groups[77]["comparability_note_original"]


def test_measure10_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 9
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(72, 81)
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)


def test_all_reviewed_batches_form_80_groups_and_98_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 81))
    assert [item["series_number"] for item in series] == list(range(1, 99))
    linked = {
        group["target_group_number"]
        for group in groups
        if group["actual_linkage_status"] == "linked"
    }
    assert linked == {4, 5, 6, 8, 9, 10, 11, 12, 14}
    assert all(
        group["actual_linkage_status"] == "not_linked"
        for group in groups
        if group["target_group_number"] not in linked
    )
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
