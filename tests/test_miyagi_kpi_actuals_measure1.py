import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure1_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure1_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure1.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure1_actuals_match_schema_and_evidence():
    actuals = load(ACTUALS)
    actuals_validator = Draft202012Validator(
        load(ACTUALS_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(actuals_validator.iter_errors(actuals)) == []

    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 6
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure1_actuals_link_five_series_and_hold_one_for_review():
    actuals = load(ACTUALS)
    records = {record["series_id"]: record for record in actuals["records"]}
    linked = {
        record["series_id"]
        for record in actuals["records"]
        if record["linkage_status"] == "linked"
    }
    assert linked == {
        "policy-indicator-miyagi-4",
        "policy-indicator-miyagi-5",
        "policy-indicator-miyagi-6",
        "policy-indicator-miyagi-8",
        "policy-indicator-miyagi-9",
    }
    assert records["policy-indicator-miyagi-7"]["linkage_status"] == "needs_review"
    assert records["policy-indicator-miyagi-7"]["match_basis"] == "definition_changed"
    assert sum(len(record["annual_results"]) for record in actuals["records"]) == 24


def test_reporting_year_measurement_year_and_legacy_target_stay_distinct():
    actuals = load(ACTUALS)
    records = {record["series_id"]: record for record in actuals["records"]}
    manufacturing = records["policy-indicator-miyagi-8"]
    assert [row["reporting_period_original"] for row in manufacturing["annual_results"]] == [
        "R3",
        "R4",
        "R5",
        "R6",
    ]
    assert [row["measurement_period_original"] for row in manufacturing["annual_results"]] == [
        "R1",
        "R2",
        "R4",
        "R4",
    ]
    assert manufacturing["evaluation_target"]["period_original"] == "R6"
    assert manufacturing["evaluation_target"]["value"] == 41289
    assert manufacturing["annual_results"][-1]["value"] == 47669
    assert manufacturing["annual_results"][-1]["achievement_rate_status"] == "above_100"


def test_measure1_catalog_statuses_match_reviewed_actual_links():
    catalog = load(CATALOG)
    groups = {group["target_group_number"]: group for group in catalog["items"]}
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {4, 5, 6, 8, 9}
    assert groups[7]["actual_linkage_status"] == "not_linked"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
