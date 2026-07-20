import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "data/entities/policy"
ACTUALS = POLICY / "miyagi_kpi_actuals_measure10_2024.json"
EVIDENCE = POLICY / "miyagi_kpi_actuals_measure10_2024_evidence_packets.json"
CATALOG = POLICY / "miyagi_kpi_catalog_measure10.json"
ACTUALS_SCHEMA = ROOT / "schemas/miyagi_kpi_actuals.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_measure10_schema_and_evidence_coverage():
    actuals = load(ACTUALS)
    validator = Draft202012Validator(load(ACTUALS_SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(actuals)) == []
    packets = load(EVIDENCE)
    evidence_validator = Draft202012Validator(load(EVIDENCE_SCHEMA))
    assert len(packets) == 9
    assert all(list(evidence_validator.iter_errors(packet)) == [] for packet in packets)
    assert {packet["subject_id"] for packet in packets} == {record["id"] for record in actuals["records"]}


def test_measure10_linkage_counts_and_definition_boundaries():
    records = load(ACTUALS)["records"]
    assert [record["series_id"] for record in records] == [f"policy-indicator-miyagi-{number}" for number in range(90, 99)]
    assert {record["series_id"] for record in records if record["linkage_status"] == "linked"} == {
        "policy-indicator-miyagi-90", "policy-indicator-miyagi-92", "policy-indicator-miyagi-93",
        "policy-indicator-miyagi-94", "policy-indicator-miyagi-95", "policy-indicator-miyagi-96",
    }
    assert {record["series_id"] for record in records if record["linkage_status"] == "needs_review"} == {
        "policy-indicator-miyagi-91", "policy-indicator-miyagi-97", "policy-indicator-miyagi-98",
    }
    assert sum(len(record["annual_results"]) for record in records) == 36


def test_measure10_latest_values_and_official_statuses():
    records = {record["series_id"]: record for record in load(ACTUALS)["records"]}
    expected = {
        90: (7602, "above_100", "A"), 91: (16.1, "numeric", "D"), 92: (2.39, "numeric", "C"),
        93: (50, "above_100", "A"), 94: (276, "numeric", "B"), 95: (961, "above_100", "A"),
        96: (492, "above_100", "A"), 97: (35, "numeric", "A"), 98: (13975, "numeric", "B"),
    }
    for number, values in expected.items():
        latest = records[f"policy-indicator-miyagi-{number}"]["annual_results"][-1]
        assert (latest["value"], latest["achievement_rate_status"], latest["achievement_grade"]) == values
    assert records["policy-indicator-miyagi-95"]["match_basis"] == "normalized_name_and_unit"
    assert records["policy-indicator-miyagi-96"]["match_basis"] == "normalized_name_and_unit"


def test_measure10_catalog_connection_statuses():
    groups = {group["target_group_number"]: group for group in load(CATALOG)["items"]}
    assert set(groups) == set(range(72, 81))
    assert {number for number, group in groups.items() if group["actual_linkage_status"] == "linked"} == {72, 74, 75, 76, 77, 78}
    assert {number for number, group in groups.items() if group["actual_linkage_status"] == "not_linked"} == {73, 79, 80}
    assert all(group["evaluation_status"] == "not_assessed" for group in groups.values())
    assert "定義" in groups[79]["comparability_note_original"]
    assert "技能実習生" in groups[80]["comparability_note_original"]
