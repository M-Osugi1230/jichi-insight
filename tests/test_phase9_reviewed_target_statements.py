import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data/catalog/phase9_review_summary.json"
SUMMARY_SCHEMA_PATH = ROOT / "schemas/phase9_review_summary.schema.json"
HISTORY_PATH = ROOT / "data/catalog/phase9_plan_history.json"
HISTORY_SCHEMA_PATH = ROOT / "schemas/phase9_plan_history.schema.json"
CATALOG_SCHEMA_PATH = ROOT / "schemas/phase9_reviewed_target_statements.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas/phase9_target_statement_evidence.schema.json"
QUEUE_PATH = ROOT / "data/catalog/phase9_execution_queue.json"
REVIEWED_DIR = ROOT / "data/reviewed/phase9"
EVIDENCE_DIR = ROOT / "data/evidence/phase9"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(instance_path: Path, schema_path: Path) -> None:
    validator = Draft202012Validator(
        load(schema_path), format_checker=FormatChecker()
    )
    errors = sorted(validator.iter_errors(load(instance_path)), key=lambda error: list(error.path))
    assert errors == [], "\n".join(error.message for error in errors[:20])


def test_phase9_summary_and_history_match_schemas():
    validate(SUMMARY_PATH, SUMMARY_SCHEMA_PATH)
    validate(HISTORY_PATH, HISTORY_SCHEMA_PATH)


def test_all_thirty_eight_reviewed_catalogs_and_evidence_files_match_schemas():
    summary = load(SUMMARY_PATH)
    expected_codes = [record["prefecture_code"] for record in summary["records"]]
    reviewed_paths = sorted(REVIEWED_DIR.glob("*.json"))
    evidence_paths = sorted(EVIDENCE_DIR.glob("*.json"))

    assert expected_codes == sorted(expected_codes)
    assert len(expected_codes) == len(set(expected_codes)) == 38
    assert [path.stem for path in reviewed_paths] == expected_codes
    assert [path.stem for path in evidence_paths] == expected_codes

    for path in reviewed_paths:
        validate(path, CATALOG_SCHEMA_PATH)
    for path in evidence_paths:
        validate(path, EVIDENCE_SCHEMA_PATH)


def test_reviewed_records_have_one_to_one_evidence_and_source_positions():
    summary = load(SUMMARY_PATH)
    total_records = 0
    total_packets = 0

    for summary_record in summary["records"]:
        code = summary_record["prefecture_code"]
        catalog = load(REVIEWED_DIR / f"{code}.json")
        evidence = load(EVIDENCE_DIR / f"{code}.json")
        records = catalog["records"]
        packets = evidence["packets"]
        record_ids = [record["id"] for record in records]
        evidence_ids = [record["evidence_id"] for record in records]
        packet_ids = [packet["id"] for packet in packets]
        packet_subject_ids = [packet["subject_id"] for packet in packets]

        assert catalog["prefecture_code"] == evidence["prefecture_code"] == code
        assert catalog["reviewed_target_statement_count"] == len(records) >= 1
        assert catalog["evidence_packet_count"] == evidence["packet_count"] == len(packets)
        assert len(record_ids) == len(set(record_ids))
        assert len(evidence_ids) == len(set(evidence_ids))
        assert evidence_ids == packet_ids
        assert record_ids == packet_subject_ids
        assert summary_record["reviewed_target_statement_count"] == len(records)
        assert summary_record["evidence_packet_count"] == len(packets)

        for record in records:
            assert record["review_status"] == "reviewed"
            assert record["policy_achievement_assessment_status"] == "not_assessed"
            assert record["numeric_tokens_original"]
            assert record["target_statement_original"]
            assert record["source_document_url"].startswith("https://")
            assert len(record["source_document_sha256"]) == 64
            assert record["source_location"]["location_kind"]
            assert record["plan_history_boundary"]
            assert record["comparability"]["status"] == "not_comparable"
            assert record["comparability"]["reasons"]

        total_records += len(records)
        total_packets += len(packets)

    assert total_records == summary["reviewed_target_statement_count"]
    assert total_packets == summary["evidence_packet_count"] == total_records
    assert summary["evidence_coverage_percent"] == 100


def test_phase9_never_infers_achievement_or_unverified_comparability():
    summary = load(SUMMARY_PATH)
    assert summary["policy_achievement_assessed_count"] == 0
    assert summary["ranking_eligible_record_count"] == 0
    for path in REVIEWED_DIR.glob("*.json"):
        catalog = load(path)
        assert catalog["policy_achievement_assessment_status"] == "not_assessed"
        assert catalog["ranking_eligibility"] == "excluded_until_comparability_verified"
        assert all(
            record["comparability"]["status"] == "not_comparable"
            for record in catalog["records"]
        )


def test_plan_history_and_execution_queue_cover_the_same_prefectures():
    summary_codes = {
        record["prefecture_code"] for record in load(SUMMARY_PATH)["records"]
    }
    history = load(HISTORY_PATH)
    history_codes = {record["prefecture_code"] for record in history["records"]}
    queue = load(QUEUE_PATH)
    queue_codes = {record["prefecture_code"] for record in queue["items"]}

    assert summary_codes == history_codes == queue_codes
    assert len(summary_codes) == 38
    assert history["tracked_history_count"] == 38
    assert all(record["history_status"] == "tracked" for record in history["records"])
    assert queue["status"] == "complete"
    assert all(record["review_status"] == "reviewed" for record in queue["items"])
