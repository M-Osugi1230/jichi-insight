import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/catalog/miyagi_policy_review_manifest.json"
SCHEMA = ROOT / "schemas/miyagi_policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_miyagi_manifest_matches_schema_and_review_stage():
    manifest = load(MANIFEST)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(manifest)) == []
    assert manifest["policy_direction_count"] == 4
    assert manifest["policy_count"] == 8
    assert manifest["measure_count"] == 18
    assert manifest["recovery_support_area_count"] == 4
    assert manifest["review_status"] == "in_progress"


def test_kpi_counts_are_verified_before_content_review():
    manifest = load(MANIFEST)
    assert manifest["expected_kpi_count"] == 128
    assert manifest["indicator_series_count"] == 149
    assert manifest["indicator_source_index_id"] == "miyagi-indicator-source-index"
    assert manifest["kpi_count_status"] == "verified"
    assert manifest["active_work_package"] == "kpi_catalog"
    assert "149系列" in manifest["open_questions"][0]


def test_work_packages_separate_inventory_hierarchy_kpis_and_evaluation():
    packages = {
        package["id"]: package for package in load(MANIFEST)["work_packages"]
    }
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
    assert packages["evaluation_linkage"]["status"] == "queued"
    assert packages["web_publication"]["status"] == "blocked"
    assert "128目標グループ" in packages["kpi_catalog"]["deliverable"]
    assert "原案・確定" in packages["evaluation_linkage"]["completion_gate"]


def test_miyagi_manifest_requires_all_quality_boundaries():
    requirements = set(load(MANIFEST)["quality_requirements"])
    assert requirements == {
        "official_order_preserved",
        "original_text_preserved",
        "three_level_hierarchy_preserved",
        "recovery_areas_kept_separate",
        "draft_evaluation_not_promoted",
        "kpi_count_not_guessed",
        "evidence_packet_required",
        "actuals_not_inferred",
    }
