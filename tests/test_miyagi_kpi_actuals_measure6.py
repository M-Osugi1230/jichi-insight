import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure6_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure6_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure6.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure6_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 5
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure6_linkage_counts_and_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        "policy-indicator-miyagi-44",
        "policy-indicator-miyagi-45",
        "policy-indicator-miyagi-46",
        "policy-indicator-miyagi-47",
        "policy-indicator-miyagi-49",
    ]
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "linked"
    } == {
        "policy-indicator-miyagi-45",
        "policy-indicator-miyagi-46",
        "policy-indicator-miyagi-49",
    }
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "needs_review"
    } == {"policy-indicator-miyagi-44", "policy-indicator-miyagi-47"}
    assert sum(len(record["annual_results"]) for record in records) == 20


def test_measure6_latest_values_and_measurement_year_boundary():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        44: (1427, "R6", "above_100", "A"),
        45: (39.9, "R6", "above_100", "A"),
        46: (94.7, "R6", "numeric", "B"),
        47: (2785, "R6", "numeric", "C"),
        49: (18, "R5", "numeric", "B"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["measurement_period_original"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    waiting = records["policy-indicator-miyagi-49"]
    assert waiting["achievement_rate_type_original"].endswith("Ⅱ")
    assert waiting["annual_results"][-1]["reporting_period_original"] == "R6"
    assert waiting["annual_results"][-1]["measurement_period_original"] == "R5"


def test_measure6_catalog_and_definition_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert groups[42]["actual_linkage_status"] == "linked"
    assert groups[45]["actual_linkage_status"] == "linked"
    assert groups[41]["actual_linkage_status"] == "not_linked"
    assert groups[43]["actual_linkage_status"] == "not_linked"
    assert groups[44]["actual_linkage_status"] == "not_linked"
    assert "登録者数" in records["policy-indicator-miyagi-44"][
        "source_indicator_name_original"
    ]
    assert "成婚退会者数" in groups[41]["series"][0]["indicator_name_original"]
    assert records["policy-indicator-miyagi-47"]["match_basis"] == "definition_changed"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
