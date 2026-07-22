import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/phase9_chubu_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/phase9_chubu_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chubu_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_chubu_batch_indexes_exact_nine_prefectures():
    registry = load(REGISTRY_PATH)
    expected_codes = ["15", "16", "17", "18", "19", "20", "21", "22", "24"]
    records = registry["records"]

    assert registry["prefecture_codes"] == expected_codes
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert all(record["numeric_target_status"] == "indexed" for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)


def test_each_chubu_prefecture_has_plan_target_and_evaluation_roles():
    records = load(REGISTRY_PATH)["records"]
    evaluation_roles = {"annual_monitoring", "annual_evaluation", "evaluation_framework"}

    for record in records:
        roles = {source["role"] for source in record["sources"]}
        assert "current_plan" in roles
        assert "numeric_target_source" in roles
        assert len(roles & evaluation_roles) == 1
        assert len({source["id"] for source in record["sources"]}) == 3
        for source in record["sources"]:
            if source["availability"] == "published":
                assert source["url"].startswith("https://")
            else:
                assert source["url"] is None


def test_recent_plan_transitions_do_not_reuse_prior_evaluations():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert by_code["15"]["current_plan_period"] == "2025年度～2032年度"
    assert "前計画の最終評価" in by_code["15"]["target_source_boundary"]

    assert by_code["16"]["current_plan_period"] == "2025年度～2029年度"
    toyama_evaluation = next(
        source
        for source in by_code["16"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert toyama_evaluation["availability"] == "not_yet_published"
    assert "旧元気とやま創造計画" in by_code["16"]["target_source_boundary"]

    assert by_code["22"]["current_plan_period"] == "2025年度～2028年度"
    shizuoka_evaluation = next(
        source
        for source in by_code["22"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert shizuoka_evaluation["availability"] == "not_yet_published"
    assert "旧白書" in by_code["22"]["target_source_boundary"]


def test_indicator_hierarchies_and_revisions_are_not_collapsed():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert all(
        token in by_code["17"]["target_source_boundary"]
        for token in ["14主要目標", "160KPI", "別階層", "創造的復興プラン"]
    )
    assert all(
        token in by_code["18"]["target_source_boundary"]
        for token in ["2040年将来構想", "実行・地域プラン", "毎年度"]
    )
    assert all(
        token in by_code["20"]["target_source_boundary"]
        for token in ["主要目標", "達成目標", "地域計画", "判定なし"]
    )
    assert all(
        token in by_code["21"]["target_source_boundary"]
        for token in ["2026年3月改訂", "旧戦略", "基本目標", "KPI"]
    )
    assert all(
        token in by_code["24"]["target_source_boundary"]
        for token in ["政策・施策KPI", "行政運営KPI", "別レイヤー"]
    )


def test_source_indexing_does_not_overstate_review_or_achievement():
    records = load(REGISTRY_PATH)["records"]
    assert all(record["review_status"] == "source_indexed" for record in records)
    assert all(
        "独自達成率" not in source["note"]
        for record in records
        for source in record["sources"]
    )
