#!/usr/bin/env python3
"""Normalize all three reviewed Saitama Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/11.json"
BOUNDARY = (
    "埼玉県5か年計画の2025年一部変更素案に対する県民・事業者の意見と"
    "県回答3行を、公式PDF、ページ、表・行位置、ハッシュ、原文、数値・期間"
    "トークン、単位、対象範囲、演算子、比較不能理由付きで保持した。3行は"
    "変更後の13指標一覧や年度施策評価そのものではなく、意見募集資料中の"
    "意見・回答であるため、KPI実績、正式な変更後目標、達成状況へ推測昇格"
    "せずPartialとする。当初版と変更後版、年度施策評価、進捗シート、県民"
    "満足度を別の評価単位として扱い、政策達成・因果・全国比較は判定しない。"
)


def load_helper(root: Path = ROOT) -> ModuleType:
    path = root / "scripts/phase11_phase9_raw.py"
    spec = importlib.util.spec_from_file_location("phase11_phase9_raw", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared normalizer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_catalog(root: Path = ROOT) -> dict:
    return load_helper(root).build_raw_catalog(
        root,
        prefecture_code="11",
        slug="saitama",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=3,
        boundary=BOUNDARY,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(build_catalog(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
