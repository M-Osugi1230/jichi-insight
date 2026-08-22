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
FIELD05 = CAT / "chiba_current_project_identities_field05.json"
FIELD06 = CAT / "chiba_current_project_identities_field06.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field06_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field06_has_exactly_15_unique_primary_identities():
    payload = load(FIELD06)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 15
    assert payload["identity_review_status"] == (
        "reviewed_complete_15_of_15_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 15
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field06_measure_partition_reconciles_to_official_15():
    payload = load(FIELD06)
    expected = {
        "6-1-1": 4,
        "6-1-2": 5,
        "6-2-1": 2,
        "6-2-2": 4,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 15


def test_chiba_field06_reposts_defer_to_field07():
    payload = load(FIELD06)
    reposts = payload["displayed_reposts"]

    assert len(reposts) == 2
    assert all(row["repost_type"] == "cross_field_repost" for row in reposts)
    assert {row["project_name"] for row in reposts} == {
        "郷土理解の促進",
        "千葉マリンスタジアムの再構築",
    }
    assert all("分野7" in row["primary_source_location"] for row in reposts)


def test_chiba_field06_resolves_prior_cross_field_primary_locations():
    field06_names = {row["project_name"] for row in load(FIELD06)["records"]}
    expected_primary_names = {
        "パラスポーツの推進",
        "アルティーリ千葉新アリーナの整備支援",
    }

    assert expected_primary_names.issubset(field06_names)


def test_chiba_field06_departments_and_pdf_locations_are_explicit():
    records = load(FIELD06)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field06_evidence_reconciles_cumulative_135_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_15_unique_projects_with_2_repost_occurrences"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 15
    assert evidence["reconciliation"] == {
        "field06_unique_project_count": 15,
        "displayed_same_field_repost_occurrence_count": 0,
        "displayed_cross_field_repost_occurrence_count": 2,
        "displayed_repost_occurrence_count": 2,
        "cumulative_current_project_identities_reviewed": 135,
        "cumulative_current_project_identities_remaining": 54,
        "cumulative_displayed_repost_occurrences_reviewed": 30,
    }


def test_chiba_fields01_to06_primary_identity_sets_are_distinct():
    identity_sets = [
        {row["project_name"] for row in load(path)["records"]}
        for path in (FIELD01, FIELD02, FIELD03, FIELD04, FIELD05, FIELD06)
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18, 34, 7, 15]
    for left_index, left_names in enumerate(identity_sets):
        for right_names in identity_sets[left_index + 1 :]:
            assert left_names.isdisjoint(right_names)


def test_chiba_manifest_retains_field06_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert (
        "data/catalog/chiba_current_project_identities_field06.json"
        in manifest["current_project_identity_batch_paths"]
    )
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] >= 135
    assert fact["identity_records_remaining"] <= 54
    assert fact["reviewed_field_counts"]["culture_sports"] == 15
    assert fact["displayed_repost_occurrences_reviewed"] >= 30
