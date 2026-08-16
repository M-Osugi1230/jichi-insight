from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
DENOMINATORS_PATH = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
MANIFEST_PATH = ROOT / "data/catalog/sapporo_phase13_policy_review_manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_sapporo_project_source_index_has_exact_official_document_spine():
    index = load(INDEX_PATH)
    fields = index["machizukuri_field_sources"]
    chapter3 = index["chapter3_sources"]

    assert index["official_code"] == "011002"
    assert index["status"] == "source_documents_indexed_project_review_in_progress"
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
    counts = {
        field["field_id"]: field["final_project_count"]
        for field in denominators["field_denominators"]
    }

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


def test_sapporo_project_source_index_preserves_known_and_pending_page_counts():
    index = load(INDEX_PATH)
    fields = {record["field_id"]: record for record in index["machizukuri_field_sources"]}
    chapter3 = {record["source_id"]: record for record in index["chapter3_sources"]}

    assert fields["children_youth"]["page_count"] == 16
    assert fields["daily_life"]["page_count"] == 13
    assert fields["community"]["page_count"] is None
    assert fields["safety_security"]["page_count"] == 10
    assert fields["economy"]["page_count"] is None
    assert fields["sports_culture"]["page_count"] == 9
    assert fields["environment"]["page_count"] is None
    assert fields["urban_space"]["page_count"] == 12
    assert chapter3["administrative_operations"]["page_count"] == 29
    assert chapter3["fiscal_operations"]["page_count"] is None


def test_sapporo_safety_source_records_complete_field_project_inventory():
    index = load(INDEX_PATH)
    safety = next(
        record for record in index["machizukuri_field_sources"]
        if record["field_id"] == "safety_security"
    )

    assert safety["content_review_status"] == "record_review_complete_at_declared_fields"
    assert safety["reviewed_project_record_count"] == 70
    assert safety["field_total_project_count"] == 70
    assert safety["field_total_project_count_reviewed"] is True
    assert safety["reviewed_page_labels"] == list(range(80, 89))


def test_sapporo_sports_culture_uses_final_51_reconciliation_not_draft_52():
    index = load(INDEX_PATH)
    sports = next(
        record for record in index["machizukuri_field_sources"]
        if record["field_id"] == "sports_culture"
    )

    assert sports["content_review_status"] == (
        "record_review_complete_high_confidence_final_reconciliation"
    )
    assert sports["field_total_project_count"] == 51
    assert sports["reviewed_project_record_count"] == 51
    assert sports["reviewed_main_project_record_count"] == 36
    assert sports["reviewed_other_project_record_count"] == 15
    assert sports["candidate_draft_record_count"] == 52
    assert sports["excluded_draft_candidate_id"] == "winter_olympic_paralympic_related"
    assert sports["reconciliation_confidence"] == "high"
    assert sports["direct_final_page104_confirmation"] is False
    assert sports["field_total_project_count_reviewed"] is True


def test_sapporo_daily_life_is_complete_85_after_direct_page68_review():
    index = load(INDEX_PATH)
    daily = next(
        record for record in index["machizukuri_field_sources"]
        if record["field_id"] == "daily_life"
    )

    assert daily["content_review_status"] == (
        "record_review_complete_at_declared_fields_direct_page68_final"
    )
    assert daily["field_total_project_count"] == 85
    assert daily["field_total_project_count_reviewed"] is True
    assert daily["reviewed_project_record_count"] == 85
    assert daily["unresolved_project_record_count"] == 0
    assert daily["reviewed_main_project_record_count"] == 62
    assert daily["reviewed_other_project_record_count"] == 23
    assert daily["blocked_page_labels"] == []
    assert daily["reviewed_page_labels"] == list(range(60, 72))
    assert daily["source_lineage"]["direct_final_visual_checked_page"] == 68
    assert daily["source_lineage"]["direct_final_visual_check_status"] == "reviewed"


def test_sapporo_remaining_candidate_fields_are_all_registered():
    index = load(INDEX_PATH)
    fields = {record["field_id"]: record for record in index["machizukuri_field_sources"]}

    assert fields["children_youth"]["candidate_project_record_count"] == 121
    assert fields["community"]["candidate_project_record_count"] == 47
    assert fields["economy"]["candidate_project_record_count"] == 74
    assert fields["environment"]["candidate_project_record_count"] == 74
    assert fields["economy"]["candidate_main_project_record_count"] == 61
    assert fields["environment"]["candidate_main_project_record_count"] == 47


def test_sapporo_urban_space_source_records_complete_field_project_inventory():
    index = load(INDEX_PATH)
    urban = next(
        record for record in index["machizukuri_field_sources"]
        if record["field_id"] == "urban_space"
    )

    assert urban["content_review_status"] == "record_review_complete_at_declared_fields"
    assert urban["field_total_project_count"] == 77
    assert urban["reviewed_project_record_count"] == 77
    assert urban["reviewed_main_project_record_count"] == 56
    assert urban["reviewed_other_project_record_count"] == 21
    assert urban["field_total_project_count_reviewed"] is True
    assert urban["source_lineage"]["final_field_project_count"] == 77
    assert urban["source_lineage"]["reviewed_record_count_matches_final_field_count"] is True


def test_sapporo_project_source_index_global_progress_is_exact_283_of_599():
    index = load(INDEX_PATH)
    summary = index["summary"]
    aggregate = index["plan_level_aggregate"]

    assert aggregate["planned_project_count"] == 599
    assert aggregate["planned_project_cost_yen"] == 1_785_400_000_000
    assert summary["total_action_plan_project_count"] == 599
    assert summary["final_field_denominators_reviewed"] == 8
    assert summary["individual_project_records_reviewed"] == 283
    assert summary["fully_reviewed_field_project_records"] == 283
    assert summary["partially_reviewed_field_project_records"] == 0
    assert summary["candidate_project_records_pending_final_identity_crosscheck_total"] == 316
    assert summary["candidate_fields_pending_final_identity_crosscheck"] == [
        "children_youth", "community", "economy", "environment"
    ]
    assert summary["remaining_action_plan_project_records"] == 316
    assert summary["field_denominator_allocation_status"] == "complete_8_fields"


def test_sapporo_project_source_index_keeps_review_boundary_explicit():
    boundary = load(INDEX_PATH)["quality_boundary"]

    assert "sports/culture 51" in boundary
    assert "283/599" in boundary
    assert "life/living 85" in boundary
    assert "remaining 316 identities" in boundary
    assert "403-item" in boundary


def test_sapporo_manifest_still_keeps_city_in_progress():
    manifest = load(MANIFEST_PATH)
    facts = {fact["id"]: fact for fact in manifest["reviewed_facts"]}

    assert manifest["status"] == "review_in_progress"
    source_index = facts["action-plan-project-source-index"]
    assert source_index["value"] == 10
    assert source_index["registry_path"] == (
        "data/catalog/sapporo_action_plan_project_source_index.json"
    )
    safety = facts["action-plan-safety-security-project-records-complete"]
    assert safety["value"] == 70
