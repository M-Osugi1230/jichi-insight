from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/asahikawa_phase15_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/phase15_municipality_completion.schema.json"
SOURCES = ROOT / "data/catalog/asahikawa_phase15_sources.json"
STRUCTURE = ROOT / "data/catalog/asahikawa_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/asahikawa_current_progress_review_summary.json"
PLAN_REVIEW = ROOT / "data/reviewed/asahikawa-city/plan_review.json"
FISCAL = ROOT / "data/reviewed/asahikawa-city/fiscal_records.json"
EVIDENCE = ROOT / "data/reviewed/asahikawa-city/evidence_packets.json"
MUNICIPALITY = ROOT / "data/reviewed/asahikawa-city/municipality.json"
FISCAL_SCHEMA = ROOT / "schemas/fiscal_record.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/evidence_packet.schema.json"
MUNICIPALITY_SCHEMA = ROOT / "schemas/municipality.schema.json"
QUEUE = ROOT / "data/catalog/phase15_core_capital_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_path: Path, instance):
    return list(
        Draft202012Validator(
            load(schema_path), format_checker=FormatChecker()
        ).iter_errors(instance)
    )


def test_asahikawa_completion_contract_validates():
    completion = load(COMPLETION)
    assert validate(COMPLETION_SCHEMA, completion) == []
    assert completion["phase"] == 15
    assert completion["status"] == "reviewed_complete"
    assert completion["official_code"] == "012041"
    assert completion["name_ja"] == "旭川市"


def test_asahikawa_completion_paths_exist():
    completion = load(COMPLETION)
    for key, value in completion["review_package"].items():
        if key == "counts":
            continue
        assert (ROOT / value).is_file(), (key, value)


def test_asahikawa_reviewed_municipality_validates():
    municipality = load(MUNICIPALITY)
    assert validate(MUNICIPALITY_SCHEMA, municipality) == []
    assert municipality["id"] == "jp-local-012041"
    assert municipality["municipality_type"] == "core_city"
    assert municipality["data_status"] == "reviewed"


def test_asahikawa_source_catalog_is_official_and_located():
    sources = load(SOURCES)
    assert sources["official_code"] == "012041"
    assert len(sources["sources"]) == 7
    assert len({source["id"] for source in sources["sources"]}) == 7
    for source in sources["sources"]:
        assert source["official_url"].startswith(
            "https://www.city.asahikawa.hokkaido.jp/"
        )
        assert source["evidence_location"]
        assert source["use_boundary"]


def test_asahikawa_current_policy_structure_matches_declared_depth():
    structure = load(STRUCTURE)
    plan = structure["current_plan"]
    counts = structure["counts"]

    assert plan["start_fiscal_year"] == 2016
    assert plan["end_fiscal_year"] == 2027
    assert plan["version"] == "基本計画 令和5年12月改定版"

    assert counts == {
        "basic_goals": 5,
        "basic_policies": 13,
        "current_plan_measures": 34,
        "priority_themes": 3,
        "implementation_basic_policies": 13,
    }
    assert len(plan["basic_goals"]) == 5
    assert len(plan["basic_policies"]) == 13
    assert len(plan["priority_themes"]) == 3
    assert plan["declared_measure_count"] == 34


def test_asahikawa_plan_review_has_stable_evidence_locations():
    review = load(PLAN_REVIEW)

    assert review["review_status"] == "reviewed"
    assert len(review["records"]) == 6
    assert all(record["decision"] == "accepted" for record in review["records"])
    assert all(record["evidence_location"] for record in review["records"])
    assert all(
        record["source_url"].startswith("https://www.city.asahikawa.hokkaido.jp/")
        for record in review["records"]
    )


def test_asahikawa_progress_preserves_evaluation_and_transition_boundaries():
    progress = load(PROGRESS)
    current = progress["current_promotion_plan"]

    assert current["period"] == "2024年度～2027年度"
    assert current["current_revision"] == "2026年6月改訂"
    assert current["design"]["annual_project_group_revision"] is True
    assert current["design"]["pdca_cycle"] is True
    assert (
        current["source_reported_indicator_appendix"]["status"]
        == "official_current_values_and_achievement_rates_published"
    )
    assert "独自政策達成判定" in progress["current_plan_inspection"]["boundary"]
    assert (
        progress["successor_plan_transition"]["status"]
        == "preparation_evidence_only"
    )
    assert "推測" in progress["successor_plan_transition"]["boundary"]


def test_asahikawa_fiscal_records_validate_and_keep_exact_states():
    records = load(FISCAL)
    assert len(records) == 3
    for record in records:
        assert validate(FISCAL_SCHEMA, record) == []

    by_id = {record["id"]: record for record in records}
    budget = by_id["jp-local-012041-fiscal-2026-total-expenditure"]
    revenue = by_id["jp-local-012041-fiscal-2024-total-revenue"]
    expenditure = by_id["jp-local-012041-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 181_800_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 182_479_594_406
    assert expenditure["amount_yen"] == 180_794_635_444


def test_asahikawa_evidence_packets_validate_and_match_fiscal_records():
    packets = load(EVIDENCE)
    fiscal_ids = {record["id"] for record in load(FISCAL)}

    assert len(packets) == 3
    for packet in packets:
        assert validate(EVIDENCE_SCHEMA, packet) == []
        assert packet["subject_id"] in fiscal_ids
        assert packet["review_status"] == "reviewed"
        assert all(claim["decision"] == "accepted" for claim in packet["claims"])
        assert all(claim["location_note"] for claim in packet["claims"])


def test_asahikawa_completion_keeps_indicator_detail_deferred():
    completion = load(COMPLETION)
    assert all(completion["quality_gate"].values())
    assert len(completion["deferred_depth"]) == 6

    deferred_ids = {row["id"] for row in completion["deferred_depth"]}
    assert "current-promotion-plan-indicator-detail" in deferred_ids
    assert "successor-comprehensive-plan-adoption" in deferred_ids
    assert "policy-outcome-causal-and-cross-city-comparability" in deferred_ids

    boundary = completion["completion_boundary"]
    assert "評価指標の全件identity/value" in boundary
    assert "Jichi Insight独自の政策達成度" in boundary
    assert "因果効果" in boundary
    assert "ランキング" in boundary


def test_asahikawa_is_complete_and_aomori_is_next():
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}

    assert by_code["012025"]["status"] == "reviewed_complete"
    assert by_code["012041"]["status"] == "reviewed_complete"
    assert by_code["012041"]["completion_path"] == (
        "data/catalog/asahikawa_phase15_completion.json"
    )
    assert by_code["022012"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 2
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 64
    assert queue["summary"]["next_official_code"] == "022012"
