import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure15_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure15_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure15.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure15_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 7
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure15_direct_links_and_annual_rows():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        f"policy-indicator-miyagi-{number}" for number in range(126, 133)
    }
    assert all(record["linkage_status"] == "linked" for record in records.values())
    assert all(record["match_basis"] == "exact_name_and_unit" for record in records.values())
    assert sum(len(record["annual_results"]) for record in records.values()) == 28


def test_measure15_latest_values_rates_and_grades():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        126: (33.0, "below_0", "D"),
        127: (3338, "below_0", "D"),
        128: (53050, "above_100", "A"),
        129: (22.6, "below_0", "D"),
        130: (36.3, "above_100", "A"),
        131: (923, "above_100", "A"),
        132: (10468, "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values


def test_measure15_measurement_and_unit_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    awareness = records["policy-indicator-miyagi-126"]
    assert {
        row["measurement_period_original"] for row in awareness["annual_results"]
    } == {"R3"}
    assert "33.3%" in awareness["comparability_note_original"]
    for number in [127, 129, 130, 131, 132]:
        rows = records[f"policy-indicator-miyagi-{number}"]["annual_results"]
        assert [row["measurement_period_original"] for row in rows] == [
            "R2",
            "R3",
            "R4",
            "R5",
        ]
    assert records["policy-indicator-miyagi-131"]["annual_results"][-1][
        "unit_original"
    ] == "g/人･日"
    assert records["policy-indicator-miyagi-132"]["annual_results"][-1][
        "unit_original"
    ] == "千ｔ"


def test_measure15_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(107, 114))
    assert all(group["actual_linkage_status"] == "linked" for group in groups.values())
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
