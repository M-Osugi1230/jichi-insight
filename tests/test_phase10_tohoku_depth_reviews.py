import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_tohoku_depth_reviews.json"
SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_reviews.schema.json"
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"
CORE_PATH = ROOT / "data/catalog/phase10_nationwide_core_linkage.json"

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


def test_tohoku_reviews_are_promoted_by_the_canonical_core_linkage():
    reviews = load(REVIEWS_PATH)
    uniformity = load(UNIFORMITY_PATH)
    core = load(CORE_PATH)

    assert uniformity["overrides"] == {}
    assert all(
        uniformity["default_depth"][dimension] == "linked"
        for dimension in DIMENSIONS
    )
    groups = [
        group
        for group in core["link_groups"]
        if group["source_registry"]
        == REVIEWS_PATH.relative_to(ROOT).as_posix()
    ]
    assert len(groups) == 1
    assert groups[0]["prefecture_codes"] == CODES
    assert groups[0]["dimensions"] == DIMENSIONS
    assert groups[0]["linkage_level"] == "document_scope"
    assert reviews["records"]


def test_tohoku_review_remains_registered_after_completion():
    completion = load(COMPLETION_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts["prefectures_with_five_layers_indexed_or_better"] == 47
    assert counts["prefectures_with_five_layers_reviewed"] == 47
    assert counts["uniform_depth_complete"] == 47
    assert completion["status"] == "complete"

    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    assert CORE_PATH.relative_to(ROOT).as_posix() in evidence_paths
    assert "tests/test_phase10_nationwide_core_linkage.py" in evidence_paths
