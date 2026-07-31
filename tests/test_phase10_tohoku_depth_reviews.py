import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_tohoku_depth_reviews.json"
SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_reviews.schema.json"
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"

CODES = ["02", "03", "05", "06", "07"]
DIMENSIONS = [
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
]
OFFICIAL_HOSTS = {
    "02": {"www.pref.aomori.lg.jp"},
    "03": {"www.pref.iwate.jp"},
    "05": {"www.pref.akita.lg.jp"},
    "06": {"www.pref.yamagata.jp"},
    "07": {"www.pref.fukushima.lg.jp"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_tohoku_depth_reviews_match_regional_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REVIEWS_PATH))) == []


def test_tohoku_has_five_reviewed_sources_per_prefecture():
    reviews = load(REVIEWS_PATH)
    records = reviews["records"]

    assert reviews["batch_id"] == "tohoku"
    assert reviews["region"] == "東北"
    assert reviews["prefecture_codes"] == CODES
    assert reviews["dimensions"] == DIMENSIONS
    assert [record["prefecture_code"] for record in records] == CODES

    for record in records:
        code = record["prefecture_code"]
        assert record["region"] == "東北"
        assert list(record["sources"]) == DIMENSIONS
        for source in record["sources"].values():
            assert urlparse(source["url"]).hostname in OFFICIAL_HOSTS[code]
            assert len(source["claim"]) >= 20
            assert len(source["boundary"]) >= 20
        assert len(record["next_linkage"]) >= 20

    assert reviews["summary"] == {
        "prefecture_count": 5,
        "dimension_count": 5,
        "reviewed_source_count": 25,
        "dimension_reviewed_counts": {dimension: 5 for dimension in DIMENSIONS},
    }
    assert reviews["policy_achievement_assessment_status"] == "not_assessed"
    assert reviews["ranking_eligibility"] == (
        "excluded_until_comparability_verified"
    )


def test_tohoku_review_promotes_only_reviewed_depth():
    reviews = load(REVIEWS_PATH)
    uniformity = load(UNIFORMITY_PATH)

    for record in reviews["records"]:
        override = uniformity["overrides"][record["prefecture_code"]]
        assert override["status"] == "linkage_in_progress"
        assert override["next_gate"] == "annual_actuals_linkage"
        assert override["next_action"] == record["next_linkage"]
        for dimension in DIMENSIONS:
            assert override["current_depth"][dimension] == "reviewed"
        assert "linked" not in {
            override["current_depth"][dimension] for dimension in DIMENSIONS
        }


def test_tohoku_review_updates_nationwide_counts_without_completion():
    completion = load(COMPLETION_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts["prefectures_with_five_layers_indexed_or_better"] == 14
    assert counts["prefectures_with_five_layers_reviewed"] == 13
    assert counts["annual_actuals_reviewed_or_better"] == 14
    assert counts["budget_reviewed_or_better"] == 14
    assert counts["settlement_reviewed_or_better"] == 13
    assert counts["priority_projects_reviewed_or_better"] == 14
    assert counts["audit_reviewed_or_better"] == 14
    assert counts["uniform_depth_complete"] == 0
    assert completion["status"] == "in_progress"

    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    assert REVIEWS_PATH.relative_to(ROOT).as_posix() in evidence_paths
    assert SCHEMA_PATH.relative_to(ROOT).as_posix() in evidence_paths
    assert (
        Path("tests/test_phase10_tohoku_depth_reviews.py").as_posix()
        in evidence_paths
    )
