import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/wave1_policy_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/wave1_policy_review_queue.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_wave_one_policy_review_queue_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_queue_covers_all_wave_one_anchors_once_in_operational_order():
    queue = load(QUEUE_PATH)
    coverage = load(ROOT / "data/catalog/prefecture_coverage.json")
    items = queue["items"]
    assert len(items) == 9
    assert [item["order"] for item in items] == list(range(9))
    assert {item["prefecture_code"] for item in items} == set(
        coverage["regional_anchor_codes"]
    )
    assert len({item["municipality_key"] for item in items}) == 9


def test_reviewed_references_and_active_miyagi_progress():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    assert queue["completed_prefecture_codes"] == ["40", "01"]
    assert queue["active_prefecture_code"] == "04"

    for code in ["40", "01"]:
        assert items[code]["status"] == "reviewed_reference"
        assert items[code]["source_inventory_status"] == "reviewed"
        assert items[code]["next_gate"] == "actuals_linkage"

    miyagi = items["04"]
    assert miyagi["status"] == "active_review"
    assert miyagi["source_inventory_status"] == "indicator_positions_reviewed"
    assert miyagi["next_gate"] == "kpi_catalog"
    assert "目標グループ1〜100・系列1〜119" in miyagi["next_action"]
    assert "目標グループ101〜104・系列120〜123" in miyagi["next_action"]
    assert "取組13の7グループ・7系列" in miyagi["priority_basis"]
    assert "累計1グループ" in miyagi["priority_basis"]
    assert "同一年の2グループ" in miyagi["priority_basis"]
    assert "原文表記3939・2428" in miyagi["priority_basis"]
    assert "後期末目標未設定" in miyagi["priority_basis"]

    assert {
        status: sum(item["status"] == status for item in queue["items"])
        for status in ["reviewed_reference", "active_review", "queued"]
    } == {"reviewed_reference": 2, "active_review": 1, "queued": 6}


def test_queue_sources_exist_and_written_reasons_are_present():
    queue = load(QUEUE_PATH)
    source_catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources = {item["id"]: item for item in source_catalog["records"]}
    for item in queue["items"]:
        assert set(item["source_ids"]) <= set(sources)
        assert item["next_action"].strip()
        assert item["priority_basis"].strip()
        assert "score" not in item
        if item["prefecture_code"] != "40":
            source = sources[item["source_ids"][0]]
            assert source["municipality_key"] == item["municipality_key"]
            assert source["title"] == item["current_plan_title"]
            assert source["collection_status"] == "indexed"
            assert source["review_status"] == "verified"
