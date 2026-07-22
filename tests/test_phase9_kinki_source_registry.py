import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/phase9_kinki_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/phase9_kinki_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kinki_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_kinki_batch_indexes_exact_five_prefectures():
    registry = load(REGISTRY_PATH)
    expected_codes = ["25", "26", "28", "29", "30"]
    records = registry["records"]

    assert registry["prefecture_codes"] == expected_codes
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert all(record["numeric_target_status"] == "indexed" for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)


def test_each_kinki_prefecture_has_plan_target_and_evaluation_roles():
    records = load(REGISTRY_PATH)["records"]
    evaluation_roles = {
        "annual_monitoring",
        "annual_evaluation",
        "evaluation_framework",
    }

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


def test_nonstandard_and_new_plan_boundaries_are_explicit():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert by_code["25"]["current_plan_period"] == "2023年度～2026年度"
    assert all(
        token in by_code["25"]["target_source_boundary"]
        for token in ["2024年7月改訂", "次期実施計画", "先行昇格"]
    )

    assert by_code["29"]["current_plan_period"] == "2026年度"
    nara_evaluation = next(
        source
        for source in by_code["29"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert nara_evaluation["target_version_scope"] == "prior_plan"
    assert all(
        token in by_code["29"]["target_source_boundary"]
        for token in ["年度版政策集", "令和8年度版", "令和6年度重点課題評価"]
    )

    assert by_code["30"]["current_plan_period"] == "2026年度～2030年度"
    wakayama_evaluation = next(
        source
        for source in by_code["30"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert wakayama_evaluation["availability"] == "not_yet_published"
    assert "旧長期総合計画" in by_code["30"]["target_source_boundary"]


def test_indicator_hierarchies_and_prior_results_are_not_collapsed():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert all(
        token in by_code["26"]["target_source_boundary"]
        for token in ["将来構想", "基本計画", "地域振興計画", "広域連携"]
    )
    assert all(
        token in by_code["28"]["target_source_boundary"]
        for token in ["ひょうごビジョン2050", "KPI", "第二期戦略", "第三期"]
    )


def test_source_indexing_does_not_overstate_review_or_achievement():
    records = load(REGISTRY_PATH)["records"]
    assert all(record["review_status"] == "source_indexed" for record in records)
    assert all(
        "独自達成率" not in source["note"]
        for record in records
        for source in record["sources"]
    )
