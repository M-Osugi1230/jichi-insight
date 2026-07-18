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
    assert len({item["prefecture_code"] for item in items}) == 9
    assert {item["prefecture_code"] for item in items} == set(
        coverage["regional_anchor_codes"]
    )
    assert len({item["municipality_key"] for item in items}) == 9


def test_fukuoka_and_hokkaido_are_reviewed_references_and_miyagi_is_active():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    assert queue["completed_prefecture_codes"] == ["40", "01"]
    assert queue["active_prefecture_code"] == "04"

    for code in ["40", "01"]:
        assert items[code]["status"] == "reviewed_reference"
        assert items[code]["source_inventory_status"] == "reviewed"
        assert items[code]["next_gate"] == "actuals_linkage"

    assert "全108指標" in items["01"]["next_action"]
    assert "Evidence Packet 108件" in items["01"]["next_action"]
    assert "年度実績" in items["01"]["next_action"]

    assert items["04"]["status"] == "active_review"
    assert items["04"]["source_inventory_status"] == "policy_hierarchy_reviewed"
    assert items["04"]["next_gate"] == "kpi_catalog"
    assert "目標指標一覧表" in items["04"]["next_action"]
    assert "一意指標数" in items["04"]["next_action"]
    assert "4基本方向・8政策・18取組" in items["04"]["priority_basis"]

    status_counts = {
        status: sum(item["status"] == status for item in queue["items"])
        for status in ["reviewed_reference", "active_review", "queued"]
    }
    assert status_counts == {
        "reviewed_reference": 2,
        "active_review": 1,
        "queued": 6,
    }


def test_queue_sources_exist_and_titles_match_the_policy_source_catalog():
    queue = load(QUEUE_PATH)
    source_catalog = load(ROOT / "data/catalog/policy_sources.json")
    sources = {item["id"]: item for item in source_catalog["records"]}
    for item in queue["items"]:
        assert set(item["source_ids"]) <= set(sources)
        if item["prefecture_code"] != "40":
            assert len(item["source_ids"]) == 1
            source = sources[item["source_ids"][0]]
            assert source["municipality_key"] == item["municipality_key"]
            assert source["title"] == item["current_plan_title"]
            assert source["collection_status"] == "indexed"
            assert source["review_status"] == "verified"


def test_queue_uses_written_reasons_instead_of_scores():
    for item in load(QUEUE_PATH)["items"]:
        assert item["next_action"].strip()
        assert item["priority_basis"].strip()
        assert "score" not in item
        assert "readiness_score" not in item
