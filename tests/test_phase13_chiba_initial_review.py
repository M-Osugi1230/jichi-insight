from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/chiba-city"
MUNICIPALITY = REVIEWED / "municipality.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
PLAN = REVIEWED / "plan_review.json"
SOURCES = ROOT / "data/catalog/chiba_phase13_sources.json"
MANIFEST = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return list(validator.iter_errors(instance))


def test_chiba_reviewed_identity_and_fiscal_records_match_shared_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "121002"
    assert municipality["name_ja"] == "千葉市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3
    assert {packet["subject_id"] for packet in evidence} == {row["id"] for row in fiscal}


def test_chiba_reviewed_sources_are_official_and_cycle_bounded():
    municipality = load(MUNICIPALITY)
    source_records = load(SOURCES)["records"]
    sources = {row["id"]: row for row in source_records}

    assert len(sources) == 9
    assert set(municipality["sources"]) == set(sources)
    assert all(row["organization"] == "千葉市" for row in source_records)
    assert all(row["url"].startswith("https://www.city.chiba.jp/") for row in source_records)
    assert all(row["confidence"] == "high" for row in source_records)
    assert sources["chiba-implementation-plan-2026-2028"]["review_status"] == (
        "reviewed_core_structure_and_project_universe_aggregate"
    )
    assert sources["chiba-implementation-plan-2023-2025"]["review_status"] == (
        "reviewed_historical_cycle_identity"
    )
    assert "360事業" in sources["chiba-implementation-progress-2024-settlement"]["boundary"]


def test_chiba_current_plan_structure_and_unique_project_universe_are_exact():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    structure = records["chiba-current-policy-structure"]
    projects = records["chiba-current-project-universe"]

    assert structure["value"] == 8
    assert structure["policy_count"] == 23
    assert structure["measure_count"] == 67
    assert projects["value"] == 189
    assert projects["unit"] == "unique_projects"
    assert projects["field_breakdown"] == {
        "environment_nature": 30,
        "safety_security": 31,
        "health_welfare": 18,
        "children_education": 34,
        "community": 7,
        "culture_sports": 15,
        "urban_transport": 32,
        "regional_economy": 22,
    }
    assert sum(projects["field_breakdown"].values()) == 189
    assert "重複" in projects["statement"]


def test_chiba_current_and_historical_implementation_cycles_are_separate():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    current = records["chiba-current-implementation-plan-period"]
    prior = records["chiba-prior-implementation-plan-period"]
    progress = records["chiba-2024-progress-universe"]

    assert current["value"] == "2026年度～2028年度"
    assert prior["value"] == "2023年度～2025年度"
    assert current["evidence_role"] == "current_implementation_layer"
    assert prior["evidence_role"] == "historical_implementation_layer"
    assert progress["evidence_role"] == "historical_annual_progress_scope"
    assert progress["value"] == 360
    assert "現行189事業とは異なる旧版母集団" in progress["review_note"]


def test_chiba_historical_progress_aggregate_is_exact_and_source_reported():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    progress = records["chiba-2024-progress-evaluation-aggregate"]
    breakdown = progress["source_reported_breakdown"]

    assert breakdown == {
        "completed": 4,
        "at_least_80_below_100": 248,
        "below_80": 106,
        "other": 2,
        "at_least_80_total": 252,
        "at_least_80_percent": 70.0,
    }
    assert 4 + 248 + 106 + 2 == progress["value"] == 360
    assert breakdown["completed"] + breakdown["at_least_80_below_100"] == 252
    assert "政策成果" in progress["review_note"]
    assert "他都市比較" in progress["review_note"]


def test_chiba_current_progress_method_keeps_project_quantity_and_kpi_distinct():
    records = {row["id"]: row for row in load(PLAN)["records"]}
    method = records["chiba-current-progress-methodology"]

    assert method["value"] == "project_quantity_and_kgi_kpi_review"
    assert "予算時・決算時" in method["statement"]
    assert "KGI/KPI" in method["statement"]
    assert "単一スコアへ統合しない" in method["review_note"]


def test_chiba_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-121002-fiscal-2026-total-revenue"]
    revenue = records["jp-local-121002-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-121002-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 541_700_000_000
    assert set(budget["sources"]) == {
        "chiba-budget-2026",
        "chiba-budget-2026-enactment",
    }
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 529_470_000_000
    assert expenditure["amount_yen"] == 525_677_000_000


def test_chiba_initial_review_contract_remains_valid_as_identity_depth_advances():
    manifest = load(MANIFEST)
    queue = load(QUEUE)
    facts = {row["id"]: row for row in manifest["reviewed_facts"]}
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    project_fact = facts["chiba-current-project-universe"]

    assert manifest["status"] == "review_in_progress"
    assert by_code["121002"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == 3
    assert queue["summary"]["review_in_progress_count"] == 1
    assert queue["summary"]["pending_record_review_count"] == 14
    assert project_fact["value"] == 189
    assert project_fact["identity_records_reviewed"] >= 30
    assert project_fact["identity_records_remaining"] <= 159
    assert (
        project_fact["identity_records_reviewed"]
        + project_fact["identity_records_remaining"]
        == 189
    )
    assert facts["chiba-2024-progress-universe"]["value"] == 360
    assert facts["chiba-2026-general-account-initial-budget"]["value"] == 541_700_000_000
    assert project_fact["source_id"] == "chiba-implementation-plan-2026-2028-full-pdf"
    assert "project identity" in manifest["quality_boundary"]
    assert "source capture" in manifest["quality_boundary"].replace("-", " ")
