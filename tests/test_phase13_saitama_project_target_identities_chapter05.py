from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH5 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter05.json"
CH1 = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
CH2A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part1.json"
CH2B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part2.json"
CH3 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter03.json"
CH4A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part1.json"
CH4B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part2.json"
IDENTITIES = ROOT / "data/catalog/saitama_current_project_identities_policy_chapters05_08.json"
EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter05_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def observed_target_count(records):
    return sum(len(row["target_names"]) for row in records)


def test_saitama_chapter05_target_identity_review_covers_all_9_projects():
    chapter05_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("05-")
    }
    payload = load(CH5)
    reviewed_ids = {row["project_code"] for row in payload["records"]}

    assert len(chapter05_ids) == 9
    assert payload["project_count"] == len(reviewed_ids) == 9
    assert reviewed_ids == chapter05_ids


def test_saitama_chapter05_has_exactly_17_named_target_identities():
    payload = load(CH5)
    identities = [
        (row["project_code"], target_name)
        for row in payload["records"]
        for target_name in row["target_names"]
    ]

    assert payload["target_indicator_identity_count"] == 17
    assert len(identities) == len(set(identities)) == 17
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter05_measure_partition_reconciles_to_17():
    records = load(CH5)["records"]
    expected = {
        "05-1-1": 7,
        "05-1-2": 4,
        "05-1-3": 2,
        "05-1-4": 4,
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
    assert sum(actual.values()) == 17


def test_saitama_chapter05_remains_identity_only_until_values_are_reviewed():
    payload = load(CH5)
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    assert payload["value_review_status"] == "pending_record_level_value_review"
    assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_77_projects_and_156_targets():
    ch1 = load(CH1)
    ch2 = load(CH2A)["records"] + load(CH2B)["records"]
    ch3 = load(CH3)
    ch4 = load(CH4A)["records"] + load(CH4B)["records"]
    ch5 = load(CH5)

    projects = (
        ch1["project_count"]
        + len(ch2)
        + ch3["project_count"]
        + len(ch4)
        + ch5["project_count"]
    )
    targets = (
        ch1["target_indicator_count"]
        + observed_target_count(ch2)
        + ch3["target_indicator_identity_count"]
        + observed_target_count(ch4)
        + ch5["target_indicator_identity_count"]
    )

    assert projects == 77
    assert targets == 156
    assert 258 - projects == 181
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter05_departments_locators_and_evidence_are_explicit():
    payload = load(CH5)
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in payload["records"])
    assert all(row["source_location"].startswith("PDF p.") for row in payload["records"])
    assert evidence["review_status"] == (
        "reviewed_9_projects_17_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 9
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 17
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
