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
    assert queue["completed_prefecture_codes"] == [
        "40", "01", "04", "13", "23", "27", "34", "37"
    ]
    assert queue["active_prefecture_code"] == "47"


def test_okinawa_is_active_after_kagawa_indicator_completion():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    active = items["47"]
    assert active["status"] == "active_review"
    assert active["next_gate"] == "kpi_catalog"
    assert all(
        token in active["next_action"]
        for token in ["令和7～9年度", "成果指標", "基本計画", "Evidence"]
    )
    assert {
        status: sum(item["status"] == status for item in queue["items"])
        for status in ["reviewed_reference", "active_review", "queued"]
    } == {"reviewed_reference": 8, "active_review": 1, "queued": 0}


def test_kagawa_is_complete_reference_with_extension_boundaries_visible():
    items = {
        item["prefecture_code"]: item for item in load(QUEUE_PATH)["items"]
    }
    kagawa = items["37"]
    assert kagawa["status"] == "reviewed_reference"
    assert kagawa["source_inventory_status"] == "reviewed"
    assert kagawa["next_gate"] == "actuals_linkage"
    assert all(
        token in kagawa["next_action"]
        for token in ["135", "141", "Evidence 135", "再掲6", "目標更新87", "令和12年"]
    )
    assert all(
        token in kagawa["priority_basis"]
        for token in ["計画期間延長", "旧目標", "新目標", "重複排除"]
    )


def test_recent_reviewed_references_keep_their_boundaries():
    items = {
        item["prefecture_code"]: item for item in load(QUEUE_PATH)["items"]
    }
    assert all(token in items["34"]["next_action"] for token in ["62", "59", "未測定3"])
    assert all(token in items["27"]["next_action"] for token in ["83", "91", "Evidence 83"])
    assert all(token in items["23"]["next_action"] for token in ["56", "62", "61", "29"])
    assert all(token in items["13"]["next_action"] for token in ["60", "25", "304", "Evidence"])
    assert all(token in items["04"]["next_action"] for token in ["128", "149", "95", "15", "54"])


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
