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
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field05_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field05_has_exactly_7_unique_primary_identities():
    payload = load(FIELD05)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 7
    assert payload["identity_review_status"] == (
        "reviewed_complete_7_of_7_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 7
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field05_measure_partition_reconciles_to_official_7():
    payload = load(FIELD05)
    expected = {
        "5-1-1": 3,
        "5-1-2": 1,
        "5-2-1": 1,
        "5-2-2": 2,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 7


def test_chiba_field05_repost_links_to_reviewed_field04_identity():
    payload = load(FIELD05)
    reposts = payload["displayed_reposts"]

    assert len(reposts) == 1
    repost = reposts[0]
    assert repost["repost_type"] == "cross_field_repost"
    assert repost["project_name"] == "こども・若者の社会参画の推進"
    assert repost["primary_review_id"] == "chiba-f04-p034"


def test_chiba_field05_resolves_prior_cross_field_primary_locations():
    field05_names = {row["project_name"] for row in load(FIELD05)["records"]}
    expected_primary_names = {
        "フェアトレードの推進",
        "町内自治会業務の負担軽減の推進",
        "土気公民館・土気市民センター・土気いきいきセンターの再整備",
    }

    assert expected_primary_names.issubset(field05_names)


def test_chiba_field05_evidence_reconciles_cumulative_120_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_7_unique_projects_with_1_repost_occurrence"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 7
    assert evidence["reconciliation"] == {
        "field05_unique_project_count": 7,
        "displayed_same_field_repost_occurrence_count": 0,
        "displayed_cross_field_repost_occurrence_count": 1,
        "displayed_repost_occurrence_count": 1,
        "cumulative_current_project_identities_reviewed": 120,
        "cumulative_current_project_identities_remaining": 69,
        "cumulative_displayed_repost_occurrences_reviewed": 28,
    }


def test_chiba_fields01_to05_primary_identity_sets_are_distinct():
    identity_sets = [
        {row["project_name"] for row in load(path)["records"]}
        for path in (FIELD01, FIELD02, FIELD03, FIELD04, FIELD05)
    ]

    assert [len(names) for names in identity_sets] == [30, 31, 18, 34, 7]
    for left_index, left_names in enumerate(identity_sets):
        for right_names in identity_sets[left_index + 1 :]:
            assert left_names.isdisjoint(right_names)


def test_chiba_manifest_retains_field05_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert (
        "data/catalog/chiba_current_project_identities_field05.json"
        in manifest["current_project_identity_batch_paths"]
    )
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] >= 120
    assert fact["identity_records_remaining"] <= 69
    assert fact["reviewed_field_counts"]["community"] == 7
    assert fact["displayed_repost_occurrences_reviewed"] >= 28
