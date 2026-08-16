from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
DENOMINATORS_PATH = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fields_by_id():
    return {record["field_id"]: record for record in load(INDEX_PATH)["machizukuri_field_sources"]}


def test_sapporo_project_source_index_has_exact_official_document_spine():
    index = load(INDEX_PATH)
    fields = index["machizukuri_field_sources"]
    chapter3 = index["chapter3_sources"]

    assert index["official_code"] == "011002"
    assert index["status"] == "action_plan_project_identity_review_complete_599_of_599"
    assert [record["sequence"] for record in fields] == list(range(1, 9))
    assert [(record["field_id"], record["field_ja"]) for record in fields] == [
        ("children_youth", "子ども・若者"),
        ("daily_life", "生活・暮らし"),
        ("community", "地域"),
        ("safety_security", "安全・安心"),
        ("economy", "経済"),
        ("sports_culture", "スポーツ・文化"),
        ("environment", "環境"),
        ("urban_space", "都市空間"),
    ]
    assert [record["sequence"] for record in chapter3] == [1, 2]


def test_sapporo_final_field_denominators_are_exact_and_sum_to_599():
    denominators = load(DENOMINATORS_PATH)
    counts = {field["field_id"]: field["final_project_count"] for field in denominators["field_denominators"]}
    assert counts == {
        "children_youth": 121,
        "daily_life": 85,
        "community": 47,
        "safety_security": 70,
        "economy": 74,
        "sports_culture": 51,
        "environment": 74,
        "urban_space": 77,
    }
    assert sum(counts.values()) == 599
    assert denominators["plan_total"]["final_project_count"] == 599
    assert denominators["draft_comparison"]["net_project_count_change"] == -1


def test_all_eight_fields_are_complete_with_exact_final_counts():
    fields = fields_by_id()
    expected = {
        "children_youth": (121, 74, 47),
        "daily_life": (85, 62, 23),
        "community": (47, 27, 20),
        "safety_security": (70, 43, 27),
        "economy": (74, 61, 13),
        "sports_culture": (51, 36, 15),
        "environment": (74, 47, 27),
        "urban_space": (77, 56, 21),
    }
    for field_id, (total, main, other) in expected.items():
        field = fields[field_id]
        assert field["field_total_project_count"] == total
        assert field["reviewed_project_record_count"] == total
        assert field["reviewed_main_project_record_count"] == main
        assert field["reviewed_other_project_record_count"] == other
        assert field["field_total_project_count_reviewed"] is True
        assert field["unresolved_project_record_count"] == 0


def test_direct_final_reconciliation_findings_are_preserved():
    fields = fields_by_id()

    children = fields["children_youth"]
    assert children["page_count"] == 16
    assert children["source_lineage"]["direct_final_visual_check_status"] == "reviewed_all_pages"
    assert children["source_lineage"]["printed_page_56_changed_field"] == "project_description_text_only"

    daily = fields["daily_life"]
    assert daily["blocked_page_labels"] == []
    assert daily["source_lineage"]["direct_final_visual_checked_page"] == 68

    community = fields["community"]
    assert community["page_count"] == 7
    assert community["reviewed_page_labels"] == list(range(73, 79))

    economy = fields["economy"]
    assert economy["page_count"] == 13
    assert economy["reviewed_page_labels"] == list(range(90, 102))

    sports = fields["sports_culture"]
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["reconciliation_confidence"] == "direct_final_visual"
    assert sports["direct_final_page104_confirmation"] is True

    environment = fields["environment"]
    assert environment["page_count"] == 10
    assert environment["final_department_correction_count"] == 5


def test_sapporo_project_source_index_global_progress_is_exact_599_of_599():
    index = load(INDEX_PATH)
    summary = index["summary"]
    aggregate = index["plan_level_aggregate"]

    assert aggregate["planned_project_count"] == 599
    assert aggregate["planned_project_cost_yen"] == 1_785_400_000_000
    assert summary["total_action_plan_project_count"] == 599
    assert summary["final_field_denominators_reviewed"] == 8
    assert summary["individual_project_records_reviewed"] == 599
    assert summary["fully_reviewed_field_project_records"] == 599
    assert summary["partially_reviewed_field_project_records"] == 0
    assert summary["candidate_project_records_pending_final_identity_crosscheck_total"] == 0
    assert summary["candidate_fields_pending_final_identity_crosscheck"] == []
    assert summary["remaining_action_plan_project_records"] == 0
    assert summary["action_plan_identity_review_status"] == "complete_599_of_599"


def test_sapporo_project_source_index_keeps_separate_403_target_boundary_explicit():
    boundary = load(INDEX_PATH)["quality_boundary"]
    assert "All 599 Action Plan 2023 project identities" in boundary
    assert "five environment department corrections" in boundary
    assert "sports/culture" in boundary
    assert "403 annual-progress target items" in boundary


def test_sapporo_manifest_keeps_city_in_progress_after_identity_completion():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    assert manifest["status"] == "review_in_progress"
    assert facts["action-plan-project-source-index"]["value"] == 10
    assert facts["action-plan-safety-security-project-records-complete"]["value"] == 70
    complete = facts["action-plan-all-project-identities-complete"]
    assert complete["value"] == 599
    assert complete["main_project_record_count"] == 406
    assert complete["other_project_record_count"] == 193
