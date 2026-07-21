#!/usr/bin/env python3
"""Normalize every completed Phase 8 anchor to reviewed_reference."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/catalog/regional_anchor_source_registry.json"
registry = json.loads(PATH.read_text(encoding="utf-8"))
for record in registry["records"]:
    record["anchor_status"] = "reviewed_reference"
    record["numeric_target_status"] = "reviewed"
PATH.write_text(
    json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
