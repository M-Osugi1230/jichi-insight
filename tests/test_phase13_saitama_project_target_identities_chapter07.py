from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
CH1 = CAT / "saitama_current_project_targets_chapter01.json"
CH2A = CAT / "saitama_current_project_target_identities_chapter02_part1.json"
CH2B = CAT / "saitama_current_project_target_identities_chapter02_part2.json"
CH3 = CAT / "saitama_current_project_target_identities_chapter03.json"
CH4A = CAT / "saitama_current_project_target_identities_chapter04_part1.json"
CH4B = CAT / "saitama_current_project_target_identities_chapter04_part2.json"
CH5 = CAT / "saitama_current_project_target_identities_chapter05.json"
CH6A = CAT / "saitama_current_project_target_identities_chapter06_part1.json"
CH6B = CAT / "saitama_current_project_target_identities_chapter06_part2.json"
CH6C = CAT / "saitama_current_project_target_identities_chapter06_part3.json"
CH7A = CAT / "saitama_current_project_target_identities_chapter07_part1.json"
CH7B = CAT / "saitama_current_project_target_identities_chapter07_part2.json"
CH7C = CAT / "saitama_current_project_target_identities_chapter07_part3.json"
IDENTITIES = CAT / "saitama_current_project_identities_policy_chapters05_08.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter07_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records(*paths: Path):
    return [row for path in paths for row in load(path)["records"]]


def target_count(rows):
    return sum(len(row["target_names"]) for row in rows)


def test_saitama_chapter07_target_identity_review_covers_all_17_projects():
    official_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("07-")
    }
    reviewed = {row["project_code"] for row in records(CH7A, CH7B, CH7C)}

    assert len(official_ids) == 17
    assert len(reviewed) == 17
    assert reviewed == official_ids


def test_saitama_chapter07_has_exactly_35_named_target_identities():
    rows = records(CH7A, CH7B, CH7C)
    identities = [
        (row["project_code"], target_name)
        for row in rows
        for target_name in row["target_names"]
    ]
    shard_counts = [
        load(path)["target_indicator_identity_count"]
        for path in (CH7A, CH7B, CH7C)
    ]

    assert len(identities) == len(set(identities)) == 35
    assert all(name.strip() for _, name in identities)
    assert shard_counts == [6, 16, 13]


def test_saitama_chapter07_measure_partition_reconciles_to_35():
    rows = records(CH7A, CH7B, CH7C)
    expected = {"07-1-1": 6, "07-1-2": 16, "07-1-3": 13}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 35


def test_saitama_chapter07_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in (CH7A, CH7B, CH7C):
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_116_projects_and_240_targets():
    ch1 = load(CH1)
    identity_rows = records(
        CH2A,
        CH2B,
        CH4A,
        CH4B,
        CH6A,
        CH6B,
        CH6C,
        CH7A,
        CH7B,
        CH7C,
    )
    ch3 = load(CH3)
    ch5 = load(CH5)

    projects = ch1["project_count"] + len(identity_rows)
    projects += ch3["project_count"] + ch5["project_count"]
    targets = ch1["target_indicator_count"] + target_count(identity_rows)
    targets += ch3["target_indicator_identity_count"]
    targets += ch5["target_indicator_identity_count"]

    assert projects == 116
    assert targets == 240
    assert 258 - projects == 142
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter07_departments_locators_and_evidence_are_explicit():
    rows = records(CH7A, CH7B, CH7C)
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in rows)
    assert all(row["source_location"].startswith("PDF p.") for row in rows)
    assert evidence["review_status"] == (
        "reviewed_17_projects_35_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 17
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 35
    assert evidence["visual_verification"]["decision"] == "accepted"
