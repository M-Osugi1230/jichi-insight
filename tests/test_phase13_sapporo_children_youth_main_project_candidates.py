from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "data/catalog"
EVIDENCE_DIR = ROOT / "data/evidence"
GOAL_CATALOGS = [
    CATALOG_DIR / "sapporo_action_plan_children_youth_main_projects_goal1_candidates.json",
    CATALOG_DIR / "sapporo_action_plan_children_youth_main_projects_goal2_candidates.json",
    CATALOG_DIR / "sapporo_action_plan_children_youth_main_projects_goal3_candidates.json",
]
GOAL_EVIDENCE = [
    EVIDENCE_DIR / "sapporo_action_plan_children_youth_main_projects_goal1_candidates_evidence.json",
    EVIDENCE_DIR / "sapporo_action_plan_children_youth_main_projects_goal2_candidates_evidence.json",
    EVIDENCE_DIR / "sapporo_action_plan_children_youth_main_projects_goal3_candidates_evidence.json",
]
OTHER_CATALOG = CATALOG_DIR / "sapporo_action_plan_children_youth_other_projects_candidates.json"
FINAL = CATALOG_DIR / "sapporo_action_plan_children_youth_final_reconciliation.json"
FINAL_EVIDENCE = EVIDENCE_DIR / "sapporo_action_plan_children_youth_final_evidence.json"
SOURCE_INDEX = CATALOG_DIR / "sapporo_action_plan_project_source_index.json"
QUEUE_REGISTRY = CATALOG_DIR / "sapporo_action_plan_candidate_queue_registry.json"
POLICY_SOURCES = CATALOG_DIR / "sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_main_records():
    return [record for path in GOAL_CATALOGS for record in load(path)["records"]]


def test_children_youth_historical_main_candidates_have_exact_74_rows_by_goal():
    catalogs = [load(path) for path in GOAL_CATALOGS]
    records = load_main_records()
    assert [catalog["summary"]["candidate_record_count"] for catalog in catalogs] == [23, 30, 21]
    assert len(records) == 74
    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert len({record["id"] for record in records}) == 74
    assert sum(record["goal"] == 1 for record in records) == 23
    assert sum(record["goal"] == 2 for record in records) == 30
    assert sum(record["goal"] == 3 for record in records) == 21


def test_children_youth_historical_main_candidates_have_one_to_one_evidence():
    records = load_main_records()
    packets = [packet for path in GOAL_EVIDENCE for packet in load(path)["evidence_packets"]]
    assert len(packets) == len(records) == 74
    assert {packet["candidate_id"] for packet in packets} == {record["id"] for record in records}


def test_children_youth_final_reconciliation_promotes_all_121_rows():
    final = load(FINAL)
    other = load(OTHER_CATALOG)
    evidence = load(FINAL_EVIDENCE)
    index = load(SOURCE_INDEX)
    children = next(field for field in index["machizukuri_field_sources"] if field["field_id"] == "children_youth")

    assert len(load_main_records()) == 74
    assert other["summary"]["candidate_record_count"] == 47
    assert final["status"] == "final_field_direct_visual_review_complete"
    assert final["summary"]["reviewed_project_record_count"] == 121
    assert final["summary"]["main_project_record_count"] == 74
    assert final["summary"]["other_project_record_count"] == 47
    assert final["summary"]["action_plan_reviewed_count_after"] == 599
    assert evidence["document_boundary"]["main_rows_crosschecked"] == 74
    assert evidence["document_boundary"]["other_rows_crosschecked"] == 47
    assert children["reviewed_project_record_count"] == 121
    assert children["unresolved_project_record_count"] == 0


def test_children_youth_page56_revision_is_description_only_boundary():
    goal3 = load(GOAL_CATALOGS[2])
    records = {record["id"]: record for record in goal3["records"]}
    cooling = records["school_facility_air_conditioning"]
    final = load(FINAL)
    revision = final["reconciliation"]["known_revision_confirmation"]

    assert cooling["draft_printed_page_label"] == 56
    assert cooling["planned_project_cost_yen"] == 13_760_000_000
    assert cooling["target_raw_ja"] == "2022：－ ⇒ 2027：292校"
    assert revision["candidate_order"] == 61
    assert revision["project_name_ja"] == "学校施設冷房設備整備事業"
    assert revision["official_revision_scope"] == "project_description_text_only"
    assert revision["final_identity_department_cost_target_unchanged"] is True


def test_children_youth_candidate_queue_is_exhausted_after_final_promotion():
    queue = load(QUEUE_REGISTRY)
    sources = {record["id"]: record for record in load(POLICY_SOURCES)["records"]}
    source = sources["sapporo-action-plan-2023-projects-children-youth"]

    assert queue["candidate_fields"] == []
    assert queue["final_reviewed_identity_count"] == 599
    assert queue["remaining_final_identity_count"] == 0
    assert source["field_total_project_count"] == 121
    assert source["reviewed_project_record_count"] == 121
    assert source["reviewed_main_project_record_count"] == 74
    assert source["reviewed_other_project_record_count"] == 47
    assert source["direct_final_all_pages_confirmation"] is True
