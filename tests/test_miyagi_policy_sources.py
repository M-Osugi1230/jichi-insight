import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/miyagi_policy_sources.json"
SCHEMA = ROOT / "schemas/policy_source_catalog.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_miyagi_policy_sources_match_catalog_schema():
    catalog = load(CATALOG)
    validator = Draft202012Validator(
        load(SCHEMA),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(catalog)) == []
    assert catalog["version"] == "0.1.0"
    assert catalog["updated_at"] == "2026-07-18"
    assert len(catalog["records"]) == 6
    assert len({record["id"] for record in catalog["records"]}) == 6


def test_current_plan_and_implementation_periods_are_separate():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    vision = records["policy-source-miyagi-future-vision-pdf"]
    implementation = records[
        "policy-source-miyagi-midterm-implementation-plan-2026"
    ]

    assert (vision["period_start"], vision["period_end"]) == (2021, 2030)
    assert vision["source_role"] == "strategic_plan"
    assert vision["review_status"] == "reviewed"
    assert (implementation["period_start"], implementation["period_end"]) == (
        2025,
        2027,
    )
    assert implementation["published_at"] == "2026-02-10"
    assert implementation["source_role"] == "implementation_plan"
    assert "kpis" in implementation["extraction_targets"]


def test_final_evaluation_and_draft_are_not_conflated():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    final = records["policy-source-miyagi-results-evaluation-2025"]
    draft = records["policy-source-miyagi-policy-evaluation-draft-2026"]

    assert final["fiscal_year"] == 2024
    assert final["format"] == "pdf"
    assert final["source_role"] == "annual_progress_report"
    assert "確定評価書" in final["notes"]

    assert draft["fiscal_year"] == 2025
    assert draft["format"] == "html"
    assert draft["source_role"] == "project_review"
    assert draft["collection_status"] == "indexed"
    assert draft["review_status"] == "verified"
    assert "評価原案" in draft["title"]
    assert "確定評価ではなく" in draft["notes"]


def test_evaluation_method_and_budget_reflection_have_distinct_roles():
    records = {record["id"]: record for record in load(CATALOG)["records"]}
    method = records["policy-source-miyagi-evaluation-system"]
    reflection = records["policy-source-miyagi-evaluation-reflection-2025"]

    assert method["source_role"] == "progress_management"
    assert method["review_status"] == "reviewed"
    assert "18施策" in method["notes"]
    assert reflection["source_role"] == "progress_management"
    assert reflection["fiscal_year"] == 2025
    assert "budgets" in reflection["extraction_targets"]
    assert "令和8年度当初予算" in reflection["notes"]
