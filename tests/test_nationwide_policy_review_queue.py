import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/nationwide_policy_review_queue.json"
SCHEMA_PATH = ROOT / "schemas/nationwide_policy_review_queue.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nationwide_queue_matches_schema_and_covers_all_prefectures():
    queue = load(QUEUE_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(queue)) == []

    items = queue["items"]
    coverage_codes = {
        record["prefecture_code"] for record in load(COVERAGE_PATH)["records"]
    }
    assert len(items) == 47
    assert [item["order"] for item in items] == list(range(47))
    assert {item["prefecture_code"] for item in items} == coverage_codes
    assert len({item["prefecture_code"] for item in items}) == 47


def test_nationwide_queue_preserves_reference_wave_and_active_work():
    queue = load(QUEUE_PATH)
    by_code = {item["prefecture_code"]: item for item in queue["items"]}

    assert queue["active_prefecture_code"] == "04"
    assert queue["completed_prefecture_codes"] == ["40", "01"]
    assert by_code["40"]["status"] == "reviewed_reference"
    assert by_code["01"]["status"] == "reviewed_reference"
    assert by_code["04"]["status"] == "active_review"
    assert by_code["04"]["next_gate"] == "actuals_linkage"
    assert "取組16〜18" in by_code["04"]["next_action"]

    wave1_codes = {
        code for code, item in by_code.items() if item["wave"] == "wave1"
    }
    assert wave1_codes == {"04", "13", "23", "27", "34", "37", "47"}


def test_all_remaining_prefectures_advance_to_source_inventory():
    queue = load(QUEUE_PATH)
    status_counts = {
        status: sum(item["status"] == status for item in queue["items"])
        for status in [
            "reviewed_reference",
            "active_review",
            "indexed_queue",
            "source_review_required",
        ]
    }
    assert status_counts == {
        "reviewed_reference": 2,
        "active_review": 1,
        "indexed_queue": 44,
        "source_review_required": 0,
    }
    assert all(
        item["next_gate"] == "source_inventory"
        for item in queue["items"]
        if item["status"] == "indexed_queue"
    )


def test_nationwide_queue_and_coverage_quality_states_agree():
    queue = load(QUEUE_PATH)
    coverage = load(COVERAGE_PATH)
    by_code = {item["prefecture_code"]: item for item in queue["items"]}

    review_required = set(coverage["current_plan_review_required_codes"])
    reviewed = set(coverage["reviewed_prefecture_codes"])
    confirmed = set(coverage["current_plan_confirmed_codes"])

    assert review_required == set()
    assert {
        code
        for code, item in by_code.items()
        if item["status"] == "source_review_required"
    } == set()
    assert {
        code
        for code, item in by_code.items()
        if item["status"] == "reviewed_reference"
    } == reviewed
    assert confirmed == {item["prefecture_code"] for item in queue["items"]}
    assert all(item["next_action"].strip() for item in queue["items"])
