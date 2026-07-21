import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure13_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure13_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure13.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure13_schema_and_evidence_coverage():
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


def test_measure13_linkage_and_definition_boundary():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        "policy-indicator-miyagi-115",
        "policy-indicator-miyagi-116",
        "policy-indicator-miyagi-117",
        "policy-indicator-miyagi-119",
    }
    assert {key for key, record in records.items() if record["linkage_status"] == "linked"} == {
        "policy-indicator-miyagi-116",
        "policy-indicator-miyagi-117",
        "policy-indicator-miyagi-119",
    }
    assert records["policy-indicator-miyagi-115"]["linkage_status"] == "needs_review"
    assert records["policy-indicator-miyagi-115"]["match_basis"] == "definition_changed"
    assert sum(len(record["annual_results"]) for record in records.values()) == 16


def test_measure13_latest_values_and_reporting_lags():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        115: (79.5, "above_100", "A", "R5"),
        116: (3489, "above_100", "A", "R5"),
        117: (2924, "numeric", "D", "R6"),
        119: (22973, "numeric", "B", "R5"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
            latest["measurement_period_original"],
        ) == values


def test_measure13_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(94, 101))
    assert {
        number for number, group in groups.items() if group["actual_linkage_status"] == "linked"
    } == {97, 98, 100}
    for number in [94, 95, 96, 99]:
        assert groups[number]["actual_linkage_status"] == "not_linked"
    assert "一致しない" in groups[96]["comparability_note_original"]
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
