import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure11_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure11_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure11.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure11_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 5
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure11_linkage_and_definition_boundary():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {f"policy-indicator-miyagi-{number}" for number in range(99, 104)}
    assert {key for key, record in records.items() if record["linkage_status"] == "linked"} == {
        "policy-indicator-miyagi-99",
        "policy-indicator-miyagi-100",
        "policy-indicator-miyagi-101",
        "policy-indicator-miyagi-103",
    }
    assert records["policy-indicator-miyagi-102"]["linkage_status"] == "needs_review"
    assert records["policy-indicator-miyagi-102"]["match_basis"] == "definition_changed"
    assert sum(len(record["annual_results"]) for record in records.values()) == 20


def test_measure11_latest_values_and_lagged_measurement():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        99: (76.5, "above_100", "A"),
        100: (82.5, "above_100", "A"),
        101: (80.0, "numeric", "D"),
        102: (19555, "numeric", "D"),
        103: (545, "below_0", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    latest103 = records["policy-indicator-miyagi-103"]["annual_results"][-1]
    assert latest103["reporting_period_original"] == "R6"
    assert latest103["measurement_period_original"] == "R5"


def test_measure11_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == {81, 82, 83, 84}
    assert {
        number for number, group in groups.items() if group["actual_linkage_status"] == "linked"
    } == {81, 82, 84}
    assert groups[83]["actual_linkage_status"] == "not_linked"
    assert "ページビュー" in groups[83]["comparability_note_original"]
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
