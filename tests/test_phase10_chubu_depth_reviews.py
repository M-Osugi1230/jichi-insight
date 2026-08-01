import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWS_PATH = ROOT / "data/catalog/phase10_chubu_depth_reviews.json"
INDEX_PATH = ROOT / "data/catalog/phase10_regional_depth_index.json"
SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_reviews.schema.json"
UNIFORMITY_PATH = ROOT / "data/catalog/phase10_uniformity.json"
COMPLETION_PATH = ROOT / "data/catalog/phase10_completion.json"

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


def effective_overrides():
    uniformity = load(UNIFORMITY_PATH)
    overrides = dict(uniformity["overrides"])
    index = load(INDEX_PATH)
    for batch in index["batches"]:
        reviews = load(ROOT / "data/catalog" / batch["filename"])
        for record in reviews["records"]:
            current = overrides.get(record["prefecture_code"], {})
            overrides[record["prefecture_code"]] = {
                **current,
                "current_depth": {
                    **current.get("current_depth", {}),
                    **{dimension: "reviewed" for dimension in DIMENSIONS},
                },
            }
    return overrides


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


def test_regional_index_drives_effective_uniform_depth():
    index = load(INDEX_PATH)
    assert [batch["slug"] for batch in index["batches"]] == [
        "tohoku",
        "kanto",
        "chubu",
    ]
    assert index["reviewed_prefecture_count"] == 19
    assert sum(len(batch["prefecture_codes"]) for batch in index["batches"]) == 19

    overrides = effective_overrides()
    for code in CODES:
        for dimension in DIMENSIONS:
            assert overrides[code]["current_depth"][dimension] == "reviewed"

    reviewed_counts = {
        dimension: sum(
            record.get("current_depth", {}).get(dimension) in {"reviewed", "linked"}
            for record in overrides.values()
        )
        for dimension in DIMENSIONS
    }
    assert reviewed_counts == {
        "annual_actuals": 28,
        "budget": 28,
        "settlement": 27,
        "priority_projects": 28,
        "audit": 28,
    }


def test_chubu_updates_completion_without_claiming_linkage():
    reviews = load(REVIEWS_PATH)
    completion = load(COMPLETION_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts["prefectures_with_five_layers_indexed_or_better"] == 28
    assert counts["prefectures_with_five_layers_reviewed"] == 27
    assert counts["annual_actuals_reviewed_or_better"] == 28
    assert counts["budget_reviewed_or_better"] == 28
    assert counts["settlement_reviewed_or_better"] == 27
    assert counts["priority_projects_reviewed_or_better"] == 28
    assert counts["audit_reviewed_or_better"] == 28
    assert counts["uniform_depth_complete"] == 0
    assert completion["status"] == "in_progress"

    assert all(
        "linked" not in source["boundary"].lower()
        for record in reviews["records"]
        for source in record["sources"].values()
    )
    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    assert REVIEWS_PATH.relative_to(ROOT).as_posix() in evidence_paths
    assert INDEX_PATH.relative_to(ROOT).as_posix() in evidence_paths
