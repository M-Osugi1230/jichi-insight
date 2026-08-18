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
CH8 = CAT / "saitama_current_project_target_identities_chapter08.json"
CH9A = CAT / "saitama_current_project_target_identities_chapter09_part1.json"
CH9B = CAT / "saitama_current_project_target_identities_chapter09_part2.json"
IDENTITIES = CAT / "saitama_current_project_identities_policy_chapters09_11.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter09_part1_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records(*paths: Path):
    return [row for path in paths for row in load(path)["records"]]


def target_count(rows):
    return sum(len(row["target_names"]) for row in rows)


def test_saitama_chapter09_part1_covers_exactly_first_15_projects():
    official = [
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith(("09-1-1-", "09-1-2-", "09-1-3-"))
    ]
    reviewed = [row["project_code"] for row in records(CH9A, CH9B)]

    assert len(official) == 15
    assert len(reviewed) == len(set(reviewed)) == 15
    assert set(reviewed) == set(official)


def test_saitama_chapter09_part1_has_exactly_36_target_identities():
    rows = records(CH9A, CH9B)
    identities = [
        (row["project_code"], target_name)
        for row in rows
        for target_name in row["target_names"]
    ]

    assert len(identities) == len(set(identities)) == 36
    assert all(name.strip() for _, name in identities)
    assert load(CH9A)["target_indicator_identity_count"] == 26
    assert load(CH9B)["target_indicator_identity_count"] == 10


def test_saitama_chapter09_part1_measure_partition_reconciles_to_36():
    rows = records(CH9A, CH9B)
    expected = {"09-1-1": 16, "09-1-2": 10, "09-1-3": 10}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 36


def test_saitama_chapter09_part1_remains_identity_only():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in (CH9A, CH9B):
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_138_projects_and_294_targets():
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
        CH8,
        CH9A,
        CH9B,
    )
    ch3 = load(CH3)
    ch5 = load(CH5)

    projects = ch1["project_count"] + len(identity_rows)
    projects += ch3["project_count"] + ch5["project_count"]
    targets = ch1["target_indicator_count"] + target_count(identity_rows)
    targets += ch3["target_indicator_identity_count"]
    targets += ch5["target_indicator_identity_count"]

    assert projects == 138
    assert targets == 294
    assert 258 - projects == 120
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter09_part1_evidence_is_explicit():
    rows = records(CH9A, CH9B)
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in rows)
    assert all(row["source_location"].startswith("PDF p.") for row in rows)
    assert evidence["review_status"] == (
        "reviewed_15_projects_36_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 15
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 36
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
