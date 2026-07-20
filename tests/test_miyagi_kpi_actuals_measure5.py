import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure5_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure5_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure5.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure5_schema_and_evidence_coverage():
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


def test_measure5_linkage_boundaries_and_rows():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [
        "policy-indicator-miyagi-34",
        "policy-indicator-miyagi-35",
        "policy-indicator-miyagi-36",
        "policy-indicator-miyagi-38",
        "policy-indicator-miyagi-39",
        "policy-indicator-miyagi-40",
    ]
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "linked"
    } == {
        "policy-indicator-miyagi-35",
        "policy-indicator-miyagi-38",
        "policy-indicator-miyagi-39",
        "policy-indicator-miyagi-40",
    }
    assert {
        record["series_id"]
        for record in records
        if record["linkage_status"] == "needs_review"
    } == {"policy-indicator-miyagi-34", "policy-indicator-miyagi-36"}
    assert sum(len(record["annual_results"]) for record in records) == 24
    assert all(
        record["match_basis"] == "definition_changed"
        for record in records
        if record["linkage_status"] == "needs_review"
    )


def test_measure5_latest_results_and_explicit_zero():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        34: (8, "R6", "numeric", "A"),
        35: (16.8, "R6", "numeric", "B"),
        36: (3229, "R6", "above_100", "A"),
        38: (377.8, "R6", "above_100", "A"),
        39: (51.9, "R6", "above_100", "A"),
        40: (3988, "R6", "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["measurement_period_original"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values
    international_rows = records["policy-indicator-miyagi-39"]["annual_results"]
    assert international_rows[0]["value"] == 0.0
    assert international_rows[0]["achievement_rate_value"] == 0.0


def test_measure5_catalog_statuses_and_scope_differences():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert {
        group["target_group_number"]
        for group in groups.values()
        if group["actual_linkage_status"] == "linked"
    } == {33, 36, 37, 38}
    assert groups[32]["actual_linkage_status"] == "not_linked"
    assert groups[34]["actual_linkage_status"] == "not_linked"
    assert groups[35]["actual_linkage_status"] == "not_linked"
    assert records["policy-indicator-miyagi-34"]["evaluation_target"]["unit_original"] == "箇所"
    assert groups[32]["series"][0]["unit_original"] == "台/日"
    assert "コンテナ貨物を除く" in records["policy-indicator-miyagi-36"][
        "source_indicator_name_original"
    ]
    assert "コンテナ貨物を除く" not in groups[34]["series"][0][
        "indicator_name_original"
    ]
    assert all(
        group["evaluation_status"] == "not_assessed" for group in groups.values()
    )
