from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION_PATH = ROOT / "data/catalog/phase11_completion.json"
COMPLETION_SCHEMA_PATH = ROOT / "schemas/phase11_completion.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase11_execution_queue.json"
QUEUE_SCHEMA_PATH = ROOT / "schemas/phase11_execution_queue.schema.json"
WAVE1_PATH = ROOT / "data/catalog/phase11_wave1_completion.json"
WAVE2_PATH = ROOT / "data/catalog/phase11_wave2_completion.json"
PHASE9_SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_completion_manifest_and_queue_validate():
    completion = load(COMPLETION_PATH)
    completion_validator = Draft202012Validator(
        load(COMPLETION_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(completion_validator.iter_errors(completion)) == []
    queue = load(QUEUE_PATH)
    queue_validator = Draft202012Validator(
        load(QUEUE_SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(queue_validator.iter_errors(queue)) == []
    for path in completion["canonical_sources"]:
        assert (ROOT / path).exists()


def test_all_prefectures_and_waves_are_complete():
    completion = load(COMPLETION_PATH)
    queue = load(QUEUE_PATH)
    assert completion["status"] == "complete"
    assert queue["status"] == "complete"
    assert all(wave["status"] == "complete" for wave in queue["waves"])
    prefecture_codes = [
        code for wave in queue["waves"] for code in wave["prefecture_codes"]
    ]
    assert len(prefecture_codes) == 47
    assert len(set(prefecture_codes)) == 47
    assert completion["prefecture_coverage"] == {
        "total_prefectures": 47,
        "wave1_reference_prefectures": 4,
        "wave2_anchor_prefectures": 5,
        "wave3_nationwide_prefectures": 38,
        "prefectures_remaining": 0,
    }


def test_wave_counts_reconcile_to_nationwide_total():
    completion = load(COMPLETION_PATH)
    wave1 = load(WAVE1_PATH)["summary"]
    wave2 = load(WAVE2_PATH)["summary"]
    wave3 = load(QUEUE_PATH)["summary"]["wave3_normalization"]
    phase9 = load(PHASE9_SUMMARY_PATH)
    summary = completion["record_summary"]
    assert wave1["record_count"] == 861
    assert wave2["records"] == 711
    assert wave3["records_complete"] == 13755
    assert phase9["prefecture_count"] == 38
    assert phase9["reviewed_target_statement_count"] == 13755
    assert phase9["evidence_packet_count"] == 13755
    assert summary["wave1_records"] == wave1["record_count"]
    assert summary["wave2_records"] == wave2["records"]
    assert summary["wave3_records"] == wave3["records_complete"]
    assert summary["total_records"] == 861 + 711 + 13755 == 15327


def test_unresolved_and_non_assessment_boundaries_remain_explicit():
    completion = load(COMPLETION_PATH)
    queue = load(QUEUE_PATH)
    summary = completion["record_summary"]
    assert summary["wave1_linked_records"] == 420
    assert summary["wave1_partial_records"] == 58
    assert summary["wave1_not_linked_records"] == 383
    assert summary["wave2_reviewed_maximum_depth_records"] == 375
    assert summary["wave3_partial_records"] == 13755
    assert summary["policy_achievement_assessment_count"] == 0
    assert summary["comparison_eligible_record_count"] == 0
    assert queue["summary"]["wave3_normalization"]["linked_records"] == 0
    assert queue["summary"]["wave3_normalization"]["partial_records"] == 13755
    assert queue["summary"]["wave3_normalization"]["next_prefecture_code"] is None
    assert "does not mean that every record is linked" in completion["completion_boundary"]
    assert "no independent policy-achievement judgment" in completion["completion_boundary"]
