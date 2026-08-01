import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_anchor_depth_reviews.json"
SCHEMA_PATH = ROOT / "schemas/phase10_anchor_depth_reviews.schema.json"
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"
CORE_PATH = ROOT / "data/catalog/phase10_nationwide_core_linkage.json"

CODES = ["01", "13", "23", "27", "34", "37", "47"]
DIMENSIONS = [
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
]
OFFICIAL_HOSTS = {
    "01": {"www.pref.hokkaido.lg.jp"},
    "13": {
        "www.seisakukikaku.metro.tokyo.lg.jp",
        "www.zaimu.metro.tokyo.lg.jp",
        "www.kansa.metro.tokyo.lg.jp",
    },
    "23": {"www.pref.aichi.jp"},
    "27": {"www.pref.osaka.lg.jp"},
    "34": {"www.pref.hiroshima.lg.jp"},
    "37": {"www.pref.kagawa.lg.jp"},
    "47": {"www.pref.okinawa.lg.jp"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_anchor_depth_reviews_match_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REVIEWS_PATH))) == []


def test_all_seven_anchors_have_five_reviewed_official_sources():
    reviews = load(REVIEWS_PATH)
    records = reviews["records"]

    assert reviews["prefecture_codes"] == CODES
    assert reviews["dimensions"] == DIMENSIONS
    assert [record["prefecture_code"] for record in records] == CODES
    assert len({record["prefecture_code"] for record in records}) == 7

    for record in records:
        code = record["prefecture_code"]
        assert list(record["sources"]) == DIMENSIONS
        for source in record["sources"].values():
            assert urlparse(source["url"]).hostname in OFFICIAL_HOSTS[code]
            assert len(source["claim"]) >= 20
            assert len(source["boundary"]) >= 20
        assert len(record["next_linkage"]) >= 20

    assert reviews["summary"] == {
        "prefecture_count": 7,
        "dimension_count": 5,
        "reviewed_source_count": 35,
        "dimension_reviewed_counts": {dimension: 7 for dimension in DIMENSIONS},
    }
    assert reviews["policy_achievement_assessment_status"] == "not_assessed"


def test_anchor_reviews_are_promoted_by_the_canonical_core_linkage():
    reviews = load(REVIEWS_PATH)
    uniformity = load(UNIFORMITY_PATH)
    core = load(CORE_PATH)

    assert uniformity["overrides"] == {}
    assert all(uniformity["default_depth"][dimension] == "linked" for dimension in DIMENSIONS)

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


def test_anchor_completion_counts_and_canonical_evidence_are_registered():
    completion = load(COMPLETION_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts["reviewed_anchor_prefectures"] == 9
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


def test_anchor_completion_keeps_safety_boundaries():
    uniformity = load(UNIFORMITY_PATH)
    completion = load(COMPLETION_PATH)

    assert uniformity["status"] == "complete"
    assert completion["status"] == "complete"
    assert uniformity["completion_rule"]["allow_partial_complete"] is False
    assert uniformity["policy_achievement_assessment_status"] == "not_assessed"
    assert uniformity["ranking_eligibility"] == (
        "excluded_until_comparability_verified"
    )
    assert all(gate["status"] == "passed" for gate in completion["gates"])
