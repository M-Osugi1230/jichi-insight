import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_pillar2.json"
EVIDENCE = POLICY / "miyagi_kpi_pillar2_evidence_packets.json"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
ALL_CATALOGS = [
    POLICY / "miyagi_kpi_catalog_pillar1.json",
    POLICY / "miyagi_kpi_catalog_measure1.json",
    POLICY / "miyagi_kpi_catalog_measure2.json",
    POLICY / "miyagi_kpi_catalog_measure3.json",
    POLICY / "miyagi_kpi_catalog_measure4.json",
    POLICY / "miyagi_kpi_catalog_measure5.json",
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_pillar2_catalog_matches_schema_and_exact_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []

    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [39, 40]
    assert [item["series_number"] for item in series] == [41, 42, 43]
    assert all(group["scope_type"] == "pillar" for group in groups)
    assert all(group["scope_number"] == 2 for group in groups)
    assert all(group["source_page"] == 57 for group in groups)
    assert all(group["printed_page"] == 56 for group in groups)


def test_pillar2_official_values_periods_and_units_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {
        item["series_number"]: item
        for group in groups.values()
        for item in group["series"]
    }
    assert tuple(value["value"] for value in series[41]["values"]) == (
        1.07,
        1.0,
        1.4,
        1.6,
    )
    assert series[41]["unit_original"] == ""
    assert series[41]["values"][1]["value_text_original"] == "1.00"

    assert tuple(value["value"] for value in series[42]["values"]) == (
        81.6,
        85.9,
        85.0,
        88.0,
    )
    assert tuple(value["value"] for value in series[43]["values"]) == (
        83.2,
        85.8,
        87.0,
        90.0,
    )
    assert [value["period_original"] for value in series[42]["values"]] == [
        "R6",
        "R7",
        "R9",
        "R12",
    ]
    assert all(group["target_setting_status"] == "set" for group in groups.values())
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups.values())
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())


def test_multi_series_and_lower_midterm_value_are_not_inferred():
    group40 = load(CATALOG)["items"][1]
    assert [item["series_number"] for item in group40["series"]] == [42, 43]
    assert "小学6年生・中学3年生の2系列を単一値へ圧縮しない" in group40[
        "comparability_note_original"
    ]
    elementary = group40["series"][0]["values"]
    assert elementary[2]["value"] < elementary[1]["value"]
    assert "公式値を補正しない" in group40["comparability_note_original"]


def test_pillar2_evidence_covers_both_target_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 2
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        "policy-target-miyagi-39",
        "policy-target-miyagi-40",
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)
    assert all(
        claim["location_note"].startswith("PDFページ57（印刷ページ56）目標値No.")
        for packet in packets
        for claim in packet["claims"]
    )


def test_all_reviewed_batches_form_40_groups_and_43_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 41))
    assert [item["series_number"] for item in series] == list(range(1, 44))
