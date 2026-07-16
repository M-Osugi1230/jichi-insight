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
    plan_source_codes = {
        source["prefecture_code"] for source in registry["plan_sources"]
    }

    assert verified_codes == {"01", "04", "13", "23", "27", "34", "37", "40", "47"}
    assert anchor_codes == verified_codes
    assert reviewed_codes == {"40"}
    assert plan_source_codes == {"34", "40", "47"}

    assert verified_codes <= known_codes
    assert anchor_codes <= known_codes
    assert reviewed_codes <= known_codes
    assert plan_source_codes <= known_codes
    assert reviewed_codes <= verified_codes
    assert reviewed_codes <= plan_source_codes

    assert len(known_codes - verified_codes) == 38
    assert len(plan_source_codes) == 3
    assert len(reviewed_codes) == 1


def test_plan_sources_preserve_review_depth_and_https_provenance():
    plan_sources = load(COVERAGE_PATH)["plan_sources"]
    sources_by_code = {
        source["prefecture_code"]: source for source in plan_sources
    }

    assert sources_by_code["34"]["review_status"] == "indexed"
    assert sources_by_code["40"]["review_status"] == "reviewed"
    assert sources_by_code["47"]["review_status"] == "indexed"

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
