#!/usr/bin/env python3
"""Materialize Miyagi measure 17 annual-result linkage into canonical state."""

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
    count = text.count(old)
    if count != 1:
        raise ValueError(f"Expected one {label} replacement, found {count}")
    return text.replace(old, new)


def update_catalog() -> None:
    path = ROOT / "data/entities/policy/miyagi_kpi_catalog_measure17.json"
    catalog = load(path)
    by_number = {item["target_group_number"]: item for item in catalog["items"]}

    for number in (120, 122, 123, 124, 125):
        by_number[number]["actual_linkage_status"] = "linked"
    by_number[121]["actual_linkage_status"] = "needs_review"

    by_number[120]["comparability_note_original"] = (
        "評価書は女性防災リーダー養成者数、現行計画は女性防災指導員登録者数と表記する。"
        "対象範囲・累計単位・令和5年度1,543人・令和6年度1,729人が一致するため接続し、"
        "評価書R6目標1,350人と現行R9目標2,350人を分離する。"
    )
    by_number[121]["comparability_note_original"] = (
        "評価書は自主防災組織の組織率、現行計画は活動カバー率と表記する。"
        "令和5年度・令和6年度80.7%は一致するが、分母・対象範囲の同一性を示す"
        "公式定義を未確認のため直接接続しない。"
    )
    by_number[122]["comparability_note_original"] = (
        "評価書の令和6年度47.3%を接続する。評価書R6目標70.0%と"
        "現行R9目標72.0%を分離する。"
    )
    by_number[123]["comparability_note_original"] = (
        "評価書の令和6年度76.4%と現行計画の現況値80.0%の資料版差を保持する。"
        "評価書R6目標75.0%と現行R9目標84%を分離する。"
    )
    by_number[124]["comparability_note_original"] = (
        "評価書の令和6年度43.1%と現行計画の現況値43.2%の資料版差を保持する。"
        "評価書R6目標38.7%と現行R9目標43.8%を分離する。"
    )
    by_number[125]["comparability_note_original"] = (
        "ハード・ソフトを独立した2系列として接続する。評価書の令和6年度652箇所・"
        "8,608箇所と現行計画の649箇所・8,602箇所の資料版差を保持し、"
        "評価書R6目標と現行R9目標を分離する。"
    )
    catalog["reviewed_at"] = UPDATED_AT
    write_json(path, catalog)


def update_manifest() -> None:
    path = ROOT / "data/catalog/miyagi_policy_review_manifest.json"
    manifest = load(path)
    manifest.update(
        {
            "updated_at": UPDATED_AT,
            "actual_linked_target_group_count": 92,
            "actual_linked_indicator_series_count": 106,
            "actual_linkage_review_needed_series_count": 18,
            "actual_result_row_count": 496,
            "actual_evidence_packet_count": 124,
        }
    )
    work_packages = {item["id"]: item for item in manifest["work_packages"]}
    work_packages["evaluation_linkage"]["deliverable"] = (
        "Measures 1 through 17 have one hundred six direct annual-result links, "
        "eighteen review records, four hundred ninety-six annual rows, and "
        "one hundred twenty-four Evidence Packets."
    )
    manifest["open_questions"] = [
        "Complete the eighteen open definition and scope reviews.",
        (
            "Verify whether the former autonomous disaster-prevention organization "
            "rate and the current activity coverage rate have the same denominator "
            "and population scope."
        ),
        (
            "Keep the measure 16 wildlife capture-count series separate from the "
            "current estimated-population series unless an official bridge is verified."
        ),
        "Connect the final FY2025 results source to the remaining 43 indicator series.",
        "Review measure 18 against the final FY2025 results source next.",
        (
            "Keep official achievement rates tied to the evaluation document's R6 "
            "targets, not the current plan's R9 targets."
        ),
        "Keep the FY2026 draft separate from any future final version.",
    ]
    write_json(path, manifest)


def update_queue() -> None:
    path = ROOT / "data/catalog/wave1_policy_review_queue.json"
    queue = load(path)
    miyagi = next(
        item for item in queue["items"] if item["prefecture_code"] == "04"
    )
    miyagi["next_action"] = (
        "KPI本文128目標・149系列は全件Reviewed済み。106系列を年度評価へ直接接続し、"
        "18系列を定義・範囲の要確認として分離した。残る43系列の年度実績接続を継続する。"
    )
    queue["updated_at"] = UPDATED_AT
    write_json(path, queue)


def update_manifest_schema() -> None:
    path = ROOT / "schemas/miyagi_policy_review_manifest.schema.json"
    schema = load(path)
    properties = schema["properties"]
    properties["actual_linked_target_group_count"]["const"] = 92
    properties["actual_linked_indicator_series_count"]["const"] = 106
    properties["actual_linkage_review_needed_series_count"]["const"] = 18
    properties["actual_result_row_count"]["const"] = 496
    properties["actual_evidence_packet_count"]["const"] = 124
    write_json(path, schema)


