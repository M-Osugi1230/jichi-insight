import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/phase9_chugoku_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/phase9_chugoku_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chugoku_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_chugoku_batch_indexes_exact_prefectures():
    registry = load(REGISTRY_PATH)
    expected_codes = ["31", "32", "33", "35"]
    records = registry["records"]

    assert registry["prefecture_codes"] == expected_codes
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert all(record["numeric_target_status"] == "indexed" for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)


def test_each_chugoku_prefecture_has_plan_target_and_evaluation_roles():
    evaluation_roles = {
        "annual_monitoring",
        "annual_evaluation",
        "evaluation_framework",
    }
    for record in load(REGISTRY_PATH)["records"]:
        roles = {source["role"] for source in record["sources"]}
        assert "current_plan" in roles
        assert "numeric_target_source" in roles
        assert len(roles & evaluation_roles) == 1
        assert len(record["sources"]) == 3
        assert len({source["id"] for source in record["sources"]}) == 3
        assert all(source["url"].startswith("https://") for source in record["sources"])


def test_chugoku_plan_and_indicator_boundaries_are_explicit():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }
    assert all(
        token in by_code["31"]["target_source_boundary"]
        for token in ["旧戦略", "Society5.0", "自動接続しない"]
    )
    assert all(
        token in by_code["33"]["target_source_boundary"]
        for token in ["第4次", "第3次", "県民満足度"]
    )
    assert all(
        token in by_code["35"]["target_source_boundary"]
        for token in ["成果指標", "県民実感", "速報値"]
    )


def test_chugoku_source_indexing_does_not_overstate_review_or_achievement():
    records = load(REGISTRY_PATH)["records"]
    assert all(record["review_status"] == "source_indexed" for record in records)
    assert all(
        "独自達成率" not in source["note"]
        for record in records
        for source in record["sources"]
    )
