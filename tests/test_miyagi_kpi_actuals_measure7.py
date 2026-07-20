import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure7_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure7_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure7.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure7_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 6
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure7_linkage_counts_and_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        "policy-indicator-miyagi-50",
        "policy-indicator-miyagi-51",
        "policy-indicator-miyagi-52",
        "policy-indicator-miyagi-55",
        "policy-indicator-miyagi-56",
        "policy-indicator-miyagi-57",
    ]
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "linked"
    } == {
        "policy-indicator-miyagi-50",
        "policy-indicator-miyagi-51",
        "policy-indicator-miyagi-52",
        "policy-indicator-miyagi-56",
        "policy-indicator-miyagi-57",
    }
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "needs_review"
    } == {"policy-indicator-miyagi-55"}
    assert sum(len(record["annual_results"]) for record in records) == 24


def test_measure7_latest_values_and_period_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        50: (198, "R6", "above_100", "A"),
        51: (36.7, "R6", "below_0", "D"),
        52: (93.1, "R6", "below_0", "D"),
        55: (398, "R6", "above_100", "A"),
        56: (373, "R6", "above_100", "A"),
        57: (80.0, "R6", "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["measurement_period_original"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    first_coverage = records["policy-indicator-miyagi-57"]["annual_results"][0]
    assert first_coverage["reporting_period_original"] == "R3"
    assert first_coverage["measurement_period_original"] == "R2"


def test_measure7_catalog_and_comparability_boundaries():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {46, 47, 48, 51, 52}
    assert groups[49]["actual_linkage_status"] == "not_linked"
    assert groups[50]["actual_linkage_status"] == "not_linked"
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert records["policy-indicator-miyagi-55"]["match_basis"] == "definition_changed"
    assert records["policy-indicator-miyagi-52"]["annual_results"][-1]["value"] == 93.1
    assert groups[48]["series"][0]["values"][0]["value"] == 94.2
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
