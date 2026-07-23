import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure16_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure16_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure16.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure16_schema_and_evidence_coverage():
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


def test_measure16_links_and_definition_boundaries():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        f"policy-indicator-miyagi-{number}" for number in range(133, 140)
    }
    assert {
        number
        for number in range(133, 140)
        if records[f"policy-indicator-miyagi-{number}"]["linkage_status"] == "linked"
    } == {133, 134, 137, 138, 139}
    assert {
        number
        for number in range(133, 140)
        if records[f"policy-indicator-miyagi-{number}"]["linkage_status"]
        == "needs_review"
    } == {135, 136}
    assert sum(len(record["annual_results"]) for record in records.values()) == 28

    for number in (135, 136):
        record = records[f"policy-indicator-miyagi-{number}"]
        assert record["match_basis"] == "definition_changed"
        assert "捕獲数" in record["source_indicator_name_original"]
        assert "推定生息数" in record["comparability_note_original"]
        assert "直接接続しない" in record["comparability_note_original"]


def test_measure16_latest_values_rates_and_grades():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        133: (6.6, "below_0", "D"),
        134: (11919, "below_0", "D"),
        135: (8547, "below_0", "D"),
        136: (4625, "above_100", "A"),
        137: (67911, "above_100", "A"),
        138: (75381, "above_100", "A"),
        139: (5996, "above_100", "A"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values


def test_measure16_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(114, 120))
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {114, 115, 117, 118, 119}
    assert groups[116]["actual_linkage_status"] == "needs_review"
    assert "捕獲数" in groups[116]["comparability_note_original"]
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
