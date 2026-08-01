import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_chubu_depth_reviews.json"
INDEX_PATH = ROOT / "data/catalog/phase10_regional_depth_index.json"
SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_reviews.schema.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"
CORE_PATH = ROOT / "data/catalog/phase10_nationwide_core_linkage.json"

CODES = ["15", "16", "17", "18", "19", "20", "21", "22"]
DIMENSIONS = [
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
]
OFFICIAL_HOSTS = {
    "15": {"www.pref.niigata.lg.jp"},
    "16": {"www.pref.toyama.jp"},
    "17": {"www.pref.ishikawa.lg.jp"},
    "18": {"www.pref.fukui.lg.jp"},
    "19": {"www.pref.yamanashi.jp"},
    "20": {"www.pref.nagano.lg.jp"},
    "21": {"www.pref.gifu.lg.jp"},
    "22": {"www.pref.shizuoka.jp"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chubu_depth_reviews_match_regional_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(load(REVIEWS_PATH))) == []


def test_chubu_has_five_reviewed_official_sources_per_prefecture():
    reviews = load(REVIEWS_PATH)
    assert reviews["batch_id"] == "chubu"
    assert reviews["region"] == "中部"
    assert reviews["prefecture_codes"] == CODES
    assert reviews["dimensions"] == DIMENSIONS
    assert [record["prefecture_code"] for record in reviews["records"]] == CODES

    for record in reviews["records"]:
        code = record["prefecture_code"]
        assert list(record["sources"]) == DIMENSIONS
        for source in record["sources"].values():
            assert urlparse(source["url"]).hostname in OFFICIAL_HOSTS[code]
            assert len(source["claim"]) >= 20
            assert len(source["boundary"]) >= 20
        assert len(record["next_linkage"]) >= 20

    assert reviews["summary"] == {
        "prefecture_count": 8,
        "dimension_count": 5,
        "reviewed_source_count": 40,
        "dimension_reviewed_counts": {dimension: 8 for dimension in DIMENSIONS},
    }
    assert reviews["policy_achievement_assessment_status"] == "not_assessed"


def test_chubu_remains_registered_in_completed_regional_index():
    index = load(INDEX_PATH)
    batches = {batch["slug"]: batch for batch in index["batches"]}

    assert index["status"] == "complete"
    assert list(batches) == [
        "tohoku",
        "kanto",
        "chubu",
        "kinki",
        "chugoku",
        "shikoku",
        "kyushu",
    ]
    assert batches["chubu"]["prefecture_codes"] == CODES
    assert batches["chubu"]["filename"] == REVIEWS_PATH.name
    assert index["reviewed_prefecture_count"] == 38
    assert sum(len(batch["prefecture_codes"]) for batch in index["batches"]) == 38


def test_chubu_reviews_feed_completed_nationwide_linkage():
    completion = load(COMPLETION_PATH)
    core = load(CORE_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts == {
        "reviewed_anchor_prefectures": 9,
        "prefectures_with_five_layers_indexed_or_better": 47,
        "prefectures_with_five_layers_reviewed": 47,
        "annual_actuals_reviewed_or_better": 47,
        "budget_reviewed_or_better": 47,
        "settlement_reviewed_or_better": 47,
        "priority_projects_reviewed_or_better": 47,
        "audit_reviewed_or_better": 47,
        "uniform_depth_complete": 47,
    }
    assert completion["status"] == "complete"

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

    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    assert CORE_PATH.relative_to(ROOT).as_posix() in evidence_paths
