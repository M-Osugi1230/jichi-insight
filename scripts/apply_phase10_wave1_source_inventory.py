#!/usr/bin/env python3
"""Apply the Phase 10 Wave 1 source inventory to canonical execution state."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPDATED_AT = "2026-07-23"
STATUS_ORDER = ["not_indexed", "indexed", "reviewed", "linked"]


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def category_prefecture_counts(inventory: dict[str, Any]) -> dict[str, int]:
    return {
        category: len(
            {
                record["prefecture_code"]
                for record in inventory["records"]
                if record["category"] == category
            }
        )
        for category in inventory["categories"]
    }


def validate_inventory_summary(inventory: dict[str, Any]) -> None:
    summary = inventory["summary"]
    linkage_counts = Counter(record["linkage_status"] for record in inventory["records"])
    expected = {
        "prefecture_count": len(set(inventory["prefecture_codes"])),
        "source_count": len(inventory["records"]),
        "category_prefecture_counts": category_prefecture_counts(inventory),
        "linked_existing_source_count": linkage_counts["linked_existing"],
        "candidate_linkage_source_count": linkage_counts["candidate_linkage"],
        "not_linked_source_count": linkage_counts["not_linked"],
    }
    if summary != expected:
        raise ValueError(f"Phase 10 source inventory summary mismatch: {summary} != {expected}")


def source_depth(
    inventory: dict[str, Any],
    prefecture_code: str,
    category: str,
) -> str:
    records = [
        record
        for record in inventory["records"]
        if record["prefecture_code"] == prefecture_code
        and record["category"] == category
    ]
    if not records:
        return "not_indexed"
    if any(record["linkage_status"] == "linked_existing" for record in records):
        return "linked"
    if any(record["source_status"] == "reviewed" for record in records):
        return "reviewed"
    return "indexed"


def update_queue(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    path = root / "data/catalog/phase10_execution_queue.json"
    queue = load(path)
    by_code = {record["prefecture_code"]: record for record in queue["wave1_records"]}

    miyagi = by_code["04"]
    miyagi["current_depth"]["annual_evaluation"] = source_depth(
        inventory, "04", "annual_evaluation"
    )
    miyagi["current_depth"]["budget"] = source_depth(inventory, "04", "budget")
    miyagi["current_depth"]["project_evaluation"] = source_depth(
        inventory, "04", "project_evaluation"
    )
    miyagi["current_depth"]["contracts"] = source_depth(inventory, "04", "contracts")
    miyagi["next_action"] = (
        "年度実績接続を維持し、索引化した令和8年度予算、事業評価制度、"
        "入札結果を政策・施策・事業IDへ照合する。"
    )

    fukuoka = by_code["40"]
    fukuoka["current_depth"]["annual_evaluation"] = source_depth(
        inventory, "40", "annual_evaluation"
    )
    fukuoka["current_depth"]["budget"] = max(
        fukuoka["current_depth"]["budget"],
        source_depth(inventory, "40", "budget"),
        key=STATUS_ORDER.index,
    )
    fukuoka["current_depth"]["project_evaluation"] = source_depth(
        inventory, "40", "project_evaluation"
    )
    fukuoka["current_depth"]["contracts"] = source_depth(inventory, "40", "contracts")
    fukuoka["next_action"] = (
        "総合計画実施状況報告、重点事業評価、Reviewed財政値、入札結果を"
        "共通事業IDへ照合し、目標との接続候補を確定する。"
    )

    records = queue["wave1_records"]
    queue["counts"]["annual_evaluation_linked"] = sum(
        record["current_depth"]["annual_evaluation"] == "linked" for record in records
    )
    queue["counts"]["annual_evaluation_indexed"] = sum(
        record["current_depth"]["annual_evaluation"] == "indexed" for record in records
    )
    queue["counts"]["budget_reviewed"] = sum(
        record["current_depth"]["budget"] == "reviewed" for record in records
    )
    queue["counts"]["project_evaluation_indexed_or_better"] = sum(
        STATUS_ORDER.index(record["current_depth"]["project_evaluation"])
        >= STATUS_ORDER.index("indexed")
        for record in records
    )
    queue["counts"]["contracts_indexed_or_better"] = sum(
        STATUS_ORDER.index(record["current_depth"]["contracts"])
        >= STATUS_ORDER.index("indexed")
        for record in records
    )
    queue["updated_at"] = UPDATED_AT
    write(path, queue)
    return queue


def update_nationwide_inventory(root: Path) -> None:
    path = root / "data/catalog/nationwide_source_inventory.json"
    inventory = load(path)
    by_code = {record["prefecture_code"]: record for record in inventory["records"]}

    by_code["04"]["sources"]["budget"] = "indexed"
    by_code["04"]["sources"]["project_evaluation"] = "indexed"
    by_code["04"]["next_action"] = (
        "年度実績を接続済み。令和8年度予算、事業評価、入札結果の入口を確認し、"
        "政策・施策・事業IDの照合を進める。"
    )

    by_code["40"]["sources"]["project_evaluation"] = "indexed"
    by_code["40"]["next_action"] = (
        "総合計画実施状況、重点事業評価、Reviewed財政値、入札結果の入口を確認済み。"
        "共通事業IDと年度実績の照合を進める。"
    )

    inventory["summary"] = {
        category: {
            status: sum(
                record["sources"][category] == status for record in inventory["records"]
            )
            for status in inventory["status_order"]
        }
        for category in inventory["categories"]
    }
    inventory["updated_at"] = UPDATED_AT
    write(path, inventory)


def update_completion(root: Path, queue: dict[str, Any]) -> None:
    path = root / "data/catalog/phase10_completion.json"
    completion = load(path)
    for key, value in queue["counts"].items():
        if key in completion["counts"]:
            completion["counts"][key] = value

    by_gate = {gate["id"]: gate for gate in completion["gates"]}
    source_path = "data/catalog/phase10_wave1_source_inventory.json"
    test_path = "tests/test_phase10_wave1_source_inventory.py"
    for gate_id in (
        "nationwide_vertical_source_inventory",
        "wave1_annual_actuals_linkage",
        "wave1_money_and_project_spine",
        "contracts_and_accountability_linkage",
    ):
        gate = by_gate[gate_id]
        gate["status"] = "in_progress"
        for evidence_path in (source_path, test_path):
            if evidence_path not in gate["evidence_paths"]:
                gate["evidence_paths"].append(evidence_path)

    completion["updated_at"] = UPDATED_AT
    write(path, completion)


def apply(root: Path) -> None:
    source_path = root / "data/catalog/phase10_wave1_source_inventory.json"
    inventory = load(source_path)
    validate_inventory_summary(inventory)
    queue = update_queue(root, inventory)
    update_nationwide_inventory(root)
    update_completion(root, queue)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    apply(args.root)


if __name__ == "__main__":
    main()
