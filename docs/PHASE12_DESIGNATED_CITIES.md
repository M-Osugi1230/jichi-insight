# Phase 12 — Designated city expansion

Status: `complete`（2026-08-12）

Phase 12では、全国20政令指定都市を都道府県と同じ状態分離、Evidence、期間、単位、母集団、比較不能境界を持つ共通基盤へ展開します。

## Completion scope

- 対象都市: 20 / 20
- Reviewed reference実装: 2市（北九州市、福岡市）
- Source inventory complete: 18 / 18
- Source inventory partial: 0
- Pending source inventory: 0
- Phase 12由来のblocked source inventory: 0
- 独自の政策達成評価: 0
- 比較可能性未確認データのランキング昇格: 0

Phase 12の完了は、20市について現時点の公式公開体系を棚卸しし、現行総合計画、実施層・進行管理、予算、決算、過年度資料との版境界、および未公開・未解決Evidenceを明示できたことを意味します。すべての個票がReviewed済みという意味ではありません。個票レビューはPhase 13で行います。

## Quality gates

1. 6桁自治体コードで同一性を固定する。
2. 現行総合計画と有効期間を確認してから政策目標をReviewedへ昇格する。
3. 予算、補正予算、執行、決算、事業費、契約額、補助額を分離する。
4. 目標年度、報告年度、測定年度、会計年度、公表年度、選挙任期を分離する。
5. 区別、市全体、対象人口、調査母集団などの分母を分離する。
6. 一次資料URL、資料名、ページ・位置、レビュー日、未解決境界を保持する。
7. 自動抽出だけでReviewedへ昇格しない。
8. 比較定義が一致しない都市間ランキングを作らない。

## Canonical files

- `data/catalog/phase12_designated_city_execution_queue.json`
- `schemas/phase12_designated_city_execution_queue.schema.json`
- `tests/test_phase12_designated_city_execution_queue.py`

## Phase 13 handoff order

Phase 12でSource Inventoryを完了した18市は、札幌市、仙台市、さいたま市、千葉市、横浜市、川崎市、相模原市、新潟市、静岡市、浜松市、名古屋市、京都市、大阪市、堺市、神戸市、岡山市、広島市、熊本市の順でPhase 13のrecord reviewへ引き渡します。

現在の個票レビュー状態は `data/catalog/phase13_designated_city_review_queue.json` を正本とします。
