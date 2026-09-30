from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/hakodate_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCES = ROOT / "data/catalog/hakodate_phase15_sources.json"
STRUCTURE = ROOT / "data/catalog/hakodate_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/hakodate_current_progress_review_summary.json"
PLAN_REVIEW = ROOT / "data/reviewed/hakodate-city/plan_review.json"
FISCAL = ROOT / "data/reviewed/hakodate-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/hakodate-city/evidence_packets.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_hakodate_completion_contract_validates():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "012025"
    assert completion["name_ja"] == "函館市"


def test_hakodate_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_hakodate_source_catalog_is_official_and_located():
    sources = load(SOURCES)
    assert sources["official_code"] == "012025"
    assert len(sources["sources"]) == 8

    ids = set()
    for source in sources["sources"]:
        ids.add(source["id"])
        assert source["official_url"].startswith(
            "https://www.city.hakodate.hokkaido.jp/"
        )
        assert source["evidence_location"]
        assert source["use_boundary"]
    assert len(ids) == 8


def test_hakodate_current_policy_structure_is_complete_at_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["start_fiscal_year"] == 2017
    assert plan["end_fiscal_year"] == 2026
    assert plan["status"] == "current_final_year"

    assert counts == {
        "priority_projects": 2,
        "basic_goals": 5,
        "current_plan_measures": 20,
        "implementation_strategy_basic_goals": 4,
    }
    assert len(plan["priority_projects"]) == 2
    assert len(plan["basic_goals"]) == 5
    assert sum(len(goal["measures"]) for goal in plan["basic_goals"]) == 20


def test_hakodate_plan_review_has_stable_evidence_locations():
    review = load(PLAN_REVIEW)

    assert review["review_status"] == "reviewed"
    assert len(review["records"]) == 6
    assert all(record["decision"] == "accepted" for record in review["records"])
    assert all(record["evidence_location"] for record in review["records"])
    assert all(
        record["source_url"].startswith("https://www.city.hakodate.hokkaido.jp/")
        for record in review["records"]
    )


def test_hakodate_progress_keeps_historical_current_and_draft_separate():
    progress = load(PROGRESS)

    current = progress["current_implementation_strategy"]
    historical = progress["historical_evaluation_context"]
    successor = progress["successor_plan_transition"]

    assert current["period"] == "2025年度～2029年度"
    assert current["current_period_kpi_actuals"]["status"] == "not_promoted_in_v1"

    classes = historical["source_reported_classes"]
    assert historical["strategy"] == "第2期函館市活性化総合戦略"
    assert historical["kpi_evaluation_count"] == 41
    assert sum(classes.values()) == 41
    assert "第3期" in historical["boundary"]

    assert successor["status"] == "draft_public_comment_open"
    assert successor["proposed_start_fiscal_year"] == 2027
    assert successor["proposed_end_fiscal_year"] == 2036
    assert successor["public_comment_start"] == "2026-09-07"
    assert successor["public_comment_end"] == "2026-10-21"
    assert "adopted current planではない" in successor["boundary"]


def test_hakodate_fiscal_records_validate_and_keep_exact_states():
    schema = load(FISCAL_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records = load(FISCAL)

    assert len(records) == 3
    for record in records:
        assert list(validator.iter_errors(record)) == []

    by_id = {record["id"]: record for record in records}

    budget = by_id["jp-local-012025-fiscal-2026-total-expenditure"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 154_100_000_000
    assert "予算案" in budget["metric_label"]

    revenue = by_id["jp-local-012025-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-012025-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 144_921_264_078
    assert expenditure["amount_yen"] == 142_388_719_238


def test_hakodate_evidence_packets_validate_and_match_fiscal_records():
    schema = load(EVIDENCE_SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert list(validator.iter_errors(packet)) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])


def test_hakodate_completion_quality_gate_and_deferred_depth_are_explicit():
    completion = load(COMPLETION)
    assert all(completion["quality_gate"].values())
    assert len(completion["deferred_depth"]) == 6
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in completion["deferred_depth"]
    )

    boundary = completion["completion_boundary"]
    assert "第3期戦略の個別KPI" in boundary
    assert "パブリックコメント中の素案" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "因果効果" in boundary
    assert "ランキング" in boundary


def test_hakodate_remains_reviewed_complete_as_queue_advances():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    hakodate = by_code["012025"]
    assert hakodate["status"] == "reviewed_complete"
    assert hakodate["completion_path"] == (
        "data/catalog/hakodate_phase15_completion.json"
    )
    assert (ROOT / hakodate["completion_path"]).is_file()
