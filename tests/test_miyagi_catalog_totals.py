import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"
SCHEMA = ROOT / "schemas/miyagi_policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_schema_and_counts():
    manifest = load(MANIFEST)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(manifest)) == []
    assert manifest["expected_kpi_count"] == 128
    assert manifest["indicator_series_count"] == 149
    assert manifest["reviewed_target_group_count"] == 128
    assert manifest["reviewed_indicator_series_count"] == 149
    assert manifest["remaining_target_group_count"] == 0
    assert manifest["remaining_indicator_series_count"] == 0
    assert manifest["kpi_evidence_packet_count"] == 128
    assert manifest["actual_linked_target_group_count"] == 71
    assert manifest["actual_linked_indicator_series_count"] == 84
    assert manifest["actual_linkage_review_needed_series_count"] == 15
    assert manifest["actual_result_row_count"] == 396
    assert manifest["actual_evidence_packet_count"] == 99
    assert manifest["active_work_package"] == "evaluation_linkage"
