from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAT = ROOT / "data/catalog"
EVD = ROOT / "data/evidence"
MANIFEST = CAT / "chiba_historical_project_identity_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def identity_path(field_number: int) -> Path:
    return CAT / f"chiba_historical_project_identities_field{field_number:02d}.json"


def evidence_path(field_number: int) -> Path:
    return EVD / f"chiba_historical_project_identities_field{field_number:02d}_evidence.json"


def test_historical_fields_1_and_2_match_official_unique_project_counts():
    field01 = load(identity_path(1))
    field02 = load(identity_path(2))

    assert field01["official_unique_project_count"] == len(field01["records"]) == 53
    assert field02["official_unique_project_count"] == len(field02["records"]) == 57
    assert len(field01["displayed_reposts"]) == 9
    assert len(field02["displayed_reposts"]) == 1


def test_historical_review_ids_are_unique_and_separate_from_current_ids():
    records = load(identity_path(1))["records"] + load(identity_path(2))["records"]
    ids = [row["review_id"] for row in records]

    assert len(ids) == len(set(ids)) == 110
    assert all(review_id.startswith("chiba-hf") for review_id in ids)
    assert not any(review_id.startswith("chiba-f0") for review_id in ids)


def test_historical_identity_rows_preserve_measure_department_and_source_coordinates():
    for field_number in (1, 2):
        payload = load(identity_path(field_number))
        for row in payload["records"]:
            assert row["measure_code"].startswith(f"{field_number}-")
            assert row["project_name"].strip()
            assert row["source_heading_text"].strip()
            assert row["responsible_departments"]
            assert all(department.strip() for department in row["responsible_departments"])
            assert row["primary_identity"] is True
            assert row["source_physical_page"] == row["source_printed_page"] + 4
            assert row["source_location"] == f"PDF p.{row['source_printed_page'] + 3}"


def test_field01_reposts_are_excluded_from_unique_53_and_same_field_reposts_link_back():
    payload = load(identity_path(1))
    records = {row["project_name"]: row for row in payload["records"]}
    reposts = payload["displayed_reposts"]

    same_field = [row for row in reposts if row["repost_type"] == "same_field_repost"]
    cross_field = [
        row
        for row in reposts
        if row["repost_type"] == "cross_field_repost_pending_primary_review"
    ]

    assert len(same_field) == 5
    assert len(cross_field) == 4
    assert all(row["primary_review_id"] for row in same_field)
    assert all(row["primary_review_id"] is None for row in cross_field)
    for row in same_field:
        assert records[row["project_name"]]["review_id"] == row["primary_review_id"]


def test_field02_single_repost_remains_cross_field_until_field7_is_reviewed():
    payload = load(identity_path(2))
    reposts = payload["displayed_reposts"]

    assert len(reposts) == 1
    assert reposts[0]["project_name"] == "バス停車帯の整備"
    assert reposts[0]["repost_type"] == "cross_field_repost_pending_primary_review"
    assert reposts[0]["primary_review_id"] is None


def test_historical_identity_evidence_reconciles_exactly():
    field01 = load(evidence_path(1))
    field02 = load(evidence_path(2))

    assert field01["reconciliation"] == {
        "official_unique_project_count": 53,
        "reviewed_unique_project_count": 53,
        "displayed_repost_count": 9,
        "count_matches_official": True,
    }
    assert field02["reconciliation"] == {
        "official_unique_project_count": 57,
        "reviewed_unique_project_count": 57,
        "displayed_repost_count": 1,
        "count_matches_official": True,
    }
    assert field01["source_pdf_sha256"] == field02["source_pdf_sha256"]
    assert len(field01["source_pdf_sha256"]) == 64


def test_historical_manifest_advances_to_110_of_360_and_blocks_linkage():
    manifest = load(MANIFEST)
    fields = {row["field_code"]: row for row in manifest["field_review_order"]}

    assert manifest["historical_project_universe"] == 360
    assert manifest["historical_identity_coverage"] == {"reviewed": 110, "remaining": 250}
    assert fields["1"]["official_unique_project_count"] == 53
    assert fields["2"]["official_unique_project_count"] == 57
    assert fields["1"]["status"] == fields["2"]["status"] == "reviewed_complete"
    assert fields["3"]["status"] == "pending_identity_review"
    assert manifest["versioned_linkage_gate"]["status"] == (
        "blocked_until_historical_identity_complete"
    )
    assert "Field 3" in manifest["next_action"]
    assert "110" in manifest["quality_boundary"]
    assert "250" in manifest["quality_boundary"]


def test_candidate_diagnostics_explain_why_only_fields_1_and_2_are_promoted_now():
    fields = {row["field_code"]: row for row in load(MANIFEST)["field_review_order"]}
    official_counts = [53, 57, 46, 46, 23, 25, 78, 32]
    candidate_counts = [53, 57, 45, 45, 22, 25, 77, 31]

    assert [fields[str(i)]["official_unique_project_count"] for i in range(1, 9)] == (
        official_counts
    )
    assert [
        fields[str(i)]["candidate_extraction"]["primary_heading_candidates"]
        for i in range(1, 9)
    ] == candidate_counts
    assert fields["1"]["candidate_extraction"]["matches_official_unique_count"] is True
    assert fields["2"]["candidate_extraction"]["matches_official_unique_count"] is True
    assert fields["6"]["candidate_extraction"]["matches_official_unique_count"] is True
    for field_number in (3, 4, 5, 7, 8):
        assert (
            fields[str(field_number)]["candidate_extraction"]["matches_official_unique_count"]
            is False
        )
