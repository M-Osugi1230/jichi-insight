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
FIELD07 = CAT / "chiba_current_project_identities_field07.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field07_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field07_has_exactly_32_unique_primary_identities():
    payload = load(FIELD07)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 32
    assert payload["identity_review_status"] == (
        "reviewed_complete_32_of_32_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 32
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field07_measure_partition_reconciles_to_official_32():
    payload = load(FIELD07)
    expected = {
        "7-1-1": 5,
        "7-1-2": 9,
        "7-1-3": 2,
        "7-1-4": 0,
        "7-2-1": 1,
        "7-2-2": 3,
        "7-2-3": 2,
        "7-3-1": 1,
        "7-3-2": 1,
        "7-4-1": 4,
        "7-4-2": 4,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 32


def test_chiba_field07_reposts_reconcile_without_identity_inflation():
    payload = load(FIELD07)
    reposts = payload["displayed_reposts"]
    same = [row for row in reposts if row["repost_type"] == "same_field_repost"]
    cross = [row for row in reposts if row["repost_type"] == "cross_field_repost"]

    assert len(reposts) == 27
    assert len(same) == 2
    assert len(cross) == 25
    assert {row["primary_review_id"] for row in same} == {"chiba-f07-p024"}
    assert all(
        row["project_name"] == "国家戦略特区制度を活用した先端技術の推進"
        for row in same
    )


def test_chiba_field07_resolves_field06_deferred_primary_locations():
    field07_names = {row["project_name"] for row in load(FIELD07)["records"]}
    assert {
        "郷土理解の促進",
        "千葉マリンスタジアムの再構築",
    }.issubset(field07_names)


def test_chiba_field07_departments_and_pdf_locations_are_explicit():
    records = load(FIELD07)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field07_evidence_reconciles_cumulative_167_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_32_unique_projects_with_27_repost_occurrences"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 32
    assert evidence["reconciliation"] == {
        "field07_unique_project_count": 32,
        "displayed_same_field_repost_occurrence_count": 2,
        "displayed_cross_field_repost_occurrence_count": 25,
        "displayed_repost_occurrence_count": 27,
        "cumulative_current_project_identities_reviewed": 167,
        "cumulative_current_project_identities_remaining": 22,
        "cumulative_displayed_repost_occurrences_reviewed": 57,
    }


def test_chiba_fields01_to07_primary_identity_sets_are_distinct():
    identity_sets = [
        {row["project_name"] for row in load(path)["records"]}
        for path in (
            FIELD01,
            FIELD02,
            FIELD03,
            FIELD04,
            FIELD05,
            FIELD06,
            FIELD07,
        )
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18, 34, 7, 15, 32]
    for left_index, left_names in enumerate(identity_sets):
        for right_names in identity_sets[left_index + 1 :]:
            assert left_names.isdisjoint(right_names)


def test_chiba_manifest_retains_field07_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert (
        "data/catalog/chiba_current_project_identities_field07.json"
        in manifest["current_project_identity_batch_paths"]
    )
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] >= 167
    assert fact["identity_records_remaining"] <= 22
    assert fact["reviewed_field_counts"]["urban_transport"] == 32
    assert fact["displayed_repost_occurrences_reviewed"] >= 57
