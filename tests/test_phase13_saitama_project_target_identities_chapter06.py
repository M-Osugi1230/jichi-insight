from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH1 = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
CH2A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part1.json"
CH2B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter02_part2.json"
CH3 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter03.json"
CH4A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part1.json"
CH4B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter04_part2.json"
CH5 = ROOT / "data/catalog/saitama_current_project_target_identities_chapter05.json"
CH6A = ROOT / "data/catalog/saitama_current_project_target_identities_chapter06_part1.json"
CH6B = ROOT / "data/catalog/saitama_current_project_target_identities_chapter06_part2.json"
CH6C = ROOT / "data/catalog/saitama_current_project_target_identities_chapter06_part3.json"
IDENTITIES = ROOT / "data/catalog/saitama_current_project_identities_policy_chapters05_08.json"
EVIDENCE = ROOT / "data/evidence/saitama_current_project_target_identities_chapter06_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def observed_target_count(records):
    return sum(len(row["target_names"]) for row in records)


def chapter06_records():
    return load(CH6A)["records"] + load(CH6B)["records"] + load(CH6C)["records"]


def test_saitama_chapter06_target_identity_review_covers_all_22_projects():
    chapter06_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("06-")
    }
    reviewed_ids = {row["project_code"] for row in chapter06_records()}

    assert len(chapter06_ids) == 22
    assert len(reviewed_ids) == 22
    assert reviewed_ids == chapter06_ids


def test_saitama_chapter06_has_exactly_49_named_target_identities():
    identities = [
        (row["project_code"], target_name)
        for row in chapter06_records()
        for target_name in row["target_names"]
    ]

    assert len(identities) == len(set(identities)) == 49
    assert all(name.strip() for _, name in identities)
    shard_counts = [
        load(path)["target_indicator_identity_count"]
        for path in (CH6A, CH6B, CH6C)
    ]
    assert shard_counts == [16, 17, 16]


def test_saitama_chapter06_measure_partition_reconciles_to_49():
    records = chapter06_records()
    expected = {"06-1-1": 16, "06-2-1": 17, "06-2-2": 13, "06-3-1": 3}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in records
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 49


def test_saitama_chapter06_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in (CH6A, CH6B, CH6C):
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_target_identity_progress_reaches_99_projects_and_205_targets():
    ch1 = load(CH1)
    ch2 = load(CH2A)["records"] + load(CH2B)["records"]
    ch3 = load(CH3)
    ch4 = load(CH4A)["records"] + load(CH4B)["records"]
    ch5 = load(CH5)
    ch6 = chapter06_records()

    projects = (
        ch1["project_count"]
        + len(ch2)
        + ch3["project_count"]
        + len(ch4)
        + ch5["project_count"]
        + len(ch6)
    )
    targets = (
        ch1["target_indicator_count"]
        + observed_target_count(ch2)
        + ch3["target_indicator_identity_count"]
        + observed_target_count(ch4)
        + ch5["target_indicator_identity_count"]
        + observed_target_count(ch6)
    )

    assert projects == 99
    assert targets == 205
    assert 258 - projects == 159
    assert 258 - ch1["project_count"] == 246


def test_saitama_chapter06_departments_locators_and_evidence_are_explicit():
    records = chapter06_records()
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert evidence["review_status"] == (
        "reviewed_22_projects_49_target_identities_values_pending"
    )
    assert sum(row["project_count"] for row in evidence["evidence"]) == 22
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 49
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])
