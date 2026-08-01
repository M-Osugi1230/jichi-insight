#!/usr/bin/env python3
"""Inventory structured Tokyo policy data and identify its plan version."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def walk(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {"node_modules", ".next", "out"} for part in path.parts):
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        raw = json.dumps(value, ensure_ascii=False)
        lowered = raw.lower()
        if "tokyo" not in lowered and "東京都" not in raw and "東京戦略" not in raw:
            continue
        ids = [
            node.get("id")
            for node in walk(value)
            if isinstance(node, dict) and isinstance(node.get("id"), str)
        ]
        plan_markers = [
            marker
            for marker in (
                "2050東京戦略",
                "未来の東京",
                "version up 2024",
                "政策ダッシュボード",
            )
            if marker in raw
        ]
        indicator_numbers = [
            node.get("indicator_number")
            for node in walk(value)
            if isinstance(node, dict) and isinstance(node.get("indicator_number"), int)
        ]
        target_numbers = [
            node.get("target_number")
            for node in walk(value)
            if isinstance(node, dict) and isinstance(node.get("target_number"), int)
        ]
        files.append(
            {
                "path": str(path.relative_to(ROOT)),
                "top_level_type": type(value).__name__,
                "top_level_keys": sorted(value.keys()) if isinstance(value, dict) else [],
                "id_count": len(ids),
                "id_samples": ids[:30],
                "plan_markers": plan_markers,
                "indicator_number_count": len(indicator_numbers),
                "indicator_number_range": (
                    [min(indicator_numbers), max(indicator_numbers)]
                    if indicator_numbers
                    else None
                ),
                "target_number_count": len(target_numbers),
                "target_number_range": (
                    [min(target_numbers), max(target_numbers)] if target_numbers else None
                ),
            }
        )
    output = {"file_count": len(files), "files": files}
    Path("tokyo-policy-inventory.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"file_count": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
