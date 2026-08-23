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
FIELD08 = CAT / "chiba_current_project_identities_field08.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field08_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field08_has_exactly_22_unique_primary_identities():
    payload = load(FIELD08)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 22
    assert payload["identity_review_status"] == (
        "reviewed_complete_22_of_22_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 22
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field08_measure_partition_reconciles_to_official_22():
    payload = load(FIELD08)
    expected = {
        "8-1-1": 3,
        "8-1-2": 3,
        "8-1-3": 3,
        "8-1-4": 0,
        "8-2-1": 3,
        "8-2-2": 1,
        "8-3-1": 4,
        "8-3-2": 3,
        "8-3-3": 2,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 22


def test_chiba_field08_reposts_reconcile_without_identity_inflation():
    payload = load(FIELD08)
    reposts = payload["displayed_reposts"]
    same = [row for row in reposts if row["repost_type"] == "same_field_repost"]
    cross = [row for row in reposts if row["repost_type"] == "cross_field_repost"]

    assert len(reposts) == 6
    assert len(same) == 3
    assert len(cross) == 3
    assert {row["primary_review_id"] for row in same} == {
        "chiba-f08-p001",
        "chiba-f08-p009",
        "chiba-f08-p017",
    }
    assert {row["project_name"] for row in cross} == {
        "青年期・壮年期等の健康な食習慣づくり",
        "農福連携の推進",
        "有害鳥獣対策の推進",
    }


def test_chiba_field08_resolves_deferred_primary_locations():
    field08_names = {row["project_name"] for row in load(FIELD08)["records"]}
    assert {
        "アントレプレナーシップ教育の推進",
        "スマート農業技術等の活用に向けた農業者への支援",
    }.issubset(field08_names)


def test_chiba_field08_departments_and_pdf_locations_are_explicit():
    records = load(FIELD08)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field08_evidence_reconciles_cumulative_189_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_22_unique_projects_with_6_repost_occurrences"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 22
    assert evidence["reconciliation"] == {
        "field08_unique_project_count": 22,
        "displayed_same_field_repost_occurrence_count": 3,
        "displayed_cross_field_repost_occurrence_count": 3,
        "displayed_repost_occurrence_count": 6,
        "cumulative_current_project_identities_reviewed": 189,
        "cumulative_current_project_identities_remaining": 0,
        "cumulative_displayed_repost_occurrences_reviewed": 63,
    }


def test_chiba_fields01_to08_primary_identity_sets_are_distinct():
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
            FIELD08,
        )
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18, 34, 7, 15, 32, 22]
    for left_index, left_names in enumerate(identity_sets):
        for right_names in identity_sets[left_index + 1 :]:
            assert left_names.isdisjoint(right_names)


def test_chiba_all_field_identity_counts_sum_to_official_189():
    paths = (FIELD01, FIELD02, FIELD03, FIELD04, FIELD05, FIELD06, FIELD07, FIELD08)
    counts = [len(load(path)["records"]) for path in paths]

    assert counts == [30, 31, 18, 34, 7, 15, 32, 22]
    assert sum(counts) == 189


def test_chiba_manifest_completes_project_identity_coverage_to_189_of_189():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert len(manifest["current_project_identity_batch_paths"]) == 8
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] == 189
    assert fact["identity_records_remaining"] == 0
    assert fact["reviewed_field_counts"] == {
        "environment_nature": 30,
        "safety_security": 31,
        "health_welfare": 18,
        "children_education": 34,
        "community": 7,
        "culture_sports": 15,
        "urban_transport": 32,
        "regional_economy": 22,
    }
    assert fact["displayed_repost_occurrences_reviewed"] == 63
    assert fact["review_status"] == "reviewed_complete_189_of_189_project_identities"
    assert "189/189" in manifest["quality_boundary"]
