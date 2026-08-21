from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
FIELD01 = CAT / "chiba_current_project_identities_field01.json"
FIELD02 = CAT / "chiba_current_project_identities_field02.json"
MANIFEST = CAT / "chiba_phase13_policy_review_manifest.json"
EVIDENCE = EVD / "chiba_current_project_identities_field02_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field02_has_exactly_31_unique_primary_identities():
    payload = load(FIELD02)
    records = payload["records"]
    ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert payload["official_unique_project_count"] == 31
    assert payload["identity_review_status"] == (
        "reviewed_complete_31_of_31_unique_projects"
    )
    assert len(records) == len(set(ids)) == len(set(names)) == 31
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field02_measure_partition_reconciles_to_official_31():
    payload = load(FIELD02)
    expected = {
        "2-1-1": 7,
        "2-1-2": 5,
        "2-2-1": 2,
        "2-2-2": 1,
        "2-3-1": 5,
        "2-3-2": 1,
        "2-3-3": 2,
        "2-4-1": 3,
        "2-4-2": 4,
        "2-4-3": 1,
    }
    actual = {
        code: sum(1 for row in payload["records"] if row["measure_code"] == code)
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 31


def test_chiba_field02_cross_field_reposts_do_not_inflate_identity_count():
    payload = load(FIELD02)
    names = {row["project_name"] for row in payload["records"]}
    reposts = payload["displayed_reposts"]
    repost_names = {row["project_name"] for row in reposts}

    assert repost_names == {
        "市立学校の体育館冷暖房設備の整備",
        "交差点の改良",
        "フェアトレードの推進",
    }
    assert names.isdisjoint(repost_names)
    assert all(row["repost_type"] == "cross_field_repost" for row in reposts)
    assert {row["primary_measure_code"] for row in reposts} == {
        "4-2-2",
        "7-2-2",
        "5-1-1",
    }


def test_chiba_field02_departments_and_pdf_locations_are_explicit():
    records = load(FIELD02)["records"]

    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["project_name"].strip() for row in records)


def test_chiba_field02_evidence_reconciles_cumulative_61_of_189():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == (
        "reviewed_complete_31_unique_projects_with_3_cross_field_reposts"
    )
    assert sum(row["unique_project_count"] for row in evidence["evidence"]) == 31
    assert len(evidence["repost_reconciliation"]) == 3
    assert evidence["reconciliation"] == {
        "field02_unique_project_count": 31,
        "displayed_cross_field_repost_count": 3,
        "cumulative_current_project_identities_reviewed": 61,
        "cumulative_current_project_identities_remaining": 128,
    }


def test_chiba_field01_and_field02_identity_sets_are_distinct():
    field01 = {row["project_name"] for row in load(FIELD01)["records"]}
    field02 = {row["project_name"] for row in load(FIELD02)["records"]}

    assert len(field01) == 30
    assert len(field02) == 31
    assert field01.isdisjoint(field02)


def test_chiba_manifest_retains_field02_completion_as_review_advances():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert (
        "data/catalog/chiba_current_project_identities_field02.json"
        in manifest["current_project_identity_batch_paths"]
    )
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] >= 61
    assert fact["identity_records_remaining"] <= 128
    assert fact["reviewed_field_counts"]["safety_security"] == 31
    assert fact["displayed_repost_occurrences_reviewed"] >= 5
