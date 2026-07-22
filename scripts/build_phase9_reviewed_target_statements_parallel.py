#!/usr/bin/env python3
"""Parallel runner for the deterministic Phase 9 Reviewed target builder."""

from __future__ import annotations

import argparse
import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests

from audit_phase9_numeric_target_sources import (
    UPDATED_AT,
    USER_AGENT,
    official_phase9_records,
)
from build_phase9_reviewed_target_statements import (
    extract_prefecture,
    update_execution_state,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
OVERRIDE_PATH = ROOT / "data/catalog/phase9_review_source_overrides.json"


def session() -> requests.Session:
    value = requests.Session()
    value.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.5",
        }
    )
    return value


def apply_source_overrides(
    prefectures: list[dict[str, Any]], root: Path
) -> list[dict[str, Any]]:
    override_path = root / "data/catalog/phase9_review_source_overrides.json"
    if not override_path.is_file():
        return prefectures
    override_document = json.loads(override_path.read_text(encoding="utf-8"))
    overrides = {
        record["prefecture_code"]: record for record in override_document["records"]
    }
    applied: list[dict[str, Any]] = []
    for prefecture in prefectures:
        value = copy.deepcopy(prefecture)
        override = overrides.get(value["prefecture_code"])
        if override is not None:
            if value["target_source"]["id"] != override["source_id"]:
                raise ValueError(
                    f"Override source ID mismatch for {value['prefecture_code']}"
                )
            value["target_source"]["title"] = override["title"]
            value["target_source"]["url"] = override["url"]
            value["review_source_override_reason"] = override["reason"]
        applied.append(value)
    if set(overrides) - {item["prefecture_code"] for item in applied}:
        raise ValueError("Phase 9 review-source override references an unknown prefecture")
    return applied


def review_one(prefecture: dict[str, Any]):
    with session() as client:
        return prefecture, extract_prefecture(client, prefecture)


def build(root: Path, workers: int) -> None:
    prefectures = apply_source_overrides(official_phase9_records(root), root)
    generated: dict[str, tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = {}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(review_one, prefecture): prefecture for prefecture in prefectures}
        for future in as_completed(futures):
            prefecture = futures[future]
            code = prefecture["prefecture_code"]
            try:
                _, result = future.result()
            except Exception as exc:
                raise RuntimeError(f"Phase 9 review failed for {code} {prefecture['name']}") from exc
            generated[code] = result
            print(
                f"Reviewed {code} {prefecture['name']}: "
                f"{result[2]['reviewed_target_statement_count']} statements",
                flush=True,
            )

    if set(generated) != {prefecture["prefecture_code"] for prefecture in prefectures}:
        raise ValueError("Parallel Phase 9 generation did not cover all prefectures")

    summaries: list[dict[str, Any]] = []
    history_records: list[dict[str, Any]] = []
    by_code = {prefecture["prefecture_code"]: prefecture for prefecture in prefectures}
    for code in sorted(generated):
        catalog, evidence, summary = generated[code]
        prefecture = by_code[code]
        write_json(root / f"data/reviewed/phase9/{code}.json", catalog)
        write_json(root / f"data/evidence/phase9/{code}.json", evidence)
        summaries.append(summary)
        history_records.append(
            {
                "prefecture_code": code,
                "name": prefecture["name"],
                "current_plan_title": prefecture["current_plan_title"],
                "current_plan_period": prefecture["current_plan_period"],
                "target_source_boundary": prefecture["target_source_boundary"],
                "source_registry_path": prefecture["registry_path"],
                "history_status": "tracked",
            }
        )

    target_count = sum(item["reviewed_target_statement_count"] for item in summaries)
    evidence_count = sum(item["evidence_packet_count"] for item in summaries)
    if len(summaries) != 38 or target_count == 0 or evidence_count != target_count:
        raise ValueError("Phase 9 reviewed summary failed completion invariants")

    write_json(
        root / "data/catalog/phase9_review_summary.json",
        {
            "id": "phase9-reviewed-prefecture-summary",
            "status": "reviewed_complete",
            "prefecture_count": len(summaries),
            "reviewed_target_statement_count": target_count,
            "evidence_packet_count": evidence_count,
            "evidence_coverage_percent": 100,
            "policy_achievement_assessed_count": 0,
            "ranking_eligible_record_count": 0,
            "records": summaries,
            "updated_at": UPDATED_AT,
        },
    )
    write_json(
        root / "data/catalog/phase9_plan_history.json",
        {
            "id": "phase9-plan-history",
            "prefecture_count": len(history_records),
            "tracked_history_count": len(history_records),
            "records": history_records,
            "updated_at": UPDATED_AT,
        },
    )
    update_execution_state(root, summaries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    if args.workers < 1 or args.workers > 16:
        raise ValueError("workers must be between 1 and 16")
    build(args.root, args.workers)


if __name__ == "__main__":
    main()
