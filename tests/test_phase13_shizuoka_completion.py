from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/shizuoka-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/shizuoka_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/shizuoka_current_policy_structure.json"
AVAILABILITY = ROOT / "data/catalog/shizuoka_current_progress_availability.json"
MANIFEST = ROOT / "data/catalog/shizuoka_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/shizuoka_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/shizuoka_phase13_completion.schema.json"
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


def test_shizuoka_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "221007"
    assert municipality["name_ja"] == "静岡市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_shizuoka_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 9
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert all(row["organization"] == "静岡市" for row in sources)
    assert all(row["confidence"] == "high" for row in sources)


def test_shizuoka_current_policy_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)
    fields = structure["fields"]

    assert structure["review_status"] == "reviewed_aggregate_policy_structure"
    assert structure["plan_period"] == "2026年度～2035年度"
    assert structure["implementation_plan_period"] == "2026年度～2030年度"
    assert structure["hierarchy"] == {
        "plan_layer_count": 3,
        "field_count": 9,
        "policy_count": 45,
        "implementation_plan_year_count": 5,
    }
    assert len(fields) == 9
    assert sum(row["policy_count"] for row in fields) == 45
    assert [row["field_name"] for row in fields] == [
        "共生・福祉・健康",
        "防災・消防・防犯",
        "こども・子育て",
        "教育・人づくり",
        "経済・産業",
        "観光・スポーツ・文化",
        "都市・社会基盤",
        "環境・森林",
        "行政経営",
    ]
    assert structure["implementation_semantics"]["revision_cycle"] == "annual"
    assert structure["implementation_semantics"]["horizon_years"] == 5
    assert "成果指標" in structure["implementation_semantics"][
        "policy_to_outcome_indicator_rule"
    ]


def test_shizuoka_current_result_unavailability_is_explicit_and_version_safe():
    availability = load(AVAILABILITY)

    current = availability["current_plan_annual_progress"]
    historical = availability["historical_progress"]

    assert availability["review_status"] == (
        "reviewed_current_result_not_yet_available"
    )
    assert current["status"] == "not_yet_available"
    assert "同一version" in current["promotion_rule"]
    assert historical["plan_version"] == "第4次静岡市総合計画"
    assert historical["reporting_fiscal_year"] == 2024
    assert historical["decision"] == (
        "historical_only_do_not_reuse_as_current_actual"
    )
    assert "流用せず" in availability["quality_boundary"]


def test_shizuoka_fiscal_top_lines_are_exact_and_state_separated():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-221007-fiscal-2026-total-revenue"]
    revenue = records["jp-local-221007-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-221007-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 403_500_000_000
    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 387_089_852_000
    assert expenditure["amount_yen"] == 376_221_432_000


def test_shizuoka_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_shizuoka_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    availability = load(AVAILABILITY)
    fiscal = load(FISCAL)

    assert counts["current_plan_layers"] == structure["hierarchy"][
        "plan_layer_count"
    ] == 3
    assert counts["current_fields"] == structure["hierarchy"]["field_count"] == 9
    assert counts["current_policies_aggregate"] == structure["hierarchy"][
        "policy_count"
    ] == 45
    assert counts["current_implementation_plan_years"] == structure["hierarchy"][
        "implementation_plan_year_count"
    ] == 5
    assert counts["current_annual_progress_records"] == 0
    assert availability["current_plan_annual_progress"]["status"] == (
        "not_yet_available"
    )
    assert counts["historical_progress_routes_preserved"] == 1
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_shizuoka_completion_deferred_depth_is_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    detail = deferred["current-policy-and-indicator-detail"]
    assert detail["policy_count"] == 45
    assert "推測しない" in detail["boundary"]

    progress = deferred["current-plan-annual-progress"]
    assert "not_yet_available" in progress["boundary"]
    assert "同一version" in progress["boundary"]

    linkage = deferred["fourth-to-fifth-plan-versioned-linkage"]
    assert "名称類似だけで確定しない" in linkage["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("2026～2035", "9分野", "45政策", "403,500,000,000"):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_shizuoka_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 7
    assert len(manifest["remaining_work"]) == 5
    assert "not-yet-available" in manifest["quality_boundary"]
    assert "not reused" in manifest["quality_boundary"]
    assert "No independent policy-achievement judgment" in manifest[
        "quality_boundary"
    ]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_shizuoka_completion_remains_stable_as_later_city_reviews_advance():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["221007"]["status"] == "reviewed_complete"
    assert by_code["221309"]["status"] == "reviewed_complete"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    )
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    )
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    )
    in_progress = [
        row for row in queue["execution_queue"]
        if row["status"] == "review_in_progress"
    ]
    if in_progress:
        assert queue["summary"]["next_official_code"] == in_progress[0]["official_code"]


def test_shizuoka_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
