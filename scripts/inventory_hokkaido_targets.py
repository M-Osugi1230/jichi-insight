#!/usr/bin/env python3
"""Inventory structured Hokkaido target data before annual-actual linkage."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = Path("hokkaido-target-inventory.json")


def count_objects(value: object) -> int:
    if isinstance(value, list):
        return sum(count_objects(item) for item in value)
    if isinstance(value, dict):
        return 1 + sum(count_objects(item) for item in value.values())
    return 0


def collect_ids(value: object) -> list[str]:
    ids: list[str] = []
    if isinstance(value, dict):
        item_id = value.get("id")
        if isinstance(item_id, str):
            ids.append(item_id)
        for item in value.values():
            ids.extend(collect_ids(item))
    elif isinstance(value, list):
        for item in value:
            ids.extend(collect_ids(item))
    return ids


def collect_indicator_keys(value: object) -> list[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = key.lower()
            if "indicator" in lowered or "target" in lowered or "kpi" in lowered:
                keys.add(key)
            keys.update(collect_indicator_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(collect_indicator_keys(item))
    return sorted(keys)


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {"node_modules", ".next", "out"} for part in path.parts):
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        raw = json.dumps(value, ensure_ascii=False).lower()
        if "hokkaido" not in raw and "北海道" not in raw:
            continue
        ids = collect_ids(value)
        hokkaido_ids = [
            item_id
            for item_id in ids
            if "hokkaido" in item_id.lower() or "北海道" in item_id
        ]
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "top_level_type": type(value).__name__,
                "top_level_keys": sorted(value.keys()) if isinstance(value, dict) else [],
                "object_count": count_objects(value),
                "id_count": len(ids),
                "hokkaido_id_count": len(hokkaido_ids),
                "hokkaido_id_samples": hokkaido_ids[:20],
                "indicator_keys": collect_indicator_keys(value),
            }
        )
    output = {
        "file_count": len(records),
        "files": records,
    }
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"file_count": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
