# Roadmap to public launch

ロードマップは日付ありきではなく、品質ゲート通過を基準に進めます。作業は並列化しますが、出典・スキーマ・評価方法が固まる前に大量収集へ進みません。

## Phase 0 — Foundation

### Deliverables

- プロジェクト憲章、PRD、編集・データ方針
- モノレポとWeb最小構成
- 初期JSON Schema
- CI、Issue、PRテンプレート
- リスク登録簿
- パイロット対象カタログ

### Exit gate

- 全自動チェック成功
- 重要概念と状態値が定義済み
- main保護、PR運用、訂正Issueが利用可能

## Phase 1 — Source map and prototype

### Deliverables

- 3自治体の公式資料マップ
- 財政、総合計画、事務事業評価、契約、議会、選挙資料の所在
- 重点事業候補リスト
- 自治体ページと事業ページのUIプロトタイプ
- 出典・品質コンポーネント

### Exit gate

- 主要資料カテゴリの90%以上について所在または未公開状態を確認
- 架空データではなく、レビュー済み実データで主要画面が成立
- スマートフォンで3分以内に主要情報を理解できる

## Phase 2 — Finance and project spine

### Deliverables

- 直近3年度以上の財政
- 重点事業30件
- 予算・補正・決算・KPI・成果
- 事業と契約、監査、議会質疑の接続
- 類似自治体比較の定義

### Exit gate

- 主要数値の出典率100%
- 単位・年度・会計区分の検証成功
- 30事業がReviewed以上
- 欠損と評価不能を正しく表示

## Phase 3 — Manifesto and executive

### Deliverables

- 現職首長の公約原文と構造化
- 公約と予算事業の対応付け
- 進捗、方針変更、説明
- 公約品質の領域別表示

### Exit gate

- 全公約が収録または収録不能理由を記録
- 対応付けに根拠と信頼度
- 公約の思想を評価していないことをレビュー

## Phase 4 — Assembly accountability

### Deliverables

- 議会構成、会派、委員会
- 議案、採決、修正、附帯決議
- 政務活動費、視察、議会費
- 情報公開と住民参加
- 首長と議会の役割別表示

### Exit gate

- 主要議案と公開資料を検証可能
- 視察費等の支出と成果資料を接続
- 議会を行政成果で直接採点していない

## Phase 5 — Trust, legal, and closed beta

### Deliverables

- 外部レビュー
- 訂正・反論受付
- 利用規約、プライバシー、免責、ライセンス
- アクセシビリティ、セキュリティ、性能
- 更新運用と障害対応
- クローズドβ

### Exit gate

- P0/P1欠陥ゼロ
- 主要表示の出典・更新日・品質率100%
- 訂正フローのテスト完了
- モバイル・アクセシビリティ基準達成
- 公開可否レビュー承認

## Phase 6 — Public beta

### Deliverables

- 福岡県・福岡市・北九州市の公開
- 方法論とデータ品質ページ
- フィードバック受付
- 更新履歴
- 利用状況計測

### Exit gate for v1

- 4週間以上の安定運用
- 重大訂正を期限内に処理
- 更新作業の再現性
- 次地域へ横展開できるデータモデル

## Phase 7 — Nationwide prefecture registry

Completion state: `complete`

Phase 7は全国共通レジストリと品質状態の完成を対象とします。47都道府県すべての実施計画、KPI、年度評価、予算、事業評価をReviewed化する工程ではありません。それらはPhase 8・9で実施します。ただし、Phase 7の時点で各都道府県について6資料カテゴリの状態を必ず持ち、未索引を未索引のまま追跡できることを必須とします。

### Deliverables

- 47都道府県の共通コード、名称、地域区分
- 公式ホームページの候補・確認状態
- 現行の政策計画入口と資料種別
- 実施計画、KPI、年度評価、予算・決算、事業評価を含む6カテゴリの全国状態インベントリ
- `registered → official_entry_verified → plan_entry_indexed → current_plan_confirmed → reviewed_data`のCoverage状態
- Coverageとは独立した自治体ページのPublished状態
- 全国カバレッジ画面、検索・地域絞り込み、品質指標
- Phase 7完了マニフェスト、JSON Schema、回帰テスト、本番Smoke

### Exit gate

- 47都道府県の登録欠落・重複が0
- 候補URLと確認済みURLをデータ・画面上で明確に分離
- 47都道府県の公式入口を手動確認
- 47都道府県の現行政策計画入口を索引化し、旧計画の誤昇格が0
- 47都道府県すべてに6資料カテゴリの明示的状態があり、`not_indexed`を不存在や0件へ変換していない
- Coverage、Reviewed、Publishedの状態が別々の正本から導出され、公開ページの有無をReviewedと混同していない
- 全国カバレッジのスキーマ検証、全回帰テスト、Lint、型検査、本番ビルド、静的出力検証が成功
- 公開サイトで47都道府県、全国品質指標、主要自治体ページ、メタデータ経路のProduction Smokeが成功
- [`data/catalog/phase7_completion.json`](../data/catalog/phase7_completion.json)が`complete`で、全ゲートが`passed`

### Scope handoff

- Phase 8：9地域拠点の実施計画・KPI・年度評価をEvidence Packet付きでReviewed化
- Phase 9：残る38県へ同じ深度を横展開し、比較可能性メタデータと更新履歴を整備

## Phase 8 — Regional anchor expansion

### Deliverables

- 北海道、宮城県、東京都、愛知県、大阪府、広島県、香川県、福岡県、沖縄県の計画体系
- 各都道府県の主要数値目標
- 年度実績・政策評価の入口
- 地域ごとの資料構造差に対応する抽出・レビュー手順

### Exit gate

- 9地域拠点すべてで総合計画と数値目標の公式入口を確認
- 各拠点にEvidence Packet付きReviewedデータ
- 目標値と年度実績の混同0
- 条件型・上限型・下限型・再掲・欠損の意味保持
- 公開ページが静的ビルドと本番Smokeを通過

## Phase 9 — Remaining prefectures

### Deliverables

- 残る38県の総合計画・数値目標
- 地域単位の収集・レビュー運用
- 横断検索と比較可能性メタデータ
- 更新周期・改定・旧計画の履歴

### Exit gate

- 47都道府県すべてで主要計画をIndexed以上
- 公開する数値のEvidence coverage 100%
- 再掲・欠損・単位・期間・母集団の品質テスト成功
- 比較不能な指標をランキングへ含めない

## Post-launch

1. 47都道府県の年度実績・重点事業・予算・契約を接続
2. 政令指定都市・中核市・県庁所在地
3. その他の市区町村
4. 議員・候補者・選挙比較
5. API、データダウンロード、報道・研究者向け機能

全国展開の詳細は [Nationwide expansion](NATIONWIDE_EXPANSION.md) を参照してください。
