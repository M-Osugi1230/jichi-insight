from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ROOT / "data/catalog/saitama_current_project_targets_chapter01.json"
IDENTITIES = (
    ROOT / "data/catalog/saitama_current_project_identities_policy_chapters01_04.json"
)
EVIDENCE = (
    ROOT / "data/evidence/saitama_current_project_targets_chapter01_evidence.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def target_records(payload: dict):
    return [target for project in payload["projects"] for target in project["targets"]]


def test_saitama_chapter01_target_review_covers_exactly_the_12_identity_projects():
    targets = load(TARGETS)
    chapter01_ids = {
        row["project_code"]
        for row in load(IDENTITIES)["records"]
        if row["project_code"].startswith("01-")
    }
    reviewed_ids = {row["project_code"] for row in targets["projects"]}

    assert targets["status"] == "reviewed_12_projects_22_target_indicators"
    assert targets["project_count"] == len(reviewed_ids) == 12
    assert reviewed_ids == chapter01_ids


def test_saitama_chapter01_has_22_unique_target_indicators_and_every_project_has_one():
    payload = load(TARGETS)
    records = target_records(payload)
    ids = [row["target_id"] for row in records]
    per_project = Counter(
        project["project_code"] for project in payload["projects"] for _ in project["targets"]
    )

    assert payload["target_indicator_count"] == len(records) == len(set(ids)) == 22
    assert all(count >= 1 for count in per_project.values())
    assert sorted(per_project.values()) == [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3]


def test_saitama_chapter01_all_targets_preserve_five_current_plan_years():
    records = target_records(load(TARGETS))
    years = {"2026", "2027", "2028", "2029", "2030"}

    assert all(set(row["annual_targets"]) == years for row in records)
    assert all(row["final_target_raw"].strip() for row in records)
    assert all(row["unit"].strip() for row in records)
    assert all(row["review_status"] == "reviewed" for row in records)


def test_saitama_chapter01_dashes_are_not_converted_to_zero():
    payload = load(TARGETS)
    by_id = {row["target_id"]: row for row in target_records(payload)}

    no_baseline = {
        "saitama-target-01-1-1-02-01",
        "saitama-target-01-2-1-03-02",
        "saitama-target-01-3-1-02-02",
    }
    for target_id in no_baseline:
        baseline = by_id[target_id]["baseline"]
        assert baseline["value"] is None
        assert baseline["value_status"] == "not_reported_dash"

    dispatch = by_id["saitama-target-01-3-1-02-01"]
    assert dispatch["annual_targets"]["2028"] is None
    assert dispatch["annual_targets"]["2029"] is None
    assert dispatch["annual_targets"]["2030"] is None
    assert dispatch["annual_target_status"] == {
        "2028": "not_applicable_dash",
        "2029": "not_applicable_dash",
        "2030": "not_applicable_dash",
    }


def test_saitama_chapter01_target_types_keep_cumulative_and_level_targets_separate():
    records = target_records(load(TARGETS))
    types = Counter(row["final_target_type"] for row in records)

    assert types["plan_period_cumulative"] == 3
    assert types["partial_plan_period_cumulative"] == 1
    assert types["annual_level"] == 6
    assert types["maintain_level"] == 12
    assert sum(types.values()) == 22


def test_saitama_chapter01_responsible_departments_and_evidence_are_explicit():
    payload = load(TARGETS)
    evidence = load(EVIDENCE)

    assert all(project["responsible_departments"] for project in payload["projects"])
    assert all(project["source_location"].startswith("PDF p") for project in payload["projects"])
    assert evidence["review_status"] == "reviewed_12_projects_22_target_indicators"
    assert sum(row["target_indicator_count"] for row in evidence["evidence"]) == 22
    assert all(row["decision"] == "accepted" for row in evidence["evidence"])


def test_saitama_chapter01_target_universe_does_not_claim_all_258_target_count():
    payload = load(TARGETS)
    boundary = payload["quality_boundary"]

    assert "第1章12事業" in boundary
    assert "22" in boundary
    assert "258事業全体の目標指標総数" in boundary
    assert "推定" in boundary
    assert "累計目標" in boundary
