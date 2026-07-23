#!/usr/bin/env python3
"""Materialize Miyagi measure 16 actuals without bridging changed definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPDATED_AT = "2026-07-23"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(
            f"Expected one {label} replacement, found {text.count(old)}"
        )
    return text.replace(old, new)


def update_catalog() -> None:
    path = ROOT / "data/entities/policy/miyagi_kpi_catalog_measure16.json"
    catalog = load(path)
    by_number = {item["target_group_number"]: item for item in catalog["items"]}

    for number in (114, 115, 117, 118, 119):
        by_number[number]["actual_linkage_status"] = "linked"
    by_number[116]["actual_linkage_status"] = "needs_review"

    by_number[114]["comparability_note_original"] = (
        "評価書の令和5年度6.7点・令和6年度6.6点を接続する。"
        "評価書R6目標7.3点と現行R9目標7.5点を分離する。"
    )
    by_number[115]["comparability_note_original"] = (
        "累計面積であり、単年度の新規取得面積へ変換しない。"
        "評価書R6目標20,000haと現行R9目標22,340haを分離する。"
    )
    by_number[116]["comparability_note_original"] = (
        "現行計画はイノシシ・ニホンジカの推定生息数、評価書は捕獲数であり、"
        "算定対象と数値の方向が異なる。2系列を独立して保持し、捕獲数を"
        "推定生息数の実績へ直接接続しない。"
    )
    by_number[117]["comparability_note_original"] = (
        "累計参加人数を単年度参加人数へ変換しない。"
        "評価書R6目標66,500人と現行R9目標72,500人を分離する。"
    )
    by_number[118]["comparability_note_original"] = (
        "評価書の令和5年度76,759ha・令和6年度75,381haを接続する。"
        "現況値より低い中期末目標を独自に方向評価しない。"
    )
    by_number[119]["comparability_note_original"] = (
        "評価書の令和6年度5,996人を現行計画の現況値へ接続する。"
        "現況値が中期末目標を上回っていても達成判定や目標修正を行わない。"
    )
    catalog["reviewed_at"] = UPDATED_AT
    write_json(path, catalog)


def update_manifest() -> None:
    path = ROOT / "data/catalog/miyagi_policy_review_manifest.json"
    manifest = load(path)
    manifest.update(
        {
            "updated_at": UPDATED_AT,
            "actual_linked_target_group_count": 87,
            "actual_linked_indicator_series_count": 100,
            "actual_linkage_review_needed_series_count": 17,
            "actual_result_row_count": 468,
            "actual_evidence_packet_count": 117,
        }
    )
    work_packages = {item["id"]: item for item in manifest["work_packages"]}
    work_packages["evaluation_linkage"]["deliverable"] = (
        "Measures 1 through 16 have one hundred direct annual-result links, "
        "seventeen review records, four hundred sixty-eight annual rows, and "
        "one hundred seventeen Evidence Packets."
    )
    manifest["open_questions"] = [
        "Complete the seventeen open definition and scope reviews.",
        (
            "Keep the measure 16 wild-boar and sika-deer capture-count series "
            "separate from the current estimated-population series unless an "
            "official definition bridge is verified."
        ),
        (
            "Locate complete four-year annual-result counterparts for current "
            "series that remain unmatched or only partially represented."
        ),
        "Connect the final FY2025 results source to the remaining 49 indicator series.",
        "Review measure 17 against the final FY2025 results source next.",
        (
            "Keep official achievement rates tied to the evaluation document's "
            "R6 targets, not the current plan's R9 targets."
        ),
        "Keep the FY2026 draft separate from any future final version.",
    ]
    write_json(path, manifest)


def update_wave1_queue() -> None:
    path = ROOT / "data/catalog/wave1_policy_review_queue.json"
    queue = load(path)
    miyagi = next(
        item for item in queue["items"] if item["prefecture_code"] == "04"
    )
    miyagi["next_action"] = (
        "KPI本文128目標・149系列は全件Reviewed済み。100系列を年度評価へ直接接続し、"
        "17系列を定義・範囲の要確認として分離した。残る49系列の年度実績接続を継続する。"
    )
    queue["updated_at"] = UPDATED_AT
    write_json(path, queue)


def update_web_loader() -> None:
    path = ROOT / "apps/web/lib/miyagiActuals.ts"
    text = path.read_text(encoding="utf-8")

    measure15_import = (
        'import measure15Actuals from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure15_2024.json";\n'
    )
    measure16_imports = (
        measure15_import
        + 'import measure16Evidence from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure16_2024_evidence_packets.json";\n'
        + 'import measure16Actuals from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure16_2024.json";\n'
    )
    text = replace_once(
        text,
        measure15_import,
        measure16_imports,
        "measure16 imports",
    )

    old_actual_spread = (
        "  ...measure15Actuals.records,\n"
        "] as MiyagiKpiActualLink[];"
    )
    new_actual_spread = (
        "  ...measure15Actuals.records,\n"
        "  ...measure16Actuals.records,\n"
        "] as MiyagiKpiActualLink[];"
    )
    text = replace_once(
        text,
        old_actual_spread,
        new_actual_spread,
        "measure16 actual spread",
    )

    old_evidence_spread = "  ...measure15Evidence,\n];"
    new_evidence_spread = (
        "  ...measure15Evidence,\n"
        "  ...measure16Evidence,\n"
        "];"
    )
    text = replace_once(
        text,
        old_evidence_spread,
        new_evidence_spread,
        "measure16 evidence spread",
    )

    old_fiscal_source = (
        "  subjectFiscalYear: measure15Actuals.subject_fiscal_year,\n"
        "  evaluationFiscalYear: measure15Actuals.evaluation_fiscal_year,"
    )
    new_fiscal_source = (
        "  subjectFiscalYear: measure16Actuals.subject_fiscal_year,\n"
        "  evaluationFiscalYear: measure16Actuals.evaluation_fiscal_year,"
    )
    text = replace_once(
        text,
        old_fiscal_source,
        new_fiscal_source,
        "latest fiscal-year source",
    )
    path.write_text(text, encoding="utf-8")


def update_tests() -> None:
    totals_path = ROOT / "tests/test_miyagi_catalog_totals.py"
    totals = totals_path.read_text(encoding="utf-8")
    replacements = [
        (
            'manifest["actual_linked_target_group_count"] == 82',
            'manifest["actual_linked_target_group_count"] == 87',
        ),
        (
            'manifest["actual_linked_indicator_series_count"] == 95',
            'manifest["actual_linked_indicator_series_count"] == 100',
        ),
        (
            'manifest["actual_linkage_review_needed_series_count"] == 15',
            'manifest["actual_linkage_review_needed_series_count"] == 17',
        ),
        (
            'manifest["actual_result_row_count"] == 440',
            'manifest["actual_result_row_count"] == 468',
        ),
        (
            'manifest["actual_evidence_packet_count"] == 110',
            'manifest["actual_evidence_packet_count"] == 117',
        ),
    ]
    for old, new in replacements:
        totals = replace_once(totals, old, new, old)
    totals_path.write_text(totals, encoding="utf-8")

    queue_path = ROOT / "tests/test_wave1_policy_review_queue.py"
    queue_test = queue_path.read_text(encoding="utf-8")
    old_queue_assertion = (
        'assert all(token in items["04"]["next_action"] for token in '
        '["128", "149", "95", "15", "54"])'
    )
    new_queue_assertion = (
        'assert all(token in items["04"]["next_action"] for token in '
        '["128", "149", "100", "17", "49"])'
    )
    queue_test = replace_once(
        queue_test,
        old_queue_assertion,
        new_queue_assertion,
        "Miyagi queue totals",
    )
    queue_path.write_text(queue_test, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_manifest()
    update_wave1_queue()
    update_web_loader()
    update_tests()


if __name__ == "__main__":
    main()
