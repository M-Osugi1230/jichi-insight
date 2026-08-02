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

- Reviewed財政・決算
- 政策、施策、事業、契約、KPIの接続
- 年度・会計区分・金額種別の分離

全国の文書スコープ接続はPhase 10で完了しました。個票単位の深掘りはPhase 11へ移行しました。

## Phase 3 — Manifesto and executive

Status: `reviewed_coverage_complete`

- 47都道府県×首長公約の公式資料・公式検索結果をReviewed
- 首長任期、候補者、原文を確認できない資料は未昇格
- 未発見と不存在を分離

現任期と原文を確認した個別公約レコードへの展開はPhase 11以降の継続研究です。

## Phase 4 — Assembly accountability

Status: `reviewed_coverage_complete`

- 47都道府県×議会の公式資料・公式検索結果をReviewed
- 行政成果と議会の役割を分離
- 発言・議案・採決単位の接続はPhase 11以降の継続研究

## Phase 5 — Trust, legal, and operations

Status: `complete_for_initial_publication`

- 利用規約、プライバシー、免責事項
- 訂正・反論受付
- アクセシビリティ、セキュリティ、運用手順
- 公開前監査とProduction Smoke

## Phase 6 — Public beta

Status: `ready`

- 全国公開サイト
- 方法論、データ品質、更新状態
- フィードバックと訂正フロー

独自ドメイン、Search Console、OGP、faviconは公開設定として別管理します。

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

対象:

- 北海道
- 宮城県
- 東京都
- 愛知県
- 大阪府
- 広島県
- 香川県
- 福岡県
- 沖縄県

9地域拠点で、政策計画、主要数値目標、Evidence Packet、公開ページ、静的出力、本番確認を完了しました。

正本: `data/catalog/phase8_completion.json`

## Phase 9 — Nationwide Reviewed targets

Status: `complete`

Phase 8を除く38県を7地域バッチで処理し、全47都道府県を同じReviewed目標基盤へ引き上げました。

完了状態:

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

目的は「一部の県だけ深い」状態を解消し、47都道府県を同じ最低粒度へ引き上げることです。

共通の11項目:

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

### Completed baseline

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 年度実績 文書スコープLinked: 47 / 47
- 予算 文書スコープLinked: 47 / 47
- 決算 文書スコープLinked: 47 / 47
- 重点事業 文書スコープLinked: 47 / 47
- 監査 文書スコープLinked: 47 / 47
- 契約 Reviewed coverage: 47 / 47
- 議会 Reviewed coverage: 47 / 47
- 首長公約 Reviewed coverage: 47 / 47
- 公開検証 Reviewed: 47 / 47
- 11項目の同一粒度完了: 47 / 47
- 独自の政策達成評価: 0件
- 比較可能性未確認の全国ランキング: 0件

説明責任3層は、都道府県公式一次資料の入口または不存在を断定しない公式検索結果までをReviewedとします。安定した一次資料が未特定の場合も、確認ホスト・検索条件・検索日・再確認条件を残しています。

### Completion boundary

Phase 10の完了は全国の**文書スコープ**です。個別の目標、予算科目、事業、契約、議会発言、監査指摘をすべて一対一接続したという意味ではありません。

次の条件をすべて検証し、完了としました。

- 47都道府県すべてが11項目の共通ゲートを通過
- 公開値・公開接続のEvidence coverageを完了範囲で検証
- 計画版、報告年度、測定年度、会計区分の混同0
- 予算、決算、事業費、契約額の混同0
- 議会、監査、公約の主体・任期・役割を未確認のまま昇格しない
- 未確認関係を推測で接続しない
- 比較可能性未確認の全国ランキングを公開しない
- Schema、回帰テスト、Lint、型検査、静的出力、Publication Audit、Production Smoke成功
- `data/catalog/phase10_completion.json`が`complete`で全ゲート`passed`

正本:

- `data/catalog/phase10_uniformity.json`
- `data/catalog/phase10_execution_queue.json`
- `data/catalog/phase10_completion.json`
- `data/catalog/phase10_nationwide_core_linkage.json`
- `data/catalog/phase10_nationwide_accountability_linkage.json`
- `docs/PHASE10_VERTICAL_LINKAGE.md`

## Phase 11 — Nationwide record-level linkage

Status: `in_progress`（2026-08-02開始）

Phase 10の文書スコープから、個別の政策目標、年度実績、予算、決算、重点事業、契約、監査、議会、公約を一対一で追跡できる個票スコープへ進みます。

### Wave 1 current state

北海道、宮城県、東京都、福岡県の既存個票データについて、代表例だけでなく全レコードを移行管理対象へ登録しました。

- 対象ファイル: 11
- 全レコード: 861
- Linked: 420
- Partial: 58
- Not linked: 383
- 独自の政策達成評価: 0件

全件移行台帳は、元カタログのファイル一覧、ID、状態内訳、件数と動的に照合します。部分接続や未接続を除外せず、解決していない状態のまま保持します。

### Next gate

1. 北海道のLinked 90件を共通個票形式へ正規化
2. 北海道のPartial 18件を理由付きで保持
3. 宮城県238件、東京都6件、福岡県86件のLinkedレコードを順次正規化
4. Partial 58件、Not linked 383件を推測で昇格しない
5. 愛知県、大阪府、広島県、香川県、沖縄県へ同じ工程を展開
6. 残る38県へ同じ品質ゲートを展開

正本:

- `data/catalog/phase11_reference_records.json`
- `data/catalog/phase11_wave1_migration.json`
- `data/catalog/phase11_execution_queue.json`
- `schemas/phase11_reference_records.schema.json`
- `schemas/phase11_wave1_migration.schema.json`
- `docs/PHASE11_RECORD_LINKAGE.md`

## After Phase 11

1. 政令指定都市
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能
6. 比較可能性が確認された指標だけを用いた比較機能
