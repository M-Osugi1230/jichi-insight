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

Status: `in_progress`（2026-08-02開始）

文書スコープから、個別の政策目標、年度実績、予算、決算、重点事業、契約、監査、議会、公約を一対一で追跡できる個票スコープへ進みます。公式資料が不足する場合は、最大到達深度と不足条件をReviewedとして固定します。

### Wave 1 — Reference implementations

Status: `complete`

北海道、宮城県、東京都、福岡県の861個票を全件正規化しました。

- Linked: 420
- Partial: 58
- Not linked: 383
- 独自の政策達成評価: 0

正本:

- `data/catalog/phase11_wave1_completion.json`
- `tests/test_phase11_wave1_completion.py`

### Wave 2 — Remaining regional anchors

Status: `complete`

愛知県、大阪府、広島県、香川県、沖縄県の5拠点を完了しました。

| 都道府県 | レコード | 到達状態 |
|---|---:|---|
| 愛知県 | 56 | 62系列、current値61系列、欠損1系列 |
| 大阪府 | 83 | Linked 77、Partial 6 |
| 広島県 | 62 | Linked 59、測定待ちPartial 3 |
| 香川県 | 135 | 135 Linked、141表示箇所、目標改定87 |
| 沖縄県 | 375 | 計画基準値→R9目標の最大深度、全件Partial |

Wave 2統合値:

- 完了拠点: 5 / 5
- レコード: 711
- 指標系列: 725
- current値あり: 340系列
- current値欠損・未接続: 385系列
- 進捗目標または明示的target: 602系列
- 最大到達深度レコード: 375
- 独自の政策達成評価: 0
- 比較対象への昇格: 0

沖縄県の正本は計画基準値とR9目標であり、Reviewed年度実績ではありません。計画基準値をannual actualへ流用せず、全国値も参考情報のまま保持します。

正本:

- `data/catalog/phase11_wave2_completion.json`
- `schemas/phase11_wave2_completion.schema.json`
- `tests/test_phase11_wave2_completion.py`
- `data/catalog/phase11_okinawa_normalization.json`

### Wave 3 — Nationwide minimum record depth

Status: `in_progress`

残る38県を都道府県コード順に処理します。最初は青森県（02）、次に岩手県（03）です。

各県は必ず次のいずれかへ到達させます。

1. 共通Schemaを通るReviewed個票接続
2. 深い接続を支える公式資料が不足する場合のReviewed最大到達深度

同じ件数ではなく、同じ昇格条件・Evidence水準・欠損状態の扱いを要求します。未公開、未確認、Partial、not assessableを推測で埋めません。

## After Phase 11

1. 政令指定都市
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能
6. 比較可能性が確認された指標だけを用いた比較機能
