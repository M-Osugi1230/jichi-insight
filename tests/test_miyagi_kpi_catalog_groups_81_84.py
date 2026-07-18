import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_measure11.json"
EVIDENCE = POLICY / "miyagi_kpi_measure11_evidence_packets.json"
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
    POLICY / "miyagi_kpi_catalog_measure10.json",
    CATALOG,
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure11_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []

    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [81, 82, 83, 84]
    assert [item["series_number"] for item in series] == [99, 100, 101, 102, 103]
    assert all(group["scope_type"] == "measure" for group in groups)
    assert all(group["scope_number"] == 11 for group in groups)
    assert all(group["source_page"] == 59 for group in groups)
    assert all(group["printed_page"] == 58 for group in groups)


def test_official_values_and_two_culture_series_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    series = {
        item["series_number"]: item
        for group in groups.values()
        for item in group["series"]
    }
    assert [item["series_number"] for item in groups[81]["series"]] == [99, 100]
    assert [value["value"] for value in series[99]["values"]] == [
        77.3,
        76.5,
        79.1,
        None,
    ]
    assert [value["value"] for value in series[100]["values"]] == [
        81.4,
        82.5,
        82.6,
        None,
    ]
    assert "2系列を単一値へ圧縮しない" in groups[81]["comparability_note_original"]

    assert [value["value"] for value in series[101]["values"]] == [
        80.0,
        80.0,
        100,
        None,
    ]
    assert [value["value"] for value in series[102]["values"]] == [
        55831,
        47766,
        72000,
        None,
    ]
    assert [value["value"] for value in series[103]["values"]] == [
        373,
        752,
        790,
        None,
    ]


def test_same_period_and_per_thousand_boundaries_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    group82_values = groups[82]["series"][0]["values"]
    assert group82_values[0]["period_original"] == "R6"
    assert group82_values[1]["period_original"] == "R6"
    assert "初期値と現況値はともに令和6年" in groups[82][
        "comparability_note_original"
    ]
    assert "人口千人当たり" in groups[84]["series"][0]["indicator_name_original"]
    assert "参加者総数へ変換しない" in groups[84]["comparability_note_original"]

    for group in groups.values():
        for series in group["series"]:
            late = series["values"][3]
            assert late["value"] is None
            assert late["status"] == "not_set"
            assert late["value_text_original"] == "-"


def test_measure11_evidence_covers_all_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 4
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        "policy-target-miyagi-81",
        "policy-target-miyagi-82",
        "policy-target-miyagi-83",
        "policy-target-miyagi-84",
    }
    assert all(packet["review_status"] == "reviewed" for packet in packets)
    assert all(packet["open_questions"] == [] for packet in packets)


def test_all_reviewed_batches_form_84_groups_and_103_series():
    groups = [group for path in ALL_CATALOGS for group in load(path)["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(1, 85))
    assert [item["series_number"] for item in series] == list(range(1, 104))
    assert all(group["actual_linkage_status"] == "not_linked" for group in groups)
    assert all(group["evaluation_status"] == "not_assessed" for group in groups)
