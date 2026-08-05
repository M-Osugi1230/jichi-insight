# Roadmap

Jichi Insightは日付ではなく、品質ゲートの通過で進行を管理します。`indexed`、`reviewed`、`linked`、`published`を混同せず、一次資料とEvidenceが不足する状態を推測で埋めません。

## Phase 0〜6 — Foundation and initial publication

Status: `complete_for_initial_publication`

プロジェクト憲章、PRD、編集・データ方針、モノレポ、Web、JSON Schema、CI、公式資料マップ、訂正・反論、利用規約、プライバシー、免責、運用手順、公開前監査、Production Smokeを整備しました。正式なPublic betaには外部法務・アクセシビリティ・運用の実地ゲートが残ります。

## Phase 7 — Nationwide prefecture registry

Status: `complete`

47都道府県の共通コード、公式入口、現行政策計画、全国資料カバレッジ、状態分離、静的出力、Production Smokeを完了しました。

## Phase 8 — Regional anchor expansion

Status: `complete`

北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県の9地域拠点で、政策計画、主要数値目標、Evidence Packet、公開ページ、静的出力、本番確認を完了しました。

## Phase 9 — Nationwide Reviewed targets

Status: `complete`

全47都道府県をEvidence-backed Reviewed目標基盤へ引き上げました。独自の政策達成評価と比較可能性未確認の全国ランキングは0件です。

## Phase 10 — Nationwide uniform depth

Status: `complete`（2026-08-01）

47都道府県を、政策・KPI、Evidence、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約、公開検証の共通文書スコープへ引き上げました。

正本:

- `data/catalog/phase10_completion.json`
- `docs/PHASE10_VERTICAL_LINKAGE.md`

## Phase 11 — Nationwide record-level linkage

Status: `complete`（2026-08-05）

47都道府県すべてを、共通Schemaを通るReviewed個票接続または公式資料上の最大到達深度へ引き上げました。全15,327レコードについて、一次資料、Evidence位置、版、期間、単位、母集団、欠損・未接続境界を保持しています。

- Wave 1: 4都道府県、861レコード
- Wave 2: 5都道府県、711レコード
- Wave 3: 38都道府県、13,755レコード
- 合計: 47都道府県、15,327レコード
- 独自の政策達成評価: 0
- 比較対象への自動昇格: 0

Phase 11完了は、すべての個票が目標・実績・予算・決算・事業・契約・監査・議会・公約まで完全接続されたことを意味しません。公式資料が不足する個票はPartialまたはNot linkedとして残し、推測で補完していません。

正本:

- `data/catalog/phase11_execution_queue.json`
- `data/catalog/phase11_completion.json`
- `schemas/phase11_completion.schema.json`
- `tests/test_phase11_completion.py`

## Phase 12 — Designated city expansion

Status: `in_progress`（2026-08-06開始）

全国20政令指定都市を、都道府県と同じ状態分離・Evidence・期間・単位・母集団・比較不能境界を持つ共通基盤へ展開します。

- 対象都市: 20
- Reviewed reference実装: 北九州市、福岡市
- 実行キュー: 残り18都市
- 次の対象: 札幌市（自治体コード011002）
- 独自の政策達成評価: 0
- 比較可能性未確認データのランキング昇格: 0

### Phase 12 quality gates

1. 6桁自治体コードで同一性を固定する。
2. 現行総合計画と有効期間を確認してから政策目標をReviewedへ昇格する。
3. 予算、補正予算、執行、決算、事業費、契約額、補助額を分離する。
4. 目標年度、報告年度、測定年度、会計年度、公表年度、選挙任期を分離する。
5. 区別、市全体、対象人口、調査母集団などの分母を分離する。
6. 一次資料URL、資料名、ページ・位置、レビュー日、未解決境界を保持する。
7. 自動抽出だけでReviewedへ昇格しない。
8. 比較定義が一致しない都市間ランキングを作らない。

正本:

- `data/catalog/phase12_designated_city_execution_queue.json`
- `schemas/phase12_designated_city_execution_queue.schema.json`
- `tests/test_phase12_designated_city_execution_queue.py`

## After Phase 12

1. 中核市・県庁所在地
2. その他市区町村
3. 選挙・候補者比較
4. API、データダウンロード、研究・報道向け機能
5. 比較可能性が確認された指標だけを用いた比較機能
