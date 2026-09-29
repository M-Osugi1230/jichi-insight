from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/osaka-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/osaka_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/osaka_current_policy_structure.json"
PROGRESS = ROOT / "data/catalog/osaka_current_progress_review_summary.json"
MANIFEST = ROOT / "data/catalog/osaka_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/osaka_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/osaka_phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(schema_name: str, instance):
    schema = load(ROOT / "schemas" / schema_name)
    return list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            instance
        )
    )


def test_osaka_shared_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "271004"
    assert municipality["name_ja"] == "大阪市"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2025, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_osaka_source_catalog_and_policy_structure():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]
    structure = load(STRUCTURE)

    assert len(sources) == 7
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "大阪市" for row in sources)
    assert all(row["confidence"] == "high" for row in sources)

    assert structure["hierarchy"] == {
        "basic_concept_urban_vision_count": 3,
        "annual_policy_domain_count": 4,
        "annual_policy_initiative_heading_count": 15,
    }
    assert len(structure["urban_visions"]) == 3
    assert sum(len(row["initiative_headings"]) for row in structure["annual_policy_domains"]) == 15
    assert structure["implementation_model"]["multi_year_implementation_plan_asserted"] is False


def test_osaka_decentralized_progress_model_preserved():
    progress = load(PROGRESS)

    assert progress["latest_completed_operating_policy_fiscal_year"] == 2025
    assert progress["organization_lanes"]["ward_count"] == 24
    assert progress["organization_lanes"]["bureau_office_lanes_listed"] == 28
    assert progress["organization_lanes"]["joint_prefecture_city_bureaus_count"] == 2
    assert progress["organization_lanes"]["joint_prefecture_city_bureaus"] == [
        "IR推進局",
        "大阪都市計画局",
    ]
    assert progress["current_fy2026_lane"]["status"] == "in_progress_not_complete_annual_result"
    assert "流用しない" in progress["current_fy2026_lane"]["boundary"]
    assert "Jichi Insight独自" in progress["evaluation_semantics"]["boundary"]


def test_osaka_fiscal_top_lines():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-271004-fiscal-2026-total-revenue"]
    revenue = records["jp-local-271004-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-271004-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 2_188_221_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 2_090_062_147_558
    assert expenditure["amount_yen"] == 2_065_562_115_148


def test_osaka_completion_contract_and_counts():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)

    counts = completion["review_package"]["counts"]
    assert counts == {
        "basic_concept_urban_visions": 3,
        "annual_policy_domains": 4,
        "annual_policy_initiative_headings": 15,
        "ward_operating_policy_lanes": 24,
        "bureau_office_lanes_listed": 28,
        "joint_prefecture_city_bureaus": 2,
        "fiscal_top_line_records": 3,
    }


def test_osaka_completion_boundaries_are_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    assert len(deferred) == 6
    assert "文言類似だけで" in deferred["fy2026-policy-to-operating-policy-linkage"]["boundary"]
    assert "FY2025自己評価" in deferred["fy2026-current-result"]["boundary"]
    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in (
        "3都市像",
        "4領域・15取組見出し",
        "24区",
        "2,188,221,000,000",
        "2,090,062,147,558",
        "2,065,562,115,148",
    ):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_osaka_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 9
    assert len(manifest["remaining_work"]) == 4
    assert "FY2025 self-evaluations are not reused as FY2026 actuals" in manifest["quality_boundary"]
    assert "No citywide aggregate achievement score" in manifest["quality_boundary"]
    assert "causal attribution" in manifest["quality_boundary"]


def test_osaka_completion_advances_queue_to_sakai():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["271004"]["status"] == "reviewed_complete"
    assert by_code["271403"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count("reviewed_complete") == 13
    assert queue["summary"]["review_in_progress_count"] == statuses.count("review_in_progress") == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count("pending_record_review") == 4
    assert queue["summary"]["next_official_code"] == "271403"


def test_osaka_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
