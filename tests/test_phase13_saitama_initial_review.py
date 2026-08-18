from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROOT = ROOT / "data/reviewed/saitama-city"
MUNICIPALITY = REVIEWED_ROOT / "municipality.json"
FISCAL = REVIEWED_ROOT / "fiscal_records.json"
EVIDENCE = REVIEWED_ROOT / "evidence_packets.json"
PLAN = REVIEWED_ROOT / "plan_review.json"
SOURCES = ROOT / "data/catalog/saitama_phase13_sources.json"
MANIFEST = ROOT / "data/catalog/saitama_phase13_policy_review_manifest.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return list(validator.iter_errors(instance))


def test_saitama_reviewed_identity_and_fiscal_records_match_shared_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "111007"
    assert municipality["name_ja"] == "さいたま市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3
    assert {packet["subject_id"] for packet in evidence} == {
        row["id"] for row in fiscal
    }


def test_saitama_reviewed_sources_are_official_and_cycle_bounded():
    municipality = load(MUNICIPALITY)
    records = load(SOURCES)["records"]
    sources = {row["id"]: row for row in records}

    assert len(sources) == 10
    assert set(municipality["sources"]) == set(sources)
    assert all(row["organization"] == "さいたま市" for row in records)
    assert all(
        row["url"].startswith("https://www.city.saitama.lg.jp/")
        for row in records
    )
    assert all(row["confidence"] == "high" for row in records)
    assert sources["saitama-implementation-plan-2026-2030"]["review_status"] == (
        "reviewed_core_methodology_and_258_project_identities"
    )
    assert sources["saitama-implementation-plan-2026-2030-policy-projects"][
        "review_status"
    ] == "reviewed_210_of_210_project_identities"
    assert sources[
        "saitama-implementation-plan-2026-2030-quality-management-projects"
    ]["review_status"] == "reviewed_48_of_48_project_identities"
    assert sources["saitama-implementation-plan-2021-2025"]["review_status"] == (
        "reviewed_historical_cycle_identity"
    )
    assert "299" in sources["saitama-progress-2024"]["boundary"]
    assert "2021～2025" in sources["saitama-progress-2024"]["boundary"]


def test_saitama_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}

    budget = records["jp-local-111007-fiscal-2026-total-revenue"]
    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 716_000_000_000
    assert set(budget["sources"]) == {
        "saitama-policy-statement-2026",
        "saitama-budget-2026",
    }

    revenue = records["jp-local-111007-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-111007-fiscal-2024-total-expenditure"]
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 725_870_000_000
    assert expenditure["amount_yen"] == 716_754_000_000
    assert revenue["fiscal_year"] == expenditure["fiscal_year"] == 2024


def test_saitama_current_and_historical_implementation_cycles_are_separate():
    records = {row["id"]: row for row in load(PLAN)["records"]}

    current = records["saitama-current-implementation-plan-period"]
    prior = records["saitama-prior-implementation-plan-period"]
    progress = records["saitama-2024-progress-review-universe"]

    assert current["value"] == "2026年度～2030年度"
    assert prior["value"] == "2021年度～2025年度"
    assert current["evidence_role"] == "current_implementation_layer"
    assert prior["evidence_role"] == "historical_implementation_layer"
    assert progress["evidence_role"] == "historical_annual_progress_scope"
    assert "2024年度実績" in current["review_note"]
    assert "新計画の実績として扱わない" in current["review_note"]
    assert "現行2026～2030" in prior["review_note"]


def test_saitama_2024_progress_distinguishes_occurrences_from_unique_projects():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    universe = records["saitama-2024-progress-review-universe"]
    projects = records["saitama-2024-project-evaluation-aggregate"]

    assert universe["value"] == 370
    assert universe["unit"] == "displayed_project_occurrences"
    assert universe["unique_project_count"] == 299
    assert universe["measure_count"] == 63

    policy = projects["source_reported_breakdown"]["policy_fields"]
    quality = projects["source_reported_breakdown"]["quality_city_management"]
    assert policy == {
        "total": 316,
        "a": 82,
        "b": 185,
        "c": 49,
        "a_or_b": 267,
        "a_or_b_percent": 84.5,
    }
    assert quality == {
        "total": 54,
        "a": 17,
        "b": 27,
        "c": 10,
        "a_or_b": 44,
        "a_or_b_percent": 81.5,
    }
    assert policy["total"] + quality["total"] == 370


def test_saitama_2024_measure_and_kpi_aggregates_preserve_source_boundaries():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    measures = records["saitama-2024-measure-evaluation-aggregate"]
    kpis = records["saitama-2024-priority-strategy-kpi-aggregate"]

    policy = measures["source_reported_breakdown"]["policy_fields"]
    quality = measures["source_reported_breakdown"]["quality_city_management"]
    assert policy["total"] == 50
    assert quality["total"] == 13
    assert policy["total"] + quality["total"] == 63
    assert policy["on_track"] == 22
    assert policy["mostly_on_track"] == 13
    assert policy["somewhat_delayed"] == 14
    assert policy["delayed"] == 1
    assert quality["on_track"] == 7
    assert quality["mostly_on_track"] == 2
    assert quality["somewhat_delayed"] == 4
    assert quality["delayed"] == 0

    kpi = kpis["source_reported_breakdown"]
    assert kpi == {
        "above_baseline": 26,
        "below_baseline": 11,
        "not_characterized_in_landing_aggregate": 3,
    }
    assert sum(kpi.values()) == 40
    assert "公式個票確認なしに割り当てない" in kpis["review_note"]


def test_saitama_current_measurement_methodology_separates_subjective_and_objective():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    method = records["saitama-current-implementation-measurement-methodology"]

    assert method["value"] == "subjective_and_objective_outcome_indicators"
    assert method["evidence_role"] == "current_progress_methodology"
    assert "主観指標" in method["statement"]
    assert "客観指標" in method["statement"]
    assert "因果効果" in method["review_note"]


def test_saitama_manifest_and_queue_show_real_review_in_progress():
    manifest = load(MANIFEST)
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    facts = {row["id"]: row for row in manifest["reviewed_facts"]}

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 12
    assert len(manifest["remaining_work"]) == 4
    assert by_code["111007"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 2
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 15
    assert facts["saitama-current-project-identity-universe"]["value"] == 258
    assert facts["saitama-current-project-identity-universe"][
        "identity_records_remaining"
    ] == 0
    assert facts["saitama-2024-progress-universe"][
        "displayed_project_occurrence_count"
    ] == 370
    assert facts["saitama-2024-progress-universe"]["unique_project_count"] == 299
    assert facts["saitama-2026-general-account-initial-budget"]["value"] == (
        716_000_000_000
    )
    assert "258/258 unique project codes" in manifest["quality_boundary"]
