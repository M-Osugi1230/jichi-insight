import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data/catalog/phase9_execution_queue.json"
SCHEMA_PATH = ROOT / "schemas/phase9_execution_queue.schema.json"
COVERAGE_PATH = ROOT / "data/catalog/prefecture_coverage.json"
SOURCE_REGISTRY_PATHS = [
    ROOT / "data/catalog/phase9_tohoku_source_registry.json",
    ROOT / "data/catalog/phase9_kanto_source_registry.json",
    ROOT / "data/catalog/phase9_chubu_source_registry.json",
    ROOT / "data/catalog/phase9_kinki_source_registry.json",
    ROOT / "data/catalog/phase9_chugoku_source_registry.json",
    ROOT / "data/catalog/phase9_shikoku_source_registry.json",
    ROOT / "data/catalog/phase9_kyushu_okinawa_source_registry.json",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase9_execution_queue_matches_schema():
    validator = Draft202012Validator(
        load(SCHEMA_PATH), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(load(QUEUE_PATH))) == []


def test_queue_contains_exactly_the_remaining_thirty_eight_prefectures():
    queue = load(QUEUE_PATH)
    coverage_codes = {
        record["prefecture_code"] for record in load(COVERAGE_PATH)["records"]
    }
    anchor_codes = set(queue["excluded_regional_anchor_codes"])
    item_codes = [item["prefecture_code"] for item in queue["items"]]

    assert len(item_codes) == 38
    assert len(set(item_codes)) == 38
    assert set(item_codes) == coverage_codes - anchor_codes
    assert set(item_codes).isdisjoint(anchor_codes)


def test_regional_batches_cover_every_queue_item_once():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    batched_codes = [
        code for batch in queue["batches"] for code in batch["prefecture_codes"]
    ]
    assert len(batched_codes) == len(set(batched_codes)) == 38
    assert set(batched_codes) == set(items)
    for batch in queue["batches"]:
        for code in batch["prefecture_codes"]:
            assert items[code]["batch_id"] == batch["id"]
            assert items[code]["region"] == batch["region"]


def test_all_seven_batches_are_reviewed_without_overstating_achievement():
    queue = load(QUEUE_PATH)
    items = {item["prefecture_code"]: item for item in queue["items"]}
    source_codes = {
        code
        for path in SOURCE_REGISTRY_PATHS
        for code in load(path)["prefecture_codes"]
    }

    assert queue["status"] == "complete"
    assert len(source_codes) == 38
    assert source_codes == set(items)
    assert all(item["policy_plan_status"] == "indexed" for item in queue["items"])
    assert all(
        item["current_plan_status"] == "current_confirmed"
        for item in queue["items"]
    )
    assert all(
        items[code]["numeric_target_status"] == "reviewed" for code in source_codes
    )
    assert all(items[code]["review_status"] == "reviewed" for code in source_codes)
    assert all(
        "主要数値目標の原文行・資料位置・EvidenceをReviewed化済み"
        in items[code]["next_action"]
        for code in source_codes
    )
    assert sum(
        item["numeric_target_status"] in {"indexed", "reviewed"}
        for item in queue["items"]
    ) == 38
    assert sum(
        item["numeric_target_status"] == "reviewed" for item in queue["items"]
    ) == 38


def test_quality_rules_block_incomparable_rankings_and_unsupported_numbers():
    rules = " ".join(load(QUEUE_PATH)["quality_rules"])
    assert "Evidence Packet" in rules
    assert "比較不能な指標はランキング対象外" in rules
    assert "欠損、未設定、非公表、0を別状態" in rules
    assert "単位、期間、母集団" in rules
    assert "再掲指標" in rules
