from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
FIELD01 = CAT / "chiba_current_project_identities_field01.json"
FIELD02 = CAT / "chiba_current_project_identities_field02.json"
FIELD03 = CAT / "chiba_current_project_identities_field03.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field03_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field03_has_exactly_18_unique_primary_identities():
    payload = load(FIELD03)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 18
    assert payload["identity_review_status"] == (
        "reviewed_complete_18_of_18_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 18
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field03_measure_partition_reconciles_to_official_18():
    payload = load(FIELD03)
    expected = {
        "3-1-1": 2,
        "3-1-2": 1,
        "3-1-3": 4,
        "3-2-1": 1,
        "3-2-2": 1,
        "3-2-3": 1,
        "3-2-4": 3,
        "3-3-1": 1,
        "3-3-2": 1,
        "3-3-3": 1,
        "3-3-4": 1,
        "3-4-1": 0,
        "3-4-2": 1,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 18


def test_chiba_field03_reposts_reconcile_without_identity_inflation():
    payload = load(FIELD03)
    records = payload["records"]
    reposts = payload["displayed_reposts"]
    cross = [row for row in reposts if row["repost_type"] == "cross_field_repost"]
    same = [row for row in reposts if row["repost_type"] == "same_field_repost"]
    names = {row["project_name"] for row in records}

    assert len(reposts) == 12
    assert len(cross) == 9
    assert len(same) == 3
    assert names.isdisjoint({row["project_name"] for row in cross})
    assert {row["primary_review_id"] for row in same} == {
        "chiba-f03-p004",
        "chiba-f03-p013",
    }
    care_center_name = "あんしんケアセンターの機能強化と介護人材の育成"
    assert sum(row["project_name"] == care_center_name for row in same) == 2


def test_chiba_field03_departments_and_pdf_locations_are_explicit():
    records = load(FIELD03)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field03_evidence_reconciles_cumulative_79_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_18_unique_projects_with_12_repost_occurrences"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 18
    assert evidence["reconciliation"] == {
        "field03_unique_project_count": 18,
        "displayed_same_field_repost_occurrence_count": 3,
        "displayed_cross_field_repost_occurrence_count": 9,
        "displayed_repost_occurrence_count": 12,
        "cumulative_current_project_identities_reviewed": 79,
        "cumulative_current_project_identities_remaining": 110,
        "cumulative_displayed_repost_occurrences_reviewed": 17,
    }


def test_chiba_fields01_to03_primary_identity_sets_are_distinct():
    identity_sets = [
        {row["project_name"] for row in load(path)["records"]}
        for path in (FIELD01, FIELD02, FIELD03)
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18]
    assert identity_sets[0].isdisjoint(identity_sets[1])
    assert identity_sets[0].isdisjoint(identity_sets[2])
    assert identity_sets[1].isdisjoint(identity_sets[2])


def test_chiba_manifest_retains_field03_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert (
        "data/catalog/chiba_current_project_identities_field03.json"
        in manifest["current_project_identity_batch_paths"]
    )
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] >= 79
    assert fact["identity_records_remaining"] <= 110
    assert fact["reviewed_field_counts"]["health_welfare"] == 18
    assert fact["displayed_repost_occurrences_reviewed"] >= 17
