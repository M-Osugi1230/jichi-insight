import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
REGIONAL_SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_reviews.schema.json"
INDEX_SCHEMA_PATH = ROOT / "schemas/phase10_regional_depth_index.schema.json"
INDEX_PATH = CATALOG / "phase10_regional_depth_index.json"
UNIFORMITY_PATH = CATALOG / "phase10_uniformity.json"
COMPLETION_PATH = CATALOG / "phase10_completion.json"

BATCHES = {
    "kinki": {
        "filename": "phase10_kinki_depth_reviews.json",
        "codes": ["24", "25", "26", "28", "29", "30"],
        "source_count": 30,
    },
    "chugoku": {
        "filename": "phase10_chugoku_depth_reviews.json",
        "codes": ["31", "32", "33", "35"],
        "source_count": 20,
    },
    "shikoku": {
        "filename": "phase10_shikoku_depth_reviews.json",
        "codes": ["36", "38", "39"],
        "source_count": 15,
    },
    "kyushu": {
        "filename": "phase10_kyushu_depth_reviews.json",
        "codes": ["41", "42", "43", "44", "45", "46"],
        "source_count": 30,
    },
}
DIMENSIONS = [
    "annual_actuals",
    "budget",
    "settlement",
    "priority_projects",
    "audit",
]
OFFICIAL_HOSTS = {
    "24": {"www.pref.mie.lg.jp"},
    "25": {"www.pref.shiga.lg.jp"},
    "26": {"www.pref.kyoto.jp"},
    "28": {"web.pref.hyogo.lg.jp"},
    "29": {"www.pref.nara.jp"},
    "30": {"www.pref.wakayama.lg.jp"},
    "31": {"www.pref.tottori.lg.jp"},
    "32": {"www.pref.shimane.lg.jp"},
    "33": {"www.pref.okayama.jp"},
    "35": {"www.pref.yamaguchi.lg.jp"},
    "36": {"www.pref.tokushima.lg.jp"},
    "38": {"www.pref.ehime.jp"},
    "39": {"www.pref.kochi.lg.jp"},
    "41": {"www.pref.saga.lg.jp"},
    "42": {"www.pref.nagasaki.jp"},
    "43": {"www.pref.kumamoto.jp"},
    "44": {"www.pref.oita.jp"},
    "45": {"www.pref.miyazaki.lg.jp"},
    "46": {"www.pref.kagoshima.jp"},
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def effective_overrides():
    uniformity = load(UNIFORMITY_PATH)
    overrides = dict(uniformity["overrides"])
    for batch in load(INDEX_PATH)["batches"]:
        reviews = load(CATALOG / batch["filename"])
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


def test_completed_regional_index_matches_schema_and_covers_38_prefectures():
    validator = Draft202012Validator(
        load(INDEX_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    index = load(INDEX_PATH)
    assert list(validator.iter_errors(index)) == []
    assert index["status"] == "complete"
    assert [batch["slug"] for batch in index["batches"]] == [
        "tohoku",
        "kanto",
        "chubu",
        "kinki",
        "chugoku",
        "shikoku",
        "kyushu",
    ]
    all_codes = [
        code
        for batch in index["batches"]
        for code in batch["prefecture_codes"]
    ]
    assert len(all_codes) == len(set(all_codes)) == 38
    assert index["reviewed_prefecture_count"] == 38


def test_remaining_four_batches_match_schema_and_official_hosts():
    validator = Draft202012Validator(
        load(REGIONAL_SCHEMA_PATH),
        format_checker=FormatChecker(),
    )
    total_sources = 0

    for slug, expected in BATCHES.items():
        reviews = load(CATALOG / expected["filename"])
        assert list(validator.iter_errors(reviews)) == []
        assert reviews["batch_id"] == slug
        assert reviews["prefecture_codes"] == expected["codes"]
        assert reviews["dimensions"] == DIMENSIONS
        assert reviews["summary"]["reviewed_source_count"] == expected[
            "source_count"
        ]
        total_sources += reviews["summary"]["reviewed_source_count"]

        for record in reviews["records"]:
            code = record["prefecture_code"]
            assert list(record["sources"]) == DIMENSIONS
            for source in record["sources"].values():
                assert urlparse(source["url"]).hostname in OFFICIAL_HOSTS[code]
                assert len(source["claim"]) >= 20
                assert len(source["boundary"]) >= 20
            assert len(record["next_linkage"]) >= 20

    assert total_sources == 95


def test_effective_five_layer_coverage_reaches_all_prefectures():
    overrides = effective_overrides()
    assert len(overrides) == 47

    reviewed_counts = {
        dimension: sum(
            record.get("current_depth", {}).get(dimension)
            in {"reviewed", "linked"}
            for record in overrides.values()
        )
        for dimension in DIMENSIONS
    }
    indexed_or_better = sum(
        all(
            record.get("current_depth", {}).get(dimension)
            in {"indexed", "reviewed", "linked"}
            for dimension in DIMENSIONS
        )
        for record in overrides.values()
    )
    fully_reviewed = sum(
        all(
            record.get("current_depth", {}).get(dimension)
            in {"reviewed", "linked"}
            for dimension in DIMENSIONS
        )
        for record in overrides.values()
    )

    assert indexed_or_better == 47
    assert fully_reviewed == 46
    assert reviewed_counts == {
        "annual_actuals": 47,
        "budget": 47,
        "settlement": 46,
        "priority_projects": 47,
        "audit": 47,
    }


def test_completion_records_source_review_without_false_phase_completion():
    completion = load(COMPLETION_PATH)
    counts = completion["nationwide_uniform_counts"]

    assert counts == {
        "reviewed_anchor_prefectures": 9,
        "prefectures_with_five_layers_indexed_or_better": 47,
        "prefectures_with_five_layers_reviewed": 46,
        "annual_actuals_reviewed_or_better": 47,
        "budget_reviewed_or_better": 47,
        "settlement_reviewed_or_better": 46,
        "priority_projects_reviewed_or_better": 47,
        "audit_reviewed_or_better": 47,
        "uniform_depth_complete": 0,
    }
    assert completion["status"] == "in_progress"
    assert "one-to-one target linkage are not complete" in completion["scope_note"]

    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    for expected in BATCHES.values():
        assert f"data/catalog/{expected['filename']}" in evidence_paths
    assert "schemas/phase10_regional_depth_index.schema.json" in evidence_paths
    assert "tests/test_phase10_remaining_regional_depth_reviews.py" in (
        evidence_paths
    )
