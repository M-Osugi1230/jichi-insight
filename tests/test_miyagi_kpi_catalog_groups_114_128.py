import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
CATALOGS = [
    POLICY / "miyagi_kpi_catalog_measure16.json",
    POLICY / "miyagi_kpi_catalog_measure17.json",
    POLICY / "miyagi_kpi_catalog_measure18.json",
]
EVIDENCE = [
    POLICY / "miyagi_kpi_measure16_evidence_packets.json",
    POLICY / "miyagi_kpi_measure17_evidence_packets.json",
    POLICY / "miyagi_kpi_measure18_evidence_packets.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_final_miyagi_catalogs_match_schema_and_sequences():
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA),
        format_checker=FormatChecker(),
    )
    catalogs = [load(path) for path in CATALOGS]
    assert all(list(validator.iter_errors(catalog)) == [] for catalog in catalogs)
    groups = [group for catalog in catalogs for group in catalog["items"]]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == list(range(114, 129))
    assert [item["series_number"] for item in series] == list(range(133, 150))
    assert all(group["source_page"] == 60 for group in groups)


def test_multiple_series_cumulative_and_zero_boundaries_are_preserved():
    groups = {
        group["target_group_number"]: group
        for catalog in CATALOGS
        for group in load(catalog)["items"]
    }
    assert [item["series_number"] for item in groups[116]["series"]] == [135, 136]
    assert [item["series_number"] for item in groups[125]["series"]] == [145, 146]
    cumulative = {
        number
        for number, group in groups.items()
        if group["series"][0]["aggregation_scope"] == "cumulative_to_date"
    }
    assert cumulative == {115, 117, 120, 123, 125, 126, 127, 128}
    assert groups[126]["series"][0]["values"][0]["value"] == 0.0
    assert groups[126]["series"][0]["values"][0]["status"] == "numeric"


def test_same_period_and_direction_boundaries_are_preserved():
    groups = {
        group["target_group_number"]: group
        for catalog in CATALOGS
        for group in load(catalog)["items"]
    }
    for number in [122, 124, 125, 128]:
        values = groups[number]["series"][0]["values"]
        assert values[0]["period_original"] == values[1]["period_original"]
        assert values[0]["value"] == values[1]["value"]
    for number in [116, 118, 119]:
        values = groups[number]["series"][0]["values"]
        assert values[1]["value"] > values[2]["value"]
    for group in groups.values():
        assert group["actual_linkage_status"] == "not_linked"
        assert group["evaluation_status"] == "not_assessed"
        late_values = [series["values"][3] for series in group["series"]]
        assert all(value["status"] == "not_set" for value in late_values)


def test_final_evidence_packets_cover_all_groups():
    packets = [packet for path in EVIDENCE for packet in load(path)]
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 15
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        f"policy-target-miyagi-{number}" for number in range(114, 129)
    }
