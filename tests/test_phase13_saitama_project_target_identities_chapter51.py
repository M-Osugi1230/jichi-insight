from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
CH51 = [
    CAT / "saitama_current_project_target_identities_chapter51_part1.json",
    CAT / "saitama_current_project_target_identities_chapter51_part2.json",
]
IDENTITIES = CAT / "saitama_current_project_identities_quality_city_management.json"
MANIFEST = CAT / "saitama_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "saitama_current_project_target_identities_chapter51_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records():
    return [row for path in CH51 for row in load(path)["records"]]


def test_saitama_chapter51_target_identity_review_covers_all_12_projects():
    official = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("51-")
    }
    reviewed = {row["project_code"] for row in records()}

    assert len(official) == 12
    assert len(reviewed) == 12
    assert reviewed == official


def test_saitama_chapter51_has_exactly_19_target_identities():
    identities = [
        (row["project_code"], target_name)
        for row in records()
        for target_name in row["target_names"]
    ]
    shard_counts = [load(path)["target_indicator_identity_count"] for path in CH51]

    assert shard_counts == [9, 10]
    assert len(identities) == len(set(identities)) == 19
    assert all(name.strip() for _, name in identities)


def test_saitama_chapter51_scope_partition_reconciles_to_19():
    rows = records()
    expected = {"51-1-1": 9, "51-1-2": 10}
    actual = {
        prefix: sum(
            len(row["target_names"])
            for row in rows
            if row["project_code"].startswith(prefix + "-")
        )
        for prefix in expected
    }

    assert actual == expected
    assert sum(actual.values()) == 19


def test_saitama_chapter51_remains_identity_only_until_values_are_reviewed():
    value_fields = {
        "baseline",
        "annual_targets",
        "final_target_raw",
        "final_target_type",
        "targets",
    }

    for path in CH51:
        payload = load(path)
        assert payload["value_review_status"] == "pending_record_level_value_review"
        assert all(value_fields.isdisjoint(row) for row in payload["records"])


def test_saitama_chapter51_departments_locators_and_evidence_are_explicit():
    evidence = load(EVIDENCE)

    assert all(row["responsible_departments"] for row in records())
    assert all(row["source_location"].startswith("PDF p.") for row in records())
    assert evidence["review_status"] == (
        "reviewed_complete_12_projects_19_target_identities_values_pending"
    )
    assert evidence["chapter_totals"] == {
        "project_count": 12,
        "target_indicator_identity_count": 19,
    }


def test_saitama_manifest_retains_chapter51_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "saitama-current-project-identity-universe"
    )

    assert fact["target_identity_projects_reviewed"] >= 222
    assert fact["target_identity_projects_remaining"] <= 36
    assert fact["observed_target_indicator_identity_count"] >= 470
    assert fact["quality_city_management_target_identity_projects_reviewed"] >= 12
    assert fact["quality_city_management_target_identity_projects_remaining"] <= 36
    assert fact["chapter51_target_identities_values_pending"] == 19
    assert fact["target_value_projects_reviewed"] == 12
    assert fact["reviewed_target_value_record_count"] == 22
