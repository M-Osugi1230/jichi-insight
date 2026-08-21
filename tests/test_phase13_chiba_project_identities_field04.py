from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
FIELD01 = CAT / "chiba_current_project_identities_field01.json"
FIELD02 = CAT / "chiba_current_project_identities_field02.json"
FIELD03 = CAT / "chiba_current_project_identities_field03.json"
FIELD04 = CAT / "chiba_current_project_identities_field04.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field04_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field04_has_exactly_34_unique_primary_identities():
    payload = load(FIELD04)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 34
    assert payload["identity_review_status"] == (
        "reviewed_complete_34_of_34_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 34
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field04_measure_partition_reconciles_to_official_34():
    payload = load(FIELD04)
    expected = {
        "4-1-1": 3,
        "4-1-2": 10,
        "4-1-3": 2,
        "4-1-4": 2,
        "4-1-5": 0,
        "4-2-1": 2,
        "4-2-2": 6,
        "4-2-3": 4,
        "4-2-4": 4,
        "4-2-5": 1,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 34
    assert sum(actual[code] for code in expected if code.startswith("4-1-")) == 17
    assert sum(actual[code] for code in expected if code.startswith("4-2-")) == 17


def test_chiba_field04_reposts_reconcile_without_identity_inflation():
    payload = load(FIELD04)
    records = payload["records"]
    reposts = payload["displayed_reposts"]
    cross = [row for row in reposts if row["repost_type"] == "cross_field_repost"]
    same = [row for row in reposts if row["repost_type"] == "same_field_repost"]
    names = {row["project_name"] for row in records}

    assert len(reposts) == 10
    assert len(same) == 8
    assert len(cross) == 2
    assert {row["project_name"] for row in cross} == {
        "発達障害支援の推進",
        "アントレプレナーシップ教育の推進",
    }
    assert names.isdisjoint({row["project_name"] for row in cross})
    assert {row["primary_field_code"] for row in cross} == {"3", "8"}
    assert {row["primary_review_id"] for row in same} <= {
        row["review_id"] for row in records
    }


def test_chiba_field04_departments_and_pdf_locations_are_explicit():
    records = load(FIELD04)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field04_evidence_reconciles_cumulative_113_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_34_unique_projects_with_10_repost_occurrences"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 34
    assert evidence["reconciliation"] == {
        "field04_unique_project_count": 34,
        "displayed_same_field_repost_occurrence_count": 8,
        "displayed_cross_field_repost_occurrence_count": 2,
        "displayed_repost_occurrence_count": 10,
        "cumulative_current_project_identities_reviewed": 113,
        "cumulative_current_project_identities_remaining": 76,
        "cumulative_displayed_repost_occurrences_reviewed": 27,
    }


def test_chiba_fields01_to04_primary_identity_sets_are_distinct():
    identity_sets = [
        {row["project_name"] for row in load(path)["records"]}
        for path in (FIELD01, FIELD02, FIELD03, FIELD04)
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18, 34]
    for index, left in enumerate(identity_sets):
        for right in identity_sets[index + 1 :]:
            assert left.isdisjoint(right)


def test_chiba_manifest_advances_project_identity_coverage_to_113_of_189():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] == 113
    assert fact["identity_records_remaining"] == 76
    assert fact["reviewed_field_counts"] == {
        "environment_nature": 30,
        "safety_security": 31,
        "health_welfare": 18,
        "children_education": 34,
    }
    assert fact["displayed_repost_occurrences_reviewed"] == 27
    assert fact["review_status"] == "reviewed_113_of_189_project_identities"
