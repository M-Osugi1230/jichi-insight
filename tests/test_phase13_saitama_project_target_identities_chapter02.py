from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART1 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part1.json"
PART2 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part2.json"
CH1 = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
IDENTITIES = ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json"
EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter02_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def chapter02_records():
    return load(PART1)["records"] + load(PART2)["records"]


def test_saitama_chapter02_target_identity_review_covers_all_19_projects():
    chapter02_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("02-")
    }
    reviewed_ids = {row["project_code"] for row in chapter02_records()}

    assert len(chapter02_ids) == 19
    assert reviewed_ids == chapter02_ids
    assert load(PART1)["project_count"] == 10
    assert load(PART2)["project_count"] == 9


def test_saitama_chapter02_has_exactly_31_named_target_identities():
    records = chapter02_records()
    names = [
        (row["project_code"], target_name)
        for row in records
        for target_name in row["target_names"]
    ]

    assert load(PART1)["target_indicator_identity_count"] == 14
    assert load(PART2)["target_indicator_identity_count"] == 17
    assert len(names) == len(set(names)) == 31
    assert all(target_name.strip() for _, target_name in names)


def test_saitama_chapter02_remains_identity_depth_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }
    for payload in (load(PART1), load(PART2)):
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert "full value review" in payload["quality_boundary"]
        assert all(
            value_fields.isdisjoint(row)
            for row in payload["records"]
        )


def test_saitama_chapter02_responsible_departments_and_locators_are_explicit():
    records = chapter02_records()

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["target_names"] for row in records)


def test_saitama_target_identity_progress_is_31_projects_and_53_observed_targets():
    chapter01 = load(CH1)
    chapter02 = chapter02_records()

    chapter01_projects = chapter01["project_count"]
    chapter02_projects = len(chapter02)
    chapter02_targets = sum(len(row["target_names"]) for row in chapter02)

    assert chapter01_projects + chapter02_projects == 31
    assert chapter01["target_indicator_count"] + chapter02_targets == 53
    assert 258 - (chapter01_projects + chapter02_projects) == 227
    assert 258 - chapter01_projects == 246


def test_saitama_chapter02_evidence_reconciles_four_environment_scopes():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_19_projects_31_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 19
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 31
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
    assert "数値へ補完しない" in evidence["quality_boundary"]
