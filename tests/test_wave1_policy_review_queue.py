import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/wave1_policy_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/wave1_policy_review_queue.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave_one_policy_review_queue_matches_schema():
    queue = load(QUEUE_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(queue)) == []


def test_queue_covers_all_wave_one_anchors_once_in_operational_order():
    queue = load(QUEUE_PATH)
    coverage = load(ROOT / "data/catalog/prefecture_coverage.json")
    items = queue["items"]

    assert len(items) == 9
    assert [item["order"] for item in items] == list(range(9))
    assert len({item["prefecture_code"] for item in items}) == 9
    assert {item["prefecture_code"] for item in items} == set(
        coverage["regional_anchor_codes"]
    )
    assert len({item["municipality_key"] for item in items}) == 9


def test_fukuoka_is_the_only_reviewed_reference_and_hokkaido_is_active():
    queue = load(QUEUE_PATH)
    items_by_code = {
        item["prefecture_code"]: item for item in queue["items"]
    }

    assert queue["completed_prefecture_codes"] == ["40"]
    assert queue["active_prefecture_code"] == "01"
    assert items_by_code["40"]["status"] == "reviewed_reference"
    assert items_by_code["40"]["source_inventory_status"] == "reviewed"
    assert items_by_code["40"]["next_gate"] == "actuals_linkage"
    assert items_by_code["01"]["status"] == "active_review"
    assert items_by_code["01"]["source_inventory_status"] == (
        "indicator_positions_reviewed"
    )
    assert items_by_code["01"]["next_gate"] == "kpi_catalog"
    assert "指標番号1〜108" in items_by_code["01"]["next_action"]
    assert "5件" in items_by_code["01"]["next_action"]
    assert sum(item["status"] == "reviewed_reference" for item in queue["items"]) == 1
    assert sum(item["status"] == "active_review" for item in queue["items"]) == 1
    assert sum(item["status"] == "queued" for item in queue["items"]) == 7


def test_queue_sources_exist_and_titles_match_the_policy_source_catalog():
    queue = load(QUEUE_PATH)
    source_catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources_by_id = {
        source["id"]: source for source in source_catalog["records"]
    }

    for item in queue["items"]:
        assert set(item["source_ids"]) <= set(sources_by_id)
        if item["prefecture_code"] != "40":
            assert len(item["source_ids"]) == 1
            source = sources_by_id[item["source_ids"][0]]
            assert source["municipality_key"] == item["municipality_key"]
            assert source["title"] == item["current_plan_title"]
            assert source["collection_status"] == "indexed"
            assert source["review_status"] == "verified"


def test_queue_uses_written_quality_reasons_instead_of_unverified_scores():
    queue = load(QUEUE_PATH)

    for item in queue["items"]:
        assert item["next_action"].strip()
        assert item["priority_basis"].strip()
        assert "score" not in item
        assert "readiness_score" not in item
