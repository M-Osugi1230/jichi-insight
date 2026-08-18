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
CH9C = CAT / "saitama_current_project_target_identities_chapter09_part3.json"
CH9D = CAT / "saitama_current_project_target_identities_chapter09_part4.json"
IDENTITIES = CAT / "saitama_current_project_identities_policy_chapters09_11.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter09_part2_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records(*paths: Path):
    return [row for path in paths for row in load(path)["records"]]


def target_count(rows):
    return sum(len(row["target_names"]) for row in rows)


def test_saitama_chapter09_part2_covers_exactly_10_projects():
    prefixes = ("09-1-4-", "09-2-1-")
    official = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith(prefixes)
    }
    reviewed = {row["project_code"] for row in records(CH9C, CH9D)}

    assert len(official) == 10
    assert len(reviewed) == 10
    assert reviewed == official


def test_saitama_chapter09_part2_has_exactly_28_target_identities():
    rows = records(CH9C, CH9D)
    identities = [
        (row["project_code"], target_name)
        for row in rows
        for target_name in row["target_names"]
    ]

    assert len(identities) == len(set(identities)) == 28
    assert all(name.strip() for _, name in identities)
    assert load(CH9C)["target_indicator_identity_count"] == 17
    assert load(CH9D)["target_indicator_identity_count"] == 11


def test_saitama_chapter09_part2_partition_reconciles_to_28():
    rows = records(CH9C, CH9D)
    expected = {"09-1-4": 17, "09-2-1": 11}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 28


def test_saitama_chapter09_part2_remains_identity_only():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in (CH9C, CH9D):
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_148_projects_and_322_targets():
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
        CH9C,
        CH9D,
    )
    ch3 = load(CH3)
    ch5 = load(CH5)

    projects = ch1["project_count"] + len(identity_rows)
    projects += ch3["project_count"] + ch5["project_count"]
    targets = ch1["target_indicator_count"] + target_count(identity_rows)
    targets += ch3["target_indicator_identity_count"]
    targets += ch5["target_indicator_identity_count"]

    assert projects == 148
    assert targets == 322
    assert 258 - projects == 110
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter09_part2_evidence_is_explicit():
    rows = records(CH9C, CH9D)
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in rows)
    assert all(row["source_location"].startswith("PDF p.") for row in rows)
    assert evidence["review_status"] == (
        "reviewed_10_projects_28_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 10
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 28
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
