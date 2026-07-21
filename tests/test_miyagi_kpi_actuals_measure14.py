import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure14_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure14_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure14.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure14_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 4
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure14_direct_links_and_annual_rows():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        f"policy-indicator-miyagi-{number}" for number in range(120, 124)
    }
    assert all(record["linkage_status"] == "linked" for record in records.values())
    assert all(record["match_basis"] == "exact_name_and_unit" for record in records.values())
    assert sum(len(record["annual_results"]) for record in records.values()) == 16


def test_measure14_latest_values_rates_and_measurement_years():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        120: (115, "above_100", "A", "R5"),
        121: (96.1, "above_100", "A", "R6"),
        122: (11385, "numeric", "B", "R6"),
        123: (47, "numeric", "B", "R6"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
            latest["measurement_period_original"],
        ) == values


def test_measure14_version_and_target_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    transport = records["policy-indicator-miyagi-120"]
    assert [row["measurement_period_original"] for row in transport["annual_results"]] == [
        "R1",
        "R2",
        "R4",
        "R5",
    ]
    shopping = records["policy-indicator-miyagi-121"]
    assert "版差" in shopping["comparability_note_original"]
    assert shopping["evaluation_target"]["value"] == 95.0
    assert records["policy-indicator-miyagi-122"]["evaluation_target"]["value"] == 10193
    assert records["policy-indicator-miyagi-123"]["evaluation_target"]["value"] == 44


def test_measure14_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(101, 105))
    assert all(group["actual_linkage_status"] == "linked" for group in groups.values())
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
