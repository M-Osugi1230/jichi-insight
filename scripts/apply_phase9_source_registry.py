#!/usr/bin/env python3
"""Apply a Phase 9 regional source registry to the execution and completion manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def apply(root: Path, registry_relative: Path) -> None:
    registry_path = root / registry_relative
    registry = load(registry_path)
    queue_path = root / "data/catalog/phase9_execution_queue.json"
    completion_path = root / "data/catalog/phase9_completion.json"
    queue = load(queue_path)
    completion = load(completion_path)

    registry_records = {
        record["prefecture_code"]: record for record in registry["records"]
    }
    expected_codes = set(registry["prefecture_codes"])
    assert set(registry_records) == expected_codes

    updated_codes: set[str] = set()
    for item in queue["items"]:
        code = item["prefecture_code"]
        if code not in registry_records:
            continue
        source_record = registry_records[code]
        assert item["current_plan_status"] == "current_confirmed"
        assert source_record["numeric_target_status"] == "indexed"
        item["numeric_target_status"] = "indexed"
        item["review_status"] = "source_indexing"
        item["next_action"] = (
            "現行計画・数値目標・年度評価の公式入口を固定済み。"
            "次に指標本文、値、単位、期間、母集団、定義変更を全件抽出し、"
            "Evidence付きReviewedデータへ昇格する。"
        )
        updated_codes.add(code)

    assert updated_codes == expected_codes
    queue["updated_at"] = registry["updated_at"]
    write(queue_path, queue)

    phase9_indexed = sum(
        item["numeric_target_status"] in {"indexed", "reviewed"}
        for item in queue["items"]
    )
    phase9_reviewed = sum(
        item["numeric_target_status"] == "reviewed" for item in queue["items"]
    )
    completion["scope_version"] = registry["updated_at"]
    completion["updated_at"] = registry["updated_at"]
    completion["counts"].update(
        {
            "numeric_target_entrances_indexed_or_reviewed": 9 + phase9_indexed,
            "evidence_backed_reviewed_prefectures": 9 + phase9_reviewed,
            "phase9_prefectures_with_numeric_targets_indexed": phase9_indexed,
            "phase9_prefectures_with_reviewed_numeric_targets": phase9_reviewed,
        }
    )
    evidence_additions = {
        "all_major_numeric_targets_indexed": [str(registry_relative)],
        "published_numeric_evidence_coverage": [str(registry_relative)],
        "semantic_quality_tests": [
            "tests/test_phase9_tohoku_source_registry.py",
        ],
    }
    for gate in completion["gates"]:
        for path in evidence_additions.get(gate["id"], []):
            if path not in gate["evidence_paths"]:
                gate["evidence_paths"].append(path)
    completion["scope_note"] = (
        "Phase 9 is in progress. All 47 major policy plans are indexed, all nine "
        "regional anchors have Evidence-backed Reviewed targets, and the Tohoku "
        "batch has official numeric-target entrances indexed for five additional "
        "prefectures. The remaining work is full indicator extraction and review "
        "for all 38 Phase 9 prefectures, followed by publication and smoke gates."
    )
    write(completion_path, completion)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    apply(args.root, args.registry)


if __name__ == "__main__":
    main()
