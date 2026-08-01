from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Missing documentation fragment: {label}")
    return text.replace(old, new, 1)


def normalize_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "`Phase 9 complete / Phase 10 in progress / 47 prefectures published / pre-alpha`",
        "`Phase 10 complete / 47 prefectures published / pre-alpha`",
        "README product status",
    )
    text = replace_once(
        text,
        "- Phase 10同一粒度完了: 0 / 47",
        "- Phase 10同一粒度完了: 47 / 47",
        "README uniform completion count",
    )
    text = replace_once(
        text,
        "Phase 9で、全47都道府県の政策目標とEvidence-backed Reviewed基盤が揃いました。Phase 10では、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約を同じ品質ゲートで接続します。",
        "Phase 9で全47都道府県の政策目標とEvidence-backed Reviewed基盤を整備し、Phase 10で年度実績、予算、決算、重点事業、監査を文書スコープ接続、契約・議会・首長公約を公式一次資料または不存在を断定しない公式検索結果までReviewedとしました。個票単位の一対一接続と政策達成評価は別工程です。",
        "README status paragraph",
    )

    baseline = """### 2026-08-01時点の完了状態

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績 文書スコープLinked: 47 / 47
- 予算 文書スコープLinked: 47 / 47
- 決算 文書スコープLinked: 47 / 47
- 重点事業 文書スコープLinked: 47 / 47
- 監査 文書スコープLinked: 47 / 47
- 契約・議会・首長公約 Reviewed coverage: 47 / 47（141役割）
  - 公式一次資料入口: 3件
  - 現任期確認待ち: 1件
  - 安定一次資料未特定の公式検索結果: 137件
- 公開検証 Reviewed: 47 / 47
- 11項目すべて同一粒度完了: 47 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

Phase 10の完了範囲は全国の文書スコープです。個別の目標、予算科目、事業、契約、議会発言、監査指摘をすべて一対一接続したという意味ではありません。公式検索で安定した一次資料が見つからない場合も、不存在とは断定せず検索結果と再確認条件をEvidenceとして保持します。

"""
    text, count = re.subn(
        r"### 2026-08-01時点の保守的な基準値\n.*?(?=正本:)",
        baseline,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("README Phase 10 baseline block not found")

    text = replace_once(
        text,
        "- [`data/catalog/phase10_uniformity.json`](data/catalog/phase10_uniformity.json)\n",
        "- [`data/catalog/phase10_uniformity.json`](data/catalog/phase10_uniformity.json)\n- [`data/catalog/phase10_nationwide_core_linkage.json`](data/catalog/phase10_nationwide_core_linkage.json)\n- [`data/catalog/phase10_nationwide_accountability_linkage.json`](data/catalog/phase10_nationwide_accountability_linkage.json)\n",
        "README canonical files",
    )

    deepening = """## Post-Phase 10 deepening order

1. Hokkaido・Miyagi・Tokyo・Fukuokaで確立した個票接続工程を他県へ展開
2. 政策・施策・事業・予算科目・契約・議会発言・監査指摘の安定IDを拡張
3. 現任期の首長公約を候補者・任期・原文単位で確認
4. 公式サイト移転や新年度資料を再探索し、検索結果から一次資料へ昇格
5. 比較可能性が確認された指標だけを将来の比較機能へ接続

この深掘りはPhase 10の完了状態を覆すものではなく、文書スコープから個票スコープへ精度を上げる継続工程です。

"""
    text, count = re.subn(
        r"## Current execution order\n.*?(?=## License)",
        deepening,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("README execution block not found")

    text = re.sub(
        r"\n## Phase 10 completion \(2026-08-01\)\n.*?\Z",
        "\n",
        text,
        flags=re.S,
    )
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize_roadmap() -> None:
    path = ROOT / "docs/ROADMAP.md"
    text = path.read_text(encoding="utf-8")
    start = text.index("## Phase 10 — Nationwide uniform depth")
    end = text.index("## After Phase 10", start)
    section = text[start:end]
    section = replace_once(
        section,
        "Status: `in_progress`",
        "Status: `complete` (2026-08-01)",
        "Roadmap Phase 10 status",
    )
    baseline = """### Completed baseline

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績・予算・決算・重点事業・監査 文書スコープLinked: 各47 / 47
- 契約・議会・首長公約 Reviewed coverage: 各47 / 47
- 公開検証 Reviewed: 47 / 47
- 11項目の同一粒度完了: 47 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

説明責任3層は、都道府県公式一次資料の入口または不存在を断定しない公式検索結果までをReviewedとします。個票単位の一対一接続は完了主張に含めません。

"""
    section, count = re.subn(
        r"### Current baseline\n.*?(?=### Execution order)",
        baseline,
        section,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Roadmap baseline block not found")

    execution = """### Post-completion deepening

1. 文書スコープから個票スコープへの一対一接続を全国へ拡張
2. 契約・議会・首長公約の安定一次資料を継続探索
3. 年度更新・計画改定・資料移転を再検証
4. 比較可能性が確認された指標だけを比較機能へ接続

"""
    section, count = re.subn(
        r"### Execution order\n.*?(?=### Exit gate)",
        execution,
        section,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Roadmap execution block not found")
    section = replace_once(
        section,
        "Phase 10は次の条件をすべて満たすまで`complete`にしません。",
        "2026年8月1日に次の条件をすべて検証し、Phase 10を`complete`としました。",
        "Roadmap exit gate",
    )
    text = text[:start] + section + text[end:]
    text = re.sub(
        r"\n## Phase 10 — Complete \(2026-08-01\)\n.*?\Z",
        "\n",
        text,
        flags=re.S,
    )
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize_methodology() -> None:
    path = ROOT / "docs/PHASE10_VERTICAL_LINKAGE.md"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "- `data/catalog/phase10_uniformity.json`\n",
        "- `data/catalog/phase10_uniformity.json`\n- `data/catalog/phase10_nationwide_core_linkage.json`\n- `data/catalog/phase10_nationwide_accountability_linkage.json`\n",
        "Methodology canonical files",
    )
    text = replace_once(
        text,
        "| Contracts and procurement | `linked` |\n| Assembly explanation | `linked` |\n| Audit | `linked` |\n| Executive manifesto | `linked` |",
        "| Contracts and procurement | `reviewed` official source or reviewed official-host search outcome |\n| Assembly explanation | `reviewed` official source or reviewed official-host search outcome |\n| Audit | `linked` at document scope |\n| Executive manifesto | `reviewed`; current-term verification required before promise records |",
        "Methodology accountability depths",
    )

    verified = """## Current verified depth on 2026-08-01

Nationwide completion state:

- Reviewed target statements: 47 / 47
- Reviewed Evidence Packet coverage: 47 / 47
- annual actuals document-scope Linked: 47 / 47
- budget document-scope Linked: 47 / 47
- settlement document-scope Linked: 47 / 47
- priority projects document-scope Linked: 47 / 47
- audit document-scope Linked: 47 / 47
- contracts Reviewed coverage: 47 / 47
- assembly Reviewed coverage: 47 / 47
- executive-manifesto Reviewed coverage: 47 / 47
- publication verification Reviewed: 47 / 47
- prefectures passing the declared eleven-dimension gate: 47 / 47

Accountability review outcomes cover 141 prefecture-role pairs. Three stable official source entrances are registered, one governor-election source remains current-term verification pending, and 137 official-host searches record that no stable primary source was identified. Those 137 records are not nonexistence claims and remain scheduled for recheck.

The completion state is nationwide document-scope coverage. Record-level one-to-one linkage is deeper in Hokkaido, Miyagi, Tokyo, and Fukuoka, but universal target-line, budget-line, project, contract, statement, and audit-finding linkage is not claimed.

"""
    text, count = re.subn(
        r"## Current verified depth on 2026-08-01\n.*?(?=## Completed source-review batches)",
        verified,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Methodology verified-depth block not found")
    text = text.replace(
        "## Execution order from here",
        "## Post-Phase 10 record-level deepening",
        1,
    )
    text = replace_once(
        text,
        "Until every condition is met, the phase remains `in_progress`.",
        "Every declared document-scope condition was verified on 2026-08-01. Phase 10 is `complete`; record-level deepening continues separately.",
        "Methodology final status",
    )
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    normalize_readme()
    normalize_roadmap()
    normalize_methodology()


if __name__ == "__main__":
    main()
