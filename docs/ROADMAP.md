# Roadmap

Jichi Insightは日付ではなく、品質ゲートの通過で進行を管理します。`indexed`、`reviewed`、`linked`、`published`を混同せず、一次資料とEvidenceが不足する状態を推測で埋めません。

## Phase 0 — Foundation

Status: `complete`

プロジェクト憲章、PRD、編集・データ方針、モノレポ、Web、JSON Schema、CI、訂正・反論、リスク、運用ルールを整備しました。

## Phase 1 — Source map and prototype

Status: `complete`

公式資料入口、財政・計画・事業・契約・議会・選挙資料マップ、出典・品質状態UIを実装しました。

## Phase 2 — Finance and project spine

Status: `integrated_into_phase10`

全国の文書スコープ接続はPhase 10で完了しました。個票単位の深掘りはPhase 11へ移行しました。

## Phase 3 — Manifesto and executive

Status: `reviewed_coverage_complete`

47都道府県の首長公約資料または公式検索結果をReviewedとし、現任期・候補者・原文を確認できない資料は個票へ昇格しません。

## Phase 4 — Assembly accountability

Status: `reviewed_coverage_complete`

47都道府県の議会資料または公式検索結果をReviewedとし、発言・議案・採決単位の接続はPhase 11以降で進めます。

## Phase 5 — Trust, legal, and operations

Status: `complete_for_initial_publication`

利用規約、プライバシー、免責事項、訂正・反論受付、アクセシビリティ、セキュリティ、運用手順、公開前監査、Production Smokeを実装しました。

## Phase 6 — Public beta

Status: `ready`

全国公開サイト、方法論、データ品質、更新状態、フィードバックと訂正フローを実装済みです。正式なPublic betaには外部法務・アクセシビリティ・運用の実地ゲートが残ります。

## Phase 7 — Nationwide prefecture registry

Status: `complete`

47都道府県の共通コード、公式入口、現行政策計画、全国資料カバレッジ、状態分離、静的出力、Production Smokeを完了しました。

正本: `data/catalog/phase7_completion.json`

## Phase 8 — Regional anchor expansion

Status: `complete`

北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県の9地域拠点で、政策計画、主要数値目標、Evidence Packet、公開ページ、静的出力、本番確認を完了しました。

正本: `data/catalog/phase8_completion.json`

## Phase 9 — Nationwide Reviewed targets

Status: `complete`

全47都道府県を同じEvidence-backed Reviewed目標基盤へ引き上げました。

- 現行政策計画: 47 / 47
- Evidence-backed Reviewed数値目標: 47 / 47
- 計画改定・後継計画・旧計画の履歴: 47 / 47
- 全国公開ページとProduction Smoke: 完了
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

## Phase 10 — Nationwide uniform depth

Status: `complete`（2026-08-01）

47都道府県を、政策・KPI、Evidence、年度実績、予算、決算、重点事業、契約、議会、監査、首長公約、公開検証の共通文書スコープへ引き上げました。

正本:

- `data/catalog/phase10_completion.json`
- `data/catalog/phase10_nationwide_core_linkage.json`
- `data/catalog/phase10_nationwide_accountability_linkage.json`
- `docs/PHASE10_VERTICAL_LINKAGE.md`

## Phase 11 — Nationwide record-level linkage

Status: `in_progress`（2026-08-02開始）

Phase 10の文書スコープから、個別の政策目標、年度実績、予算、決算、重点事業、契約、監査、議会、公約を一対一で追跡できる個票スコープへ進みます。

### Wave 1 — Reference implementations

Status: `complete`

北海道、宮城県、東京都、福岡県の既存個票を全件移行・正規化しました。

- 対象レコード: 861 / 861
- Linked: 420 / 420
- Partial: 58 / 58
- Not linked: 383 / 383
- 独自の政策達成評価: 0件

正本:

- `data/catalog/phase11_wave1_migration.json`
- `data/catalog/phase11_wave1_completion.json`
- `schemas/phase11_record_linkage.schema.json`
- `tests/test_phase11_wave1_completion.py`

### Wave 2 — Remaining regional anchors

Status: `in_progress`

対象は愛知県、大阪府、広島県、香川県、沖縄県です。

#### 愛知県 — complete

- 指標行: 56
- 系列: 62
- current値あり / 欠損: 61 / 1
- 実施計画由来の進捗目標: 29
- 再掲行: 2
- 目標改定行: 1

#### 大阪府 — complete

- 指標行: 83
- 系列: 91
- Linked / Partial: 77 / 6
- current値あり / 欠損: 85 / 6
- 明示的target: 1

2040年代の経済目標1件と初回調査前の5件をPartialとして保持し、旧ビジョン系列と事業一覧を自動接続しません。

#### 広島県 — complete

- 指標: 62
- Linked / Partial: 59 / 3
- 政策分野: 17
- 測定待ち: 3
- 定性目標: 1

複合セルを推測で分解せず、基準値・現状値・目標値・目標年度・変更区分・出典・Evidence ID・ページを原文のまま保持します。

#### 香川県 — complete

- 固有指標: 135
- Linked: 135
- 表示箇所: 141
- 再掲指標: 6
- R7→R8目標改定: 87
- 同値目標版: 48

現状値、R7目標、延長後R8目標を別Measurementとして保持します。訂正値、複数系列、累積期間、参考目標を原文のまま残し、再掲を別指標として重複計上しません。

正本:

- `data/catalog/phase11_kagawa_normalization.json`
- `schemas/phase11_kagawa_normalization.schema.json`
- `scripts/normalize_phase11_kagawa.py`
- `tests/test_phase11_kagawa_normalization.py`

#### Wave 2 progress

- 完了地域拠点: 4 / 5
- 正規化済み行: 336
- 正規化済み系列: 350
- current値あり: 340系列
- current値欠損: 10系列
- 進捗目標または明示的target: 227系列
- 次の対象: 沖縄県

沖縄県は主要36・成果339、合計375指標を最大到達深度として正規化します。現在の正本は計画基準値とR9目標であり、Reviewed年度実績ではないため、375件をPartialとして保持し、年次実績を捏造しません。

### Wave 3 — Nationwide minimum record depth

Status: `pending`

残る38県へ同じ品質ゲートを展開します。同じ件数ではなく、同じ昇格条件・Evidence水準・欠損状態の扱いを要求します。

## After Phase 11

1. 政令指定都市
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能
6. 比較可能性が確認された指標だけを用いた比較機能
