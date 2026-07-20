import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/wave1_policy_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/wave1_policy_review_queue.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_queue_schema_and_order():
    queue = load(QUEUE_PATH)
    validator = Draft202012Validator(load(SCHEMA_PATH), format_checker=FormatChecker())
    assert list(validator.iter_errors(queue)) == []
    coverage = load(ROOT / "data/catalog/prefecture_coverage.json")
    items = queue["items"]
    assert len(items) == 9
    assert [item["order"] for item in items] == list(range(9))
    assert {item["prefecture_code"] for item in items} == set(
        coverage["regional_anchor_codes"]
    )
    assert queue["completed_prefecture_codes"] == ["40", "01"]
    assert queue["active_prefecture_code"] == "04"


def test_active_queue_progress_tokens():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    active = items["04"]
    assert active["status"] == "active_review"
    assert active["source_inventory_status"] == "reviewed"
    assert active["next_gate"] == "actuals_linkage"
    assert all(token in active["next_action"] for token in ["35", "6", "114", "7"])
    assert all(token in active["priority_basis"] for token in ["128", "149"])
    assert {
        status: sum(item["status"] == status for item in queue["items"])
        for status in ["reviewed_reference", "active_review", "queued"]
    } == {"reviewed_reference": 2, "active_review": 1, "queued": 6}


def test_queue_sources_and_descriptions():
    queue = load(QUEUE_PATH)
    source_catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources = {item["id"]: item for item in source_catalog["records"]}
    for item in queue["items"]:
        assert set(item["source_ids"]) <= set(sources)
        assert item["next_action"].strip()
        assert item["priority_basis"].strip()
        if item["prefecture_code"] != "40":
            source = sources[item["source_ids"][0]]
            assert source["municipality_key"] == item["municipality_key"]
            assert source["title"] == item["current_plan_title"]
            assert source["collection_status"] == "indexed"
            assert source["review_status"] == "verified"
