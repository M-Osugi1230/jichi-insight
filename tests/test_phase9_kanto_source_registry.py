import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/catalog/phase9_kanto_source_registry.json"
SCHEMA_PATH = ROOT / "schemas/phase9_kanto_source_registry.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kanto_source_registry_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(REGISTRY_PATH))) == []


def test_kanto_batch_indexes_exact_six_prefectures():
    registry = load(REGISTRY_PATH)
    expected_codes = ["08", "09", "10", "11", "12", "14"]
    records = registry["records"]

    assert registry["prefecture_codes"] == expected_codes
    assert [record["prefecture_code"] for record in records] == expected_codes
    assert all(record["numeric_target_status"] == "indexed" for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)


def test_each_kanto_prefecture_has_plan_target_and_evaluation_roles():
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


def test_new_plan_and_evaluation_boundaries_are_explicit():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert by_code["08"]["current_plan_period"] == "2026年度～2029年度"
    assert "モニタリング資料" in by_code["08"]["target_source_boundary"]

    assert by_code["09"]["current_plan_period"] == "2026年度～2030年度"
    tochigi_evaluation = next(
        source
        for source in by_code["09"]["sources"]
        if source["role"] == "annual_evaluation"
    )
    assert tochigi_evaluation["availability"] == "not_yet_published"
    assert "旧とちぎ未来創造プラン" in by_code["09"]["target_source_boundary"]

    assert by_code["12"]["current_plan_period"] == "2025年度～2028年度"
    assert all(
        token in by_code["12"]["target_source_boundary"]
        for token in ["89社会目標", "76社会目標", "別バージョン"]
    )


def test_indicator_hierarchies_and_revisions_are_not_collapsed():
    by_code = {
        record["prefecture_code"]: record
        for record in load(REGISTRY_PATH)["records"]
    }

    assert all(
        token in by_code["10"]["target_source_boundary"]
        for token in ["2040年ビジョン", "基本計画", "KPI", "ロードマップ"]
    )
    assert all(
        token in by_code["11"]["target_source_boundary"]
        for token in ["13指標", "当初版", "変更後版"]
    )
    assert all(
        token in by_code["14"]["target_source_boundary"]
        for token in ["指標", "KPI", "別階層"]
    )


def test_monitoring_and_evaluation_materials_do_not_overstate_review():
    records = load(REGISTRY_PATH)["records"]
    assert all("達成率へ" not in record["target_source_boundary"] for record in records)
    assert all(record["review_status"] == "source_indexed" for record in records)
    assert all(
        source["target_version_scope"] == "current_plan"
        for record in records
        for source in record["sources"]
    )
