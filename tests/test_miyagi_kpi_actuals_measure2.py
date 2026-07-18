import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure2_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure2_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure2.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure2_actuals_match_schema_and_evidence():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(
        load(ACTUALS_SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(actuals)) == []

    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 5
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure2_links_four_series_and_holds_one_for_review():
    actuals = load(ACTUALS)
    records = {record["series_id"]: record for record in actuals["records"]}
    linked = {
        record["series_id"]
        for record in actuals["records"]
        if record["linkage_status"] == "linked"
    }
    assert linked == {
        "policy-indicator-miyagi-10",
        "policy-indicator-miyagi-11",
        "policy-indicator-miyagi-12",
        "policy-indicator-miyagi-14",
    }
    assert records["policy-indicator-miyagi-13"]["linkage_status"] == "needs_review"
    assert records["policy-indicator-miyagi-13"]["match_basis"] == "definition_changed"
    assert sum(len(record["annual_results"]) for record in actuals["records"]) == 20


def test_measure2_official_rates_and_reporting_periods_are_preserved():
    actuals = load(ACTUALS)
    records = {record["series_id"]: record for record in actuals["records"]}

    lodging = records["policy-indicator-miyagi-10"]
    assert lodging["evaluation_target"]["value"] == 990
    assert lodging["annual_results"][-1]["value"] == 988
    assert lodging["annual_results"][-1]["achievement_rate_status"] == "below_0"
    assert lodging["annual_results"][-1]["achievement_grade"] == "D"

    foreign = records["policy-indicator-miyagi-11"]
    assert foreign["achievement_rate_type_original"] == "現状維持型Ⅰ"
    assert foreign["evaluation_target"]["value"] == 50.0
    assert foreign["annual_results"][-1]["value"] == 74.3
    assert foreign["annual_results"][-1]["achievement_rate_status"] == "above_100"

    service = records["policy-indicator-miyagi-14"]
    assert service["evaluation_baseline"]["period_original"] == "H29"
    assert [row["reporting_period_original"] for row in service["annual_results"]] == [
        "R3",
        "R4",
        "R5",
        "R6",
    ]
    assert [row["measurement_period_original"] for row in service["annual_results"]] == [
        "R1",
        "R2",
        "R3",
        "R4",
    ]
    assert service["annual_results"][-1]["value"] == 29182


def test_measure2_catalog_statuses_match_reviewed_actual_links():
    catalog = load(CATALOG)
    groups = {group["target_group_number"]: group for group in catalog["items"]}
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {10, 11, 12, 14}
    assert groups[13]["actual_linkage_status"] == "not_linked"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
