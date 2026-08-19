from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
CH52 = [
    CAT / f"saitama_current_project_target_identities_chapter52_part{i}.json"
    for i in range(1, 7)
]
IDENTITIES = CAT / "saitama_current_project_identities_quality_city_management.json"
MANIFEST = CAT / "saitama_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter52_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [row for path in CH52 for row in load(path)["records"]]


def test_saitama_chapter52_target_identity_review_covers_all_36_projects():
    official = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("52-")
    }
    reviewed = {row["project_code"] for row in records()}

    assert len(official) == 36
    assert len(reviewed) == 36
    assert reviewed == official


def test_saitama_chapter52_has_exactly_61_target_identities():
    identities = [
        (row["project_code"], target_name)
        for row in records()
        for target_name in row["target_names"]
    ]
    shard_counts = [load(path)["target_indicator_identity_count"] for path in CH52]

    assert shard_counts == [7, 20, 9, 14, 6, 5]
    assert len(identities) == len(set(identities)) == 61
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter52_scope_partition_reconciles_to_61():
    rows = records()
    expected = {
        "52-1": 7,
        "52-2": 20,
        "52-3": 9,
        "52-4": 14,
        "52-5": 6,
        "52-6": 5,
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
    assert sum(actual.values()) == 61


def test_saitama_chapter52_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in CH52:
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_chapter52_departments_locators_and_evidence_are_explicit():
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records())
    assert all(row["source_location"].startswith("PDF p.") for row in records())
    assert evidence["review_status"] == (
        "reviewed_complete_36_projects_61_target_identities_values_pending"
    )
    assert evidence["chapter_totals"] == {
        "project_count": 36,
        "target_indicator_identity_count": 61,
    }
    assert evidence["quality_city_management_completion"] == {
        "project_count": 48,
        "target_indicator_identity_count": 80,
        "target_identity_status": "complete",
    }
    assert evidence["all_current_projects_completion"] == {
        "project_count": 258,
        "target_indicator_identity_count": 531,
        "target_identity_status": "complete",
    }


def test_saitama_manifest_closes_current_target_identity_universe_without_value_promotion():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-project-identity-universe"
    )

    assert fact["target_identity_projects_reviewed"] == 258
    assert fact["target_identity_projects_remaining"] == 0
    assert fact["policy_fields_target_identity_projects_reviewed"] == 210
    assert fact["quality_city_management_target_identity_projects_reviewed"] == 48
    assert fact["quality_city_management_target_identity_projects_remaining"] == 0
    assert fact["observed_target_indicator_identity_count"] == 531
    assert fact["total_target_indicator_count"] == 531
    assert fact["total_target_indicator_count_status"] == "reviewed_complete_all_258_projects"
    assert fact["chapter52_target_identities_values_pending"] == 61
    assert fact["target_value_projects_reviewed"] == 12
    assert fact["target_value_projects_remaining"] == 246
    assert fact["reviewed_target_value_record_count"] == 22
