from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIVERSE = ROOT / "data/catalog/saitama_current_project_universe_registry.json"
IDENTITY_PATHS = [
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json",
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters05_08.json",
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters09_11.json",
    ROOT / "data/catalog/saitama_current_project_identities_quality_city_management.json",
]
EVIDENCE = ROOT / "data/evidence/saitama_current_project_universe_evidence.json"
SOURCES = ROOT / "data/catalog/saitama_phase13_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def all_records():
    return [record for path in IDENTITY_PATHS for record in load(path)["records"]]


def test_saitama_current_project_universe_is_exactly_258_unique_codes():
    universe = load(UNIVERSE)
    records = all_records()
    codes = [record["project_code"] for record in records]

    assert universe["status"] == "project_identity_review_complete_258_of_258"
    assert universe["project_universe"]["current_project_code_count"] == 258
    assert universe["project_universe"]["identity_records_reviewed"] == 258
    assert universe["project_universe"]["identity_records_remaining"] == 0
    assert len(records) == len(codes) == len(set(codes)) == 258
    assert all(record["review_status"] == "reviewed_identity" for record in records)


def test_saitama_current_project_identity_files_reconcile_210_plus_48():
    universe = load(UNIVERSE)
    policy = [record for record in all_records() if record["project_code"][:2].isdigit() and int(record["project_code"][:2]) <= 11]
    management = [record for record in all_records() if record["project_code"].startswith(("51-", "52-"))]

    assert len(policy) == universe["project_universe"]["policy_fields_project_count"] == 210
    assert len(management) == universe["project_universe"]["quality_city_management_project_count"] == 48
    assert len(policy) + len(management) == 258


def test_saitama_policy_chapter_counts_match_official_index_partition():
    universe = load(UNIVERSE)
    expected = {
        row["chapter_code"]: row["project_count"]
        for row in universe["policy_fields_chapter_counts"]
    }
    actual = Counter(
        record["project_code"][:2]
        for record in all_records()
        if record["project_code"][:2] in expected
    )

    assert dict(actual) == expected
    assert sum(expected.values()) == 210


def test_saitama_quality_management_chapter_counts_match_official_index_partition():
    universe = load(UNIVERSE)
    expected = {
        row["chapter_code"]: row["project_count"]
        for row in universe["quality_city_management_counts"]
    }
    actual = Counter(
        record["project_code"][:2]
        for record in all_records()
        if record["project_code"][:2] in expected
    )

    assert dict(actual) == expected == {"51": 12, "52": 36}


def test_saitama_current_project_codes_have_expected_shape_and_nonempty_names():
    records = all_records()
    assert all(len(record["project_code"].split("-")) == 4 for record in records)
    assert all(part.isdigit() for record in records for part in record["project_code"].split("-"))
    assert all(record["project_name"].strip() for record in records)
    assert all(isinstance(record["plan_page"], int) and record["plan_page"] > 0 for record in records)


def test_saitama_current_project_universe_stays_separate_from_old_progress_universe():
    universe = load(UNIVERSE)
    historical = universe["historical_boundary"]

    assert historical["old_cycle_displayed_project_occurrences"] == 370
    assert historical["old_cycle_unique_projects"] == 299
    assert historical["current_plan_project_codes"] == 258
    assert historical["linkage_status"] == "not_reviewed"
    assert "同一視しない" in historical["rule"]
    assert "名称一致だけで" in historical["rule"]


def test_saitama_project_universe_evidence_and_sources_are_official_and_bounded():
    evidence = load(EVIDENCE)
    source_map = {row["id"]: row for row in load(SOURCES)["records"]}

    assert len(evidence["evidence"]) == 3
    assert evidence["review_status"] == (
        "reviewed_structural_universe_and_quality_management_identities"
    )
    for source_id in (
        "saitama-implementation-plan-2026-2030-policy-projects",
        "saitama-implementation-plan-2026-2030-quality-management-projects",
    ):
        assert source_id in source_map
        assert source_map[source_id]["url"].startswith("https://www.city.saitama.lg.jp/")
        assert source_map[source_id]["confidence"] == "high"
