from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "data/reviewed/kyoto-city"
MUNICIPALITY = REVIEWED / "municipality.json"
PLAN = REVIEWED / "plan_review.json"
FISCAL = REVIEWED / "fiscal_records.json"
EVIDENCE = REVIEWED / "evidence_packets.json"
SOURCES = ROOT / "data/catalog/kyoto_phase13_sources.json"
STRUCTURE = ROOT / "data/catalog/kyoto_current_strategy_structure.json"
PROGRESS = ROOT / "data/catalog/kyoto_current_progress_review_summary.json"
MANIFEST = ROOT / "data/catalog/kyoto_phase13_policy_review_manifest.json"
COMPLETION = ROOT / "data/catalog/kyoto_phase13_completion.json"
COMPLETION_SCHEMA = ROOT / "schemas/kyoto_phase13_completion.schema.json"
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


def test_kyoto_shared_municipality_fiscal_and_evidence_contracts():
    municipality = load(MUNICIPALITY)
    fiscal = load(FISCAL)
    evidence = load(EVIDENCE)

    assert validate("municipality.schema.json", municipality) == []
    assert all(validate("fiscal_record.schema.json", row) == [] for row in fiscal)
    assert all(validate("evidence_packet.schema.json", row) == [] for row in evidence)
    assert municipality["official_code"] == "261009"
    assert municipality["name_ja"] == "京都市"
    assert municipality["municipality_type"] == "designated_city"
    assert municipality["data_status"] == "reviewed"
    assert municipality["fiscal_years"] == [2024, 2026]
    assert len(fiscal) == len(evidence) == 3


def test_kyoto_source_catalog_matches_municipality_sources():
    municipality = load(MUNICIPALITY)
    sources = load(SOURCES)["records"]

    assert len(sources) == 9
    assert set(municipality["sources"]) == {row["id"] for row in sources}
    assert {row["organization"] for row in sources} <= {
        "京都市", "京都市監査事務局"
    }
    assert all(row["confidence"] == "high" for row in sources)


def test_kyoto_current_strategy_structure_is_complete_at_declared_level():
    structure = load(STRUCTURE)

    assert structure["review_status"] == "reviewed_current_strategy_policy_identity"
    assert structure["basic_concept_period"] == "2026年～2050年"
    assert structure["strategy_period"] == "2024年度～2027年度"
    assert structure["hierarchy"] == {
        "current_strategy_policy_count": 6,
        "strategy_component_count": 3,
        "strategic_perspective_count": 3,
    }
    assert len(structure["policies"]) == 6
    assert len({row["policy_code"] for row in structure["policies"]}) == 6
    assert structure["strategy_components"] == [
        "政策",
        "しごとの仕方改革",
        "持続可能な行財政運営の確立",
    ]
    assert structure["strategic_perspectives"] == ["ひらく", "きわめる", "つなぐ"]
    assert "市会へ報告" in structure["progress_management_semantics"][
        "review_route"
    ]


def test_kyoto_current_and_historical_progress_lanes_are_separate():
    progress = load(PROGRESS)

    current = progress["current_strategy_lane"]
    historical = progress["historical_basic_plan_lane"]

    assert current["plan_version"] == "新京都戦略（2024年度～2027年度）"
    assert current["policy_count"] == 6
    assert current["evidence_role"] == "current_strategy_implementation_progress"

    assert historical["plan_version"] == "はばたけ未来へ！京（みやこ）プラン2025"
    assert historical["policy_field_count"] == 27
    assert historical["evidence_role"] == "historical_policy_progress_and_evaluation"
    assert "流用しない" in historical["boundary"]

    roles = {row["id"]: row for row in progress["accountability_lanes"]}
    assert roles["municipal_progress_reporting"]["role"] == "source_reported_progress"
    assert roles["city_assembly_reporting"]["role"] == (
        "legislative_accountability_route"
    )
    assert roles["settlement_audit"]["role"] == "financial_accountability_route"


def test_kyoto_fiscal_top_lines_keep_exact_budget_and_rounded_settlement():
    records = {row["id"]: row for row in load(FISCAL)}
    budget = records["jp-local-261009-fiscal-2026-total-revenue"]
    revenue = records["jp-local-261009-fiscal-2024-total-revenue"]
    expenditure = records["jp-local-261009-fiscal-2024-total-expenditure"]

    assert budget["stage"] == "initial_budget"
    assert budget["amount_yen"] == 1_007_967_000_000

    assert revenue["stage"] == expenditure["stage"] == "settlement"
    assert revenue["amount_yen"] == 980_100_000_000
    assert expenditure["amount_yen"] == 971_800_000_000
    assert "rounded source value" in revenue["note"]
    assert "rounded source value" in expenditure["note"]


def test_kyoto_completion_contract_matches_schema_and_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(COMPLETION_SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    for key, value in completion["review_package"].items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_kyoto_completion_counts_derive_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    structure = load(STRUCTURE)
    progress = load(PROGRESS)
    fiscal = load(FISCAL)

    assert counts["current_strategy_policies"] == structure["hierarchy"][
        "current_strategy_policy_count"
    ] == 6
    assert counts["current_strategy_components"] == structure["hierarchy"][
        "strategy_component_count"
    ] == 3
    assert counts["strategic_perspectives"] == structure["hierarchy"][
        "strategic_perspective_count"
    ] == 3
    assert counts["historical_basic_plan_policy_fields"] == progress[
        "historical_basic_plan_lane"
    ]["policy_field_count"] == 27
    assert counts["accountability_roles"] == len(
        progress["accountability_lanes"]
    ) == 3
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_kyoto_completion_deferred_depth_is_explicit():
    completion = load(COMPLETION)
    deferred = {row["id"]: row for row in completion["deferred_depth"]}

    assert deferred["current-policy-kpi-detail"]["policy_count"] == 6
    assert "推測しない" in deferred["current-policy-kpi-detail"]["boundary"]
    assert "旧京プラン2025" in deferred["current-progress-record-detail"]["boundary"]
    assert "文言類似だけで" in deferred["basic-concept-strategy-linkage"]["boundary"]

    assert all(
        row["status"] == "deferred_not_required_for_v1_completion"
        for row in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in (
        "2026～2050",
        "2024～2027",
        "6政策",
        "27政策分野",
        "1,007,967,000,000",
        "980,100,000,000",
        "971,800,000,000",
    ):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_kyoto_policy_manifest_keeps_non_inference_boundaries():
    manifest = load(MANIFEST)

    assert manifest["status"] == "review_in_progress"
    assert len(manifest["reviewed_facts"]) == 9
    assert len(manifest["remaining_work"]) == 5
    assert "not reused" in manifest["quality_boundary"]
    assert "rounded source values" in manifest["quality_boundary"]
    assert "No independent policy-achievement judgment" in manifest[
        "quality_boundary"
    ]
    assert "causal attribution" in manifest["quality_boundary"]
    assert "cross-city comparability" in manifest["quality_boundary"]


def test_kyoto_completion_advances_queue_to_osaka():
    queue = load(QUEUE)
    completion = load(COMPLETION)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["261009"]["status"] == "reviewed_complete"
    assert by_code["271004"]["status"] == "review_in_progress"
    assert queue["summary"]["reviewed_complete_count"] == statuses.count(
        "reviewed_complete"
    ) == 12
    assert queue["summary"]["review_in_progress_count"] == statuses.count(
        "review_in_progress"
    ) == 1
    assert queue["summary"]["pending_record_review_count"] == statuses.count(
        "pending_record_review"
    ) == 5
    assert queue["summary"]["next_official_code"] == "271004"


def test_kyoto_completion_quality_gates_are_all_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"
