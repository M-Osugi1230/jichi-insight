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
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(registry)) == []


def test_all_forty_seven_prefectures_are_registered_once_in_official_order():
    records = load(COVERAGE_PATH)["records"]
    expected_codes = [f"{number:02d}" for number in range(1, 48)]

    assert len(records) == 47
    assert [record["prefecture_code"] for record in records] == expected_codes
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


def test_all_current_policy_plan_entries_are_confirmed_and_reviewed():
    registry = load(COVERAGE_PATH)
    known_codes = {record["prefecture_code"] for record in registry["records"]}
    all_codes = {f"{number:02d}" for number in range(1, 48)}
    verified_codes = set(registry["verified_official_codes"])
    indexed_codes = set(registry["plan_entry_indexed_codes"])
    anchor_codes = set(registry["regional_anchor_codes"])
    reviewed_codes = set(registry["reviewed_prefecture_codes"])
    confirmed_codes = set(registry["current_plan_confirmed_codes"])
    review_required_codes = set(registry["current_plan_review_required_codes"])
    source_codes = {source["prefecture_code"] for source in registry["plan_sources"]}

    assert known_codes == all_codes
    assert verified_codes == all_codes
    assert indexed_codes == all_codes
    assert source_codes == all_codes
    assert anchor_codes == {"01", "04", "13", "23", "27", "34", "37", "40", "47"}
    assert reviewed_codes == all_codes
    assert confirmed_codes == all_codes
    assert review_required_codes == set()
    assert reviewed_codes == confirmed_codes
    assert len(confirmed_codes) == 47


def test_plan_sources_preserve_nonstandard_plan_structures_and_statuses():
    sources = load(COVERAGE_PATH)["plan_sources"]
    by_code = {source["prefecture_code"]: source for source in sources}

    assert len(sources) == 47
    assert len(by_code) == 47
    assert len({source["url"] for source in sources}) == 47
    assert all(source["url"].startswith("https://") for source in sources)
    assert all(source["title"].strip() for source in sources)
    assert all(source["plan_status"] == "current_confirmed" for source in sources)
    assert all(source["review_status"] == "reviewed" for source in sources)

    assert by_code["29"]["source_kind"] == "annual_policy_portfolio"
    assert by_code["39"]["source_kind"] == "regional_strategy"
    assert by_code["41"]["source_kind"] == "regional_strategy"
    assert by_code["29"]["title"] == "奈良県政策集＜令和8年度版＞"
    assert by_code["39"]["title"] == "高知県元気な未来創造戦略＜令和8年度版＞"
    assert by_code["41"]["title"] == "佐賀県施策方針2023"

    assert by_code["02"]["title"] == "青森県基本計画「青森新時代」への架け橋"
    assert by_code["05"]["title"] == "秋田県総合計画 ～秋田再興への第一歩～"
    assert by_code["08"]["title"].startswith("第3次茨城県総合計画")
    assert by_code["16"]["title"].startswith("富山県総合計画")
    assert by_code["30"]["title"] == "和歌山県総合計画（2026～2030）"
    assert by_code["32"]["title"] == "第2期島根創生計画"
    assert by_code["42"]["title"] == "長崎県総合計画みんなの未来図2030"


def test_old_or_candidate_plans_are_not_silently_promoted():
    sources = load(COVERAGE_PATH)["plan_sources"]
    superseded_titles = {
        "「未来の東京」戦略",
        "将来ビジョン・大阪",
        "大阪の再生・成長に向けた新戦略",
        "島根創生計画（第1期）",
        "第2期高知県まち・ひと・しごと創生総合戦略",
        "県政運営指針（令和7年改定）",
        "佐賀県総合計画2015",
        "佐賀県行政運営計画（公式掲載入口）",
        "奈良新「都」づくり戦略・政策推進プラン",
    }
    assert all(source["title"] not in superseded_titles for source in sources)


def test_reviewed_codes_and_plan_sources_are_consistent():
    registry = load(COVERAGE_PATH)
    reviewed_codes = set(registry["reviewed_prefecture_codes"])
    reviewed_plan_sources = {
        source["prefecture_code"]
        for source in registry["plan_sources"]
        if source["review_status"] in {"reviewed", "verified"}
    }
    assert reviewed_codes == reviewed_plan_sources == {
        f"{number:02d}" for number in range(1, 48)
    }
