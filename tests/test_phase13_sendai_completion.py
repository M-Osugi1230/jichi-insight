from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/sendai_phase13_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/sendai_phase13_completion.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
LINKAGE_PATH = ROOT / "data/catalog/sendai_phase13_progress_linkage.json"
PLAN_PATH = ROOT / "data/reviewed/sendai-city/plan_review.json"
FISCAL_PATH = ROOT / "data/reviewed/sendai-city/fiscal_records.json"
FISCAL_EVIDENCE_PATH = ROOT / "data/reviewed/sendai-city/evidence_packets.json"
SURVEY_SUMMARY_PATH = ROOT / "data/catalog/sendai_survey_2025_summary_scores.json"
SURVEY_SUMMARY_EVIDENCE_PATH = ROOT / "data/evidence/sendai_survey_2025_summary_scores_evidence.json"
SURVEY_PRIORITY_PATH = ROOT / "data/catalog/sendai_survey_2025_priority_policy.json"
SURVEY_PRIORITY_EVIDENCE_PATH = ROOT / "data/evidence/sendai_survey_2025_priority_policy_evidence.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_completion_contract_matches_schema_and_paths_exist():
    completion = load(COMPLETION_PATH)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA_PATH), format_checker=FormatChecker()
    )

    assert list(validator.iter_errors(completion)) == []
    package = completion["review_package"]
    for key in (
        "review_history_manifest_path",
        "progress_linkage_path",
        "plan_review_path",
        "source_catalog_path",
        "survey_review_manifest_path",
        "fiscal_records_path",
        "fiscal_evidence_path",
    ):
        assert (ROOT / package[key]).is_file()


def test_sendai_completion_counts_are_derived_from_reviewed_records():
    completion = load(COMPLETION_PATH)
    counts = completion["review_package"]["counts"]
    plan = load(PLAN_PATH)
    fiscal = load(FISCAL_PATH)
    project_files = sorted(
        (ROOT / "data/catalog").glob("sendai_challenge_project_reviews_part*.json")
    )
    project_records = [
        record for path in project_files for record in load(path)["records"]
    ]
    survey_summary = load(SURVEY_SUMMARY_PATH)
    survey_priority = load(SURVEY_PRIORITY_PATH)

    assert counts["plan_core_records"] == len(plan["records"]) == 6
    assert len(project_files) == 36
    assert counts["challenge_project_core_records"] == len(project_records) == 108
    assert len({record["id"] for record in project_records}) == 108
    assert counts["citizen_survey_summary_items"] == (
        len(survey_summary["current_state_items"])
        + len(survey_summary["policy_evaluation_items"])
    ) == 34
    assert counts["citizen_survey_priority_items"] == len(
        survey_priority["items"]
    ) == 26
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_sendai_completion_evidence_covers_declared_record_packages():
    project_files = sorted(
        (ROOT / "data/catalog").glob("sendai_challenge_project_reviews_part*.json")
    )
    project_evidence_files = sorted(
        (ROOT / "data/evidence").glob(
            "sendai_challenge_project_reviews_part*_evidence.json"
        )
    )
    project_ids = {
        record["id"]
        for path in project_files
        for record in load(path)["records"]
    }
    project_evidence_ids = {
        packet["project_id"]
        for path in project_evidence_files
        for packet in load(path)["evidence_packets"]
    }

    summary = load(SURVEY_SUMMARY_PATH)
    summary_ids = {
        item["id"]
        for item in summary["current_state_items"]
        + summary["policy_evaluation_items"]
    }
    summary_evidence_ids = {
        packet["subject_id"] for packet in load(SURVEY_SUMMARY_EVIDENCE_PATH)
    }
    priority_ids = {item["id"] for item in load(SURVEY_PRIORITY_PATH)["items"]}
    priority_evidence_ids = {
        packet["subject_id"] for packet in load(SURVEY_PRIORITY_EVIDENCE_PATH)
    }
    fiscal_ids = {record["id"] for record in load(FISCAL_PATH)}
    fiscal_evidence_ids = {
        packet["subject_id"] for packet in load(FISCAL_EVIDENCE_PATH)
    }

    assert len(project_evidence_files) == 36
    assert project_evidence_ids == project_ids
    assert summary_evidence_ids == summary_ids
    assert priority_evidence_ids == priority_ids
    assert fiscal_evidence_ids == fiscal_ids


def test_sendai_completion_preserves_deferred_depth_without_inference():
    completion = load(COMPLETION_PATH)
    deferred = {item["id"]: item for item in completion["deferred_depth"]}
    expected_ids = {
        "survey-response-distributions",
        "survey-attribute-cross-tabs",
        "survey-additional-layers",
        "project-outcome-kpi-evidence",
        "fiscal-detail-project-linkage",
    }

    assert set(deferred) == expected_ids
    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )
    boundary = completion["completion_boundary"]
    assert "全公開データを網羅" in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary
    assert "deferred_depth" in boundary


def test_sendai_completion_and_phase13_queue_are_consistent():
    completion = load(COMPLETION_PATH)
    linkage = load(LINKAGE_PATH)
    queue = load(QUEUE_PATH)
    sendai = next(
        item for item in queue["execution_queue"] if item["official_code"] == "041009"
    )
    statuses = [item["status"] for item in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert linkage["status"] == "reviewed_complete"
    assert linkage["summary"]["municipality_phase13_complete"] is True
    assert sendai["status"] == "reviewed_complete"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 1
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 16


def test_sendai_completion_quality_gates_are_all_explicitly_true():
    completion = load(COMPLETION_PATH)
    quality_gate = completion["quality_gate"]

    assert quality_gate
    assert all(value is True for value in quality_gate.values())
    assert completion["completion_depth"] == "declared_review_package_v1"
