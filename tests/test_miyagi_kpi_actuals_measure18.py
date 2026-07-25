import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure18_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure18_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure18.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure18_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []

    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 3
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in actuals["records"]
    }


def test_measure18_links_and_definition_boundary():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        "policy-indicator-miyagi-147",
        "policy-indicator-miyagi-148",
        "policy-indicator-miyagi-149",
    }
    bridge = records["policy-indicator-miyagi-147"]
    assert bridge["linkage_status"] == "needs_review"
    assert bridge["match_basis"] == "definition_changed"
    assert bridge["confidence"] == "medium"
    assert "44.3%" in bridge["comparability_note_original"]
    assert "0.0%" in bridge["comparability_note_original"]
    assert "直接接続しない" in bridge["comparability_note_original"]
    assert records["policy-indicator-miyagi-148"]["linkage_status"] == "linked"
    assert records["policy-indicator-miyagi-149"]["linkage_status"] == "linked"
    assert sum(len(record["annual_results"]) for record in records.values()) == 12


def test_measure18_latest_values_and_source_version_differences():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        147: (54.5, "above_100", "A"),
        148: (61.1, "above_100", "A"),
        149: (752, "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values

    assert "資料版差" in records["policy-indicator-miyagi-148"]["comparability_note_original"]
    assert "資料版差" in records["policy-indicator-miyagi-149"]["comparability_note_original"]


def test_measure18_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == {126, 127, 128}
    assert groups[126]["actual_linkage_status"] == "needs_review"
    assert groups[126]["confidence"] == "high"
    assert groups[127]["actual_linkage_status"] == "linked"
    assert groups[128]["actual_linkage_status"] == "linked"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
