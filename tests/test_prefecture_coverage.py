import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
SCHEMA_PATH = ROOT / "schemas/prefecture_coverage.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_prefecture_coverage_registry_matches_schema():
    registry = load(COVERAGE_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(registry)) == []


def test_all_forty_seven_prefectures_are_registered_once_in_official_order():
    registry = load(COVERAGE_PATH)
    records = registry["records"]

    assert len(records) == 47
    assert [record["prefecture_code"] for record in records] == [
        f"{number:02d}" for number in range(1, 48)
    ]
    assert [record["entity_id"] for record in records] == [
        f"jp-pref-{number:02d}" for number in range(1, 48)
    ]

    for field in ("prefecture_code", "entity_id", "slug", "name", "official_url"):
        values = [record[field] for record in records]
        assert len(values) == len(set(values))


def test_region_grouping_covers_all_prefectures_without_overlap():
    records = load(COVERAGE_PATH)["records"]
    expected_counts = {
        "北海道": 1,
        "東北": 6,
        "関東": 7,
        "中部": 9,
        "近畿": 7,
        "中国": 5,
        "四国": 4,
        "九州・沖縄": 8,
    }
    actual_counts = {
        region: sum(record["region"] == region for record in records)
        for region in expected_counts
    }
    assert actual_counts == expected_counts
    assert sum(actual_counts.values()) == 47


def test_quality_stages_are_explicit_and_do_not_overstate_coverage():
    registry = load(COVERAGE_PATH)
    known_codes = {record["prefecture_code"] for record in registry["records"]}
    verified_codes = set(registry["verified_official_codes"])
    anchor_codes = set(registry["regional_anchor_codes"])
    reviewed_codes = set(registry["reviewed_prefecture_codes"])
    current_plan_codes = set(registry["current_plan_confirmed_codes"])
    plan_source_codes = {
        source["prefecture_code"] for source in registry["plan_sources"]
    }

    expected_anchor_codes = {
        "01",
        "04",
        "13",
        "23",
        "27",
        "34",
        "37",
        "40",
        "47",
    }
    assert verified_codes == expected_anchor_codes
    assert anchor_codes == expected_anchor_codes
    assert reviewed_codes == {"40"}
    assert current_plan_codes == {"13"}
    assert plan_source_codes == expected_anchor_codes

    assert verified_codes <= known_codes
    assert anchor_codes <= known_codes
    assert reviewed_codes <= known_codes
    assert current_plan_codes <= known_codes
    assert plan_source_codes <= known_codes
    assert reviewed_codes <= verified_codes
    assert reviewed_codes <= plan_source_codes
    assert current_plan_codes <= plan_source_codes

    assert len(known_codes - verified_codes) == 38
    assert len(plan_source_codes) == 9
    assert len(current_plan_codes) == 1
    assert len(plan_source_codes - current_plan_codes) == 8
    assert len(reviewed_codes) == 1


def test_wave_one_plan_sources_preserve_review_depth_and_https_provenance():
    plan_sources = load(COVERAGE_PATH)["plan_sources"]
    sources_by_code = {
        source["prefecture_code"]: source for source in plan_sources
    }

    for code in ("01", "04", "13", "23", "27", "34", "37", "47"):
        assert sources_by_code[code]["review_status"] == "indexed"
    assert sources_by_code["40"]["review_status"] == "reviewed"

    assert sources_by_code["01"]["title"] == "北海道総合計画"
    assert sources_by_code["04"]["title"] == "新・宮城の将来ビジョン"
    assert (
        sources_by_code["13"]["title"]
        == "2050東京戦略 ～東京 もっとよくなる～"
    )
    assert sources_by_code["13"]["url"].endswith("/basic-plan/2050-tokyo")
    assert sources_by_code["23"]["title"] == "あいちビジョン2030"
    assert sources_by_code["27"]["title"] == "将来ビジョン・大阪"
    assert (
        sources_by_code["37"]["title"]
        == "「人生100年時代のフロンティア県・香川」実現計画"
    )

    assert all(source["title"] != "「未来の東京」戦略" for source in plan_sources)
    assert all("/basic-plan/choki-plan" not in source["url"] for source in plan_sources)

    for source in plan_sources:
        assert source["url"].startswith("https://")
        assert source["title"].strip()
        assert source["verified_at"] == "2026-07-16"


def test_only_fukuoka_is_marked_reviewed_until_other_primary_sources_are_checked():
    registry = load(COVERAGE_PATH)
    reviewed_codes = set(registry["reviewed_prefecture_codes"])
    reviewed_plan_sources = {
        source["prefecture_code"]
        for source in registry["plan_sources"]
        if source["review_status"] in {"reviewed", "verified"}
    }
    assert reviewed_codes == reviewed_plan_sources == {"40"}
