from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
CH11 = [
    CAT / f"saitama_current_project_target_identities_chapter11_part{i}.json"
    for i in range(1, 5)
]
IDENTITIES = CAT / "saitama_current_project_identities_policy_chapters09_11.json"
MANIFEST = CAT / "saitama_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter11_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [row for path in CH11 for row in load(path)["records"]]


def test_saitama_chapter11_target_identity_review_covers_all_25_projects():
    official = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("11-")
    }
    reviewed = {row["project_code"] for row in records()}

    assert len(official) == 25
    assert len(reviewed) == 25
    assert reviewed == official


def test_saitama_chapter11_has_exactly_46_target_identities():
    identities = [
        (row["project_code"], target_name)
        for row in records()
        for target_name in row["target_names"]
    ]
    shard_counts = [load(path)["target_indicator_identity_count"] for path in CH11]

    assert shard_counts == [15, 17, 4, 10]
    assert len(identities) == len(set(identities)) == 46
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter11_scope_partition_reconciles_to_46():
    rows = records()
    expected = {
        "11-1-1": 6,
        "11-1-2": 9,
        "11-1-3": 5,
        "11-1-4": 7,
        "11-1-5": 5,
        "11-2-1": 4,
        "11-3-1": 10,
    }
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 46


def test_saitama_chapter11_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in CH11:
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_chapter11_departments_locators_and_evidence_are_explicit():
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records())
    assert all(row["source_location"].startswith("PDF p.") for row in records())
    assert evidence["review_status"] == (
        "reviewed_complete_25_projects_46_target_identities_values_pending"
    )
    assert evidence["chapter_totals"] == {
        "project_count": 25,
        "target_indicator_identity_count": 46,
    }
    assert evidence["policy_fields_completion"] == {
        "project_count": 210,
        "target_identity_status": "complete",
    }


def test_saitama_manifest_reaches_policy_fields_target_identity_completion():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-project-identity-universe"
    )

    assert fact["target_identity_projects_reviewed"] == 210
    assert fact["target_identity_projects_remaining"] == 48
    assert fact["observed_target_indicator_identity_count"] == 451
    assert fact["policy_fields_target_identity_projects_reviewed"] == 210
    assert fact["policy_fields_target_identity_projects_remaining"] == 0
    assert fact["chapter11_target_identities_values_pending"] == 46
    assert fact["target_value_projects_reviewed"] == 12
    assert fact["reviewed_target_value_record_count"] == 22
