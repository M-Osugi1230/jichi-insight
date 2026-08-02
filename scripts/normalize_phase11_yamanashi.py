#!/usr/bin/env python3
"""Normalize all 314 reviewed Yamanashi Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/19.json"
BOUNDARY = (
    "山梨県総合計画2023年策定版のPhase 9 Reviewed正本314行を、6つの"
    "公式PDF、ページ、表・行位置、ハッシュ、原文、数値・期間トークン、単位、"
    "対象範囲、演算子、比較不能理由付きで保持した。資料別Reviewed行数"
    "2・4・4・0・0・304は正本314件と一致し、戦略4・5の0行資料を推測で"
    "補完しない。5戦略のアクションプランに掲げる目標・重要業績指標と、"
    "総合計画実施状況報告、施策評価、事務事業評価、部局別成果を別の評価単位"
    "として扱う。行政評価の事業評価を計画指標の独自達成率へ置換せず、"
    "現況値・目標値・全国値・圏域別値・暫定値・複数年値を自動で同一系列へ"
    "結合しない。参考資料の大量抽出行も、定義・単位・期間・対象範囲を確認"
    "せず構造化annual actualまたはfuture targetへ推測昇格せずPartialとし、"
    "政策達成・因果・全国比較は判定しない。"
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
        prefecture_code="19",
        slug="yamanashi",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=314,
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
