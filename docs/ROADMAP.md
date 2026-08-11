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

愛知県、大阪府、広島県、香川県、沖縄県の5拠点、711レコード、725指標系列を完了しました。

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

### Wave 3 — Nationwide minimum record depth

Status: `complete`

残る38県、13,755レコードを都道府県コード順に処理しました。全件が共通Schemaと同じEvidence・欠損状態・非評価境界を通過する設計です。

- 完了県: 38 / 38
- Reviewed最大到達深度: 13,755レコード
- Linkedへ推測昇格したレコード: 0
- Partial: 13,755
- 政策達成・因果関係・全国比較の独自判定: 0

正本:

- `data/catalog/phase11_execution_queue.json`
- `data/catalog/phase11_completion.json`
- `schemas/phase11_completion.schema.json`
- `tests/test_phase11_completion.py`

## Phase 12 — Designated-city source inventory

Status: `in_progress`

政令指定都市20市を対象に、都道府県フェーズで確立したEvidence・期間・財政状態・非評価境界を市レベルへ展開します。北九州市・福岡市の2市をReviewed referenceとして保持し、残る18市を公式コード順に処理します。

2026-08-11時点の正本では、18市のsource inventoryを全市で作成済みです。そのうち13市が`source_inventory_complete`、5市が`source_inventory_partial`です。Partialの5市は静岡市、堺市、神戸市、岡山市、広島市で、未解決の現行資料層を推測で補完しません。

Phase 12の完了条件は、対象市の単なるURL収集ではなく、現行総合計画、実施層、年度進捗、予算、決算等の役割分離と、公式URL・資料名・証拠位置・版・期間・未解決境界が保持されたsource inventoryであることです。

正本:

- `data/catalog/phase12_designated_city_execution_queue.json`
- `data/indexed/*-city/source_inventory.json`
- `tests/test_phase12_designated_city_execution_queue.py`

## Phase 13 — Designated-city record review

Status: `in_progress`

Phase 12で`source_inventory_complete`となった市だけを、個票レベルのReviewed昇格対象にします。北九州市・福岡市の2市をReviewed referenceとし、13市がreview queueに入り、5市はPhase 12のPartial解消までblockします。

2026-08-11時点では札幌市と仙台市が`review_in_progress`、残る11市が`pending_record_review`です。個々の市のレビュー進捗は各市のreview manifestを正本とし、このRoadmapには変動しやすい個票件数を固定しません。

Phase 13では、以下を品質ゲートとして維持します。

- すべてのReviewed個票が公式URLとページ・表・節等のrecord-level evidence locationを持つ
- 総合計画、実施計画、年度進捗、予算、決算を別のevidence roleとして保持する
- 予算案、成立予算、補正、執行、決算、事業費、契約額、補助額を混同しない
- 目標年、報告年、測定年、会計年度、公開年、計画版を区別する
- 自治体の自己評価はsource-reported factとして保持し、Jichi Insight独自の達成判定へ変換しない
- 比較可能性の別レビューなしに自治体間ランキングへ昇格しない
- Schema、Evidence coverage、回帰テストを通過するまで市単位のPhase 13完了を宣言しない

正本:

- `data/catalog/phase13_designated_city_review_queue.json`
- `data/catalog/*_phase13_review_manifest.json`
- `data/catalog/*_challenge_project_reviews_part*.json`
- `data/evidence/*_evidence.json`
- `tests/test_phase13_*.py`

## After Phase 13

1. Phase 12のPartial 5市を解消し、全20政令指定都市をPhase 13へ通す
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能
6. 比較可能性が確認された指標だけを用いた比較機能
