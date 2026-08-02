#!/usr/bin/env python3
"""Normalize all 225 reviewed Kanagawa Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/14.json"
BOUNDARY = (
    "新かながわグランドデザインのPhase 9 Reviewed正本225行を、6つの公式"
    "資料、PDFページ、抽出位置、ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、演算子、比較不能理由付きで保持した。基本構想と実施計画、分冊"
    "版・全文版・A4版には重複掲載があり、資料メタデータ上のReviewed行数合計"
    "233と正本225件を区別する。実施計画の『指標』と『KPI』は目的・責任範囲"
    "が異なるため別階層で扱い、目次、目標年次、本文、複数数値、改定注記を"
    "構造化annual actualまたはfuture targetへ推測昇格せずPartialとする。"
    "評価報告書の達成状況、追加公表実績、修正情報を計画策定時の原文へ上書き"
    "せず、政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="14",
        slug="kanagawa",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=225,
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
