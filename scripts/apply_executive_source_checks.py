#!/usr/bin/env python3
"""Guarded integration for executive election and manifesto source checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    if new in content:
        return
    if content.count(old) != 1:
        raise RuntimeError(f"Expected exactly one match in {path}: {old!r}")
    target.write_text(content.replace(old, new), encoding="utf-8")


replace_once(
    "scripts/validate_repository.py",
    '    "data/catalog/fukuoka_finance_sources.json",\n',
    '    "data/catalog/fukuoka_finance_sources.json",\n'
    '    "data/catalog/executive_sources.json",\n',
)

replace_once(
    "scripts/validate_static_export.py",
    '    ROOT / "data" / "catalog" / "fukuoka_assembly_sources.json",\n',
    '    ROOT / "data" / "catalog" / "fukuoka_assembly_sources.json",\n'
    '    ROOT / "data" / "catalog" / "executive_sources.json",\n',
)

replace_once(
    "scripts/validate_static_export.py",
    '                    "公約原文の登録",\n'
    '                    "現職名と任期が分かっても、実績評価はできない。",\n',
    '                    "個別選挙結果",\n'
    '                    "公式選挙公報",\n'
    '                    "選挙公報登録済み",\n'
    '                    "公式選挙結果のみ",\n'
    '                    "公約進捗評価",\n'
    '                    "資料があることと、公約を評価できることは別です。",\n',
)

replace_once(
    "README.md",
    '- 公開済み評価：0件\n',
    '- 公開済み評価：0件\n'
    '- Reviewed現職首長：3人\n'
    '- 個別選挙結果ページ：3件\n'
    '- 公式選挙公報：1件（北九州市長選挙）\n'
    '- 公約進捗評価：0件\n',
)
