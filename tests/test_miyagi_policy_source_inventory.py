import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data/catalog/miyagi_policy_source_inventory.json"
SCHEMA = ROOT / "schemas/prefecture_policy_source_inventory.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_inventory_matches_reusable_schema():
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(INVENTORY))) == []


def test_inventory_preserves_plan_hierarchy_and_current_periods():
    inventory = load(INVENTORY)
    assert inventory["prefecture_code"] == "04"
    assert inventory["municipality_key"] == "miyagi-prefecture"
    assert inventory["plan_title_original"] == "新・宮城の将来ビジョン"
    assert inventory["plan_period"]["start_fiscal_year"] == 2021
    assert inventory["plan_period"]["end_fiscal_year"] == 2030
    assert inventory["policy_count"] == 8
    assert inventory["measure_count"] == 18
    assert inventory["inventory_status"] == "source_inventory_reviewed"
    assert inventory["next_gate"] == "policy_hierarchy"


def test_sources_are_unique_official_and_internally_linked():
    inventory = load(INVENTORY)
    sources = inventory["sources"]
    ids = [source["id"] for source in sources]
    known_ids = set(ids)

    assert len(sources) == 10
    assert len(ids) == len(known_ids)
    assert all(
        urlparse(source["url"]).netloc == "www.pref.miyagi.jp"
        for source in sources
    )
    assert all(source["review_status"] == "verified" for source in sources)
    assert all(
        set(source["parent_source_ids"]) <= known_ids
        for source in sources
    )
    for relationship in inventory["relationships"]:
        assert relationship["from_source_id"] in known_ids
        assert relationship["to_source_id"] in known_ids


def test_current_implementation_plan_is_the_february_2026_revision():
    inventory = load(INVENTORY)
    sources = {source["id"]: source for source in inventory["sources"]}
    current = sources[inventory["current_implementation_plan_id"]]

    assert current["source_role"] == "implementation_plan"
    assert current["publication_status"] == "current"
    assert current["published_at"] == "2026-02-10"
    assert current["coverage_period"]["start_fiscal_year"] == 2025
    assert current["coverage_period"]["end_fiscal_year"] == 2027
    assert "令和8年2月改定" in current["title_original"]
    assert current["page_count"] == 61


def test_main_plan_and_final_evaluation_pdf_boundaries_are_verified():
    inventory = load(INVENTORY)
    sources = {source["id"]: source for source in inventory["sources"]}
    vision = sources["miyagi-source-vision-pdf"]
    evaluation = sources[inventory["latest_final_evaluation_id"]]

    assert vision["page_count"] == 84
    assert vision["coverage_period"]["start_fiscal_year"] == 2021
    assert vision["coverage_period"]["end_fiscal_year"] == 2030
    assert evaluation["page_count"] == 210
    assert evaluation["publication_status"] == "final"
    assert evaluation["activity_fiscal_year"] == 2024
    assert evaluation["evaluation_fiscal_year"] == 2025
    assert evaluation["published_at"] == "2025-09-18"


def test_draft_evaluation_is_not_promoted_to_final():
    inventory = load(INVENTORY)
    sources = {source["id"]: source for source in inventory["sources"]}
    draft = sources[inventory["latest_draft_evaluation_id"]]
    committee = sources["miyagi-source-evaluation-committee-2026"]

    assert draft["publication_status"] == "draft"
    assert draft["activity_fiscal_year"] == 2025
    assert draft["evaluation_fiscal_year"] == 2026
    assert draft["published_at"] == "2026-06-10"
    assert committee["publication_status"] == "process"
    assert committee["published_at"] == "2026-07-13"
    assert "確定評価ではなく原案" in draft["notes"]
    assert "最終評価結果と混同しない" in committee["notes"]


def test_quality_boundaries_keep_targets_actuals_and_evaluations_separate():
    inventory = load(INVENTORY)
    boundaries = "\n".join(inventory["quality_boundaries"])

    assert "目標値" in boundaries
    assert "年度実績" in boundaries
    assert "自己評価" in boundaries
    assert "行政評価委員会意見" in boundaries
    assert "活動年度" in boundaries
    assert "評価実施年度" in boundaries
    assert "評価原案" in boundaries
    assert "確定評価" in boundaries
    assert "Reviewedへ昇格しない" in boundaries
