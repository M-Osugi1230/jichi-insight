import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure8_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure8_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure8.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure8_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 18
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure8_linkage_counts_and_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        "policy-indicator-miyagi-58",
        "policy-indicator-miyagi-59",
        *[f"policy-indicator-miyagi-{number}" for number in range(61, 77)],
    ]
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "needs_review"
    } == {
        "policy-indicator-miyagi-59",
        "policy-indicator-miyagi-68",
        "policy-indicator-miyagi-69",
    }
    assert sum(record["linkage_status"] == "linked" for record in records) == 15
    assert sum(len(record["annual_results"]) for record in records) == 72


def test_measure8_latest_values_and_period_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        58: (32.0, "numeric", "D"),
        59: (88.9, "below_0", "D"),
        61: (95.0, "numeric", "A"),
        62: (95.2, "above_100", "A"),
        63: (67.9, "below_0", "D"),
        64: (1.2, "above_100", "A"),
        65: (82.7, "below_0", "D"),
        66: (58.2, "below_0", "D"),
        67: (11.8, "below_0", "D"),
        68: (85.9, "above_100", "A"),
        69: (87.0, "above_100", "A"),
        70: (-4.5, "below_0", "D"),
        71: (-5.0, "below_0", "D"),
        72: (3.0, "above_100", "A"),
        73: (-0.09, "numeric", "D"),
        74: (-0.17, "numeric", "D"),
        75: (0.72, "above_100", "A"),
        76: (-1.00, "numeric", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    first_progression = records["policy-indicator-miyagi-72"]["annual_results"][0]
    assert first_progression["reporting_period_original"] == "R3"
    assert first_progression["measurement_period_original"] == "R2"
    assert "policy-indicator-miyagi-60" not in records


def test_measure8_catalog_and_definition_boundaries():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {53, 55, 56, 57, 58, 60, 61, 62}
    assert groups[54]["actual_linkage_status"] == "not_linked"
    assert groups[59]["actual_linkage_status"] == "not_linked"
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert records["policy-indicator-miyagi-59"]["match_basis"] == "definition_changed"
    assert records["policy-indicator-miyagi-68"]["match_basis"] == "definition_changed"
    assert records["policy-indicator-miyagi-65"]["match_basis"] == "normalized_name_and_unit"
    assert groups[62]["series"][2]["values"][1]["value"] == 1.19
    assert groups[62]["series"][2]["values"][1]["value_text_original"] == "1,19"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
