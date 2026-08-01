#!/usr/bin/env python3
"""Inventory existing Miyagi records before adding Phase 10 money linkage."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "miyagi-data-inventory.json"


def is_miyagi_path(path: Path) -> bool:
    lowered = path.as_posix().lower()
    return "miyagi" in lowered or "04_" in path.name.lower()


def summarize_json(path: Path) -> dict:
    relative = path.relative_to(ROOT).as_posix()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {"path": relative, "parse_error": str(exc)}

    summary: dict = {"path": relative, "type": type(value).__name__}
    if isinstance(value, dict):
        summary["top_level_keys"] = sorted(value)
        for key in (
            "id",
            "prefecture_code",
            "municipality_key",
            "status",
            "review_status",
            "updated_at",
        ):
            if key in value:
                summary[key] = value[key]
        for key in (
            "items",
            "records",
            "series",
            "targets",
            "evidence_packets",
            "work_packages",
        ):
            if isinstance(value.get(key), list):
                summary[f"{key}_count"] = len(value[key])
    elif isinstance(value, list):
        summary["item_count"] = len(value)
    return summary


def main() -> None:
    candidates = sorted(
        path
        for root in (ROOT / "data", ROOT / "schemas", ROOT / "tests", ROOT / "apps")
        if root.exists()
        for path in root.rglob("*")
        if path.is_file() and is_miyagi_path(path)
    )
    json_summaries = [
        summarize_json(path) for path in candidates if path.suffix == ".json"
    ]
    result = {
        "file_count": len(candidates),
        "files": [path.relative_to(ROOT).as_posix() for path in candidates],
        "json_summaries": json_summaries,
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"file_count": len(candidates)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
