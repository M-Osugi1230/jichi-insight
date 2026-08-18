from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
CH10 = [
    CAT / f"saitama_current_project_target_identities_chapter10_part{i}.json"
    for i in range(1, 4)
]
IDENTITIES = CAT / "saitama_current_project_identities_policy_chapters09_11.json"
MANIFEST = CAT / "saitama_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter10_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [row for path in CH10 for row in load(path)["records"]]


def test_saitama_chapter10_target_identity_review_covers_all_18_projects():
    official = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("10-")
    }
    reviewed = {row["project_code"] for row in records()}

    assert len(official) == 18
    assert len(reviewed) == 18
    assert reviewed == official


def test_saitama_chapter10_has_exactly_41_target_identities():
    identities = [
        (row["project_code"], target_name)
        for row in records()
        for target_name in row["target_names"]
    ]
    shard_counts = [load(path)["target_indicator_identity_count"] for path in CH10]

    assert shard_counts == [12, 12, 17]
    assert len(identities) == len(set(identities)) == 41
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter10_scope_partition_reconciles_to_41():
    rows = records()
    expected = {"10-1-1": 12, "10-1-2": 12, "10-1-3": 17}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 41


def test_saitama_chapter10_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in CH10:
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_chapter10_departments_locators_and_evidence_are_explicit():
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records())
    assert all(row["source_location"].startswith("PDF p.") for row in records())
    assert evidence["review_status"] == (
        "reviewed_complete_18_projects_41_target_identities_values_pending"
    )
    assert evidence["chapter_totals"] == {
        "project_count": 18,
        "target_indicator_identity_count": 41,
    }
    assert sum(row["project_count"] for row in evidence["evidence"]) == 18
    assert sum(row["target_identity_count"] for row in evidence["evidence"]) == 41


def test_saitama_manifest_retains_chapter10_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-project-identity-universe"
    )

    assert fact["target_identity_projects_reviewed"] >= 185
    assert fact["target_identity_projects_remaining"] <= 73
    assert fact["observed_target_indicator_identity_count"] >= 405
    assert fact["chapter10_target_identities_values_pending"] == 41
    assert fact["target_value_projects_reviewed"] == 12
    assert fact["reviewed_target_value_record_count"] == 22
