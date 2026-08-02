# Roadmap

Jichi Insightは日付ではなく、品質ゲートの通過で進行を管理します。`indexed`、`reviewed`、`linked`、`published`を混同せず、一次資料とEvidenceが不足する状態を推測で埋めません。

## Phase 0 — Foundation

Status: `complete`

- プロジェクト憲章、PRD、編集・データ方針
- モノレポ、Web、JSON Schema、CI
- 訂正・反論、リスク、運用ルール

## Phase 1 — Source map and prototype

Status: `complete`

- パイロット自治体の公式資料マップ
- 財政、計画、事業、契約、議会、選挙資料の入口
- 出典・品質状態を表示するUI

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

- 利用規約、プライバシー、免責事項
- 訂正・反論受付
- アクセシビリティ、セキュリティ、運用手順
- 公開前監査とProduction Smoke

## Phase 6 — Public beta

Status: `ready`

全国公開サイト、方法論、データ品質、更新状態、フィードバックと訂正フローを実装済みです。正式なPublic betaには外部法務・アクセシビリティ・運用の実地ゲートが残ります。

## Phase 7 — Nationwide prefecture registry

Status: `complete`

- 47都道府県の共通コード、名称、地域区分
- 47/47公式入口確認
- 47/47現行政策計画確認
- 全国資料カバレッジ
- Coverage、Reviewed、Publishedの状態分離
- 静的出力とProduction Smoke

正本: `data/catalog/phase7_completion.json`

## Phase 8 — Regional anchor expansion

Status: `complete`

北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県の9地域拠点で、政策計画、主要数値目標、Evidence Packet、公開ページ、静的出力、本番確認を完了しました。

正本: `data/catalog/phase8_completion.json`

## Phase 9 — Nationwide Reviewed targets

Status: `complete`

全47都道府県を同じEvidence-backed Reviewed目標基盤へ引き上げました。

- 現行政策計画: 47 / 47
- 主要数値目標入口: 47 / 47
- Evidence-backed Reviewed数値目標: 47 / 47
- 計画改定・後継計画・旧計画の履歴: 47 / 47
- 全国公開ページとProduction Smoke: 完了
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

正本:

- `data/catalog/phase9_completion.json`
- `data/catalog/phase9_review_summary.json`
- `docs/PHASE9_EXECUTION.md`

## Phase 10 — Nationwide uniform depth

Status: `complete`（2026-08-01）

47都道府県すべてを次の11項目の共通ゲートへ引き上げました。

1. 政策・KPI
2. Evidence Packet
3. 年度実績
4. 予算
5. 決算
6. 重点事業
7. 契約
8. 議会
9. 監査
10. 首長公約
11. 公開検証

完了は全国の**文書スコープ**です。個別目標・予算科目・事業・契約・議会発言・監査指摘をすべて一対一接続したという意味ではありません。

- Reviewed政策目標・Evidence: 47 / 47
- 年度実績・予算・決算・重点事業・監査 文書スコープLinked: 47 / 47
- 契約・議会・首長公約 Reviewed coverage: 47 / 47
- 公開検証 Reviewed: 47 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

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

- 対象ファイル: 11
- 対象レコード: 861 / 861
- Linked: 420 / 420
- Partial: 58 / 58
- Not linked: 383 / 383
- 正規化済み都道府県: 4 / 4
- 独自の政策達成評価: 0件
- 比較対象へ昇格したレコード: 0件

4つのNormalizerを統合実行し、全861件について共通Schema、ID一意性、元カタログ件数、状態内訳、Evidence参照、非評価境界を一括検証します。

正本:

- `data/catalog/phase11_wave1_migration.json`
- `data/catalog/phase11_wave1_completion.json`
- `schemas/phase11_record_linkage.schema.json`
- `tests/test_phase11_wave1_completion.py`

### Wave 2 — Remaining regional anchors

Status: `in_progress`

対象:

- 愛知県
- 大阪府
- 広島県
- 香川県
- 沖縄県

#### 愛知県

Status: `complete`

2026年8月2日に愛知県公式ページを再確認し、最新掲載年次資料が2026年3月30日更新の「あいちレポート2025」であることを確認しました。既存Reviewedカタログはこの最新資料に基づいています。

- 指標行: 56 / 56
- 固有指標: 54
- 系列: 62 / 62
- current値あり: 61系列
- current値欠損: 1系列
- target値あり: 29系列
- 再掲行: 2
- 2025年次資料での目標改定行: 1
- 独自の政策達成評価: 0件
- 比較対象へ昇格したレコード: 0件

1行に複数系列、1系列に複数基準年がある構造を圧縮せず、全baseline/current/target値を系列ID、期間、原文値、解析値、source status、単位、集計範囲、演算子、方向性、比較注意事項付きで保持します。

current値欠損または目標改定がある行はPartialとし、値を推測・上書きしません。再掲2行は元ページと再掲ページの両方をEvidenceとして保持します。

正本:

- `data/catalog/phase11_aichi_normalization.json`
- `schemas/phase11_aichi_normalization.schema.json`
- `scripts/normalize_phase11_aichi.py`
- `tests/test_phase11_aichi_normalization.py`

#### Wave 2 progress

- 完了地域拠点: 1 / 5
- 正規化済み行: 56
- 正規化済み系列: 62
- 次の対象: 大阪府

大阪府では、Reviewed戦略指標と最新公式進捗資料を全件棚卸しし、各系列の期間・欠損・目標版を確認してから昇格します。

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
