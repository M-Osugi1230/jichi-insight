import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"
SCHEMA = ROOT / "schemas/miyagi_policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_schema_counts_and_progress():
    manifest = load(MANIFEST)
    validator = Draft202012Validator(load(SCHEMA), format_checker=FormatChecker())
    assert list(validator.iter_errors(manifest)) == []
    assert manifest["expected_kpi_count"] == 128
    assert manifest["indicator_series_count"] == 149
    assert manifest["reviewed_target_group_count"] == 113
    assert manifest["reviewed_indicator_series_count"] == 132
    assert manifest["remaining_target_group_count"] == 15
    assert manifest["remaining_indicator_series_count"] == 17
    assert manifest["kpi_evidence_packet_count"] == 113
    assert 113 + 15 == 128
    assert 132 + 17 == 149
    assert manifest["active_work_package"] == "kpi_catalog"
    assert manifest["review_status"] == "in_progress"


def test_manifest_work_packages_and_quality_requirements():
    manifest = load(MANIFEST)
    packages = {item["id"]: item for item in manifest["work_packages"]}
    assert list(packages) == [
        "source_inventory",
        "policy_hierarchy",
        "kpi_source_index",
        "kpi_catalog",
        "evaluation_linkage",
        "web_publication",
    ]
    assert packages["source_inventory"]["status"] == "completed"
    assert packages["policy_hierarchy"]["status"] == "completed"
    assert packages["kpi_source_index"]["status"] == "completed"
    assert packages["kpi_catalog"]["status"] == "active"
    assert "目標グループ1〜113" in packages["kpi_catalog"]["deliverable"]
    assert "残る15目標グループ" in packages["kpi_catalog"]["deliverable"]
    assert packages["evaluation_linkage"]["status"] == "queued"
    assert packages["web_publication"]["status"] == "active"
    assert "目標グループ114〜119" in manifest["open_questions"][0]
    assert len(manifest["quality_requirements"]) == 8
    assert len(set(manifest["quality_requirements"])) == 8
