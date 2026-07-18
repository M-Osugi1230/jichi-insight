import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
CATALOG = POLICY / "miyagi_kpi_catalog_pillar4.json"
EVIDENCE = POLICY / "miyagi_kpi_pillar4_evidence_packets.json"
CATALOG_SCHEMA = ROOT / "schemas/miyagi_kpi_catalog.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_pillar4_catalog_matches_schema_and_sequences():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(CATALOG_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(catalog)) == []
    groups = catalog["items"]
    series = [item for group in groups for item in group["series"]]
    assert [group["target_group_number"] for group in groups] == [105, 106]
    assert [item["series_number"] for item in series] == [124, 125]
    assert all(group["scope_type"] == "pillar" for group in groups)
    assert all(group["scope_number"] == 4 for group in groups)
    assert all(group["source_page"] == 60 for group in groups)


def test_pillar4_values_periods_and_units_are_preserved():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    first = groups[105]["series"][0]
    second = groups[106]["series"][0]
    assert [value["value"] for value in first["values"]] == [
        16602,
        16904,
        13252,
        11264,
    ]
    assert first["values"][0]["period_original"] == "R2"
    assert first["values"][0]["period_year"] == 2020
    assert first["unit_original"] == "千t-CO2"
    assert [value["value"] for value in second["values"]] == [102.8, 102.7, 100, 100]
    assert all(group["target_setting_status"] == "set" for group in groups.values())
    assert all(
        value["status"] == "numeric"
        for group in groups.values()
        for value in group["series"][0]["values"]
    )


def test_pillar4_evidence_covers_both_groups():
    packets = load(EVIDENCE)
    validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 2
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        "policy-target-miyagi-105",
        "policy-target-miyagi-106",
    }
