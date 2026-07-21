#!/usr/bin/env python3
"""Advance Phase 8 canonical registries after Okinawa indicator review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATED_AT = "2026-07-22"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def write(relative: str, value: object) -> None:
    (ROOT / relative).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


EVIDENCE_PATHS = {
    "13": [
        "data/catalog/tokyo_policy_target_review_manifest.json",
        "data/reviewed/tokyo_policy_target_cards.json",
        "data/evidence/tokyo_policy_target_card_evidence.json",
    ],
    "23": [
        "data/catalog/aichi_policy_indicator_review_manifest.json",
        "data/reviewed/aichi_policy_indicators.json",
        "data/evidence/aichi_policy_indicator_evidence.json",
    ],
    "27": [
        "data/catalog/osaka_beyond_expo_indicator_review_manifest.json",
        "data/reviewed/osaka_beyond_expo_indicators.json",
        "data/evidence/osaka_beyond_expo_indicator_evidence.json",
    ],
    "34": [
        "data/catalog/hiroshima_revised_vision_indicator_review_manifest.json",
        "data/reviewed/hiroshima_revised_vision_indicators_part1.json",
        "data/reviewed/hiroshima_revised_vision_indicators_part2.json",
        "data/reviewed/hiroshima_revised_vision_indicators_part3.json",
    ],
    "37": [
        "data/catalog/kagawa_extended_plan_indicator_review_manifest.json",
        "data/evidence/kagawa_extended_plan_indicator_evidence_part1.json",
        "data/evidence/kagawa_extended_plan_indicator_evidence_part2.json",
        "data/evidence/kagawa_extended_plan_indicator_evidence_part3.json",
    ],
    "47": [
        "data/catalog/okinawa_midterm_indicator_review_manifest.json",
        "data/evidence/okinawa_midterm_major_indicator_evidence.json",
        "data/evidence/okinawa_midterm_outcome_indicator_evidence_part1.json",
        "data/evidence/okinawa_midterm_outcome_indicator_evidence_part2.json",
        "data/evidence/okinawa_midterm_outcome_indicator_evidence_part3.json",
    ],
}


def update_anchor_registry() -> None:
    registry = load("data/catalog/regional_anchor_source_registry.json")
    registry["updated_at"] = UPDATED_AT
    for record in registry["records"]:
        code = record["prefecture_code"]
        if code in EVIDENCE_PATHS:
            record["anchor_status"] = "reviewed_reference"
            record["numeric_target_status"] = "reviewed"
            record["evidence_paths"] = EVIDENCE_PATHS[code]
    write("data/catalog/regional_anchor_source_registry.json", registry)


def update_publication_registry() -> None:
    registry = load("data/catalog/published_prefecture_pages.json")
    registry["updated_at"] = UPDATED_AT
    if not any(record["prefecture_code"] == "47" for record in registry["records"]):
        registry["records"].append(
            {
                "prefecture_code": "47",
                "route": "/municipalities/okinawa",
                "publication_status": "published",
            }
        )
    registry["records"].sort(key=lambda record: record["prefecture_code"])
    write("data/catalog/published_prefecture_pages.json", registry)


def update_phase7() -> None:
    manifest = load("data/catalog/phase7_completion.json")
    manifest["scope_version"] = UPDATED_AT
    manifest["counts"]["published_prefecture_pages"] = 9
    write("data/catalog/phase7_completion.json", manifest)


def update_phase8() -> None:
    manifest = load("data/catalog/phase8_completion.json")
    manifest["scope_version"] = UPDATED_AT
    manifest["status"] = "complete"
    manifest["updated_at"] = UPDATED_AT
    manifest["counts"] = {
        "regional_anchors": 9,
        "anchors_with_plan_and_kpi_entrances": 9,
        "anchors_with_six_category_source_map": 6,
        "anchors_with_reviewed_numeric_targets": 9,
        "anchors_with_published_prefecture_pages": 9,
        "anchors_pending_numeric_target_review": 0,
    }
    for gate in manifest["gates"]:
        gate["status"] = "passed"
        if gate["id"] == "evidence_packet_review":
            gate["evidence_paths"].extend(
                path
                for path in EVIDENCE_PATHS["47"]
                if path not in gate["evidence_paths"]
            )
        if gate["id"] == "semantic_preservation":
            path = "tests/test_okinawa_midterm_indicators.py"
            if path not in gate["evidence_paths"]:
                gate["evidence_paths"].append(path)
    manifest["next_review_order"] = []
    manifest["scope_note"] = (
        "Phase 8 is complete. All nine regional anchors have official plan and KPI "
        "entrances, Evidence Packet-backed Reviewed numeric targets, published "
        "prefecture pages, semantic-preservation tests, static export coverage and "
        "Production Smoke coverage. Annual actuals and budget-to-outcome linkage "
        "continue as deeper Phase 9 work."
    )
    write("data/catalog/phase8_completion.json", manifest)


def update_phase9() -> None:
    manifest = load("data/catalog/phase9_completion.json")
    manifest["scope_version"] = UPDATED_AT
    manifest["updated_at"] = UPDATED_AT
    manifest["counts"]["evidence_backed_reviewed_prefectures"] = 9
    for gate in manifest["gates"]:
        if gate["id"] == "published_numeric_evidence_coverage":
            path = "data/catalog/okinawa_midterm_indicator_review_manifest.json"
            if path not in gate["evidence_paths"]:
                gate["evidence_paths"].append(path)
        if gate["id"] == "semantic_quality_tests":
            path = "tests/test_okinawa_midterm_indicators.py"
            if path not in gate["evidence_paths"]:
                gate["evidence_paths"].append(path)
    manifest["scope_note"] = (
        "Phase 9 is in progress. All 47 major policy plans are indexed and all nine "
        "regional anchors now have Evidence-backed Reviewed targets. Completion "
        "still requires numeric-target indexing and review for the remaining 38 "
        "prefectures, semantic and history tests, ranking exclusions and nationwide "
        "publication smoke verification."
    )
    write("data/catalog/phase9_completion.json", manifest)


def update_wave1_queue() -> None:
    queue = load("data/catalog/wave1_policy_review_queue.json")
    queue["updated_at"] = UPDATED_AT
    queue["active_prefecture_code"] = None
    queue["completed_prefecture_codes"] = [
        "40",
        "01",
        "04",
        "13",
        "23",
        "27",
        "34",
        "37",
        "47",
    ]
    for item in queue["items"]:
        if item["prefecture_code"] != "47":
            continue
        item["status"] = "reviewed_reference"
        item["source_inventory_status"] = "reviewed"
        item["next_gate"] = "actuals_linkage"
        item["next_action"] = (
            "主要指標36件・成果指標339件、合計375件とEvidence 375件を"
            "Reviewed済み。離島指標32件、SDGs優先課題43件、定性目標9件を"
            "保持し、次に令和4～6年度PDCA実績を定義照合して接続する。"
        )
        item["priority_basis"] = (
            "基本計画、現行中期実施計画、主要指標、成果指標、活動指標、"
            "過年度PDCA評価を別レイヤーで扱う計画階層モデルの基準実装。"
        )
    write("data/catalog/wave1_policy_review_queue.json", queue)


def main() -> None:
    update_anchor_registry()
    update_publication_registry()
    update_phase7()
    update_phase8()
    update_phase9()
    update_wave1_queue()


if __name__ == "__main__":
    main()
