# Public release checklist

最終更新: 2026-11-14

このチェックリストは、実装の有無ではなく、公開判断に必要な証跡がリポジトリ上で確認できるかを基準に管理します。

- `[x]` 証跡確認済み
- `[ ]` 未完了または最終確認未実施

## Current release position

- 公開状態: **pre-alpha**（正式なPublic betaの承認前）。GitHub Pagesで公開済み
- 直近の公開検証: 2026-11-13 success（`.github/publication-status.json`）
- Phase 11: 全国47都道府県・15,327個票を共通Schemaで正規化／公式一次資料上の最大到達深度まで完了
- Phase 13: 政令指定都市20/20のv1 record-review foundation完了（うち2市はReviewed reference）
- Phase 14: 中核市・県庁所在地67/67の公式Source Inventory完了
- Phase 15: 4/67自治体 reviewed_complete、1自治体 review_in_progress、62自治体 pending_record_review（正本キューの更新日は2026-10-09）
- 各Phaseの`complete`は全政策・予算・事業・契約・実績の完全な接続や全国比較可能性を保証しない
- Public betaの未完了事項は、訂正・反論の通し試験、外部法務・中立性レビュー、実機アクセシビリティ監査、障害復旧・運用確認、最終公開承認
- 正式な公開判断の親Issue: [#12 Public beta trust and launch gate](https://github.com/M-Osugi1230/jichi-insight/issues/12)
- **Phase 15の全67自治体レビュー完了はPublic betaの必須条件ではない**。未完了範囲を明示し、審査済みデータのみ公開する


## Data

- [x] 47都道府県の公式入口と現行政策計画
- [x] 47都道府県のEvidence-backed Reviewed政策目標
- [x] 年度実績、予算、決算、重点事業、監査の文書スコープ接続
- [x] 契約、議会、首長公約のReviewed coverage
- [x] 計画版、報告年度、測定年度、会計区分の分離
- [x] 予算、決算、事業費、契約額の分離
- [x] 比較可能性未確認のランキングを公開しない
- [x] 独自の政策達成・未達判定を公開しない
- [x] Wave 1の861個票を全件正規化・統合検証
- [x] 愛知県56行・62系列を全件正規化
- [x] 大阪府83行・91系列を全件正規化
- [x] 広島県62指標を全件正規化
- [x] 香川県135固有指標・141表示箇所を全件正規化
- [x] 沖縄県375指標をReviewed最大到達深度として全件正規化
- [x] 沖縄県の計画基準値を年度実績へ昇格しない
- [x] 沖縄県の全国値を沖縄県実績として扱わない
- [x] Wave 2の5拠点・711件を一つの統合ゲートで検証
- [x] Wave 3の38県・13,755個票をReviewed最大到達深度へ引き上げ（`data/catalog/phase11_completion.json`）
- [x] Phase 13の20政令指定都市のv1レビュー基盤を完了（`data/catalog/phase13_completion.json`）
- [x] Phase 14の67自治体の公式資料インベントリを完了（`data/catalog/phase14_completion.json`）
- [ ] Phase 15の残り63自治体の個票レビュー（うち盛岡市は進行中。Public betaの必須条件ではない）
- [ ] 議会発言、採決、監査指摘、首長公約を個票単位で接続
- [ ] 比較可能性確認済み指標だけを横断比較へ昇格

## Product

- [x] Home、全国カバレッジ、47都道府県ページ
- [x] Phase 9 Reviewed目標ページ
- [x] Phase 10完了・深度マトリクスページ
- [x] 方法論、データ品質、出典、欠損表示
- [x] 利用規約、プライバシー、免責ページ
- [x] `robots.txt`、`sitemap.xml`、静的出力、GitHub Pages配信
- [ ] Phase 11個票接続の公開進捗ページ
- [ ] 個別事業ページの全国共通テンプレート
- [ ] 首長・公約ページ
- [ ] 議会・議案・採決ページ
- [ ] 比較可能性確認済み指標の比較画面
- [ ] 訂正申請フォームの本番送信テスト
- [ ] 変更履歴の公開画面
- [ ] 404、空状態、エラー状態の本番確認

## Trust

- [x] 事実、比較、解釈、評価を分離
- [x] 一次資料優先、未確認を推測で補完しない
- [x] 政治思想、政党、人物の好悪を採点しない
- [x] 首長、行政、議会、監査を役割別に扱う
- [x] 根拠不足時に評価しない品質状態
- [x] PartialとNot linkedをスキップしない
- [x] Wave 1のPartial 58件とNot linked 383件を未昇格保持
- [x] 愛知県の欠損値・目標改定・再掲を別状態として保持
- [x] 大阪府の将来目標・未調査値・旧系列・事業因果を推測しない
- [x] 広島県の未測定値・複合値・定性条件を原文保持
- [x] 香川県の目標版・再掲・訂正値・累積期間を原文保持
- [x] 沖縄県375件をannual actual未接続のPartialとして保持
- [x] 沖縄県の公式資料内異常値を無断訂正しない
- [ ] 訂正・反論フローの本番通し試験
- [ ] 中立性、方法論、重大表現の外部レビュー
- [ ] 公開可否レビューの承認記録

## Engineering

- [x] リポジトリ検証、全Pythonテスト、Lint、型検査、production build
- [x] Phase 10完了ゲート
- [x] Phase 11共通個票Schema
- [x] Wave 1全861件の統合ゲート
- [x] 愛知県・大阪府・広島県・香川県・沖縄県の決定的Normalizer
- [x] Wave 2全711件の統合Schema・参照整合性テスト
- [x] GitHub Pages、Publication Audit、本番HTTP verification、Production Smoke
- [x] Wave 3の地域バッチNormalizerと統合ゲート（Phase 11完了）
- [ ] mainブランチ保護設定の最終確認
- [ ] dependency audit、secrets scan、Actions least-privilege監査
- [ ] preview / staging / production境界の確定
- [ ] rollback、backup、monitoring、incident訓練

## UX and accessibility

- [x] スマートフォンを主要導線の前提として設計
- [x] 見出し構造と色だけに依存しない状態ラベル
- [x] 出典・品質・未確認範囲を主要ページに表示
- [ ] 実機スマートフォン、キーボード、スクリーンリーダー監査
- [ ] 画像・図表の代替テキスト、コントラスト監査
- [ ] Lighthouse accessibility測定
- [ ] 初見ユーザーによる3分理解テスト

## Legal and policy

- [x] 編集方針、データ品質、訂正・反論、データ方針
- [x] 利用規約、プライバシーポリシー、免責ページ
- [ ] 公開文書の外部法務確認
- [ ] コード、方法論、構造化データのライセンス確定
- [ ] 原資料の転載・引用範囲確認
- [ ] 個人情報、政治資金情報、要配慮情報の取扱確認

## Operations

- [x] リリース、訂正、障害、ロールバック、バックアップ手順
- [x] Production Smokeと公開検証の自動化
- [ ] 更新責任者とレビュー責任者を明記
- [ ] 定期更新頻度、計画改定検知、訂正回答期限を確定
- [ ] P0 / P1障害連絡経路を確定
- [ ] 公開後4週間の安定運用計測方法を確定

## Repository hygiene

- [x] 後続作業で置換済みの旧PRを閉じる
- [x] Wave 1のNormalizerと統合ゲート
- [x] Wave 2の5拠点Normalizerと統合ゲート
- [x] Phase 11実行キューと完了記録を全国47都道府県・15,327件へ更新
- [ ] 初期ロードマップIssueを現在の完了状態へ再分類
- [ ] README、Roadmap、Release Checklist、公開ページの状態同期を回帰テスト化

## Final go / no-go gates

正式なPublic betaへ進むには、最低限次をすべて満たします。

1. 本番CI、build、deployment、Publication Audit、Production Smokeが成功
2. 公開対象の主張に一次資料とEvidenceがある
3. 公開範囲と個票未接続範囲が主要画面で一致
4. 利用規約、プライバシー、免責、ライセンスの確認が完了
5. 訂正受付、変更履歴、障害対応、ロールバックを本番相当環境で試験
6. モバイル、キーボード、読み上げ、Lighthouse監査を完了
7. 外部レビューと重大表現の法務確認を完了
8. 公開責任者が公開境界と未収録範囲を承認

## Current recommendation（2026-11-14）

**正式Public betaを最優先の並走トラックとする。** Phase 15データの個票レビューは別トラックとして継続する。

1. Issue #12のTrust / Legal / Accessibility / Operationsについて、確認日・証跡URL・レビュアーを記録する。
2. 自動化可能なCI、定期Production Smoke、公開範囲の同期テスト、更新日表示を整備する。
3. 人による承認が必要な法務、重大表現・中立性、訂正フローの本番相当試験、読み上げ・実機テストを実施する。
4. P0/P1既知問題0件とGo / No-Go承認を確認して初めて「Public beta」と表記する。
5. Phase 15は正本キューとhuman reviewを維持し、未検証候補をReviewedとして公開しない。

進捗の正本は`data/catalog/phase15_core_capital_review_queue.json`および`data/catalog/phase11_completion.json`。このチェックリストは公開判断の証跡であり、実装やレビューの完了を推定してチェックしない。
