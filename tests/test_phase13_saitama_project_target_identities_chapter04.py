from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART1 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part1.json"
PART2 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part2.json"
CH1 = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
CH2A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part1.json"
CH2B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part2.json"
CH3 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter03.json"
IDENTITIES = ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json"
EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter04_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def chapter04_records():
    return load(PART1)["records"] + load(PART2)["records"]


def observed_target_count(records):
    return sum(len(row["target_names"]) for row in records)


def test_saitama_chapter04_target_identity_review_covers_all_25_projects():
    chapter04_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("04-")
    }
    records = chapter04_records()
    reviewed_ids = {row["project_code"] for row in records}

    assert len(chapter04_ids) == 25
    assert len(reviewed_ids) == 25
    assert reviewed_ids == chapter04_ids
    assert load(PART1)["project_count"] == 13
    assert load(PART2)["project_count"] == 12


def test_saitama_chapter04_has_exactly_54_named_target_identities():
    records = chapter04_records()
    identities = [
        (row["project_code"], target_name)
        for row in records
        for target_name in row["target_names"]
    ]

    assert load(PART1)["target_indicator_identity_count"] == 31
    assert load(PART2)["target_indicator_identity_count"] == 23
    assert len(identities) == len(set(identities)) == 54
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter04_submeasure_partition_reconciles_to_54():
    records = chapter04_records()
    expected = {
        "04-1-1": 11,
        "04-1-2": 20,
        "04-1-3": 9,
        "04-1-4": 4,
        "04-1-5": 10,
    }
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in records
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 54


def test_saitama_chapter04_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }
    for payload in (load(PART1), load(PART2)):
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_68_projects_and_139_targets():
    ch1 = load(CH1)
    ch2 = load(CH2A)["records"] + load(CH2B)["records"]
    ch3 = load(CH3)
    ch4 = chapter04_records()

    projects = ch1["project_count"] + len(ch2) + ch3["project_count"] + len(ch4)
    targets = (
        ch1["target_indicator_count"]
        + observed_target_count(ch2)
        + ch3["target_indicator_identity_count"]
        + observed_target_count(ch4)
    )

    assert projects == 68
    assert targets == 139
    assert 258 - projects == 190
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter04_departments_locators_and_evidence_are_explicit():
    records = chapter04_records()
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert evidence["review_status"] == (
        "reviewed_25_projects_54_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 25
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 54
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
