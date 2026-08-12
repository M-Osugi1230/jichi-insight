from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PRIORITY_PATH = ROOT / "data/catalog/sendai_survey_2025_priority_policy.json"
SUMMARY_PATH = ROOT / "data/catalog/sendai_survey_2025_summary_scores.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_survey_2025_priority_policy_evidence.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_priority_policy_preserves_multiple_response_method():
    registry = load(PRIORITY_PATH)
    question = registry["question"]

    assert registry["official_code"] == "041009"
    assert registry["survey_year"] == 2025
    assert question["question_number"] == 10
    assert question["response_mode"] == "multiple_response_up_to_10"
    assert question["maximum_selections"] == 10
    assert question["percentage_denominator"] == "valid_respondents"
    assert "Do not normalize" in question["normalization_rule"]


def test_sendai_priority_policy_covers_all_26_policy_codes_once():
    priority = load(PRIORITY_PATH)
    summary = load(SUMMARY_PATH)
    items = priority["items"]
    priority_codes = [item["policy_code"] for item in items]
    summary_codes = [
        item["policy_code"] for item in summary["policy_evaluation_items"]
    ]

    assert priority["summary"]["policy_item_count"] == len(items) == 26
    assert [item["source_order"] for item in items] == list(range(1, 27))
    assert len(set(priority_codes)) == 26
    assert set(priority_codes) == set(summary_codes)
    assert priority["summary"]["no_response_percent"] == 3.4
    assert priority["summary"]["source_pdf_page_index_0_based"] == 52


def test_sendai_priority_policy_preserves_official_top_bottom_and_ties():
    items = load(PRIORITY_PATH)["items"]
    by_code = {item["policy_code"]: item for item in items}

    assert items[0]["policy_code"] == "3-3"
    assert items[0]["response_percent"] == 54.9
    assert items[1]["policy_code"] == "5-2"
    assert items[1]["response_percent"] == 53.8
    assert items[-1]["policy_code"] == "4-1"
    assert items[-1]["response_percent"] == 10.6
    assert by_code["2-3"]["response_percent"] == 30.1
    assert by_code["7-3"]["response_percent"] == 30.1
    assert by_code["6-2"]["response_percent"] == 20.0
    assert by_code["7-1"]["response_percent"] == 20.0


def test_sendai_priority_policy_locks_correct_8x_code_text_mapping():
    by_code = {
        item["policy_code"]: item
        for item in load(PRIORITY_PATH)["items"]
    }

    assert by_code["8-1"]["statement_ja"] == (
        "賑わいと活力が行きわたる、回遊性の高い都心づくり"
    )
    assert by_code["8-1"]["response_percent"] == 24.3
    assert by_code["8-2"]["statement_ja"] == (
        "都心機能強化に向けた開発とビジネスの好循環を生み出す取り組み"
    )
    assert by_code["8-2"]["response_percent"] == 15.6
    assert by_code["8-3"]["statement_ja"] == (
        "域内外から人を惹きつける魅力ある空間づくり"
    )
    assert by_code["8-3"]["response_percent"] == 27.1


def test_sendai_priority_policy_has_one_to_one_valid_evidence():
    registry = load(PRIORITY_PATH)
    packets = load(EVIDENCE_PATH)
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    expected_subject_ids = {
        f"sendai-survey-priority-{item['policy_code']}"
        for item in registry["items"]
    }

    assert len(packets) == 26
    assert {packet["subject_id"] for packet in packets} == expected_subject_ids
    assert {packet["id"] for packet in packets} == {
        item["evidence_id"] for item in registry["items"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(
        "複数回答" in packet["claims"][0]["review_note"]
        for packet in packets
    )


def test_sendai_priority_policy_does_not_become_jichi_ranking():
    boundary = load(PRIORITY_PATH)["quality_boundary"]

    assert "not a Jichi Insight priority ranking" in boundary
    assert "not" in boundary
    assert "budget allocation recommendation" in boundary
    assert "causal impact estimate" in boundary
