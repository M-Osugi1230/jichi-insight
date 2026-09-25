from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COMPLETION = ROOT / "data/catalog/chiba_phase13_completion.json"
SCHEMA = ROOT / "schemas/chiba_phase13_completion.schema.json"
QUEUE = ROOT / "data/catalog/phase13_designated_city_review_queue.json"
POLICY = ROOT / "data/catalog/chiba_phase13_policy_review_manifest.json"
WORK = ROOT / "data/catalog/chiba_current_project_work_item_review_manifest.json"
HIST = ROOT / "data/catalog/chiba_historical_project_identity_review_manifest.json"
LINKAGE = ROOT / "data/catalog/chiba_versioned_project_linkage_review.json"
INDICATORS = ROOT / "data/reviewed/chiba-city/current_policy_indicators.json"
FISCAL = ROOT / "data/reviewed/chiba-city/fiscal_records.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_chiba_completion_contract_matches_schema_and_declared_paths_exist():
    completion = load(COMPLETION)
    validator = Draft202012Validator(
        load(SCHEMA), format_checker=FormatChecker()
    )
    assert list(validator.iter_errors(completion)) == []

    package = completion["review_package"]
    for key, value in package.items():
        if key.endswith("_path"):
            assert (ROOT / value).is_file(), (key, value)


def test_chiba_completion_counts_are_derived_from_reviewed_layers():
    completion = load(COMPLETION)
    counts = completion["review_package"]["counts"]
    work = load(WORK)
    historical = load(HIST)
    linkage = load(LINKAGE)
    indicators = load(INDICATORS)
    fiscal = load(FISCAL)

    assert counts["current_project_identities"] == (
        work["project_identity_coverage"]["reviewed"]
    ) == 189
    assert counts["current_work_items"] == (
        work["work_item_structuring"]["structured_work_items"]
    ) == 406
    assert counts["current_quantitative_policy_indicators"] == (
        indicators["quantitative_indicator_count"]
    ) == 40
    assert counts["current_overall_goal_indicators"] == 1
    assert counts["current_qualitative_constituent_factors_primary"] == (
        indicators["qualitative_constituent_factor_primary_count"]
    ) == 6
    assert counts["historical_project_identities"] == (
        historical["historical_identity_coverage"]["reviewed"]
    ) == 360
    assert counts["historical_repost_occurrences"] == (
        historical["historical_repost_reconciliation"]["displayed_reposts"]
    ) == 68
    assert counts["versioned_reviewed_relations"] == (
        linkage["summary"]["reviewed_relation_count"]
    ) == 66
    assert counts["versioned_strong_rule_relations"] == (
        linkage["summary"]["strong_rule_relation_count"]
    ) == 60
    assert counts["versioned_manual_relations"] == (
        linkage["summary"]["manual_reviewed_relation_count"]
    ) == 6
    assert counts["historical_identities_without_reviewed_relation"] == (
        linkage["summary"]["historical_without_reviewed_relation"]
    ) == 294
    assert counts["current_identities_without_reviewed_relation"] == (
        linkage["summary"]["current_without_reviewed_relation"]
    ) == 123
    assert counts["fiscal_top_line_records"] == len(fiscal) == 3


def test_chiba_completion_deferred_depth_is_explicit_and_not_promoted():
    completion = load(COMPLETION)
    deferred = {item["id"]: item for item in completion["deferred_depth"]}

    versioned = deferred["versioned-linkage-beyond-reviewed-continuations"]
    assert versioned["historical_count"] == 294
    assert versioned["current_count"] == 123
    assert "名称類似" in versioned["boundary"]
    assert "終了" in versioned["boundary"]
    assert "新規" in versioned["boundary"]

    annual = deferred["current-cycle-annual-progress-publication"]
    assert "2024年度進捗360事業" in annual["boundary"]
    assert "流用しない" in annual["boundary"]

    assert all(
        item["status"] == "deferred_not_required_for_v1_completion"
        for item in deferred.values()
    )

    boundary = completion["completion_boundary"]
    for token in ("189", "406", "360", "68", "66", "294", "123"):
        assert token in boundary
    assert "政策達成度" in boundary
    assert "因果効果" in boundary
    assert "他都市比較可能性" in boundary


def test_chiba_completion_remains_stable_as_later_city_reviews_advance():
    completion = load(COMPLETION)
    queue = load(QUEUE)
    by_code = {row["official_code"]: row for row in queue["execution_queue"]}
    statuses = [row["status"] for row in queue["execution_queue"]]

    assert completion["status"] == "reviewed_complete"
    assert by_code["121002"]["status"] == "reviewed_complete"
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


def test_chiba_completion_quality_gates_are_all_explicitly_true():
    completion = load(COMPLETION)
    assert completion["quality_gate"]
    assert all(value is True for value in completion["quality_gate"].values())
    assert completion["completion_depth"] == "declared_review_package_v1"


def test_chiba_completion_keeps_policy_manifest_conservative():
    completion = load(COMPLETION)
    policy = load(POLICY)

    assert policy["status"] == "review_in_progress"
    assert "No independent policy-achievement judgment" in policy["quality_boundary"]
    assert "cross-city comparability" in policy["quality_boundary"]
    assert completion["status"] == "reviewed_complete"
