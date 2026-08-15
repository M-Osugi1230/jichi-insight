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
    EVIDENCE_DIR
    / "sapporo_action_plan_children_youth_main_projects_goal1_candidates_evidence.json",
    EVIDENCE_DIR
    / "sapporo_action_plan_children_youth_main_projects_goal2_candidates_evidence.json",
    EVIDENCE_DIR
    / "sapporo_action_plan_children_youth_main_projects_goal3_candidates_evidence.json",
]
OTHER_CATALOG = (
    CATALOG_DIR / "sapporo_action_plan_children_youth_other_projects_candidates.json"
)
SOURCE_INDEX = CATALOG_DIR / "sapporo_action_plan_project_source_index.json"
READINESS = CATALOG_DIR / "sapporo_phase13_completion_readiness.json"
POLICY_SOURCES = CATALOG_DIR / "sapporo_policy_sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_main_records():
    return [record for path in GOAL_CATALOGS for record in load(path)["records"]]


def test_children_youth_main_candidates_have_exact_74_rows_by_goal():
    catalogs = [load(path) for path in GOAL_CATALOGS]
    records = load_main_records()

    assert [catalog["summary"]["candidate_record_count"] for catalog in catalogs] == [
        23,
        30,
        21,
    ]
    assert len(records) == 74
    assert [record["candidate_order"] for record in records] == list(range(1, 75))
    assert len({record["id"] for record in records}) == 74
    assert sum(record["goal"] == 1 for record in records) == 23
    assert sum(record["goal"] == 2 for record in records) == 30
    assert sum(record["goal"] == 3 for record in records) == 21
    assert all(
        record["candidate_status"] == "draft_identity_cost_target_transcribed"
        for record in records
    )


def test_children_youth_main_candidates_have_one_to_one_evidence():
    records = load_main_records()
    packets = [
        packet
        for path in GOAL_EVIDENCE
        for packet in load(path)["evidence_packets"]
    ]

    assert len(packets) == len(records) == 74
    assert {packet["candidate_id"] for packet in packets} == {
        record["id"] for record in records
    }
    assert len({packet["evidence_id"] for packet in packets}) == 74
    assert all(
        packet["draft_pdf_page_index_0_based"]
        == packet["draft_printed_page_label"] + 5
        for packet in packets
    )


def test_children_youth_candidate_inventory_is_exact_121_without_promotion():
    main_records = load_main_records()
    other = load(OTHER_CATALOG)
    index = load(SOURCE_INDEX)
    children = next(
        field
        for field in index["machizukuri_field_sources"]
        if field["field_id"] == "children_youth"
    )

    assert len(main_records) == 74
    assert other["summary"]["candidate_record_count"] == 47
    assert len(main_records) + other["summary"]["candidate_record_count"] == 121
    assert children["field_total_project_count"] == 121
    assert children["candidate_project_record_count"] == 121
    assert children["candidate_main_project_record_count"] == 74
    assert children["candidate_other_project_record_count"] == 47
    assert children["reviewed_final_identity_count"] == 0
    assert children["action_plan_reviewed_progress_increment"] == 0

    summary = index["summary"]
    assert summary["individual_project_records_reviewed"] == 276
    assert summary["remaining_action_plan_project_records"] == 323
    assert summary["candidate_project_records_pending_final_identity_crosscheck"] == 121


def test_children_youth_page56_revision_is_description_only_boundary():
    goal3 = load(GOAL_CATALOGS[2])
    records = {record["id"]: record for record in goal3["records"]}
    cooling = records["school_facility_air_conditioning"]
    evidence = load(GOAL_EVIDENCE[2])
    packet = next(
        item
        for item in evidence["evidence_packets"]
        if item["candidate_id"] == "school_facility_air_conditioning"
    )

    assert cooling["draft_printed_page_label"] == 56
    assert cooling["planned_project_cost_yen"] == 13_760_000_000
    assert cooling["target_raw_ja"] == "2022：－ ⇒ 2027：292校"
    assert "description" in cooling["revision_note"]
    assert goal3["revision_crosscheck"]["printed_page_56_intersects_this_goal"] is True
    assert evidence["revision_crosscheck"]["changed_field"] == (
        "project_description_text_only"
    )
    assert packet["evidence_status"] == (
        "draft_candidate_location_reviewed_description_revision_not_promoted"
    )


def test_children_youth_candidate_queue_is_reflected_in_readiness_and_sources():
    readiness = load(READINESS)
    layer = next(
        item
        for item in readiness["verified_reviewed_layers"]
        if item["layer"] == "action_plan_project_records"
    )
    gate = next(
        item
        for item in readiness["blocking_gates"]
        if item["id"] == "action-plan-project-records"
    )
    sources = {record["id"]: record for record in load(POLICY_SOURCES)["records"]}
    source = sources["sapporo-action-plan-2023-projects-children-youth"]

    assert layer["reviewed_record_count"] == 276
    assert layer["candidate_queue_record_count"] == 121
    assert layer["candidate_queue_main_record_count"] == 74
    assert layer["candidate_queue_other_record_count"] == 47
    assert layer["candidate_queue_reviewed_final_identity_count"] == 0
    assert gate["candidate_reconciliation_scope"] == 121
    assert gate["reviewed_scope"] == 276
    assert gate["remaining_scope"] == 323

    assert source["field_total_project_count"] == 121
    assert source["candidate_project_record_count"] == 121
    assert source["candidate_main_project_record_count"] == 74
    assert source["candidate_other_project_record_count"] == 47
    assert source["reviewed_final_identity_count"] == 0
    assert source["action_plan_reviewed_progress_increment"] == 0
