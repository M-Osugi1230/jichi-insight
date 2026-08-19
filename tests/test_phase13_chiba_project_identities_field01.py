from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/chiba_current_project_identities_field01.json"
EVIDENCE = ROOT / "data/evidence/chiba_current_project_identities_field01_evidence.json"
MANIFEST = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_field01_has_exact_official_30_unique_project_identities():
    payload = load(CATALOG)
    records = payload["records"]

    assert payload["official_unique_project_count"] == 30
    assert payload["identity_review_status"] == (
        "reviewed_complete_30_of_30_unique_projects"
    )
    assert len(records) == 30
    assert len({row["review_id"] for row in records}) == 30
    assert len({row["project_name"] for row in records}) == 30
    assert all(row["primary_identity"] is True for row in records)


def test_chiba_field01_measure_partition_reconciles_to_30():
    payload = load(CATALOG)
    expected = {
        "1-1-1": 7,
        "1-1-2": 2,
        "1-1-3": 8,
        "1-2-1": 9,
        "1-2-2": 2,
        "1-2-3": 2,
    }
    actual = {
        code: sum(row["measure_code"] == code for row in payload["records"])
        for code in expected
    }

    assert payload["measure_partition"] == expected
    assert actual == expected
    assert sum(actual.values()) == 30


def test_chiba_field01_names_departments_and_locations_are_explicit():
    records = load(CATALOG)["records"]

    assert all(row["project_name"].strip() for row in records)
    assert all(row["responsible_departments"] for row in records)
    assert all(row["source_location"].startswith("PDF p.") for row in records)
    assert all(row["measure_code"].startswith("1-") for row in records)


def test_chiba_field01_same_field_repost_is_not_duplicated():
    payload = load(CATALOG)
    records = payload["records"]
    reposts = {row["project_name"]: row for row in payload["displayed_reposts"]}

    yatsuda = [row for row in records if row["project_name"] == "谷津田の森林整備"]
    assert len(yatsuda) == 1
    assert yatsuda[0]["measure_code"] == "1-1-1"
    assert yatsuda[0]["source_location"] == "PDF p.22"
    assert reposts["谷津田の森林整備"]["repost_type"] == "same_field_repost"
    assert reposts["谷津田の森林整備"]["display_measure_code"] == "1-2-2"
    assert reposts["谷津田の森林整備"]["source_location"] == "PDF p.30"
    assert reposts["谷津田の森林整備"]["primary_review_id"] == (
        yatsuda[0]["review_id"]
    )


def test_chiba_field01_cross_field_repost_is_excluded_from_unique_30():
    payload = load(CATALOG)
    names = {row["project_name"] for row in payload["records"]}
    reposts = {row["project_name"]: row for row in payload["displayed_reposts"]}
    arena = reposts["アルティーリ千葉新アリーナの整備支援"]

    assert "アルティーリ千葉新アリーナの整備支援" not in names
    assert arena["repost_type"] == "cross_field_repost"
    assert arena["source_location"] == "PDF p.29"
    assert arena["primary_source_location"] == "PDF p.95 / 分野6 スポーツ"
    assert arena["decision"] == (
        "exclude_from_field01_unique_30_and_defer_identity_to_primary_field_review"
    )


def test_chiba_field01_evidence_reconciles_reposts_and_official_total():
    evidence = load(EVIDENCE)

    assert evidence["review_status"] == "reviewed_complete_30_unique_project_identities"
    assert evidence["field_total"] == {
        "official_unique_project_count": 30,
        "reviewed_primary_identity_count": 30,
        "displayed_repost_occurrence_count": 2,
    }
    assert sum(row["primary_identity_count"] for row in evidence["evidence"]) == 30
    assert len(evidence["repost_findings"]) == 2


def test_chiba_manifest_advances_project_identity_review_to_30_of_189():
    manifest = load(MANIFEST)
    fact = next(
        row
        for row in manifest["reviewed_facts"]
        if row["id"] == "chiba-current-project-universe"
    )

    assert manifest["current_project_identity_batch_paths"] == [
        "data/catalog/chiba_current_project_identities_field01.json"
    ]
    assert fact["value"] == 189
    assert fact["identity_records_reviewed"] == 30
    assert fact["identity_records_remaining"] == 159
    assert fact["reviewed_field_counts"] == {"environment_nature": 30}
    assert fact["displayed_repost_occurrences_reviewed"] == 2
    assert fact["review_status"] == "reviewed_30_of_189_project_identities"
