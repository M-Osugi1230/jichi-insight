#!/usr/bin/env python3
"""Normalize all 114 reviewed Fukui Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/18.json"
BOUNDARY = (
    "福井県長期ビジョン2025年3月改定版のPhase 9 Reviewed正本114行を、"
    "6つの公式PDF、ページ、抽出位置、ハッシュ、原文、数値・期間トークン、"
    "単位、対象範囲、演算子、比較不能理由付きで保持した。資料別Reviewed行数"
    "1・102・0・7・3・1は正本114件と一致し、0行の全文版を推測で埋めない。"
    "2040年を見据える長期ビジョン、2025〜2029年度の実行プラン、東西の"
    "地域プラン、人口減少対策戦略を別階層・別役割で扱う。資料索引上の3つの"
    "広域区分と地域プラン運用上の6地域区分を混同しない。毎年度設定する"
    "チャレンジ目標と結果は実行レビューであり、長期ビジョン全体の達成評価へ"
    "読み替えない。目次、体系説明、施策、複数数値を構造化annual actual"
    "またはfuture targetへ推測昇格せずPartialとし、政策達成・因果・全国比較"
    "は判定しない。"
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
        prefecture_code="18",
        slug="fukui",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=114,
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
