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
    assert [
        manifest["policy_direction_count"],
        manifest["policy_count"],
        manifest["measure_count"],
        manifest["recovery_support_area_count"],
    ] == [4, 8, 18, 4]
    assert manifest["expected_kpi_count"] == 128
    assert manifest["indicator_series_count"] == 149
    assert manifest["reviewed_target_group_count"] == 80
    assert manifest["reviewed_indicator_series_count"] == 98
    assert manifest["remaining_target_group_count"] == 48
    assert manifest["remaining_indicator_series_count"] == 51
    assert manifest["kpi_evidence_packet_count"] == 80
    assert 80 + 48 == 128
    assert 98 + 51 == 149
    assert manifest["active_work_package"] == "kpi_catalog"
    assert manifest["review_status"] == "in_progress"


def test_work_packages_and_quality_boundaries():
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
    assert "目標グループ1〜80" in packages["kpi_catalog"]["deliverable"]
    assert "残る48目標グループ" in packages["kpi_catalog"]["deliverable"]
    assert packages["evaluation_linkage"]["status"] == "queued"
    assert packages["web_publication"]["status"] == "active"
    assert "段階公開" in packages["web_publication"]["deliverable"]
    assert "目標グループ81〜84" in manifest["open_questions"][0]
    assert "累計3グループ" in manifest["open_questions"][1]
    assert "ハイフンを0へ変換しない" in manifest["open_questions"][1]
    assert set(manifest["quality_requirements"]) == {
        "official_order_preserved",
        "original_text_preserved",
        "three_level_hierarchy_preserved",
        "recovery_areas_kept_separate",
        "draft_evaluation_not_promoted",
        "kpi_count_not_guessed",
        "evidence_packet_required",
        "actuals_not_inferred",
    }
