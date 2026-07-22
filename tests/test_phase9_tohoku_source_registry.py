import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/phase9_tohoku_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/phase9_tohoku_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_tohoku_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_tohoku_batch_indexes_exact_five_prefectures():
    registry = load(REGISTRY_PATH)
    expected_codes = ["02", "03", "05", "06", "07"]
    records = registry["records"]

    assert registry["prefecture_codes"] == expected_codes
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert all(record["numeric_target_status"] == "indexed" for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)


def test_each_tohoku_prefecture_has_plan_target_and_evaluation_roles():
    records = load(REGISTRY_PATH)["records"]
    required_roles = {"current_plan", "numeric_target_source", "annual_evaluation"}

    for record in records:
        assert {source["role"] for source in record["sources"]} == required_roles
        assert len({source["id"] for source in record["sources"]}) == 3
        assert record["target_source_boundary"].strip()
        for source in record["sources"]:
            if source["availability"] == "published":
                assert source["url"].startswith("https://")
            else:
                assert source["url"] is None


def test_plan_version_boundaries_are_explicit():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert by_code["05"]["current_plan_period"] == "2026年度～2029年度"
    assert "新秋田元気創造プラン" in by_code["05"]["target_source_boundary"]
    akita_evaluation = next(
        source
        for source in by_code["05"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert akita_evaluation["availability"] == "not_yet_published"

    yamagata_evaluation = next(
        source
        for source in by_code["06"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert yamagata_evaluation["target_version_scope"] == "prior_plan"
    assert "旧KPI" in by_code["06"]["target_source_boundary"]


def test_indicator_hierarchies_are_not_collapsed():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }
    assert all(
        token in by_code["02"]["target_source_boundary"]
        for token in ["観察指標", "KPI", "政策点検"]
    )
    assert all(
        token in by_code["03"]["target_source_boundary"]
        for token in ["政策推進", "復興推進", "地域振興", "行政経営"]
    )
    assert all(
        token in by_code["07"]["target_source_boundary"]
        for token in ["34指標", "279指標", "別階層"]
    )
