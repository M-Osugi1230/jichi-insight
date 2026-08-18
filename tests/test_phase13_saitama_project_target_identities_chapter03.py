from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH3 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter03.json"
CH1 = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
CH2_PART1 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part1.json"
CH2_PART2 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part2.json"
IDENTITIES = ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json"
EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter03_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def chapter02_records():
    return load(CH2_PART1)["records"] + load(CH2_PART2)["records"]


def test_saitama_chapter03_target_identity_review_covers_all_12_projects():
    chapter03_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("03-")
    }
    payload = load(CH3)
    reviewed_ids = {row["project_code"] for row in payload["records"]}

    assert len(chapter03_ids) == 12
    assert payload["project_count"] == len(reviewed_ids) == 12
    assert reviewed_ids == chapter03_ids


def test_saitama_chapter03_has_exactly_32_named_target_identities():
    payload = load(CH3)
    names = [
        (row["project_code"], target_name)
        for row in payload["records"]
        for target_name in row["target_names"]
    ]

    assert payload["target_indicator_identity_count"] == 32
    assert len(names) == len(set(names)) == 32
    assert all(target_name.strip() for _, target_name in names)


def test_saitama_chapter03_target_partition_is_13_health_plus_19_sports():
    payload = load(CH3)
    health = [row for row in payload["records"] if row["project_code"].startswith("03-1-")]
    sports = [row for row in payload["records"] if row["project_code"].startswith("03-2-")]

    assert len(health) == 5
    assert len(sports) == 7
    assert sum(len(row["target_names"]) for row in health) == 13
    assert sum(len(row["target_names"]) for row in sports) == 19


def test_saitama_chapter03_remains_identity_depth_until_values_are_reviewed():
    payload = load(CH3)
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    assert payload["value_review_status"] == "pending_record_level_value_review"
    assert all(value_fields.isdisjoint(row) for row in payload["records"])
    assert "identity-only" in payload["quality_boundary"]


def test_saitama_target_identity_progress_reaches_43_projects_and_85_observed_targets():
    ch1 = load(CH1)
    ch2 = chapter02_records()
    ch3 = load(CH3)

    projects = ch1["project_count"] + len(ch2) + ch3["project_count"]
    observed_targets = (
        ch1["target_indicator_count"]
        + sum(len(row["target_names"]) for row in ch2)
        + ch3["target_indicator_identity_count"]
    )

    assert projects == 43
    assert observed_targets == 85
    assert 258 - projects == 215
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter03_responsible_departments_and_evidence_are_explicit():
    payload = load(CH3)
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in payload["records"])
    assert all(row["source_location"].startswith("PDF p.") for row in payload["records"])
    assert evidence["review_status"] == (
        "reviewed_12_projects_32_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 12
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 32
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
