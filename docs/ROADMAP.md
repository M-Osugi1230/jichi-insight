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

Status: `in_progress`

- Reviewed財政・決算
- 政策、施策、事業、契約、KPIの接続
- 年度・会計区分・金額種別の分離

この工程はPhase 10の全国均質化へ統合して継続します。

## Phase 3 — Manifesto and executive

Status: `in_progress`

- 首長任期、選挙結果、公約原文、資料探索履歴
- 公約と政策・予算・事業の接続
- 未発見と不存在の分離

## Phase 4 — Assembly accountability

Status: `in_progress`

- 議会、議案、採決、委員会、視察、説明
- 行政成果と議会の役割を分離
- 政策系列への議会Evidence接続

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

Status: `in_progress`

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

Phase 10では、資料入口を確認した`indexed`と、定義・期間・対象範囲を照合して同じ政策系列へ接続した`linked`を分離します。

### Current baseline

- Reviewed政策目標: 47 / 47
- Reviewed Evidence: 47 / 47
- 公開検証基盤: 47 / 47
- 年度実績 linked: 1 / 47
- 予算 indexed以上: 2 / 47
- 決算 reviewed以上: 1 / 47
- 重点事業 indexed以上: 2 / 47
- 契約 indexed以上: 2 / 47
- 議会 indexed以上: 1 / 47
- 監査 indexed以上: 0 / 47
- 首長公約 indexed以上: 1 / 47
- 11項目の同一粒度完了: 0 / 47

### Execution order

1. 宮城県で年度実績から予算・決算・事業・契約へ接続
2. 福岡県でReviewed財政・決算から政策目標へ接続
3. 残る7地域拠点を同じ工程へ引き上げ
4. 東北、関東、中部、近畿、中国、四国、九州・沖縄の順に全国展開
5. 議会、監査、公約まで含めた説明責任の接続
6. 全47都道府県の公開検証

### Exit gate

Phase 10は次の条件をすべて満たすまで`complete`にしません。

- 47都道府県すべてが11項目の共通ゲートを通過
- 公開値・公開接続のEvidence coverage 100%
- 計画版、報告年度、測定年度、会計区分の混同0
- 予算、決算、事業費、契約額の混同0
- 議会、監査、公約の主体・任期・役割の誤接続0
- 未確認関係を推測で接続しない
- 比較可能性未確認の全国ランキングを公開しない
- Schema、回帰テスト、Lint、型検査、静的出力、Production Smoke成功
- `data/catalog/phase10_completion.json`が`complete`で全ゲート`passed`

詳細は [Phase 10 nationwide uniform depth](PHASE10_VERTICAL_LINKAGE.md) を参照してください。

## After Phase 10

1. 政令指定都市
2. 中核市・県庁所在地
3. その他市区町村
4. 選挙・候補者比較
5. API、データダウンロード、研究・報道向け機能

## Phase 10 — Complete (2026-08-01)

All 47 prefectures satisfy the declared 11-dimension completion depths. Nationwide document-scope linkage and accountability-source review are complete; record-level deepening continues as the next research track without changing Phase 10 status.
