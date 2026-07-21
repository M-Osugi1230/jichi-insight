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
    assert queue["completed_prefecture_codes"] == ["40", "01", "04", "13", "23", "27"]
    assert queue["active_prefecture_code"] == "34"


def test_hiroshima_is_active_after_osaka_indicator_completion():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    active = items["34"]
    assert active["status"] == "active_review"
    assert active["next_gate"] == "kpi_catalog"
    assert all(
        token in active["next_action"]
        for token in ["改定版", "アクションプラン", "KPI", "Evidence"]
    )
    assert {
        status: sum(item["status"] == status for item in queue["items"])
        for status in ["reviewed_reference", "active_review", "queued"]
    } == {"reviewed_reference": 6, "active_review": 1, "queued": 2}


def test_osaka_is_complete_indicator_reference_with_lineage_boundaries_visible():
    items = {
        item["prefecture_code"]: item
        for item in load(QUEUE_PATH)["items"]
    }
    osaka = items["27"]
    assert osaka["status"] == "reviewed_reference"
    assert osaka["source_inventory_status"] == "reviewed"
    assert osaka["next_gate"] == "actuals_linkage"
    assert all(
        token in osaka["next_action"]
        for token in ["83", "91", "Evidence 83", "経済目標1", "客観KPI27", "主観指標55"]
    )
    assert all(
        token in osaka["priority_basis"]
        for token in ["最終戦略", "旧ビジョン実績", "事業一覧", "別系統"]
    )


def test_aichi_is_complete_indicator_reference_with_evaluation_boundary_visible():
    items = {
        item["prefecture_code"]: item
        for item in load(QUEUE_PATH)["items"]
    }
    aichi = items["23"]
    assert aichi["status"] == "reviewed_reference"
    assert aichi["source_inventory_status"] == "reviewed"
    assert aichi["next_gate"] == "management_evaluation_linkage"
    assert all(
        token in aichi["next_action"]
        for token in ["56", "62", "61", "29", "再掲", "目標改定"]
    )


def test_tokyo_is_complete_target_card_reference_with_actuals_work_visible():
    items = {
        item["prefecture_code"]: item
        for item in load(QUEUE_PATH)["items"]
    }
    tokyo = items["13"]
    assert tokyo["status"] == "reviewed_reference"
    assert tokyo["source_inventory_status"] == "reviewed"
    assert tokyo["next_gate"] == "actuals_linkage"
    assert all(
        token in tokyo["next_action"]
        for token in ["60", "25", "304", "Evidence", "年度実績"]
    )


def test_miyagi_remains_a_reviewed_reference_with_actuals_work_visible():
    items = {
        item["prefecture_code"]: item
        for item in load(QUEUE_PATH)["items"]
    }
    miyagi = items["04"]
    assert miyagi["status"] == "reviewed_reference"
    assert miyagi["next_gate"] == "actuals_linkage"
    assert all(token in miyagi["next_action"] for token in ["128", "149", "95", "15", "54"])


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
