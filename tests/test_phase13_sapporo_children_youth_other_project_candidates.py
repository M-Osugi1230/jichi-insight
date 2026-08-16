from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = (
    ROOT / "data/catalog/sapporo_action_plan_children_youth_other_projects_candidates.json"
)
EVIDENCE_PATH = (
    ROOT
    / "data/evidence/sapporo_action_plan_children_youth_other_projects_candidates_evidence.json"
)
DENOMINATORS_PATH = ROOT / "data/catalog/sapporo_action_plan_final_field_denominators.json"
SOURCE_INDEX_PATH = ROOT / "data/catalog/sapporo_action_plan_project_source_index.json"
FINAL_PATH = ROOT / "data/catalog/sapporo_action_plan_children_youth_final_reconciliation.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_children_youth_other_historical_candidate_inventory_has_exact_47_rows():
    catalog = load(CATALOG_PATH)
    records = catalog["records"]
    summary = catalog["summary"]
    assert catalog["status"] == "draft_candidate_inventory_final_identity_crosscheck_pending"
    assert len(records) == summary["candidate_record_count"] == 47
    assert summary["goal1_candidate_count"] == 26
    assert summary["goal2_candidate_count"] == 10
    assert summary["goal3_candidate_count"] == 11
    assert summary["record_type"] == "other_project"


def test_children_youth_other_candidate_inventory_preserves_goal_and_draft_page_counts():
    records = load(CATALOG_PATH)["records"]
    assert Counter(record["goal"] for record in records) == {1: 26, 2: 10, 3: 11}
    assert Counter(record["draft_page_label"] for record in records) == {
        52: 9,
        53: 17,
        59: 10,
        63: 11,
    }
    assert [record["candidate_order"] for record in records] == list(range(1, 48))
    assert len({record["id"] for record in records}) == 47


def test_children_youth_other_candidate_inventory_preserves_representative_costs():
    records = {record["id"]: record for record in load(CATALOG_PATH)["records"]}
    assert records["private_nursery_subsidy"]["planned_project_cost_yen"] == 15_830_000_000
    assert (
        records["private_nursery_development_subsidy"]["planned_project_cost_yen"] == 7_949_000_000
    )
    assert (
        records["second_child_guidance_center_development"]["planned_project_cost_yen"]
        == 3_451_000_000
    )
    assert (
        records["youth_science_museum_exhibit_zone_development"]["planned_project_cost_yen"]
        == 851_000_000
    )
    assert (
        records["reading_challenge_children_reading_promotion"]["planned_project_cost_yen"]
        == 31_000_000
    )


def test_children_youth_other_candidates_have_one_to_one_draft_evidence():
    catalog = load(CATALOG_PATH)
    evidence = load(EVIDENCE_PATH)
    packets = evidence["evidence_packets"]
    assert len(packets) == len(catalog["records"]) == 47
    assert [packet["candidate_order"] for packet in packets] == list(range(1, 48))
    assert {packet["project_id"] for packet in packets} == {
        record["id"] for record in catalog["records"]
    }


def test_children_youth_final_denominator_and_final_review_are_both_exact_121():
    catalog = load(CATALOG_PATH)
    denominators = load(DENOMINATORS_PATH)
    final = load(FINAL_PATH)
    children = next(
        field
        for field in denominators["field_denominators"]
        if field["field_id"] == "children_youth"
    )

    assert children["final_project_count"] == 121
    assert catalog["final_field_denominator"]["project_count"] == 121
    assert catalog["summary"]["candidate_record_count"] == 47
    assert final["summary"]["reviewed_project_record_count"] == 121
    assert final["summary"]["other_project_record_count"] == 47


def test_children_youth_final_promotion_is_reflected_in_global_reviewed_count():
    index = load(SOURCE_INDEX_PATH)
    children = next(
        field
        for field in index["machizukuri_field_sources"]
        if field["field_id"] == "children_youth"
    )
    assert children["reviewed_project_record_count"] == 121
    assert children["reviewed_other_project_record_count"] == 47
    assert index["summary"]["individual_project_records_reviewed"] == 599
    assert index["summary"]["remaining_action_plan_project_records"] == 0
