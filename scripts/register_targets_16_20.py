#!/usr/bin/env python3
"""Integrate Fukuoka policy target catalogs for initiatives 16–20."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one match in {path}: {old[:80]!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


replace_once(
    "apps/web/lib/policyTargets.ts",
    'import initiative15Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_targets.json";\n',
    'import initiative15Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_targets.json";\n'
    'import initiative16Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_16_target_evidence_packet.json";\n'
    'import initiative16Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_16_targets.json";\n'
    'import initiative17Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_17_target_evidence_packet.json";\n'
    'import initiative17Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_17_targets.json";\n'
    'import initiative18Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_18_target_evidence_packet.json";\n'
    'import initiative18Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_18_targets.json";\n'
    'import initiative19Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_19_target_evidence_packet.json";\n'
    'import initiative19Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_19_targets.json";\n'
    'import initiative20Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_target_evidence_packet.json";\n'
    'import initiative20Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_targets.json";\n',
)
replace_once(
    "apps/web/lib/policyTargets.ts",
    '    | "14"\n    | "15";\n',
    '    | "14"\n    | "15"\n    | "16"\n    | "17"\n    | "18"\n    | "19"\n    | "20";\n',
)
replace_once(
    "apps/web/lib/policyTargets.ts",
    '  { slug: "15", title: "ジェンダー平等の社会づくり", catalog: initiative15Catalog as PolicyTargetCatalog, evidence: initiative15Evidence as PolicyTargetEvidence },\n',
    '  { slug: "15", title: "ジェンダー平等の社会づくり", catalog: initiative15Catalog as PolicyTargetCatalog, evidence: initiative15Evidence as PolicyTargetEvidence },\n'
    '  { slug: "16", title: "高齢者、障がいのある人への支援", catalog: initiative16Catalog as PolicyTargetCatalog, evidence: initiative16Evidence as PolicyTargetEvidence },\n'
    '  { slug: "17", title: "社会的・経済的に厳しい状況にある方への支援", catalog: initiative17Catalog as PolicyTargetCatalog, evidence: initiative17Evidence as PolicyTargetEvidence },\n'
    '  { slug: "18", title: "人権が尊重される心豊かな社会づくり", catalog: initiative18Catalog as PolicyTargetCatalog, evidence: initiative18Evidence as PolicyTargetEvidence },\n'
    '  { slug: "19", title: "外国人材に選ばれる地域づくり", catalog: initiative19Catalog as PolicyTargetCatalog, evidence: initiative19Evidence as PolicyTargetEvidence },\n'
    '  { slug: "20", title: "安全で安心して暮らせる地域づくり", catalog: initiative20Catalog as PolicyTargetCatalog, evidence: initiative20Evidence as PolicyTargetEvidence },\n',
)

for path, replacements in {
    "apps/web/app/policies/page.tsx": [
        ("取組1から15は数値目標まで構造化しましたが", "取組1から20は数値目標まで構造化しましたが"),
        ("取組1から15の指標1から76まで。", "取組1から20の指標1から99まで。"),
        ("取組16から30の数値目標", "取組21から30の数値目標"),
        ("次は取組16以降の数値目標を順に接続する。", "次は取組21以降の数値目標を順に接続する。"),
    ],
    "apps/web/app/data-quality/page.tsx": [
        ("取組1から15の基準値・目標値76件を期間単位付きで登録。", "取組1から20の基準値・目標値99件を期間単位付きで登録。"),
    ],
    "README.md": [
        ("Fukuoka policy targets 1–76 reviewed", "Fukuoka policy targets 1–99 reviewed"),
        ("Reviewed政策数値目標：76件（取組1〜15、指標1〜76）", "Reviewed政策数値目標：99件（取組1〜20、指標1〜99）"),
        ("再掲行：7行", "再掲行：9行"),
        ("次工程：取組16以降の数値目標", "次工程：取組21以降の数値目標"),
    ],
    "tests/test_policy_targets_extended.py": [
        ("for number in range(11, 16)", "for number in range(11, 21)"),
        ("through_seventy_six", "through_ninety_nine"),
        ("assert len(catalogs) == 15", "assert len(catalogs) == 20"),
        ("        3,\n    ]", "        3,\n        7,\n        5,\n        1,\n        3,\n        7,\n    ]"),
        ("list(range(1, 77))", "list(range(1, 100))"),
    ],
}.items():
    for old, new in replacements:
        replace_once(path, old, new)
