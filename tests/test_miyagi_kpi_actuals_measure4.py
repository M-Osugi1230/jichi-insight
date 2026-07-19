import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure4_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure4_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure4.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure4_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 10
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure4_links_ten_series_and_40_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        f"policy-indicator-miyagi-{number}" for number in range(24, 34)
    ]
    assert all(record["linkage_status"] == "linked" for record in records)
    assert sum(len(record["annual_results"]) for record in records) == 40
    normalized = [
        record["series_id"]
        for record in records
        if record["match_basis"] == "normalized_name_and_unit"
    ]
    assert normalized == ["policy-indicator-miyagi-27"]


def test_measure4_latest_results_and_measurement_periods():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        24: (61.1, "R6", "numeric", "D"),
        25: (35.5, "R5", "above_100", "A"),
        26: (131, "R5", "below_0", "D"),
        27: (24, "R6", "below_0", "D"),
        28: (69, "R5", "numeric", "D"),
        29: (10.0, "R6", "numeric", "D"),
        30: (11.2, "R6", "above_100", "A"),
        31: (67, "R6", "above_100", "A"),
        32: (3.2, "R6", "below_0", "D"),
        33: (5452, "R5", "below_0", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["measurement_period_original"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    program_rows = records["policy-indicator-miyagi-31"]["annual_results"]
    assert program_rows[0]["achievement_rate_value"] == 0.0
    assert program_rows[1]["achievement_rate_value"] == 0.0
    assert records["policy-indicator-miyagi-29"][
        "achievement_rate_type_original"
    ].endswith("Ⅱ")


def test_measure4_target_and_group_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert [series["series_number"] for series in groups[26]["series"]] == [26, 27, 28]
    assert records["policy-indicator-miyagi-24"]["evaluation_target"]["value"] == 62.0
    assert groups[24]["series"][0]["values"][2]["value"] == 61.4
    assert records["policy-indicator-miyagi-29"]["evaluation_target"]["value"] == 8.7
    assert groups[27]["series"][0]["values"][2]["value"] == 8.8
    assert records["policy-indicator-miyagi-32"]["evaluation_target"]["value"] == 4.8
    assert groups[30]["series"][0]["values"][2]["value"] == 3.6
    assert records["policy-indicator-miyagi-33"]["evaluation_target"]["value"] == 6300
    assert groups[31]["series"][0]["values"][2]["value"] == 4900
    assert all(group["actual_linkage_status"] == "linked" for group in groups.values())
    assert all(
        group["evaluation_status"] == "not_assessed" for group in groups.values()
    )
