from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"
QUEUE_SCHEMA = ROOT / "schemas/phase15_core_capital_review_queue.schema.json"
PHASE14_REGISTRY = ROOT / "data/catalog/phase14_core_capital_target_registry.json"
PHASE14_COMPLETION = ROOT / "data/catalog/phase14_completion.json"
PHASE13_COMPLETION = ROOT / "data/catalog/phase13_completion.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_phase15_queue_validates_and_starts_from_phase14_completion():
    queue = load(QUEUE)
    validator = Draft202012Validator(
        load(QUEUE_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(queue)) == []
    assert queue["phase"] == 15
    assert queue["status"] == "in_progress"
    assert queue["source_phase"] == 14
    assert queue["source_completion_path"] == "data/catalog/phase14_completion.json"
    assert load(PHASE14_COMPLETION)["status"] == "complete"


def test_phase15_queue_matches_exact_phase14_target_universe():
    queue = load(QUEUE)
    registry = load(PHASE14_REGISTRY)

    queued = queue["execution_queue"]
    targets = registry["targets"]

    assert len(queued) == len(targets) == 67
    assert [row["official_code"] for row in queued] == [
        row["official_code"] for row in targets
    ]
    assert [row["standard_area_code"] for row in queued] == [
        row["standard_area_code"] for row in targets
    ]
    assert [row["name_ja"] for row in queued] == [row["name_ja"] for row in targets]
    assert [row["wave"] for row in queued] == [row["wave"] for row in targets]

    for queued_row, target in zip(queued, targets, strict=True):
        assert target["status"] == "source_inventory_complete"
        assert queued_row["phase14_role"] == target["phase14_role"]
        assert queued_row["municipality_type"] == target["municipality_type"]


def test_phase15_queue_excludes_phase13_designated_cities():
    queue = load(QUEUE)
    phase13 = load(PHASE13_COMPLETION)

    phase15_codes = {row["official_code"] for row in queue["execution_queue"]}
    designated_codes = {
        row["official_code"] for row in phase13["reference_implementations"]
    }
    designated_codes.update(
        row["official_code"] for row in phase13["reviewed_completion_contracts"]
    )

    assert len(phase15_codes) == 67
    assert len(designated_codes) == 20
    assert phase15_codes.isdisjoint(designated_codes)


def test_phase15_current_statuses_are_canonical():
    queue = load(QUEUE)
    statuses = Counter(row["status"] for row in queue["execution_queue"])

    assert statuses == {
        "reviewed_complete": 46,
        "pending_record_review": 21,
    }
    assert queue["summary"] == {
        "target_count": 67,
        "reviewed_complete_count": 46,
        "review_in_progress_count": 0,
        "pending_record_review_count": 21,
        "blocked_source_inventory_count": 0,
        "next_official_code": "292010",
    }

    completed = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "reviewed_complete"
    ]
    assert [row["name_ja"] for row in completed] == [
        "函館市",
        "旭川市",
        "青森市",
        "八戸市",
        "盛岡市",
        "秋田市",
        "山形市",
        "福島市",
        "郡山市",
        "いわき市",
        "水戸市",
        "宇都宮市",
        "前橋市",
        "高崎市",
        "川越市",
        "川口市",
        "越谷市",
        "船橋市",
        "柏市",
        "新宿区",
        "八王子市",
        "横須賀市",
        "富山市",
        "金沢市",
        "福井市",
        "甲府市",
        "長野市",
        "松本市",
        "岐阜市",
        "豊橋市",
        "岡崎市",
        "一宮市",
        "豊田市",
        "津市",
        "大津市",
        "豊中市",
        "吹田市",
        "高槻市",
        "枚方市",
        "八尾市",
        "寝屋川市",
        "東大阪市",
        "姫路市",
        "尼崎市",
        "明石市",
        "西宮市",
    ]
    assert completed[0]["completion_path"] == "data/catalog/hakodate_phase15_completion.json"
    assert completed[1]["completion_path"] == "data/catalog/asahikawa_phase15_completion.json"
    assert completed[2]["completion_path"] == "data/catalog/aomori_phase15_completion.json"
    assert completed[3]["completion_path"] == "data/catalog/hachinohe_phase15_completion.json"
    assert completed[4]["completion_path"] == "data/catalog/morioka_phase15_completion.json"
    assert completed[5]["completion_path"] == "data/catalog/akita_phase15_completion.json"
    assert completed[6]["completion_path"] == "data/catalog/yamagata_phase15_completion.json"
    assert completed[7]["completion_path"] == "data/catalog/fukushima_phase15_completion.json"
    assert completed[8]["completion_path"] == "data/catalog/koriyama_phase15_completion.json"
    assert completed[9]["completion_path"] == "data/catalog/iwaki_phase15_completion.json"
    assert completed[10]["completion_path"] == "data/catalog/mito_phase15_completion.json"
    assert completed[11]["completion_path"] == "data/catalog/utsunomiya_phase15_completion.json"
    assert completed[12]["completion_path"] == "data/catalog/maebashi_phase15_completion.json"
    assert completed[13]["completion_path"] == "data/catalog/takasaki_phase15_completion.json"
    assert completed[14]["completion_path"] == "data/catalog/kawagoe_phase15_completion.json"
    assert completed[15]["completion_path"] == "data/catalog/kawaguchi_phase15_completion.json"
    assert completed[16]["completion_path"] == "data/catalog/koshigaya_phase15_completion.json"
    assert completed[17]["completion_path"] == "data/catalog/funabashi_phase15_completion.json"
    assert completed[18]["completion_path"] == "data/catalog/kashiwa_phase15_completion.json"
    assert completed[19]["completion_path"] == "data/catalog/shinjuku_phase15_completion.json"
    assert completed[20]["completion_path"] == "data/catalog/hachioji_phase15_completion.json"
    assert completed[21]["completion_path"] == "data/catalog/yokosuka_phase15_completion.json"
    assert completed[22]["completion_path"] == "data/catalog/toyama_phase15_completion.json"
    assert completed[23]["completion_path"] == "data/catalog/kanazawa_phase15_completion.json"
    assert completed[24]["completion_path"] == "data/catalog/fukui_phase15_completion.json"
    assert completed[25]["completion_path"] == "data/catalog/kofu_phase15_completion.json"
    assert completed[26]["completion_path"] == "data/catalog/nagano_phase15_completion.json"
    assert completed[27]["completion_path"] == "data/catalog/matsumoto_phase15_completion.json"
    assert completed[28]["completion_path"] == "data/catalog/gifu_phase15_completion.json"
    assert completed[29]["completion_path"] == "data/catalog/toyohashi_phase15_completion.json"
    assert completed[30]["completion_path"] == "data/catalog/okazaki_phase15_completion.json"
    assert completed[31]["completion_path"] == "data/catalog/ichinomiya_phase15_completion.json"
    assert completed[32]["completion_path"] == "data/catalog/toyota_phase15_completion.json"
    assert completed[33]["completion_path"] == "data/catalog/tsu_phase15_completion.json"
    assert completed[34]["completion_path"] == "data/catalog/otsu_phase15_completion.json"
    assert completed[35]["completion_path"] == "data/catalog/toyonaka_phase15_completion.json"
    assert completed[36]["completion_path"] == "data/catalog/suita_phase15_completion.json"
    assert completed[37]["completion_path"] == "data/catalog/takatsuki_phase15_completion.json"
    assert completed[38]["completion_path"] == "data/catalog/hirakata_phase15_completion.json"
    assert completed[39]["completion_path"] == "data/catalog/yao_phase15_completion.json"
    assert completed[40]["completion_path"] == "data/catalog/neyagawa_phase15_completion.json"
    assert completed[41]["completion_path"] == "data/catalog/higashiosaka_phase15_completion.json"
    assert completed[42]["completion_path"] == "data/catalog/himeji_phase15_completion.json"
    assert completed[43]["completion_path"] == "data/catalog/amagasaki_phase15_completion.json"
    assert completed[44]["completion_path"] == "data/catalog/akashi_phase15_completion.json"
    assert completed[45]["completion_path"] == "data/catalog/nishinomiya_phase15_completion.json"

    current = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "review_in_progress"
    ]
    assert current == []

    pending = [
        row
        for row in queue["execution_queue"]
        if row["status"] == "pending_record_review"
    ]
    assert pending[0]["name_ja"] == "奈良市"
    assert pending[0]["official_code"] == "292010"
    assert pending[0]["sequence"] == 47
    assert pending[0]["wave"] == 5
    assert pending[0]["completion_path"] is None


def test_phase15_all_source_inventories_exist_and_remain_unreviewed():
    queue = load(QUEUE)

    for row in queue["execution_queue"]:
        path = ROOT / row["source_inventory_path"]
        assert path.is_file(), row
        inventory = load(path)
        assert inventory["official_code"] == row["official_code"]
        assert inventory["name_ja"] == row["name_ja"]
        assert inventory["status"] == "source_inventory_complete"
        assert inventory["review_status"] == "indexed_not_reviewed"


def test_phase15_quality_gate_preserves_non_inference_and_fiscal_states():
    queue = load(QUEUE)
    gate = "\n".join(queue["quality_gate"])

    assert "record-level evidence locator" in gate
    assert "Proposal" in gate
    assert "enacted budget" in gate
    assert "supplementary budget" in gate
    assert "Historical or prior-plan evidence" in gate
    assert "Draft, transition, not-yet-published" in gate
    assert "independent Jichi Insight achievement judgments" in gate
    assert "causal attribution" in gate
    assert "cross-city comparison eligibility" in gate
    assert "regression tests" in gate
