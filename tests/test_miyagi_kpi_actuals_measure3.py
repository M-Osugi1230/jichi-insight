import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure3_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure3_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure3.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure3_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 9
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure3_links_nine_series_and_36_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        f"policy-indicator-miyagi-{number}" for number in range(15, 24)
    ]
    assert all(record["linkage_status"] == "linked" for record in records)
    assert all(record["match_basis"] == "exact_name_and_unit" for record in records)
    assert sum(len(record["annual_results"]) for record in records) == 36


def test_measure3_latest_results_and_measurement_periods():
    records = {
        record["series_id"]: record for record in load(ACTUALS)["records"]
    }
    expected = {
        15: (1924, "R5", "below_0", "D"),
        16: (324, "R5", "below_0", "D"),
        17: (888, "R5", "above_100", "A"),
        18: (2586, "R4", "above_100", "A"),
        19: (97.3, "R5", "numeric", "C"),
        20: (1145, "R4", "above_100", "A"),
        21: (7160, "R4", "above_100", "A"),
        22: (2407, "R4", "numeric", "C"),
        23: (152, "R6", "below_0", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["measurement_period_original"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    for number in [20, 21, 22]:
        rows = records[f"policy-indicator-miyagi-{number}"]["annual_results"]
        assert rows[-2]["measurement_period_original"] == "R4"
        assert rows[-1]["measurement_period_original"] == "R4"
        assert rows[-2]["value"] == rows[-1]["value"]
    value_added = records["policy-indicator-miyagi-22"]["annual_results"]
    assert value_added[-2]["achievement_grade"] == "B"
    assert value_added[-1]["achievement_grade"] == "C"
    assert value_added[-1]["achievement_rate_value"] == 69.3


def test_measure3_targets_and_catalog_boundaries():
    records = {
        record["series_id"]: record for record in load(ACTUALS)["records"]
    }
    groups = {
        group["target_group_number"]: group for group in load(CATALOG)["items"]
    }
    assert records["policy-indicator-miyagi-15"]["evaluation_target"]["value"] == 2116
    assert groups[15]["series"][0]["values"][2]["value"] == 2210
    assert records["policy-indicator-miyagi-23"]["evaluation_target"]["value"] == 241
    assert groups[23]["series"][0]["values"][2]["value"] == 292
    assert groups[23]["series"][0]["aggregation_scope"] == "cumulative_to_date"
    assert all(group["actual_linkage_status"] == "linked" for group in groups.values())
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
