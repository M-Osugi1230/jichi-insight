import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/catalog/nationwide_source_inventory.json"
SCHEMA_PATH = ROOT / "schemas/nationwide_source_inventory.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
QUEUE_PATH = ROOT / "data/catalog/nationwide_policy_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_nationwide_source_inventory_matches_schema_and_all_prefectures():
    inventory = load(INVENTORY_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(inventory)) == []

    records = inventory["records"]
    expected_codes = [f"{number:02d}" for number in range(1, 48)]
    assert len(records) == 47
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert len({record["prefecture_code"] for record in records}) == 47


def test_inventory_codes_agree_with_coverage_and_execution_queue():
    inventory_codes = {
        record["prefecture_code"] for record in load(INVENTORY_PATH)["records"]
    }
    coverage_codes = {
        record["prefecture_code"] for record in load(COVERAGE_PATH)["records"]
    }
    queue_codes = {
        item["prefecture_code"] for item in load(QUEUE_PATH)["items"]
    }
    assert inventory_codes == coverage_codes == queue_codes


def test_inventory_summary_is_derived_from_records():
    inventory = load(INVENTORY_PATH)
    categories = inventory["categories"]
    statuses = inventory["status_order"]

    for category in categories:
        counts = Counter(
            record["sources"][category] for record in inventory["records"]
        )
        assert inventory["summary"][category] == {
            status: counts[status] for status in statuses
        }
        assert sum(inventory["summary"][category].values()) == 47


def test_source_depth_is_conservative_and_evidence_backed():
    records = {
        record["prefecture_code"]: record for record in load(INVENTORY_PATH)["records"]
    }

    assert records["01"]["sources"] == {
        "policy_plan": "reviewed",
        "implementation_plan": "not_indexed",
        "kpi_source": "reviewed",
        "annual_evaluation": "not_indexed",
        "budget": "not_indexed",
        "project_evaluation": "not_indexed",
    }
    assert records["04"]["sources"] == {
        "policy_plan": "reviewed",
        "implementation_plan": "reviewed",
        "kpi_source": "reviewed",
        "annual_evaluation": "linked",
        "budget": "not_indexed",
        "project_evaluation": "not_indexed",
    }
    assert records["40"]["sources"] == {
        "policy_plan": "reviewed",
        "implementation_plan": "reviewed",
        "kpi_source": "reviewed",
        "annual_evaluation": "indexed",
        "budget": "reviewed",
        "project_evaluation": "not_indexed",
    }

    for code, record in records.items():
        if code not in {"01", "04", "40"}:
            assert record["sources"]["policy_plan"] == "indexed"
            assert all(
                status == "not_indexed"
                for category, status in record["sources"].items()
                if category != "policy_plan"
            )


def test_no_prefecture_is_mistakenly_marked_complete():
    inventory = load(INVENTORY_PATH)
    assert inventory["summary"]["project_evaluation"] == {
        "not_indexed": 47,
        "indexed": 0,
        "reviewed": 0,
        "linked": 0,
    }
    assert all(record["next_action"].strip() for record in inventory["records"])
    assert all(
        "linked" not in record["sources"].values()
        or record["prefecture_code"] == "04"
        for record in inventory["records"]
    )
