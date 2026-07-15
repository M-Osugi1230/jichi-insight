#!/usr/bin/env python3
from pathlib import Path

path = Path("apps/web/lib/policyTargets.ts")
text = path.read_text(encoding="utf-8")

changes = [
    (
        'import initiative12Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_12_targets.json";\n',
        'import initiative12Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_12_targets.json";\n'
        'import initiative13Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_13_target_evidence_packet.json";\n'
        'import initiative13Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_13_targets.json";\n'
        'import initiative14Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_14_target_evidence_packet.json";\n'
        'import initiative14Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_14_targets.json";\n'
        'import initiative15Evidence from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_target_evidence_packet.json";\n'
        'import initiative15Catalog from "../../../data/entities/policy/fukuoka_prefecture_initiative_15_targets.json";\n',
    ),
    (
        '    | "11"\n    | "12";\n',
        '    | "11"\n    | "12"\n    | "13"\n    | "14"\n    | "15";\n',
    ),
    (
        '  {\n    slug: "12",\n    title: "健康づくり、安心で質の高い医療の提供",\n    catalog: initiative12Catalog as PolicyTargetCatalog,\n    evidence: initiative12Evidence as PolicyTargetEvidence,\n  },\n',
        '  {\n    slug: "12",\n    title: "健康づくり、安心で質の高い医療の提供",\n    catalog: initiative12Catalog as PolicyTargetCatalog,\n    evidence: initiative12Evidence as PolicyTargetEvidence,\n  },\n'
        '  { slug: "13", title: "スポーツ立県福岡の実現", catalog: initiative13Catalog as PolicyTargetCatalog, evidence: initiative13Evidence as PolicyTargetEvidence },\n'
        '  { slug: "14", title: "文化芸術の振興", catalog: initiative14Catalog as PolicyTargetCatalog, evidence: initiative14Evidence as PolicyTargetEvidence },\n'
        '  { slug: "15", title: "ジェンダー平等の社会づくり", catalog: initiative15Catalog as PolicyTargetCatalog, evidence: initiative15Evidence as PolicyTargetEvidence },\n',
    ),
]

for old, new in changes:
    if new in text:
        continue
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one match: {old[:40]}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
