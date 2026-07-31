import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_reference_depth_reviews.json"
SCHEMA_PATH = ROOT / "schemas/phase10_reference_depth_reviews.schema.json"
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"

DIMENSIONS = {
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "assembly",
    "audit",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_reference_depth_reviews_match_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REVIEWS_PATH))) == []


def test_reference_reviews_are_official_unique_and_conservative():
    reviews = load(REVIEWS_PATH)
    records = reviews["records"]

    assert reviews["prefecture_codes"] == ["04", "40"]
    assert len(records) == len({record["id"] for record in records})
    assert {record["prefecture_code"] for record in records} == {"04", "40"}
    assert {record["dimension"] for record in records} == DIMENSIONS
    assert all(
        record["url"].startswith(
            (
                "https://www.pref.miyagi.jp/",
                "https://www.pref.fukuoka.lg.jp/",
            )
        )
        for record in records
    )
    assert all(record["resulting_depth"] != "linked" for record in records)
    assert all(len(record["boundary"]) >= 20 for record in records)
    assert reviews["policy_achievement_assessment_status"] == "not_assessed"


def test_reference_summary_is_derived_from_records():
    reviews = load(REVIEWS_PATH)
    records = reviews["records"]
    dimension_counts = {
        dimension: len(
            {
                record["prefecture_code"]
                for record in records
                if record["dimension"] == dimension
            }
        )
        for dimension in sorted(DIMENSIONS)
    }
    depth_counts = Counter(record["resulting_depth"] for record in records)

    assert reviews["summary"] == {
        "prefecture_count": 2,
        "record_count": len(records),
        "dimension_prefecture_counts": {
            dimension: dimension_counts[dimension]
            for dimension in (
                "annual_actuals",
                "budget",
                "settlement",
                "priority_projects",
                "assembly",
                "audit",
            )
        },
        "resulting_depth_counts": {
            "indexed": depth_counts["indexed"],
            "reviewed": depth_counts["reviewed"],
            "linked": depth_counts["linked"],
        },
    }


def test_reference_reviews_back_every_promoted_uniformity_dimension():
    reviews = load(REVIEWS_PATH)
    uniformity = load(UNIFORMITY_PATH)
    by_key = {
        (record["prefecture_code"], record["dimension"]): record
        for record in reviews["records"]
    }

    expected = {
        ("04", "budget"): "reviewed",
        ("04", "settlement"): "indexed",
        ("04", "priority_projects"): "reviewed",
        ("04", "assembly"): "indexed",
        ("04", "audit"): "reviewed",
        ("40", "annual_actuals"): "reviewed",
        ("40", "budget"): "reviewed",
        ("40", "settlement"): "reviewed",
        ("40", "priority_projects"): "reviewed",
        ("40", "assembly"): "indexed",
        ("40", "audit"): "reviewed",
    }

    for key, depth in expected.items():
        code, dimension = key
        assert by_key[key]["resulting_depth"] == depth
        assert uniformity["overrides"][code]["current_depth"][dimension] == depth

    assert set(by_key) == set(expected)
