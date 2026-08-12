from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SOURCE_INDEX_PATH = ROOT / "data/catalog/sendai_survey_2025_source_index.json"
REGISTRY_PATH = ROOT / "data/catalog/sendai_survey_2025_summary_scores.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_survey_2025_summary_scores_evidence.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_survey_source_index_preserves_official_source_roles():
    index = load(SOURCE_INDEX_PATH)
    records = {record["id"]: record for record in index["records"]}

    assert index["official_code"] == "041009"
    assert index["survey_year"] == 2025
    assert set(records) == {
        "sendai-city-survey-2025-page",
        "sendai-city-survey-2025-report-pdf",
        "sendai-city-survey-2025-simple-csv",
        "sendai-city-survey-2025-cross-csv",
    }
    assert records["sendai-city-survey-2025-report-pdf"]["page_count"] == 92
    assert all(record["official_host"] == "www.city.sendai.jp" for record in records.values())
    assert "administrative performance" in index["quality_boundary"]


def test_sendai_survey_methodology_keeps_dates_and_denominators_separate():
    registry = load(REGISTRY_PATH)
    methodology = registry["methodology"]

    assert methodology["sample_count"] == 6000
    assert methodology["valid_response_count"] == 2794
    assert methodology["reported_valid_response_rate_percent"] == 46.8
    assert methodology["questionnaire_sent_date"] == "2025-04-30"
    assert methodology["response_deadline_date"] == "2025-05-23"
    assert methodology["aggregation_cutoff_date"] == "2025-05-29"
    assert "30件" in methodology["valid_response_rate_denominator_note"]
    assert "母数から除外" in methodology["current_state_score_rule"]
    assert "母数から除外" in methodology["policy_score_rule"]


def test_sendai_survey_has_exact_eight_current_and_twenty_six_policy_scores():
    registry = load(REGISTRY_PATH)
    current = registry["current_state_items"]
    policy = registry["policy_evaluation_items"]
    summary = registry["summary"]

    assert summary["current_state_item_count"] == len(current) == 8
    assert summary["policy_evaluation_item_count"] == len(policy) == 26
    assert summary["total_summary_score_item_count"] == 34
    assert [item["question_number"] for item in current] == list(range(1, 9))
    assert len({item["id"] for item in current + policy}) == 34
    assert summary["response_category_review_complete"] is False
    assert summary["cross_tab_review_complete"] is False


def test_sendai_current_state_scores_preserve_three_year_history():
    current = {
        item["question_number"]: item
        for item in load(REGISTRY_PATH)["current_state_items"]
    }

    assert current[1]["scores"] == {"2025": 2.98, "2024": 3.05, "2023": 3.06}
    assert current[5]["scores"] == {"2025": 2.56, "2024": 2.57, "2023": 2.59}
    assert current[8]["scores"] == {"2025": 2.85, "2024": 2.98, "2023": 2.99}
    assert all(item["source_pdf_page_index_0_based"] == 14 for item in current.values())


def test_sendai_policy_scores_preserve_exact_official_codes_and_extremes():
    policy = {
        item["policy_code"]: item
        for item in load(REGISTRY_PATH)["policy_evaluation_items"]
    }

    assert len(policy) == 26
    assert policy["1-1"]["statement_ja"] == "勾当台・定禅寺通エリアの活性化"
    assert policy["1-1"]["score_2025"] == 3.19
    assert policy["1-3"]["score_2025"] == 3.17
    assert policy["7-1"]["score_2025"] == 3.04
    assert policy["9-2"]["statement_ja"] == "安定した行政経営基盤の維持"
    assert policy["9-2"]["score_2025"] == 2.57
    assert all(item["source_pdf_page_index_0_based"] == 16 for item in policy.values())


def test_sendai_survey_summary_scores_have_one_to_one_valid_evidence():
    registry = load(REGISTRY_PATH)
    packets = load(EVIDENCE_PATH)
    items = registry["current_state_items"] + registry["policy_evaluation_items"]
    validator = Draft202012Validator(
        load(EVIDENCE_SCHEMA_PATH), format_checker=FormatChecker()
    )

    assert len(packets) == len(items) == 34
    assert {packet["subject_id"] for packet in packets} == {item["id"] for item in items}
    assert {packet["id"] for packet in packets} == {item["evidence_id"] for item in items}
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(packet["subject_type"] == "kpi" for packet in packets)
    assert all(
        "行政実績" in packet["claims"][0]["review_note"]
        for packet in packets
    )


def test_sendai_survey_registry_does_not_claim_policy_achievement():
    registry = load(REGISTRY_PATH)
    boundary = registry["quality_boundary"]

    assert "not administrative output" in boundary
    assert "not" in boundary
    assert "Jichi Insight policy scores" in boundary
    assert registry["summary"]["policy_evaluation_history_depth"] == "2025_summary_only"
