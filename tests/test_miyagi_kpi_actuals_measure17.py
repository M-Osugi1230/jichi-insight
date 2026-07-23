import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure17_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure17_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure17.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure17_schema_and_evidence_coverage():
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


def test_measure17_links_and_definition_boundary():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    assert set(records) == {
        f"policy-indicator-miyagi-{number}" for number in range(140, 147)
    }
    assert {
        number
        for number in range(140, 147)
        if records[f"policy-indicator-miyagi-{number}"]["linkage_status"] == "linked"
    } == {140, 142, 143, 144, 145, 146}
    assert records["policy-indicator-miyagi-141"]["linkage_status"] == "needs_review"
    assert records["policy-indicator-miyagi-141"]["match_basis"] == "definition_changed"
    assert "組織率" in records["policy-indicator-miyagi-141"]["source_indicator_name_original"]
    assert "活動カバー率" in records["policy-indicator-miyagi-141"]["comparability_note_original"]
    assert "直接接続しない" in records["policy-indicator-miyagi-141"]["comparability_note_original"]
    assert sum(len(record["annual_results"]) for record in records.values()) == 28


def test_measure17_latest_values_and_source_version_differences():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        140: (1729, "above_100", "A"),
        141: (80.7, "below_0", "D"),
        142: (47.3, "below_0", "D"),
        143: (76.4, "above_100", "A"),
        144: (43.1, "above_100", "A"),
        145: (652, "above_100", "A"),
        146: (8608, "numeric", "D"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (
            latest["value"],
            latest["achievement_rate_status"],
            latest["achievement_grade"],
        ) == values

    for number in (143, 144, 145, 146):
        assert "資料版差" in records[f"policy-indicator-miyagi-{number}"]["comparability_note_original"]


def test_measure17_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(120, 126))
    assert {
        number
        for number, group in groups.items()
        if group["actual_linkage_status"] == "linked"
    } == {120, 122, 123, 124, 125}
    assert groups[121]["actual_linkage_status"] == "needs_review"
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
