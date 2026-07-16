import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/catalog/hokkaido_policy_review_manifest.json"
SCHEMA = ROOT / "schemas/policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_manifest_schema_and_queue_link():
    manifest = load(MANIFEST)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(manifest)) == []

    queue = load(ROOT / "data/catalog/wave1_policy_review_queue.json")
    active = next(
        item
        for item in queue["items"]
        if item["prefecture_code"] == queue["active_prefecture_code"]
    )
    assert manifest["prefecture_code"] == "01"
    assert active["status"] == "active_review"
    assert active["source_inventory_status"] == "indicator_relationships_reviewed"
    assert active["next_gate"] == "kpi_catalog"
    assert set(manifest["plan_source_ids"]) <= set(active["source_ids"])


def test_manifest_counts_and_boundaries():
    manifest = load(MANIFEST)
    assert manifest["expected_indicator_count"] == 108
    assert manifest["reviewed_indicator_count"] == 91
    assert manifest["remaining_indicator_count"] == 17
    assert manifest["indicator_evidence_packet_count"] == 91
    assert (
        manifest["reviewed_indicator_count"]
        + manifest["remaining_indicator_count"]
        == 108
    )
    assert (
        manifest["indicator_evidence_packet_count"]
        == manifest["reviewed_indicator_count"]
    )
    assert "掲載行は113" in manifest["count_basis"]
    assert "差分5件" in manifest["count_basis"]
    assert "指標1〜91" in manifest["count_basis"]
    assert manifest["extraction_status"] == "in_progress"
    assert manifest["active_work_package"] == "indicator_catalog"


def test_work_packages_record_fifteen_reviewed_fields():
    packages = {
        item["id"]: item
        for item in load(MANIFEST)["work_packages"]
    }
    assert list(packages) == [
        "policy_hierarchy",
        "indicator_source_index",
        "indicator_catalog",
        "evidence_packets",
        "web_publication",
    ]
    assert packages["policy_hierarchy"]["status"] == "completed"
    assert packages["indicator_source_index"]["status"] == "completed"
    assert packages["indicator_catalog"]["status"] == "active"
    assert "指標1〜91" in packages["indicator_catalog"]["deliverable"]
    assert "指標92〜108" in packages["indicator_catalog"]["deliverable"]
    assert "指標1〜91" in packages["evidence_packets"]["deliverable"]
    assert "残る17指標" in packages["evidence_packets"]["deliverable"]
    assert packages["web_publication"]["status"] == "blocked"


def test_manifest_requires_all_safeguards():
    manifest = load(MANIFEST)
    assert set(manifest["quality_requirements"]) == {
        "official_order_preserved",
        "original_text_preserved",
        "units_and_periods_preserved",
        "conditional_targets_not_numericized",
        "missing_values_not_zeroed",
        "repeated_indicators_reference_only",
        "evidence_packet_required",
        "actuals_not_inferred",
    }
    assert len(manifest["open_questions"]) == 3
