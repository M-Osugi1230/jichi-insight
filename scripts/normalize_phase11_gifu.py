#!/usr/bin/env python3
"""Normalize all 1,500 reviewed Gifu Phase 9 statements."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RELATIVE_PATH = "data/reviewed/phase9/21.json"
BOUNDARY = (
    "岐阜県のPhase 9 Reviewed正本1,500行を、登録済み6資料の候補行総数3,232行とは分離して保持する。"
    "正本は本編5行、令和5年度実施状況報告書869行、令和8年3月改訂施策編186行、"
    "令和7年度実施状況報告書440行から構成される。令和6年度実施状況報告書の修正版と修正通知は、"
    "候補行を持つ公式資料として登録を維持するが、改訂・重複整理後の正本レコードには採用されていない。"
    "資料別候補行数を加算して正規化件数とせず、ページ・表・行位置、文書ハッシュ、原文、数値・期間トークン、"
    "単位、対象範囲、演算子、比較不能理由を各正本行に保持する。戦略本文、施策編、年度別実施状況、"
    "修正版、修正通知に現れる名称や数値が近似しても、明示的なReviewed crosswalkなしに同一系列へ結合しない。"
    "現況値、基準値、目標値、単年度実績、累計、参考値、全国値、予算・決算・事業費を推測分解せず、"
    "structured annual actualまたはfuture targetへ昇格しない。文字抽出ノイズ、欠損、複数系列、注記、"
    "改定前後の値は原文のまま保存し、政策達成、因果関係、自治体間比較、ランキングは判定しない。"
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
        prefecture_code="21",
        slug="gifu",
        source_registry=SOURCE_RELATIVE_PATH,
        expected_record_count=1500,
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
