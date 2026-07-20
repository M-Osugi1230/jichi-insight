import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure9_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure9_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure9.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure9_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 8
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure9_linkage_counts_and_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        "policy-indicator-miyagi-77",
        "policy-indicator-miyagi-78",
        "policy-indicator-miyagi-79",
        "policy-indicator-miyagi-80",
        "policy-indicator-miyagi-81",
        "policy-indicator-miyagi-83",
        "policy-indicator-miyagi-84",
        "policy-indicator-miyagi-85",
    ]
    assert all(record["linkage_status"] == "linked" for record in records)
    assert sum(len(record["annual_results"]) for record in records) == 32
    assert "policy-indicator-miyagi-82" not in {
        record["series_id"] for record in records
    }


def test_measure9_latest_values_and_period_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        77: (50.2, "below_0", "D"),
        78: (40.6, "below_0", "D"),
        79: (77.3, "below_0", "D"),
        80: (34.9, "numeric", "B"),
        81: (87.7, "numeric", "B"),
        83: (94.6, "above_100", "A"),
        84: (91.1, "numeric", "B"),
        85: (74.7, "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    for number in [83, 84, 85]:
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert latest["reporting_period_original"] == "R6"
        assert latest["measurement_period_original"] == "R5"
    assert records["policy-indicator-miyagi-85"]["match_basis"] == (
        "normalized_name_and_unit"
    )


def test_measure9_catalog_and_partial_history_boundary():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(63, 69))
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {63, 64, 65, 67, 68}
    assert groups[66]["actual_linkage_status"] == "partial"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
    assert "2年分" in groups[66]["comparability_note_original"]
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert "policy-indicator-miyagi-81" in records
    assert "policy-indicator-miyagi-82" not in records
