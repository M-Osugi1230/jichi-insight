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
CORE_PATH = CATALOG / "phase10_nationwide_core_linkage.json"

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


def expanded_uniformity():
    uniformity = load(UNIFORMITY_PATH)
    return {
        f"{value:02d}": {
            **uniformity["default_depth"],
            **uniformity["overrides"].get(f"{value:02d}", {}).get(
                "current_depth",
                {},
            ),
        }
        for value in range(1, 48)
    }


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
    records = expanded_uniformity()
    assert len(records) == 47

    for depth in records.values():
        assert {dimension: depth[dimension] for dimension in DIMENSIONS} == {
            dimension: "linked" for dimension in DIMENSIONS
        }


def test_completion_and_core_registry_preserve_all_regional_sources():
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
    assert "document scope" in completion["scope_note"]
    assert "missing stable source is never treated" in completion["scope_note"]

    core_registries = {
        group["source_registry"] for group in core["link_groups"]
    }
    for expected in BATCHES.values():
        assert f"data/catalog/{expected['filename']}" in core_registries

    evidence_paths = {
        path
        for gate in completion["gates"]
        for path in gate["evidence_paths"]
    }
    assert CORE_PATH.relative_to(ROOT).as_posix() in evidence_paths
    assert "tests/test_phase10_nationwide_core_linkage.py" in evidence_paths
