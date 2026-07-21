import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure12_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure12_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure12.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure12_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 8
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure12_direct_links_and_unmatched_current_series():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        *(f"policy-indicator-miyagi-{number}" for number in range(104, 111)),
        "policy-indicator-miyagi-112",
    }
    assert set(records) == expected
    assert all(record["linkage_status"] == "linked" for record in records.values())
    assert all(record["match_basis"] == "exact_name_and_unit" for record in records.values())
    assert "policy-indicator-miyagi-111" not in records
    assert sum(len(record["annual_results"]) for record in records.values()) == 32


def test_measure12_latest_values_and_official_rates():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        104: (31.9, "below_0", "D"),
        105: (68.4, "above_100", "A"),
        106: (17.6, "below_0", "D"),
        107: (108, "below_0", "D"),
        108: (69.8, "below_0", "D"),
        109: (13115, "numeric", "D"),
        110: (12, "numeric", "D"),
        112: (33112, "numeric", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values


def test_measure12_reporting_measurement_lags_and_target_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    for number in [104, 105, 106, 112]:
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert latest["reporting_period_original"] == "R6"
        assert latest["measurement_period_original"] == "R5"
    assert records["policy-indicator-miyagi-109"]["evaluation_target"]["value"] == 13564
    assert "13,185" in records["policy-indicator-miyagi-109"]["comparability_note_original"]
    assert "13,331" in records["policy-indicator-miyagi-109"]["comparability_note_original"]


def test_measure12_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(85, 94))
    assert {
        number for number, group in groups.items() if group["actual_linkage_status"] == "linked"
    } == {85, 86, 87, 88, 89, 90, 91, 93}
    assert groups[92]["actual_linkage_status"] == "not_linked"
    assert "推測で接続しない" in groups[92]["comparability_note_original"]
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
