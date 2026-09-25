from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
PROJECTS = CAT / "kawasaki_current_project_identities.json"
EVIDENCE = EVD / "kawasaki_current_project_identities_evidence.json"
STRUCTURE = CAT / "kawasaki_current_policy_structure.json"

EXPECTED_MEASURE_COUNTS = {
    "1-1-1": 6,
    "1-1-2": 4,
    "1-1-3": 12,
    "1-1-4": 6,
    "1-2-1": 5,
    "1-2-2": 4,
    "1-2-3": 8,
    "1-3-1": 7,
    "1-3-2": 8,
    "1-4-1": 11,
    "1-4-2": 8,
    "1-4-3": 6,
    "1-4-4": 5,
    "1-4-5": 8,
    "1-4-6": 5,
    "1-5-1": 14,
    "1-5-2": 5,
    "2-1-1": 5,
    "2-1-2": 15,
    "2-2-1": 5,
    "2-2-2": 6,
    "2-2-3": 6,
    "2-2-4": 7,
    "2-2-5": 5,
    "3-1-1": 10,
    "3-1-2": 8,
    "3-1-3": 19,
    "3-2-1": 6,
    "3-2-2": 8,
    "4-1-1": 6,
    "4-1-2": 6,
    "4-1-3": 6,
    "4-1-4": 5,
    "4-1-5": 6,
    "4-2-1": 5,
    "4-2-2": 2,
    "4-3-1": 20,
    "4-4-1": 8,
    "4-4-2": 5,
    "4-4-3": 4,
    "4-5-1": 5,
    "4-5-2": 5,
    "4-6-1": 6,
    "4-7-1": 6,
    "5-1-1": 4,
    "5-1-2": 13,
    "5-1-3": 7,
    "5-2-1": 9,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_kawasaki_project_universe_reconciles_exactly_to_350_and_48_measures():
    payload = load(PROJECTS)
    records = payload["records"]

    assert payload["review_status"] == "reviewed_complete_350_project_identities"
    assert payload["project_universe_count"] == len(records) == 350
    assert payload["measure_coverage_count"] == 48
    assert payload["measure_project_counts"] == EXPECTED_MEASURE_COUNTS
    assert sum(EXPECTED_MEASURE_COUNTS.values()) == 350
    assert {row["measure_code"] for row in records} == set(
        EXPECTED_MEASURE_COUNTS
    )


def test_kawasaki_project_ids_names_and_source_locations_are_globally_unique():
    records = load(PROJECTS)["records"]
    review_ids = [row["review_id"] for row in records]
    names = [row["project_name"] for row in records]

    assert len(review_ids) == len(set(review_ids)) == 350
    assert len(names) == len(set(names)) == 350
    assert all(row["review_status"] == "reviewed_identity" for row in records)
    assert all(
        row["source_id"] == "kawasaki-fourth-implementation-plan-official-pdf"
        for row in records
    )
    assert {row["source_pdf_page"] for row in records} == {6, 7, 8, 9}
    assert {row["source_booklet_page"] for row in records} == {162, 163, 164, 165}
    assert all("資料編 冊子p." in row["source_location"] for row in records)


def test_kawasaki_main_action_marker_is_preserved_without_dropping_other_projects():
    payload = load(PROJECTS)
    records = payload["records"]

    assert payload["main_action_count"] == sum(
        row["main_action"] for row in records
    ) == 235
    assert sum(not row["main_action"] for row in records) == 115

    by_name = {row["project_name"]: row for row in records}
    assert by_name["災害対応力強化事業"]["main_action"] is True
    assert by_name["臨海部・津波防災対策事業"]["main_action"] is False
    assert by_name["川崎駅周辺総合整備事業"]["main_action"] is True
    assert by_name["市街地開発事業等の支援・指導業務"]["main_action"] is False


def test_kawasaki_four_name_exceptions_are_retained_as_real_projects():
    names = {row["project_name"] for row in load(PROJECTS)["records"]}

    assert {
        "川崎病院の運営",
        "井田病院の運営",
        "多摩病院の運営管理",
        "児童福祉施設等の指導・監査",
    } <= names


def test_kawasaki_project_measure_coverage_matches_reviewed_structure():
    structure = load(STRUCTURE)
    structure_codes = {
        measure["measure_code"]
        for basic_policy in structure["basic_policies"]
        for policy in basic_policy["policies"]
        for measure in policy["measures"]
    }
    project_codes = {
        row["measure_code"] for row in load(PROJECTS)["records"]
    }

    assert len(structure_codes) == 48
    assert project_codes == structure_codes


def test_kawasaki_project_evidence_reconciles_source_hash_and_counts():
    payload = load(PROJECTS)
    evidence = load(EVIDENCE)
    reconciliation = evidence["reconciliation"]

    assert len(payload["source_pdf_sha256"]) == 64
    assert evidence["source_pdf_sha256"] == payload["source_pdf_sha256"]
    assert evidence["source_page_range"] == {
        "split_pdf_start": 6,
        "split_pdf_end": 9,
        "booklet_start": 162,
        "booklet_end": 165,
    }
    assert reconciliation == {
        "official_project_universe_count": 350,
        "reviewed_project_identity_count": 350,
        "official_measure_count": 48,
        "reviewed_measure_coverage_count": 48,
        "main_action_count": 235,
        "unique_project_name_count": 350,
        "count_matches_official": True,
    }
    assert len(evidence["records"]) == 350
    assert {row["review_id"] for row in evidence["records"]} == {
        row["review_id"] for row in payload["records"]
    }
