import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
NEW_CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure8.json",
    POLICY / "miyagi_kpi_catalog_measure9.json",
]
NEW_EVIDENCE = [
    POLICY / "miyagi_kpi_measure8_evidence_packets.json",
    POLICY / "miyagi_kpi_measure9_evidence_packets.json",
]
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
    assert [group["target_group_number"] for group in reviewed] == list(range(53, 69))
    assert [item["series_number"] for item in series] == list(range(58, 86))
    assert len(reviewed) == 16
    assert len(series) == 28
    assert [
        (group["scope_number"], group["target_group_number"])
        for group in reviewed
    ] == [
        *[(8, number) for number in range(53, 63)],
        *[(9, number) for number in range(63, 69)],
    ]


def test_multi_series_groups_and_page_boundary_are_preserved():
    by_group = {group["target_group_number"]: group for group in groups()}
    multi_series_counts = {
        number: len(by_group[number]["series"])
        for number in [54, 55, 58, 59, 60, 62, 63, 66, 67]
    }
    assert multi_series_counts == {
        54: 2,
        55: 2,
        58: 3,
        59: 2,
        60: 2,
        62: 4,
        63: 2,
        66: 2,
        67: 2,
    }
    assert by_group[66]["source_page"] == 57
    assert "PDFページ57〜58" in by_group[66]["comparability_note_original"]
    assert by_group[67]["source_page"] == 58
    assert by_group[68]["source_page"] == 58


def test_negative_zero_plus_and_original_comma_are_preserved():
    series = {
        item["series_number"]: item
        for group in groups()
        for item in group["series"]
    }
    assert [value["value"] for value in series[70]["values"][:3]] == [
        -3.0,
        -2.5,
        0,
    ]
    assert [value["value"] for value in series[71]["values"][:3]] == [
        -1.5,
        -1.0,
        0,
    ]
    assert series[64]["values"][0]["value_text_original"] == "+1.3"
    assert series[72]["values"][2]["value_text_original"] == "+1.5"
    assert series[75]["values"][1]["value"] == 1.19
    assert series[75]["values"][1]["value_text_original"] == "1,19"
    assert all(
        item["values"][3]["status"] == "not_set"
        and item["values"][3]["value"] is None
        and item["values"][3]["value_text_original"] == "-"
        for item in series.values()
    )


def test_declining_midterm_targets_are_not_corrected():
    by_group = {group["target_group_number"]: group for group in groups()}
    for number in [55, 59, 62, 66, 67]:
        assert "公式値を修正しない" in by_group[number]["comparability_note_original"]

    group55_junior = by_group[55]["series"][1]["values"]
    group66_junior = by_group[66]["series"][1]["values"]
    assert group55_junior[2]["value"] < group55_junior[1]["value"]
    assert group66_junior[2]["value"] < group66_junior[1]["value"]


def test_evidence_covers_all_16_groups():
    packets = [packet for path in NEW_EVIDENCE for packet in load(path)]
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 16
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(53, 69)
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_all_reviewed_batches_form_68_groups_and_85_series():
    reviewed = groups(ALL_CATALOGS)
    series = [item for group in reviewed for item in group["series"]]
    assert [group["target_group_number"] for group in reviewed] == list(range(1, 69))
    assert [item["series_number"] for item in series] == list(range(1, 86))
    assert all(group["actual_linkage_status"] == "not_linked" for group in reviewed)
    assert all(group["evaluation_status"] == "not_assessed" for group in reviewed)
