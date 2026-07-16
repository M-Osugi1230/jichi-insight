import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/catalog/hokkaido_policy_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/policy_review_manifest.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hokkaido_policy_review_manifest_matches_schema():
    manifest = load(MANIFEST_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(manifest)) == []


def test_hokkaido_manifest_is_linked_to_the_active_wave_one_queue_item():
    manifest = load(MANIFEST_PATH)
    queue = load(ROOT / "data/catalog/wave1_policy_review_queue.json")
    active_item = next(
        item
        for item in queue["items"]
        if item["prefecture_code"] == queue["active_prefecture_code"]
    )

    assert manifest["prefecture_code"] == "01"
    assert manifest["municipality_key"] == "hokkaido-prefecture"
    assert active_item["prefecture_code"] == manifest["prefecture_code"]
    assert active_item["status"] == "active_review"
    assert active_item["source_inventory_status"] == (
        "indicator_relationships_reviewed"
    )
    assert active_item["next_gate"] == "kpi_catalog"
    assert set(manifest["plan_source_ids"]) <= set(active_item["source_ids"])


def test_hokkaido_manifest_preserves_the_official_indicator_boundaries():
    manifest = load(MANIFEST_PATH)

    assert manifest["expected_indicator_count"] == 108
    assert "掲載行は113" in manifest["count_basis"]
    assert "差分5件" in manifest["count_basis"]
    assert manifest["extraction_status"] == "in_progress"
    assert manifest["active_work_package"] == "indicator_catalog"


def test_hokkaido_work_packages_complete_source_index_and_activate_catalog():
    manifest = load(MANIFEST_PATH)
    packages = manifest["work_packages"]
    packages_by_id = {package["id"]: package for package in packages}

    assert [package["id"] for package in packages] == [
        "policy_hierarchy",
        "indicator_source_index",
        "indicator_catalog",
        "evidence_packets",
        "web_publication",
    ]
    assert sum(package["status"] == "active" for package in packages) == 1
    assert packages_by_id["policy_hierarchy"]["status"] == "completed"
    assert packages_by_id["indicator_source_index"]["status"] == "completed"
    assert "追加の政策分野参照5件" in packages_by_id[
        "indicator_source_index"
    ]["deliverable"]
    assert "検証済み" in packages_by_id["indicator_source_index"][
        "completion_gate"
    ]
    assert packages_by_id["indicator_catalog"]["status"] == "active"
    assert "108指標" in packages_by_id["indicator_catalog"]["deliverable"]
    assert packages_by_id["web_publication"]["status"] == "blocked"
    assert all(package["deliverable"].strip() for package in packages)
    assert all(package["completion_gate"].strip() for package in packages)


def test_hokkaido_manifest_requires_all_non_negotiable_kpi_safeguards():
    manifest = load(MANIFEST_PATH)

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
