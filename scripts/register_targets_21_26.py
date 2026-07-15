#!/usr/bin/env python3
"""Integrate Fukuoka policy target catalogs for initiatives 21–26."""

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
    'import initiative20Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_targets.json";\n',
    'import initiative20Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_20_targets.json";\n'
    'import initiative21Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_21_target_evidence_packet.json";\n'
    'import initiative21Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_21_targets.json";\n'
    'import initiative22Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_22_target_evidence_packet.json";\n'
    'import initiative22Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_22_targets.json";\n'
    'import initiative23Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_23_target_evidence_packet.json";\n'
    'import initiative23Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_23_targets.json";\n'
    'import initiative24Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_24_target_evidence_packet.json";\n'
    'import initiative24Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_24_targets.json";\n'
    'import initiative25Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_25_target_evidence_packet.json";\n'
    'import initiative25Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_25_targets.json";\n'
    'import initiative26Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_26_target_evidence_packet.json";\n'
    'import initiative26Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_26_targets.json";\n',
)
replace_once(
    "apps/web/lib/policyTargets.ts",
    '    | "19"\n    | "20";\n',
    '    | "19"\n    | "20"\n    | "21"\n    | "22"\n    | "23"\n    | "24"\n    | "25"\n    | "26";\n',
)
replace_once(
    "apps/web/lib/policyTargets.ts",
    '  { slug: "20", title: "安全で安心して暮らせる地域づくり", catalog: initiative20Catalog as PolicyTargetCatalog, evidence: initiative20Evidence as PolicyTargetEvidence },\n',
    '  { slug: "20", title: "安全で安心して暮らせる地域づくり", catalog: initiative20Catalog as PolicyTargetCatalog, evidence: initiative20Evidence as PolicyTargetEvidence },\n'
    '  { slug: "21", title: "豊かな自然環境の保全と快適な生活環境の創造", catalog: initiative21Catalog as PolicyTargetCatalog, evidence: initiative21Evidence as PolicyTargetEvidence },\n'
    '  { slug: "22", title: "環境に負荷をかけない社会への移行", catalog: initiative22Catalog as PolicyTargetCatalog, evidence: initiative22Evidence as PolicyTargetEvidence },\n'
    '  { slug: "23", title: "防災・減災・県土強靱化", catalog: initiative23Catalog as PolicyTargetCatalog, evidence: initiative23Evidence as PolicyTargetEvidence },\n'
    '  { slug: "24", title: "地域の活力向上", catalog: initiative24Catalog as PolicyTargetCatalog, evidence: initiative24Evidence as PolicyTargetEvidence },\n'
    '  { slug: "25", title: "県内各地域の振興", catalog: initiative25Catalog as PolicyTargetCatalog, evidence: initiative25Evidence as PolicyTargetEvidence },\n'
    '  { slug: "26", title: "生活と産業を支える基盤の整備", catalog: initiative26Catalog as PolicyTargetCatalog, evidence: initiative26Evidence as PolicyTargetEvidence },\n',
)

for path, replacements in {
    "apps/web/app/policies/page.tsx": [
        ("取組1から20は数値目標まで構造化しましたが", "取組1から26は数値目標まで構造化しましたが"),
        ("取組1から20の指標1から99まで。", "取組1から26の指標1から118まで。"),
        ("取組21から30の数値目標", "取組27から30の数値目標"),
        ("次は取組21以降の数値目標を順に接続する。", "次は取組27以降の数値目標を順に接続する。"),
    ],
    "apps/web/app/data-quality/page.tsx": [
        ("取組1から20の基準値・目標値99件を期間単位付きで登録。", "取組1から26の基準値・目標値118件を期間単位付きで登録。"),
    ],
    "README.md": [
        ("Fukuoka policy targets 1–99 reviewed", "Fukuoka policy targets 1–118 reviewed"),
        ("Reviewed政策数値目標：99件（取組1〜20、指標1〜99）", "Reviewed政策数値目標：118件（取組1〜26、指標1〜118）"),
        ("再掲行：9行", "再掲行：15行"),
        ("次工程：取組21以降の数値目標", "次工程：取組27以降の数値目標"),
    ],
    "tests/test_policy_targets_extended.py": [
        ("for number in range(11, 21)", "for number in range(11, 27)"),
        ("through_ninety_nine", "through_one_hundred_eighteen"),
        ("assert len(catalogs) == 20", "assert len(catalogs) == 26"),
        ("        7,\n    ]", "        7,\n        2,\n        1,\n        3,\n        2,\n        6,\n        5,\n    ]"),
        ("list(range(1, 100))", "list(range(1, 119))"),
    ],
}.items():
    for old, new in replacements:
        replace_once(path, old, new)
