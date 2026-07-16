import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/hokkaido_policy_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_policy_review_manifest_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(MANIFEST_PATH))) == []


def test_hokkaido_manifest_is_linked_to_the_active_wave_one_queue_item():
    manifest = load(MANIFEST_PATH)
    queue = load(ROOT / "data/catalog/wave1_policy_review_queue.json")
    active_item = next(
        item for item in queue["items"]
        if item["prefecture_code"] == queue["active_prefecture_code"]
    )
    assert manifest["prefecture_code"] == "01"
    assert active_item["status"] == "active_review"
    assert active_item["source_inventory_status"] == "indicator_relationships_reviewed"
    assert active_item["next_gate"] == "kpi_catalog"
    assert set(manifest["plan_source_ids"]) <= set(active_item["source_ids"])


def test_hokkaido_manifest_preserves_boundaries_and_partial_counts():
    manifest = load(MANIFEST_PATH)
    assert manifest["expected_indicator_count"] == 108
    assert manifest["reviewed_indicator_count"] == 29
    assert manifest["remaining_indicator_count"] == 79
    assert manifest["indicator_evidence_packet_count"] == 29
    assert manifest["reviewed_indicator_count"] + manifest["remaining_indicator_count"] == 108
    assert manifest["indicator_evidence_packet_count"] == manifest["reviewed_indicator_count"]
    assert "掲載行は113" in manifest["count_basis"]
    assert "差分5件" in manifest["count_basis"]
    assert "指標1〜29" in manifest["count_basis"]
    assert manifest["extraction_status"] == "in_progress"
    assert manifest["active_work_package"] == "indicator_catalog"


def test_hokkaido_work_packages_record_three_reviewed_fields():
    manifest = load(MANIFEST_PATH)
    packages = {item["id"]: item for item in manifest["work_packages"]}
    assert list(packages) == ["policy_hierarchy", "indicator_source_index", "indicator_catalog", "evidence_packets", "web_publication"]
    assert packages["policy_hierarchy"]["status"] == "completed"
    assert packages["indicator_source_index"]["status"] == "completed"
    assert packages["indicator_catalog"]["status"] == "active"
    assert "指標1〜29" in packages["indicator_catalog"]["deliverable"]
    assert "指標30〜108" in packages["indicator_catalog"]["deliverable"]
    assert packages["evidence_packets"]["status"] == "active"
    assert "指標1〜29" in packages["evidence_packets"]["deliverable"]
    assert "残る79指標" in packages["evidence_packets"]["deliverable"]
    assert packages["web_publication"]["status"] == "blocked"


def test_hokkaido_manifest_requires_all_safeguards():
    manifest = load(MANIFEST_PATH)
    assert set(manifest["quality_requirements"]) == {
        "official_order_preserved", "original_text_preserved",
        "units_and_periods_preserved", "conditional_targets_not_numericized",
        "missing_values_not_zeroed", "repeated_indicators_reference_only",
        "evidence_packet_required", "actuals_not_inferred",
    }
    assert len(manifest["open_questions"]) == 3
