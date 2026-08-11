from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/catalog/sendai_challenge_project_reviews_part10.json"
EVIDENCE_PATH = ROOT / "data/evidence/sendai_challenge_project_reviews_part10_evidence.json"
MANIFEST_PATH = ROOT / "data/catalog/sendai_phase13_review_manifest.json"
SCHEMA_PATH = ROOT / "schemas/evidence_packet.schema.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sendai_challenge_part10_counts_and_coverage_are_exact():
    data = load(DATA_PATH)
    summary = data["summary"]

    assert summary["prior_reviewed_record_count"] == 27
    assert summary["batch_reviewed_record_count"] == 3
    assert summary["cumulative_reviewed_record_count"] == 30
    assert summary["total_source_project_count"] == 108
    assert summary["remaining_record_count"] == 78
    assert summary["complete"] is False


def test_sendai_challenge_part10_records_are_exact_and_source_reported():
    records = load(DATA_PATH)["records"]
    assert len(records) == 3
    assert [record["project_name_ja"] for record in records] == [
        "認知症地域支援推進事業",
        "生涯学習を通じた共生社会推進事業",
        "ひきこもり者地域支援事業",
    ]
    assert [record["source_pdf_page_index_0_based"] for record in records] == [
        37,
        38,
        40,
    ]
    assert [record["source_reported_evaluation"] for record in records] == [
        "circle",
        "circle",
        "circle",
    ]
    assert [record["responsible_bureau_ja"] for record in records] == [
        "健康福祉局",
        "教育局",
        "健康福祉局",
    ]
    assert [record["lead_section_ja"] for record in records] == [
        "地域包括ケア推進課",
        "生涯学習課",
        "障害者支援課",
    ]


def test_sendai_challenge_part10_evidence_is_one_to_one_and_valid():
    data = load(DATA_PATH)
    packets = load(EVIDENCE_PATH)
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert len(packets) == 3
    assert {packet["subject_id"] for packet in packets} == {
        record["id"] for record in data["records"]
    }
    assert {packet["id"] for packet in packets} == {
        record["evidence_id"] for record in data["records"]
    }
    assert all(list(validator.iter_errors(packet)) == [] for packet in packets)
    assert all(packet["subject_type"] == "project" for packet in packets)
    assert all(packet["review_status"] == "reviewed" for packet in packets)


def test_sendai_manifest_keeps_part10_history_without_freezing_later_progress():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}
    part10 = facts["sendai-challenge-project-records-part10"]

    assert part10["value"] == 3
    assert part10["cumulative_value"] == 30
    assert part10["source_reported_breakdown"] == {"circle": 3}
    assert "累計30/108" in part10["interpretation_boundary"]
    assert "残り78事業" in part10["interpretation_boundary"]
    assert "independent Jichi Insight achievement scores" in manifest[
        "quality_boundary"
    ]