def update_web_loader() -> None:
    path = ROOT / "apps/web/lib/miyagiActuals.ts"
    text = path.read_text(encoding="utf-8")

    old_import = (
        'import measure16Actuals from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure16_2024.json";\n'
    )
    evidence_import = (
        'import measure17Evidence from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure17_2024_evidence_packets.json";\n'
    )
    actuals_import = (
        'import measure17Actuals from "../../../data/entities/policy/'
        'miyagi_kpi_actuals_measure17_2024.json";\n'
    )
    text = replace_once(
        text,
        old_import,
        old_import + evidence_import + actuals_import,
        "measure17 imports",
    )
    text = replace_once(
        text,
        "  ...measure16Actuals.records,\n] as MiyagiKpiActualLink[];",
        "  ...measure16Actuals.records,\n  ...measure17Actuals.records,\n] as "
        "MiyagiKpiActualLink[];",
        "measure17 actual spread",
    )
    text = replace_once(
        text,
        "  ...measure16Evidence,\n];",
        "  ...measure16Evidence,\n  ...measure17Evidence,\n];",
        "measure17 evidence spread",
    )
    text = replace_once(
        text,
        "  subjectFiscalYear: measure16Actuals.subject_fiscal_year,\n"
        "  evaluationFiscalYear: measure16Actuals.evaluation_fiscal_year,",
        "  subjectFiscalYear: measure17Actuals.subject_fiscal_year,\n"
        "  evaluationFiscalYear: measure17Actuals.evaluation_fiscal_year,",
        "latest fiscal-year source",
    )
    path.write_text(text, encoding="utf-8")


def update_tests_and_static_requirement() -> None:
    totals_path = ROOT / "tests/test_miyagi_catalog_totals.py"
    totals = totals_path.read_text(encoding="utf-8")
    replacements = [
        ("== 87", "== 92", "linked target groups"),
        ("== 100", "== 106", "linked series"),
        ("== 17", "== 18", "review-needed series"),
        ("== 468", "== 496", "annual rows"),
        ("== 117", "== 124", "actual Evidence"),
    ]
    for old, new, label in replacements:
        totals = replace_once(totals, old, new, label)
    totals_path.write_text(totals, encoding="utf-8")

    queue_path = ROOT / "tests/test_wave1_policy_review_queue.py"
    queue_test = queue_path.read_text(encoding="utf-8")
    queue_test = replace_once(
        queue_test,
        '["128", "149", "100", "17", "49"]',
        '["128", "149", "106", "18", "43"]',
        "Miyagi queue totals",
    )
    queue_path.write_text(queue_test, encoding="utf-8")

    static_path = ROOT / "scripts/validate_static_export.py"
    static_text = static_path.read_text(encoding="utf-8")
    static_text = replace_once(
        static_text,
        "468件の実績推移を公開",
        "496件の実績推移を公開",
        "Miyagi static annual-row count",
    )
    static_path.write_text(static_text, encoding="utf-8")


def update_cross_catalog_tests() -> None:
    final_path = ROOT / "tests/test_miyagi_kpi_catalog_groups_114_128.py"
    final_text = final_path.read_text(encoding="utf-8")
    old_mapping = (
        '        118: "linked",\n'
        '        119: "linked",\n'
        "    }"
    )
    new_mapping = (
        '        118: "linked",\n'
        '        119: "linked",\n'
        '        120: "linked",\n'
        '        121: "needs_review",\n'
        '        122: "linked",\n'
        '        123: "linked",\n'
        '        124: "linked",\n'
        '        125: "linked",\n'
        "    }"
    )
    final_text = replace_once(
        final_text,
        old_mapping,
        new_mapping,
        "measure17 expected linkage mapping",
    )
    final_path.write_text(final_text, encoding="utf-8")

    sequence_path = ROOT / "tests/test_miyagi_kpi_catalog_groups_53_68.py"
    sequence_text = sequence_path.read_text(encoding="utf-8")
    sequence_text = replace_once(
        sequence_text,
        '    POLICY / "miyagi_kpi_catalog_measure16.json",\n]',
        '    POLICY / "miyagi_kpi_catalog_measure16.json",\n'
        '    POLICY / "miyagi_kpi_catalog_measure17.json",\n]',
        "measure17 catalog inclusion",
    )
    sequence_text = replace_once(
        sequence_text,
        "def test_all_reviewed_batches_form_119_groups_and_139_series():",
        "def test_all_reviewed_batches_form_125_groups_and_146_series():",
        "reviewed-batch test name",
    )
    sequence_text = replace_once(
        sequence_text,
        "list(range(1, 120))",
        "list(range(1, 126))",
        "reviewed target-group range",
    )
    sequence_text = replace_once(
        sequence_text,
        "list(range(1, 140))",
        "list(range(1, 147))",
        "reviewed series range",
    )
    sequence_path.write_text(sequence_text, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_manifest()
    update_queue()
    update_manifest_schema()
    update_web_loader()
    update_tests_and_static_requirement()
    update_cross_catalog_tests()


if __name__ == "__main__":
    main()
